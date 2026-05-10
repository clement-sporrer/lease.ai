import { supabase } from '@/src/lib/supabase'

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000'

type JsonPrimitive = string | number | boolean | null
type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue }

type ApiEnvelope<T> = {
  data: T
  meta?: { total?: number; page?: number; per_page?: number }
}

type ApiErrorBody = {
  error?: {
    code?: string
    message?: string
    details?: Record<string, JsonValue>
  }
}

export class ApiError extends Error {
  status: number
  code?: string
  details?: Record<string, JsonValue>

  constructor(message: string, status: number, code?: string, details?: Record<string, JsonValue>) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

async function getAuthHeaders(extraHeaders?: HeadersInit): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (!token) throw new ApiError('Not authenticated', 401, 'NOT_AUTHENTICATED')

  const normalized: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }

  if (extraHeaders instanceof Headers) {
    extraHeaders.forEach((value, key) => {
      normalized[key] = value
    })
  } else if (Array.isArray(extraHeaders)) {
    for (const [key, value] of extraHeaders) normalized[key] = value
  } else if (extraHeaders) {
    Object.assign(normalized, extraHeaders)
  }

  return normalized
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await getAuthHeaders(init?.headers)
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  })

  const rawText = await response.text()
  const contentType = response.headers.get('content-type') ?? ''
  const isJson = contentType.includes('application/json') || contentType.includes('+json')
  let parsed: unknown = null

  if (rawText) {
    if (isJson) {
      try {
        parsed = JSON.parse(rawText)
      } catch {
        parsed = rawText
      }
    } else {
      parsed = rawText
    }
  }

  if (!response.ok) {
    const errorBody =
      parsed && typeof parsed === 'object' ? (parsed as ApiErrorBody) : null
    const message =
      errorBody?.error?.message ??
      (typeof parsed === 'string' && parsed.trim()
        ? parsed.trim()
        : `Request failed with status ${response.status}`)
    throw new ApiError(
      message,
      response.status,
      errorBody?.error?.code,
      errorBody?.error?.details,
    )
  }

  if (parsed && typeof parsed === 'object' && 'data' in (parsed as ApiEnvelope<T>)) {
    return (parsed as ApiEnvelope<T>).data
  }

  if (isJson || !rawText) {
    return parsed as T
  }

  throw new ApiError(
    `Unexpected non-JSON response from ${path}`,
    response.status,
    'INVALID_RESPONSE',
  )
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'GET' })
}

export function apiPost<T>(path: string, body: unknown, headers?: HeadersInit): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
}

export function apiPatch<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'PATCH',
    body: JSON.stringify(body),
  })
}

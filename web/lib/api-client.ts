const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export async function apiFetch<T>(
  path: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const code = (body as { error?: { code?: string } })?.error?.code ?? 'UNKNOWN'
    const message =
      (body as { error?: { message?: string } })?.error?.message ?? `HTTP ${response.status}`
    throw new Error(`[${code}] ${message}`)
  }

  return response.json() as Promise<T>
}

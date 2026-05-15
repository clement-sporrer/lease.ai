'use client'

import { useRef, useState } from 'react'
import { createBrowserClient } from '@supabase/ssr'
import { ProvenanceBadge } from '@/components/shared/ProvenanceBadge'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

interface ExtractionResult {
  extraction_source: string | null
  line_items?: unknown[]
}

interface Props {
  dealId: string
  onSuccess?: () => void
}

function createSupabaseBrowser() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

async function getAccessToken(): Promise<string | null> {
  const supabase = createSupabaseBrowser()
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token ?? null
}

export function QuoteUploadZone({ dealId, onSuccess }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [result, setResult] = useState<ExtractionResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleFile(file: File) {
    if (file.type !== 'application/pdf') {
      setError('Seuls les fichiers PDF sont acceptés.')
      return
    }

    setIsExtracting(true)
    setError(null)
    setResult(null)

    try {
      const token = await getAccessToken()
      if (!token) {
        setError('Session expirée — veuillez vous reconnecter.')
        return
      }

      const response = await fetch(
        `${API_BASE}/deals/${dealId}/quotes/upload-and-extract`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/pdf',
          },
          body: file,
        }
      )

      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        const message =
          (body as { error?: { message?: string } })?.error?.message ??
          `Erreur ${response.status}`
        setError(message)
        return
      }

      const data = (await response.json()) as ExtractionResult
      setResult(data)
      onSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur inattendue est survenue.')
    } finally {
      setIsExtracting(false)
    }
  }

  function onDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragging(true)
  }

  function onDragLeave(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragging(false)
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) void handleFile(file)
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) void handleFile(file)
    // reset so same file can be re-uploaded
    e.target.value = ''
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6">
      <h2 className="mb-4 text-base font-semibold" style={{ color: '#0D183D' }}>
        Upload devis (PDF)
      </h2>

      <div
        role="button"
        tabIndex={0}
        aria-label="Zone de dépôt de fichier PDF"
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        className={`flex min-h-[120px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed transition-colors ${
          isDragging
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100'
        }`}
      >
        {isExtracting ? (
          <div className="flex flex-col items-center gap-2">
            <Spinner />
            <span className="text-sm text-gray-500">Extraction en cours…</span>
          </div>
        ) : (
          <span className="text-sm text-gray-400">
            Glisser un PDF ici ou cliquer pour sélectionner
          </span>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={onInputChange}
      />

      {result && (
        <div className="mt-4 flex items-center gap-2">
          <ProvenanceBadge source={result.extraction_source} />
          <span className="text-sm text-teal-700">Extraction réussie</span>
          {Array.isArray(result.line_items) && result.line_items.length > 0 && (
            <span className="text-xs text-gray-500">
              ({result.line_items.length} ligne{result.line_items.length > 1 ? 's' : ''})
            </span>
          )}
        </div>
      )}

      {error && (
        <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>
      )}
    </div>
  )
}

function Spinner() {
  return (
    <svg
      className="h-5 w-5 animate-spin text-blue-500"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  )
}

'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import type { DocumentItem } from '@/lib/types/admin'

const STATUS_COLOR: Record<string, string> = {
  validated: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  uploaded: 'bg-blue-100 text-blue-800',
  pending: 'bg-gray-100 text-gray-600',
  pending_upload: 'bg-gray-100 text-gray-600',
}

const STATUS_LABEL: Record<string, string> = {
  validated: 'Validé',
  rejected: 'Refusé',
  uploaded: 'Uploadé',
  pending: 'En attente',
  pending_upload: "En attente d'upload",
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

interface Props {
  documents: DocumentItem[]
  canWrite: boolean
  token: string
}

export function DocumentList({ documents, canWrite, token }: Props) {
  const router = useRouter()
  const [loadingId, setLoadingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function validate(docId: string) {
    setLoadingId(docId)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}/validate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({})) as { error?: { message?: string } }
        setError(body?.error?.message ?? 'Erreur lors de la validation')
      } else {
        router.refresh()
      }
    } catch {
      setError('Erreur réseau')
    } finally {
      setLoadingId(null)
    }
  }

  async function reject(docId: string) {
    const reason = window.prompt('Raison du refus :')
    if (!reason?.trim()) return
    setLoadingId(docId)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}/reject`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({})) as { error?: { message?: string } }
        setError(body?.error?.message ?? 'Erreur lors du refus')
      } else {
        router.refresh()
      }
    } catch {
      setError('Erreur réseau')
    } finally {
      setLoadingId(null)
    }
  }

  return (
    <div className="mb-4 rounded-xl border border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-700">
        Documents
      </h3>
      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}
      {documents.length === 0 ? (
        <p className="text-sm text-gray-400">Aucun document.</p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {documents.map((doc) => (
            <li key={doc.id} className="flex items-center justify-between gap-4 py-3">
              <div className="flex min-w-0 items-center gap-3">
                <span
                  className={`inline-flex shrink-0 items-center rounded px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[doc.status] ?? 'bg-gray-100 text-gray-600'}`}
                >
                  {STATUS_LABEL[doc.status] ?? doc.status}
                </span>
                <span className="truncate text-sm text-gray-700">{doc.file_name || doc.type}</span>
              </div>
              {canWrite && doc.status !== 'validated' && doc.status !== 'rejected' && (
                <div className="flex shrink-0 gap-2">
                  <button
                    onClick={() => validate(doc.id)}
                    disabled={loadingId === doc.id}
                    className="rounded border border-green-300 px-3 py-1 text-xs text-green-700 hover:bg-green-50 disabled:opacity-50"
                  >
                    Valider
                  </button>
                  <button
                    onClick={() => reject(doc.id)}
                    disabled={loadingId === doc.id}
                    className="rounded border border-red-300 px-3 py-1 text-xs text-red-700 hover:bg-red-50 disabled:opacity-50"
                  >
                    Refuser
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

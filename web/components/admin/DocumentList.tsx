'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { EmptyState } from '@/components/shared/EmptyState'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Button } from '@/components/ui/button'
import type { DocumentItem } from '@/lib/types/admin'
import { DocumentViewerButton } from '@/components/admin/DocumentViewer'

const DOC_STATUS_MAP: Record<string, string> = {
  validated: 'financier_approved',
  rejected: 'financier_rejected',
  uploaded: 'submitted',
  pending: 'draft',
  pending_upload: 'draft',
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

  async function postDoc(docId: string, path: string, body?: object) {
    setLoadingId(docId)
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}/${path}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        ...(body ? { body: JSON.stringify(body) } : {}),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({})) as { error?: { message?: string } }
        toast.error(data?.error?.message ?? 'Erreur serveur')
      } else {
        router.refresh()
      }
    } catch {
      toast.error('Erreur réseau')
    } finally {
      setLoadingId(null)
    }
  }

  async function handleReject(docId: string) {
    const reason = window.prompt('Raison du refus :')
    if (!reason?.trim()) return
    await postDoc(docId, 'reject', { reason })
  }

  return (
    <div className="mb-4 rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-50">
        <h3 className="text-sm font-semibold text-navy-900">Documents</h3>
      </div>
      {documents.length === 0 ? (
        <EmptyState title="Aucun document" subtitle="Les documents uploadés par le partenaire apparaîtront ici." />
      ) : (
        <ul className="divide-y divide-gray-50">
          {documents.map((doc) => (
            <li key={doc.id} className="flex items-center justify-between gap-4 px-6 py-3">
              <div className="flex min-w-0 items-center gap-3">
                <StatusBadge status={DOC_STATUS_MAP[doc.status] ?? 'draft'} className="shrink-0" />
                <span className="truncate text-sm text-gray-700">{doc.file_name || doc.type}</span>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                {doc.status !== 'pending_upload' && (
                  <DocumentViewerButton documentId={doc.id} fileName={doc.file_name || doc.type} />
                )}
                {canWrite && doc.status !== 'validated' && doc.status !== 'rejected' && (
                  <>
                    <Button variant="success" size="xs" onClick={() => postDoc(doc.id, 'validate')} disabled={loadingId === doc.id}>
                      Valider
                    </Button>
                    <Button variant="danger" size="xs" onClick={() => handleReject(doc.id)} disabled={loadingId === doc.id}>
                      Refuser
                    </Button>
                  </>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

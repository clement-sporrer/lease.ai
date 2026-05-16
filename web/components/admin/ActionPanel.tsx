'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

interface Props {
  dealId: string
  token: string
  canWrite: boolean
}

type Modal = 'request_doc' | 'pre_approve' | 'reject' | null

export function ActionPanel({ dealId, token, canWrite }: Props) {
  const router = useRouter()
  const [modal, setModal] = useState<Modal>(null)
  const [loading, setLoading] = useState(false)
  const [docType, setDocType] = useState('')
  const [reason, setReason] = useState('')
  const [justification, setJustification] = useState('')

  async function post(path: string, body: object) {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json() as { error?: { message?: string } }
      if (!res.ok) {
        toast.error(data?.error?.message ?? `Erreur ${res.status}`)
      } else {
        setModal(null)
        setDocType('')
        setReason('')
        setJustification('')
        toast.success('Action effectuée avec succès')
        router.refresh()
      }
    } catch {
      toast.error('Erreur réseau — réessayez.')
    } finally {
      setLoading(false)
    }
  }

  if (!canWrite) return null

  return (
    <div className="sticky bottom-0 flex items-center gap-3 border-t border-gray-200 bg-white px-8 py-4">
      <Button variant="warning" onClick={() => setModal('request_doc')}>
        Demander une pièce
      </Button>
      <Button variant="success" onClick={() => setModal('pre_approve')}>
        Pré-accorder
      </Button>
      <Button variant="danger" onClick={() => setModal('reject')}>
        Refuser
      </Button>

      {modal === 'request_doc' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h4 className="mb-4 font-semibold text-navy-900">Demander une pièce</h4>
            <label className="mb-1 block text-sm text-gray-600">Type de document</label>
            <input
              className="mb-3 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              placeholder="rib, kbis, id_card..."
            />
            <label className="mb-1 block text-sm text-gray-600">Raison</label>
            <textarea
              className="mb-4 w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setModal(null)}>
                Annuler
              </Button>
              <Button
                variant="warning"
                disabled={loading || !docType || !reason}
                onClick={() =>
                  post(`/admin/deals/${dealId}/request-document`, { document_type: docType, reason })
                }
              >
                Envoyer
              </Button>
            </div>
          </div>
        </div>
      )}

      {modal === 'pre_approve' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h4 className="mb-4 font-semibold text-navy-900">Pré-accorder le dossier</h4>
            <label className="mb-1 block text-sm text-gray-600">
              Justification{' '}
              <span className="font-normal text-gray-400">(requise si checklist incomplète)</span>
            </label>
            <textarea
              className="mb-4 w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setModal(null)}>
                Annuler
              </Button>
              <Button
                variant="success"
                disabled={loading}
                onClick={() =>
                  post(`/admin/deals/${dealId}/pre-approve`, { justification: justification || null })
                }
              >
                Confirmer
              </Button>
            </div>
          </div>
        </div>
      )}

      {modal === 'reject' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h4 className="mb-4 font-semibold text-navy-900">Refuser le dossier</h4>
            <label className="mb-1 block text-sm text-gray-600">
              Raison <span className="text-red-500">*</span>
            </label>
            <textarea
              className="mb-4 w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={() => setModal(null)}>
                Annuler
              </Button>
              <Button
                variant="danger"
                disabled={loading || !reason}
                onClick={() => post(`/admin/deals/${dealId}/reject`, { reason })}
              >
                Confirmer le refus
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

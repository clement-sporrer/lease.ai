'use client'

import { useState, useTransition } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { requestDocument, preApproveDeal, rejectDeal } from '@/lib/actions/admin-actions'

interface Props {
  dealId: string
  canWrite: boolean
}

type Modal = 'request_doc' | 'pre_approve' | 'reject' | null

export function ActionPanel({ dealId, canWrite }: Props) {
  const [isPending, startTransition] = useTransition()
  const [modal, setModal] = useState<Modal>(null)
  const [docType, setDocType] = useState('')
  const [reason, setReason] = useState('')
  const [justification, setJustification] = useState('')

  function closeModal() {
    setModal(null)
    setDocType('')
    setReason('')
    setJustification('')
  }

  function dispatch(action: () => Promise<{ error?: string }>) {
    startTransition(async () => {
      const result = await action()
      if (result.error) {
        toast.error(result.error)
      } else {
        closeModal()
        toast.success('Action effectuée avec succès')
      }
    })
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
              <Button variant="ghost" size="sm" onClick={closeModal}>
                Annuler
              </Button>
              <Button
                variant="warning"
                disabled={isPending || !docType || !reason}
                onClick={() => dispatch(() => requestDocument(dealId, docType, reason))}
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
              <Button variant="ghost" size="sm" onClick={closeModal}>
                Annuler
              </Button>
              <Button
                variant="success"
                disabled={isPending}
                onClick={() => dispatch(() => preApproveDeal(dealId, justification || null))}
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
              <Button variant="ghost" size="sm" onClick={closeModal}>
                Annuler
              </Button>
              <Button
                variant="danger"
                disabled={isPending || !reason}
                onClick={() => dispatch(() => rejectDeal(dealId, reason))}
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

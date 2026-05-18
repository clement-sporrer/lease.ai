'use client'

import { useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { activateContract } from '@/lib/actions/contract-actions'
import { Button } from '@/components/ui/button'
import type { ActivationChecklist as ActivationChecklistType, Contract } from '@/lib/types/contract'

const CHECKLIST_VISIBLE_STATUSES = new Set(['signed', 'activation_pending', 'active'])

interface Props {
  dealId: string
  dealStatus: string
  contract: Contract | null
  checklist: ActivationChecklistType | null
}

export function ActivationChecklist({ dealId, dealStatus, contract, checklist }: Props) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()

  if (!CHECKLIST_VISIBLE_STATUSES.has(dealStatus) || !contract) return null

  const isAlreadyActive = dealStatus === 'active'

  function handleActivate() {
    if (!contract) return
    startTransition(async () => {
      const result = await activateContract(contract.id, dealId)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        toast.success('Contrat activé — dossier actif')
        router.refresh()
      }
    })
  }

  const failedConditions = checklist?.items.filter(item => !item.satisfied) ?? []

  return (
    <div className="rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
        <h2 className="text-sm font-semibold text-navy-900">Checklist d&apos;activation</h2>
        {!isAlreadyActive && (
          <Button
            variant="primary"
            size="sm"
            onClick={handleActivate}
            disabled={isPending || !checklist?.all_satisfied}
            title={
              !checklist?.all_satisfied
                ? `${failedConditions.length} condition(s) manquante(s)`
                : undefined
            }
          >
            {isPending ? 'Activation…' : 'Activer le contrat'}
          </Button>
        )}
        {isAlreadyActive && (
          <span className="inline-flex items-center gap-1 rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700 ring-1 ring-teal-200">
            ✓ Actif
          </span>
        )}
      </div>
      <div className="px-6 py-5">
        {checklist ? (
          <ul className="space-y-2.5">
            {checklist.items.map(item => (
              <li key={item.key} className="flex items-center gap-3">
                <span
                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-bold ${
                    item.satisfied
                      ? 'bg-teal-100 text-teal-700'
                      : 'bg-red-50 text-red-500 ring-1 ring-red-200'
                  }`}
                >
                  {item.satisfied ? '✓' : '✗'}
                </span>
                <span className={`text-sm ${item.satisfied ? 'text-gray-700' : 'text-gray-500'}`}>
                  {item.label}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="italic text-gray-400 text-sm">Chargement de la checklist…</p>
        )}
        {!isAlreadyActive && failedConditions.length > 0 && (
          <p className="mt-4 text-xs text-red-500">
            {failedConditions.length} condition(s) à remplir avant activation.
          </p>
        )}
      </div>
    </div>
  )
}

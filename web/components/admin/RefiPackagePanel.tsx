'use client'

import { useState, useTransition } from 'react'
import { toast } from 'sonner'
import { createRefiPackage, sendRefiPackage } from '@/lib/actions/refi-actions'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { MoneyAmount } from '@/components/shared/MoneyAmount'
import type { Deal } from '@/lib/types/admin'
import type { RefiPackage } from '@/lib/types/refi'

interface Props {
  deal: Deal
  existingPackage: RefiPackage | null
}

export function RefiPackagePanel({ deal, existingPackage }: Props) {
  const [pkg, setPkg] = useState<RefiPackage | null>(existingPackage)
  const [isPending, startTransition] = useTransition()

  const canCreate = deal.status === 'pre_approved' && pkg === null
  const canSend = pkg?.status === 'draft'

  function handleCreate() {
    startTransition(async () => {
      const result = await createRefiPackage(deal.id)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        setPkg(result.data)
        toast.success('Package de refinancement créé')
      }
    })
  }

  function handleSend() {
    if (!pkg) return
    startTransition(async () => {
      const result = await sendRefiPackage(pkg.id, deal.id)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        setPkg(result.data)
        toast.success('Package envoyé au financier')
      }
    })
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden mb-4">
      <div className="px-6 py-4 border-b border-gray-50">
        <h2 className="text-sm font-semibold text-navy-900">Package de refinancement</h2>
      </div>
      <div className="px-6 py-5">
        {pkg ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Statut</span>
              <StatusBadge status={pkg.status} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Montant</span>
              <MoneyAmount cents={pkg.amount_cents} className="text-sm font-mono tabular-nums" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Durée</span>
              <span className="text-sm font-mono">
                {pkg.duration_months != null ? `${pkg.duration_months} mois` : '—'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Loyer mensuel</span>
              <MoneyAmount cents={pkg.monthly_payment_cents} className="text-sm font-mono tabular-nums" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Score risque</span>
              <span className="text-sm font-mono">
                {pkg.risk_band ?? '—'}{pkg.risk_score != null ? ` (${pkg.risk_score.toFixed(1)})` : ''}
              </span>
            </div>
            {canSend && (
              <Button variant="primary" className="mt-2 w-full" onClick={handleSend} disabled={isPending}>
                {isPending ? 'Envoi…' : 'Envoyer au financier'}
              </Button>
            )}
          </div>
        ) : (
          <div className="text-center py-4">
            <p className="text-sm text-gray-400 mb-4">Aucun package créé</p>
            {canCreate && (
              <Button variant="primary" onClick={handleCreate} disabled={isPending}>
                {isPending ? 'Création…' : 'Générer le package refi'}
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

'use client'

import { useState, useTransition } from 'react'
import { toast } from 'sonner'
import { createRefiPackage, sendRefiPackage } from '@/lib/actions/refi-actions'
import { MoneyAmount } from '@/components/shared/MoneyAmount'
import type { Deal } from '@/lib/types/admin'
import type { RefiPackage } from '@/lib/types/refi'

interface Props {
  deal: Deal
  existingPackage: RefiPackage | null
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  draft: { label: 'Brouillon', color: 'bg-gray-100 text-gray-600' },
  sent: { label: 'Envoyé au financier', color: 'bg-blue-50 text-blue-700' },
  financier_approved: { label: 'Approuvé', color: 'bg-teal-50 text-teal-700' },
  financier_rejected: { label: 'Refusé', color: 'bg-red-50 text-red-700' },
}

export function RefiPackagePanel({ deal, existingPackage }: Props) {
  const [pkg, setPkg] = useState<RefiPackage | null>(existingPackage)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  const canCreate = deal.status === 'pre_approved' && pkg === null
  const canSend = pkg?.status === 'draft'

  function handleCreate() {
    setError(null)
    startTransition(async () => {
      const result = await createRefiPackage(deal.id)
      if ('error' in result) {
        toast.error(result.error)
        setError(result.error)
      } else {
        setPkg(result.data)
        toast.success('Package de refinancement créé')
      }
    })
  }

  function handleSend() {
    if (!pkg) return
    setError(null)
    startTransition(async () => {
      const result = await sendRefiPackage(pkg.id, deal.id)
      if ('error' in result) {
        toast.error(result.error)
        setError(result.error)
      } else {
        setPkg(result.data)
        toast.success('Package envoyé au financier')
      }
    })
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
      <h2 className="text-base font-semibold mb-4" style={{ color: '#0D183D' }}>
        Package de refinancement
      </h2>

      {pkg ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Statut</span>
            <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_LABELS[pkg.status]?.color ?? 'bg-gray-100 text-gray-600'}`}>
              {STATUS_LABELS[pkg.status]?.label ?? pkg.status}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Montant</span>
            <MoneyAmount cents={pkg.amount_cents} className="text-sm" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Durée</span>
            <span className="text-sm font-mono">
              {pkg.duration_months !== null && pkg.duration_months !== undefined
                ? `${pkg.duration_months} mois`
                : '—'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Loyer mensuel</span>
            <MoneyAmount cents={pkg.monthly_payment_cents} className="text-sm" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Score risque</span>
            <span className="text-sm font-mono">
              {pkg.risk_band ?? '—'}{pkg.risk_score != null ? ` (${pkg.risk_score.toFixed(1)})` : ''}
            </span>
          </div>

          {canSend && (
            <button
              onClick={handleSend}
              disabled={isPending}
              className="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isPending ? 'Envoi…' : 'Envoyer au financier'}
            </button>
          )}
        </div>
      ) : (
        <div className="text-center py-6">
          <p className="text-sm text-gray-400 mb-4">Aucun package créé</p>
          {canCreate && (
            <button
              onClick={handleCreate}
              disabled={isPending}
              className="rounded-lg px-5 py-2 text-sm font-medium text-white disabled:opacity-50 transition-colors"
              style={{ backgroundColor: '#0D183D' }}
            >
              {isPending ? 'Création…' : 'Générer le package refi'}
            </button>
          )}
        </div>
      )}

      {error && (
        <p className="mt-3 text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>
      )}
    </div>
  )
}

'use client'

import { useTransition, useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { generateOffer } from '@/lib/actions/offer-actions'
import { MoneyAmount } from '@/components/shared/MoneyAmount'
import type { Offer } from '@/lib/types/offer'

const GENERATABLE_STATUSES = new Set(['financier_approved', 'firm_offer_generated'])

interface Props {
  dealId: string
  activeOffer: Offer | null
  dealStatus: string
}

export function OfferPanel({ dealId, activeOffer, dealStatus }: Props) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [error, setError] = useState<string | null>(null)

  const canGenerate = GENERATABLE_STATUSES.has(dealStatus)
  const nextVersion = (activeOffer?.version ?? 0) + 1

  function handleGenerate() {
    setError(null)
    startTransition(async () => {
      const result = await generateOffer(dealId)
      if ('error' in result) {
        toast.error(result.error)
        setError(result.error)
      } else {
        toast.success(`Offre V${nextVersion} générée`)
        router.refresh()
      }
    })
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-semibold" style={{ color: '#0D183D' }}>
          Offre ferme
        </h2>
        <button
          onClick={handleGenerate}
          disabled={isPending || !canGenerate}
          className="rounded-lg bg-blue-600 px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-40"
        >
          {isPending ? 'Génération…' : `Générer V${nextVersion}`}
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      {activeOffer ? (
        <div className="space-y-2.5">
          <Row label={`Version V${activeOffer.version}`}>
            <span
              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium ${
                activeOffer.is_active
                  ? 'bg-teal-50 text-teal-700 ring-1 ring-teal-200'
                  : 'bg-gray-100 text-gray-500'
              }`}
            >
              {activeOffer.is_active ? '✓ Actif' : '✗ Inactif'}
            </span>
          </Row>
          <Row label="Montant">
            <MoneyAmount cents={activeOffer.amount_cents} className="text-sm" />
          </Row>
          <Row label="Mensualité">
            <MoneyAmount cents={activeOffer.monthly_payment_cents} className="text-sm" />
          </Row>
          <Row label="Durée">
            <span className="font-mono text-sm tabular-nums">
              {activeOffer.duration_months != null ? `${activeOffer.duration_months} mois` : '—'}
            </span>
          </Row>
          {activeOffer.risk_band && (
            <Row label="Bande de risque">
              <span className="font-mono text-sm">{activeOffer.risk_band}</span>
            </Row>
          )}
          {activeOffer.valid_until && (
            <Row label="Valide jusqu'au">
              <span className="text-sm text-gray-600">
                {new Date(activeOffer.valid_until).toLocaleDateString('fr-FR')}
              </span>
            </Row>
          )}
        </div>
      ) : (
        <p className="italic text-gray-400">Aucune offre générée</p>
      )}
    </div>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-500">{label}</span>
      {children}
    </div>
  )
}

import type { Deal } from '@/lib/types/admin'

function fmt(cents: number | null): string {
  if (cents === null) return '—'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100)
}

export function QuoteSummary({ deal }: { deal: Deal }) {
  return (
    <div className="mb-4 rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-50">
        <h3 className="text-sm font-semibold text-navy-900">Devis</h3>
      </div>
      <div className="px-6 py-5">
        <dl className="grid grid-cols-3 gap-x-6 gap-y-3 text-sm">
          <div>
            <dt className="text-xs text-gray-400 mb-0.5">Montant total</dt>
            <dd className="font-mono font-semibold tabular-nums text-gray-800">
              {fmt(deal.amount_cents)}
            </dd>
          </div>
          <div>
            <dt className="text-xs text-gray-400 mb-0.5">Durée</dt>
            <dd className="text-gray-800">
              {deal.duration_months ? `${deal.duration_months} mois` : '—'}
            </dd>
          </div>
          <div>
            <dt className="text-xs text-gray-400 mb-0.5">Mensualité indicative</dt>
            <dd className="font-mono font-semibold tabular-nums text-gray-800">
              {fmt(deal.monthly_payment_cents)}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  )
}

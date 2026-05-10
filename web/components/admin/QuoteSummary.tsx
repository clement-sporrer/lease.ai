import type { Deal } from '@/lib/types/admin'

function fmt(cents: number | null): string {
  if (cents === null) return '—'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100)
}

export function QuoteSummary({ deal }: { deal: Deal }) {
  return (
    <div className="mb-4 rounded-xl border border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-700">Devis</h3>
      <dl className="grid grid-cols-3 gap-x-6 gap-y-3 text-sm">
        <div>
          <dt className="text-gray-500">Montant total</dt>
          <dd className="font-semibold tabular-nums">{fmt(deal.amount_cents)}</dd>
        </div>
        <div>
          <dt className="text-gray-500">Durée</dt>
          <dd>{deal.duration_months ? `${deal.duration_months} mois` : '—'}</dd>
        </div>
        <div>
          <dt className="text-gray-500">Mensualité indicative</dt>
          <dd className="font-semibold tabular-nums">{fmt(deal.monthly_payment_cents)}</dd>
        </div>
      </dl>
    </div>
  )
}

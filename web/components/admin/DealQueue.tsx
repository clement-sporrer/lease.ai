import Link from 'next/link'
import { EmptyState } from '@/components/shared/EmptyState'
import { StatusBadge } from '@/components/shared/StatusBadge'
import type { Deal } from '@/lib/types/admin'

function formatAmount(cents: number | null): string {
  if (cents === null) return '—'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100)
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function DealQueue({ deals }: { deals: Deal[] }) {
  if (deals.length === 0) {
    return <EmptyState title="Aucun dossier en attente" subtitle="Les nouveaux dossiers soumis apparaîtront ici." />
  }

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-left bg-gray-50/60">
          <th className="px-6 py-3 pr-4">Réf</th>
          <th className="py-3 pr-4">Statut</th>
          <th className="py-3 pr-4">Montant</th>
          <th className="py-3 pr-4">Durée</th>
          <th className="py-3 pr-4">Score</th>
          <th className="py-3 pr-6">Mis à jour</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-50">
        {deals.map((deal) => (
          <tr key={deal.id} className="hover:bg-gray-50/70 transition-colors group">
            <td className="px-6 py-3 pr-4">
              <Link
                href={`/admin/deals/${deal.id}`}
                className="font-mono text-xs text-navy-900/50 group-hover:text-navy-900 transition-colors"
              >
                {deal.public_id}
              </Link>
            </td>
            <td className="py-3 pr-4">
              <StatusBadge status={deal.status} />
            </td>
            <td className="py-3 pr-4 font-mono text-xs tabular-nums text-gray-700">
              {formatAmount(deal.amount_cents)}
            </td>
            <td className="py-3 pr-4 text-gray-600">
              {deal.duration_months ? `${deal.duration_months} mois` : '—'}
            </td>
            <td className="py-3 pr-4">
              {deal.risk_score !== null ? (
                <span className="font-mono text-xs tabular-nums text-gray-700">
                  {Math.round(deal.risk_score)}/100
                </span>
              ) : (
                <span className="text-gray-300">—</span>
              )}
            </td>
            <td className="py-3 pr-6 text-xs text-gray-400 tabular-nums">
              {formatDate(deal.updated_at)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

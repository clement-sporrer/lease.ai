import Link from 'next/link'
import type { Deal } from '@/lib/types/admin'

const STATUS_LABEL: Record<string, string> = {
  submitted: 'Soumis',
  internal_review: 'En révision',
  missing_documents: 'Pièces manquantes',
}

const STATUS_COLOR: Record<string, string> = {
  submitted: 'bg-blue-100 text-blue-800',
  internal_review: 'bg-yellow-100 text-yellow-800',
  missing_documents: 'bg-red-100 text-red-800',
}

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
    return (
      <p className="py-8 text-center text-sm text-gray-400">Aucun dossier en attente.</p>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-xs uppercase tracking-wide text-gray-500">
            <th className="pb-3 pr-4 font-medium">ID</th>
            <th className="pb-3 pr-4 font-medium">Statut</th>
            <th className="pb-3 pr-4 font-medium">Montant</th>
            <th className="pb-3 pr-4 font-medium">Durée</th>
            <th className="pb-3 pr-4 font-medium">Score</th>
            <th className="pb-3 font-medium">Mis à jour</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {deals.map((deal) => (
            <tr key={deal.id} className="transition-colors hover:bg-gray-50">
              <td className="py-3 pr-4">
                <Link
                  href={`/admin/deals/${deal.id}`}
                  className="font-mono text-xs text-blue-600 hover:underline"
                >
                  {deal.public_id}
                </Link>
              </td>
              <td className="py-3 pr-4">
                <span
                  className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[deal.status] ?? 'bg-gray-100 text-gray-700'}`}
                >
                  {STATUS_LABEL[deal.status] ?? deal.status}
                </span>
              </td>
              <td className="py-3 pr-4 tabular-nums">{formatAmount(deal.amount_cents)}</td>
              <td className="py-3 pr-4">
                {deal.duration_months ? `${deal.duration_months} mois` : '—'}
              </td>
              <td className="py-3 pr-4">
                {deal.risk_score !== null ? (
                  <span className="tabular-nums">{Math.round(deal.risk_score)}/100</span>
                ) : (
                  <span className="text-gray-400">—</span>
                )}
              </td>
              <td className="py-3 text-gray-500">{formatDate(deal.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

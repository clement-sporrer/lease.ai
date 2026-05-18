import { StatusBadge } from '@/components/shared/StatusBadge'
import type { Deal } from '@/lib/types/admin'

export function DealReviewHeader({ deal }: { deal: Deal }) {
  const updatedAt = new Date(deal.updated_at).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
  return (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <div className="mb-2 flex items-center gap-3">
          <h2 className="font-mono text-lg font-bold text-navy-900 tabular-nums">
            {deal.public_id}
          </h2>
          <StatusBadge status={deal.status} />
        </div>
        <p className="text-xs text-gray-400">Mis à jour le {updatedAt}</p>
      </div>
    </div>
  )
}

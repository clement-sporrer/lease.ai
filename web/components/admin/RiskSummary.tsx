import { RiskBadge } from '@/components/shared/StatusBadge'
import type { Deal } from '@/lib/types/admin'

const BAND_LABEL: Record<string, string> = {
  A: 'Très faible',
  B: 'Faible',
  C: 'Modéré',
  D: 'Élevé',
  E: 'Très élevé',
}

export function RiskSummary({ deal }: { deal: Deal }) {
  return (
    <div className="mb-4 rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-50">
        <h3 className="text-sm font-semibold text-navy-900">Score de risque</h3>
      </div>
      <div className="px-6 py-5">
        {deal.risk_score !== null && deal.risk_band ? (
          <div className="flex items-center gap-4">
            <span className="font-mono text-3xl font-bold text-navy-900 tabular-nums">
              {Math.round(deal.risk_score)}
            </span>
            <span className="text-sm text-gray-400">/100</span>
            <RiskBadge band={deal.risk_band} />
            {BAND_LABEL[deal.risk_band] && (
              <span className="text-sm text-gray-500">{BAND_LABEL[deal.risk_band]}</span>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-400">Score non calculé.</p>
        )}
      </div>
    </div>
  )
}

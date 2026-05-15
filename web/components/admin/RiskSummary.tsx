import type { Deal } from '@/lib/types/admin'

const BAND_COLOR: Record<string, string> = {
  A: 'bg-green-100 text-green-800',
  B: 'bg-teal-100 text-teal-800',
  C: 'bg-yellow-100 text-yellow-800',
  D: 'bg-orange-100 text-orange-800',
  E: 'bg-red-100 text-red-800',
}

const BAND_LABEL: Record<string, string> = {
  A: 'Très faible',
  B: 'Faible',
  C: 'Modéré',
  D: 'Élevé',
  E: 'Très élevé',
}

export function RiskSummary({ deal }: { deal: Deal }) {
  const band = deal.risk_band
  return (
    <div className="mb-4 rounded-xl border border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-700">
        Score de risque
      </h3>
      {deal.risk_score !== null && band ? (
        <div className="flex items-center gap-4">
          <span className="font-mono text-3xl font-bold">{Math.round(deal.risk_score)}</span>
          <span className="text-sm text-gray-500">/100</span>
          <span
            className={`inline-flex items-center rounded px-2.5 py-0.5 text-xs font-semibold ${BAND_COLOR[band] ?? 'bg-gray-100 text-gray-700'}`}
          >
            {BAND_LABEL[band] ?? band}
          </span>
        </div>
      ) : (
        <p className="text-sm text-gray-400">Score non calculé.</p>
      )}
    </div>
  )
}

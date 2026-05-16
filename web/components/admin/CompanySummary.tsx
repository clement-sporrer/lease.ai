import { ProvenanceBadge } from '@/components/shared/ProvenanceBadge'

interface CompanyData {
  name?: string
  siren?: string
  sector?: string
  creation_date?: string
  is_recent?: boolean
  is_inactive?: boolean
  enrichment_source?: string
}

export function CompanySummary({ enrichment }: { enrichment?: CompanyData }) {
  return (
    <div className="mb-4 rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="flex items-center gap-2 px-6 py-4 border-b border-gray-50">
        <h3 className="text-sm font-semibold text-navy-900">Entreprise</h3>
        {enrichment?.enrichment_source && (
          <ProvenanceBadge source={enrichment.enrichment_source} />
        )}
      </div>
      <div className="px-6 py-5">
        {enrichment ? (
          <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Nom</dt>
              <dd className="font-medium text-gray-800">{enrichment.name ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">SIREN</dt>
              <dd className="font-mono text-gray-800">{enrichment.siren ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Secteur</dt>
              <dd className="text-gray-800">{enrichment.sector ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Création</dt>
              <dd className="text-gray-800">{enrichment.creation_date ?? '—'}</dd>
            </div>
            {enrichment.is_recent && (
              <div className="col-span-2">
                <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-yellow-50 text-yellow-700">
                  Société récente
                </span>
              </div>
            )}
            {enrichment.is_inactive && (
              <div className="col-span-2">
                <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-red-50 text-red-700">
                  Société inactive
                </span>
              </div>
            )}
          </dl>
        ) : (
          <p className="text-sm text-gray-400">Données non disponibles.</p>
        )}
      </div>
    </div>
  )
}

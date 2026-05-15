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
    <div className="mb-4 rounded-xl border border-gray-200 bg-white p-6">
      <div className="mb-4 flex items-center gap-2">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-700">
          Entreprise
        </h3>
        {enrichment?.enrichment_source && (
          <ProvenanceBadge source={enrichment.enrichment_source} />
        )}
      </div>
      {enrichment ? (
        <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
          <div>
            <dt className="text-gray-500">Nom</dt>
            <dd className="font-medium">{enrichment.name ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">SIREN</dt>
            <dd className="font-mono">{enrichment.siren ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Secteur</dt>
            <dd>{enrichment.sector ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Création</dt>
            <dd>{enrichment.creation_date ?? '—'}</dd>
          </div>
          {enrichment.is_recent && (
            <div className="col-span-2">
              <span className="inline-flex items-center rounded px-2 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-800">
                ⚠ Société récente
              </span>
            </div>
          )}
          {enrichment.is_inactive && (
            <div className="col-span-2">
              <span className="inline-flex items-center rounded px-2 py-0.5 text-xs font-medium bg-red-100 text-red-800">
                ⚠ Société inactive
              </span>
            </div>
          )}
        </dl>
      ) : (
        <p className="text-sm text-gray-400">Données non disponibles.</p>
      )}
    </div>
  )
}

import type { Deal, DealStatus } from '@/lib/types/admin'

const STATUS_LABEL: Record<DealStatus, string> = {
  draft: 'Brouillon',
  company_enriched: 'Entreprise enrichie',
  quote_added: 'Devis ajouté',
  indicative_offer_ready: 'Offre indicative',
  submitted: 'Soumis',
  internal_review: 'En révision',
  missing_documents: 'Pièces manquantes',
  pre_approved: 'Pré-accordé',
  financier_rejected: 'Refusé',
  refi_package_ready: 'Package refi prêt',
  refi_review: 'Révision financeur',
  financier_approved: 'Approuvé financeur',
  firm_offer_generated: 'Offre ferme',
  contract_generated: 'Contrat généré',
  signing: 'Signature',
  signed: 'Signé',
  activation_pending: 'Activation en cours',
  active: 'Actif',
  cancelled: 'Annulé',
}

const STATUS_COLOR: Record<string, string> = {
  submitted: 'bg-blue-100 text-blue-800',
  internal_review: 'bg-yellow-100 text-yellow-800',
  missing_documents: 'bg-red-100 text-red-800',
  pre_approved: 'bg-green-100 text-green-800',
  financier_rejected: 'bg-red-200 text-red-900',
}

export function DealReviewHeader({ deal }: { deal: Deal }) {
  const color = STATUS_COLOR[deal.status] ?? 'bg-gray-100 text-gray-700'
  const submittedAt = new Date(deal.created_at).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
  return (
    <div className="mb-8 flex items-start justify-between">
      <div>
        <div className="mb-1 flex items-center gap-3">
          <h2 className="font-mono text-lg font-bold text-gray-900">{deal.public_id}</h2>
          <span
            className={`inline-flex items-center rounded px-2.5 py-0.5 text-xs font-semibold ${color}`}
          >
            {STATUS_LABEL[deal.status] ?? deal.status}
          </span>
        </div>
        <p className="text-sm text-gray-500">Soumis le {submittedAt}</p>
      </div>
    </div>
  )
}

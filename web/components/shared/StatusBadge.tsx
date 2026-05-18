import { cn } from '@/lib/utils'

type Tone = 'gray' | 'blue' | 'yellow' | 'orange' | 'green' | 'teal' | 'red'

const TONE_CLASSES: Record<Tone, { badge: string; dot: string }> = {
  gray:   { badge: 'bg-gray-100 text-gray-600',     dot: 'bg-gray-400' },
  blue:   { badge: 'bg-blue-50 text-blue-700',      dot: 'bg-blue-500' },
  yellow: { badge: 'bg-yellow-50 text-yellow-700',  dot: 'bg-yellow-500' },
  orange: { badge: 'bg-orange-50 text-orange-700',  dot: 'bg-orange-500' },
  green:  { badge: 'bg-green-50 text-green-700',    dot: 'bg-green-500' },
  teal:   { badge: 'bg-teal-50 text-teal-700',      dot: 'bg-teal-500' },
  red:    { badge: 'bg-red-50 text-red-700',        dot: 'bg-red-500' },
}

const DEAL_STATUS: Record<string, { label: string; tone: Tone }> = {
  draft:                  { label: 'Brouillon',      tone: 'gray' },
  company_enriched:       { label: 'Enrichi',        tone: 'blue' },
  quote_added:            { label: 'Devis ajouté',   tone: 'blue' },
  indicative_offer_ready: { label: 'Offre indicative', tone: 'blue' },
  submitted:              { label: 'Soumis',         tone: 'blue' },
  internal_review:        { label: 'En révision',    tone: 'yellow' },
  missing_documents:      { label: 'Docs manquants', tone: 'orange' },
  pre_approved:           { label: 'Pré-approuvé',   tone: 'green' },
  refi_package_ready:     { label: 'Refi préparé',   tone: 'teal' },
  refi_review:            { label: 'Refi en cours',  tone: 'teal' },
  financier_approved:     { label: 'Approuvé',       tone: 'green' },
  financier_rejected:     { label: 'Refusé',         tone: 'red' },
  firm_offer_generated:   { label: 'Offre ferme',    tone: 'teal' },
  contract_generated:     { label: 'Contrat généré', tone: 'teal' },
  signing:                { label: 'Signature',      tone: 'yellow' },
  signed:                 { label: 'Signé',          tone: 'green' },
  activation_pending:     { label: 'Activation…',   tone: 'yellow' },
  active:                 { label: 'Actif',          tone: 'teal' },
  // refi package statuses
  sent:                   { label: 'En attente',     tone: 'blue' },
}

const RISK_BAND: Record<string, { tone: Tone }> = {
  A: { tone: 'green' },
  B: { tone: 'teal' },
  C: { tone: 'yellow' },
  D: { tone: 'orange' },
  E: { tone: 'red' },
}

interface StatusBadgeProps {
  status: string
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = DEAL_STATUS[status] ?? { label: status, tone: 'gray' as Tone }
  const { badge, dot } = TONE_CLASSES[config.tone]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
        badge,
        className
      )}
    >
      <span className={cn('h-1.5 w-1.5 shrink-0 rounded-full', dot)} />
      {config.label}
    </span>
  )
}

interface RiskBadgeProps {
  band: string | null
  className?: string
}

export function RiskBadge({ band, className }: RiskBadgeProps) {
  if (!band) {
    return (
      <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-400', className)}>
        —
      </span>
    )
  }
  const config = RISK_BAND[band] ?? { tone: 'gray' as Tone }
  const { badge } = TONE_CLASSES[config.tone]
  return (
    <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold font-mono', badge, className)}>
      {band}
    </span>
  )
}

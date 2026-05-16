import Link from 'next/link'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { DecisionButtons } from '@/components/financier/DecisionButtons'
import type { RefiPackage, FinancierDecision } from '@/lib/types/refi'

interface Props {
  params: Promise<{ id: string }>
}

type PackageStatus = RefiPackage['status']

const STATUS_BADGE: Record<PackageStatus, { label: string; className: string }> = {
  sent: { label: 'En attente', className: 'bg-blue-100 text-blue-700' },
  financier_approved: { label: 'Approuvé', className: 'bg-green-100 text-green-700' },
  financier_rejected: { label: 'Rejeté', className: 'bg-red-100 text-red-700' },
  draft: { label: 'Brouillon', className: 'bg-gray-100 text-gray-600' },
}

function StatusBadge({ status }: { status: PackageStatus }) {
  const { label, className } = STATUS_BADGE[status] ?? STATUS_BADGE.draft
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${className}`}>{label}</span>
  )
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatAmount(cents: number | null): string {
  if (cents === null) return '—'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100)
}

export default async function PackageDetailPage({ params }: Props) {
  const { id } = await params
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  let pkg: RefiPackage | null = null
  let decisions: FinancierDecision[] = []

  try {
    pkg = await apiFetch<RefiPackage>(`/refi-packages/${id}`, session.access_token)
  } catch {
    // API unavailable or not found
  }

  try {
    const decisionsResult = await apiFetch<{ data: FinancierDecision[] }>(
      `/refi-packages/${id}/decisions`,
      session.access_token
    )
    decisions = decisionsResult.data
  } catch {
    // decisions endpoint may not exist yet or package has none
  }

  if (!pkg) {
    return (
      <DashboardShell role="financier" title="Package introuvable">
        <p className="text-sm text-gray-500">Impossible de charger ce package.</p>
      </DashboardShell>
    )
  }

  const title = pkg.company_name ?? `Package ${pkg.id.slice(0, 8)}…`
  const subtitle = pkg.deal_public_id ? `Dossier ${pkg.deal_public_id}` : undefined

  return (
    <DashboardShell role="financier" title={title} subtitle={subtitle}>
      <div className="max-w-2xl space-y-6">
        <Link
          href="/financier"
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800 transition-colors"
        >
          ← Retour aux packages
        </Link>

        {/* Package summary */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-navy-900">Détails du package</h2>
            <StatusBadge status={pkg.status} />
          </div>

          <dl className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
            <div>
              <dt className="text-gray-500">Référence dossier</dt>
              <dd className="font-mono text-gray-800 mt-0.5">{pkg.deal_public_id ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Créé le</dt>
              <dd className="text-gray-800 mt-0.5">{formatDate(pkg.created_at)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Montant</dt>
              <dd className="font-mono text-gray-800 mt-0.5">{formatAmount(pkg.amount_cents)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Durée</dt>
              <dd className="font-mono text-gray-800 mt-0.5">
                {pkg.duration_months !== null ? `${pkg.duration_months} mois` : '—'}
              </dd>
            </div>
            <div>
              <dt className="text-gray-500">Mensualité</dt>
              <dd className="font-mono text-gray-800 mt-0.5">
                {formatAmount(pkg.monthly_payment_cents)}
              </dd>
            </div>
            <div>
              <dt className="text-gray-500">Score de risque</dt>
              <dd className="font-mono text-gray-800 mt-0.5">
                {pkg.risk_score !== null ? pkg.risk_score : '—'}
                {pkg.risk_band ? ` (${pkg.risk_band})` : ''}
              </dd>
            </div>
            {pkg.sent_at && (
              <div>
                <dt className="text-gray-500">Envoyé le</dt>
                <dd className="text-gray-800 mt-0.5">{formatDate(pkg.sent_at)}</dd>
              </div>
            )}
          </dl>
        </div>

        {/* Existing decisions */}
        {decisions.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-base font-semibold text-navy-900 mb-4">Décisions enregistrées</h2>
            <div className="space-y-3">
              {decisions.map((d) => (
                <div key={d.id} className="flex items-start gap-3 text-sm">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium shrink-0 ${
                      d.decision === 'approved'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {d.decision === 'approved' ? 'Approuvé' : 'Rejeté'}
                  </span>
                  <div>
                    {d.reason && <p className="text-gray-700">{d.reason}</p>}
                    <p className="text-gray-400 text-xs mt-0.5">{formatDate(d.decided_at)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Decision buttons — only shown when package is pending */}
        {pkg.status === 'sent' && (
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-base font-semibold text-navy-900 mb-4">Votre décision</h2>
            <DecisionButtons packageId={pkg.id} />
          </div>
        )}
      </div>
    </DashboardShell>
  )
}

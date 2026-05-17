import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { DecisionButtons } from '@/components/financier/DecisionButtons'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Breadcrumb } from '@/components/ui/breadcrumb'
import type { RefiPackage, FinancierDecision } from '@/lib/types/refi'

interface Props {
  params: Promise<{ id: string }>
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
        <Breadcrumb crumbs={[
          { label: 'Tableau de bord', href: '/financier' },
          { label: title },
        ]} />

        {/* Package summary */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
            <h2 className="text-sm font-semibold text-navy-900">Détails du package</h2>
            <StatusBadge status={pkg.status} />
          </div>
          <dl className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm px-6 py-5">
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Référence dossier</dt>
              <dd className="font-mono text-gray-800">{pkg.deal_public_id ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Créé le</dt>
              <dd className="text-gray-800 tabular-nums">{formatDate(pkg.created_at)}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Montant</dt>
              <dd className="font-mono text-gray-800 tabular-nums">{formatAmount(pkg.amount_cents)}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Durée</dt>
              <dd className="font-mono text-gray-800">
                {pkg.duration_months !== null ? `${pkg.duration_months} mois` : '—'}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Mensualité</dt>
              <dd className="font-mono text-gray-800 tabular-nums">
                {formatAmount(pkg.monthly_payment_cents)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-400 mb-0.5">Score de risque</dt>
              <dd className="font-mono text-gray-800">
                {pkg.risk_score !== null ? pkg.risk_score : '—'}
                {pkg.risk_band ? ` (${pkg.risk_band})` : ''}
              </dd>
            </div>
            {pkg.sent_at && (
              <div>
                <dt className="text-xs text-gray-400 mb-0.5">Envoyé le</dt>
                <dd className="text-gray-800 tabular-nums">{formatDate(pkg.sent_at)}</dd>
              </div>
            )}
          </dl>
        </div>

        {/* Existing decisions */}
        {decisions.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-50">
              <h2 className="text-sm font-semibold text-navy-900">Décisions enregistrées</h2>
            </div>
            <div className="px-6 py-5 space-y-3">
              {decisions.map((d) => (
                <div key={d.id} className="flex items-start gap-3 text-sm">
                  <StatusBadge
                    status={d.decision === 'approved' ? 'financier_approved' : 'financier_rejected'}
                    className="shrink-0"
                  />
                  <div>
                    {d.reason && <p className="text-gray-700">{d.reason}</p>}
                    <p className="text-gray-400 text-xs mt-0.5 tabular-nums">{formatDate(d.decided_at)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Decision buttons — only shown when package is pending */}
        {pkg.status === 'sent' && (
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-50">
              <h2 className="text-sm font-semibold text-navy-900">Votre décision</h2>
            </div>
            <div className="px-6 py-5">
              <DecisionButtons packageId={pkg.id} />
            </div>
          </div>
        )}
      </div>
    </DashboardShell>
  )
}

import Link from 'next/link'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'
import { StatusBadge, RiskBadge } from '@/components/shared/StatusBadge'

interface QueueDeal {
  id: string
  public_id: string
  company_id: string
  status: string
  risk_band: string | null
  created_at: string
  updated_at: string
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const APPROVED_STATUSES = new Set(['pre_approved', 'firm_offer_generated', 'financier_approved'])

export default async function AdminDashboard() {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  let deals: QueueDeal[] = []
  let apiError = false
  try {
    const result = await apiFetch<{ data: QueueDeal[]; meta: { total: number } }>(
      '/admin/queue',
      session.access_token,
    )
    deals = result.data
  } catch {
    apiError = true
  }

  const queueCount = deals.length
  const inReviewCount = deals.filter((d) => d.status === 'internal_review').length
  const approvedCount = deals.filter((d) => APPROVED_STATUSES.has(d.status)).length
  const preApprovedCount = deals.filter((d) => d.status === 'pre_approved').length

  const recent = [...deals]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 10)

  return (
    <DashboardShell role="admin" title="Tableau de bord" subtitle="Vue opérationnelle ADV">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="File d'attente" value={String(queueCount)} color="warning" />
        <StatCard label="En révision" value={String(inReviewCount)} />
        <StatCard label="Accordés ce mois" value={String(approvedCount)} color="teal" />
        <StatCard label="Pré-approuvés" value={String(preApprovedCount)} color="teal" />
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Dossiers en attente</h2>
        </div>
        {apiError ? (
          <p className="px-6 py-4 text-sm text-red-500">Impossible de charger la file d'attente.</p>
        ) : recent.length === 0 ? (
          <p className="px-6 py-8 text-sm text-gray-400 text-center">Aucun dossier en attente.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-left bg-gray-50/60">
                <th className="px-6 py-3 pr-4">Réf</th>
                <th className="py-3 pr-4">Statut</th>
                <th className="py-3 pr-4">Risque</th>
                <th className="py-3 pr-4">Date</th>
                <th className="py-3 pr-6" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {recent.map((deal) => (
                <tr
                  key={deal.id}
                  className="hover:bg-gray-50/70 transition-colors group"
                >
                  <td className="px-6 py-3 pr-4 font-mono text-xs text-gray-700 tabular-nums">
                    {deal.public_id}
                  </td>
                  <td className="py-3 pr-4">
                    <StatusBadge status={deal.status} />
                  </td>
                  <td className="py-3 pr-4">
                    <RiskBadge band={deal.risk_band} />
                  </td>
                  <td className="py-3 pr-4 text-gray-400 text-xs tabular-nums">
                    {formatDate(deal.created_at)}
                  </td>
                  <td className="py-3 pr-6 text-right">
                    <Link
                      href={`/admin/deals/${deal.id}`}
                      className="text-xs font-medium text-navy-900/40 group-hover:text-navy-900 transition-colors"
                    >
                      Voir →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </DashboardShell>
  )
}

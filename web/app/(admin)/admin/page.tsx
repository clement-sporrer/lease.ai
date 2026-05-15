import Link from 'next/link'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

interface QueueDeal {
  id: string
  public_id: string
  company_id: string
  status: string
  risk_band: string | null
  created_at: string
  updated_at: string
}

type DealStatus = QueueDeal['status']

const STATUS_BADGE: Record<string, { label: string; className: string }> = {
  submitted: { label: 'Soumis', className: 'bg-blue-100 text-blue-700' },
  internal_review: { label: 'En révision', className: 'bg-yellow-100 text-yellow-700' },
  missing_documents: { label: 'Docs manquants', className: 'bg-orange-100 text-orange-700' },
  pre_approved: { label: 'Pré-approuvé', className: 'bg-green-100 text-green-700' },
  financier_rejected: { label: 'Refusé', className: 'bg-red-100 text-red-700' },
}

const RISK_BADGE: Record<string, { label: string; className: string }> = {
  A: { label: 'A', className: 'bg-green-100 text-green-700' },
  B: { label: 'B', className: 'bg-teal-100 text-teal-700' },
  C: { label: 'C', className: 'bg-yellow-100 text-yellow-700' },
  D: { label: 'D', className: 'bg-orange-100 text-orange-700' },
}

function StatusBadge({ status }: { status: DealStatus }) {
  const badge = STATUS_BADGE[status] ?? { label: status, className: 'bg-gray-100 text-gray-600' }
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${badge.className}`}>
      {badge.label}
    </span>
  )
}

function RiskBadge({ band }: { band: string | null }) {
  if (!band) {
    return (
      <span className="rounded-full px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-600">
        —
      </span>
    )
  }
  const badge = RISK_BADGE[band] ?? { label: band, className: 'bg-gray-100 text-gray-600' }
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${badge.className}`}>
      {badge.label}
    </span>
  )
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
  try {
    const result = await apiFetch<{ data: QueueDeal[]; meta: { total: number } }>(
      '/admin/deals/queue',
      session.access_token,
    )
    deals = result.data
  } catch {
    // API unavailable — show empty state rather than crash
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

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-navy-900 mb-4">Dossiers en attente</h2>
        {recent.length === 0 ? (
          <p className="text-sm text-gray-400">Aucun dossier en attente.</p>
        ) : (
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="text-gray-500 font-medium text-left border-b border-gray-100">
                <th className="pb-2 pr-4">Réf</th>
                <th className="pb-2 pr-4">Statut</th>
                <th className="pb-2 pr-4">Risque</th>
                <th className="pb-2 pr-4">Date</th>
                <th className="pb-2" />
              </tr>
            </thead>
            <tbody>
              {recent.map((deal) => (
                <tr
                  key={deal.id}
                  className="border-b border-gray-50 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-2 pr-4 font-mono text-gray-700">{deal.public_id}</td>
                  <td className="py-2 pr-4">
                    <StatusBadge status={deal.status} />
                  </td>
                  <td className="py-2 pr-4">
                    <RiskBadge band={deal.risk_band} />
                  </td>
                  <td className="py-2 pr-4 text-gray-500">{formatDate(deal.created_at)}</td>
                  <td className="py-2 text-right">
                    <Link
                      href={`/admin/deals/${deal.id}`}
                      className="text-blue-600 hover:text-blue-800 font-medium text-xs"
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

import Link from 'next/link'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'
import { StatusBadge } from '@/components/shared/StatusBadge'
import type { RefiPackage } from '@/lib/types/refi'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export default async function FinancierDashboard() {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  let packages: RefiPackage[] = []
  try {
    const result = await apiFetch<{ data: RefiPackage[] }>('/refi-packages', session.access_token)
    packages = result.data
  } catch {
    // API unavailable — show empty state rather than crash
  }

  const totalCount = packages.length
  const pendingCount = packages.filter((p) => p.status === 'sent').length
  const approvedCount = packages.filter((p) => p.status === 'financier_approved').length
  const rejectedCount = packages.filter((p) => p.status === 'financier_rejected').length

  const recent = [...packages]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 10)

  return (
    <DashboardShell
      role="financier"
      title="Tableau de bord"
      subtitle="Suivi des packages de refinancement"
    >
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Packages reçus" value={String(totalCount)} />
        <StatCard label="Décisions en attente" value={String(pendingCount)} color="warning" />
        <StatCard label="Approuvés" value={String(approvedCount)} color="teal" />
        <StatCard label="Rejetés" value={String(rejectedCount)} color="danger" />
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Packages récents</h2>
        </div>
        {recent.length === 0 ? (
          <p className="px-6 py-8 text-sm text-gray-400 text-center">
            Aucun package de refinancement pour le moment.
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-left bg-gray-50/60">
                <th className="px-6 py-3 pr-4">Dossier</th>
                <th className="py-3 pr-4">Société</th>
                <th className="py-3 pr-4">Statut</th>
                <th className="py-3 pr-4">Créé le</th>
                <th className="py-3 pr-6" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {recent.map((pkg) => (
                <tr
                  key={pkg.id}
                  className="hover:bg-gray-50/70 transition-colors group"
                >
                  <td className="px-6 py-3 pr-4 font-mono text-xs text-gray-600 tabular-nums">
                    {pkg.deal_public_id ?? pkg.id.slice(0, 8) + '…'}
                  </td>
                  <td className="py-3 pr-4 font-medium text-gray-800 text-sm">
                    {pkg.company_name ?? '—'}
                  </td>
                  <td className="py-3 pr-4">
                    <StatusBadge status={pkg.status} />
                  </td>
                  <td className="py-3 pr-4 text-gray-400 text-xs tabular-nums">
                    {formatDate(pkg.created_at)}
                  </td>
                  <td className="py-3 pr-6 text-right">
                    <Link
                      href={`/financier/packages/${pkg.id}`}
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

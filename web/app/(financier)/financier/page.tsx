import Link from 'next/link'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'
import type { RefiPackage } from '@/lib/types/refi'

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

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-navy-900 mb-4">Packages récents</h2>
        {recent.length === 0 ? (
          <p className="text-sm text-gray-400">Aucun package de refinancement pour le moment.</p>
        ) : (
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="text-gray-500 font-medium text-left border-b border-gray-100">
                <th className="pb-2 pr-4">Dossier</th>
                <th className="pb-2 pr-4">Société</th>
                <th className="pb-2 pr-4">Statut</th>
                <th className="pb-2 pr-4">Créé le</th>
                <th className="pb-2" />
              </tr>
            </thead>
            <tbody>
              {recent.map((pkg) => (
                <tr
                  key={pkg.id}
                  className="border-b border-gray-50 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-2 pr-4 font-mono text-xs text-gray-600">
                    {pkg.deal_public_id ?? pkg.id.slice(0, 8) + '…'}
                  </td>
                  <td className="py-2 pr-4 font-medium text-gray-800">
                    {pkg.company_name ?? '—'}
                  </td>
                  <td className="py-2 pr-4">
                    <StatusBadge status={pkg.status} />
                  </td>
                  <td className="py-2 pr-4 text-gray-500">{formatDate(pkg.created_at)}</td>
                  <td className="py-2 text-right">
                    <Link
                      href={`/financier/packages/${pkg.id}`}
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

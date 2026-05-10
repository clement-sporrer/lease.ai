import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

const MOCK = {
  packages: 4,
  pending: 2,
  approved: 6,
  exposure: '€ 1 240 000',
}

export default function FinancierDashboard() {
  return (
    <DashboardShell role="financier" title="Tableau de bord" subtitle="Suivi des packages de refinancement">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Packages reçus" value={String(MOCK.packages)} />
        <StatCard label="Décisions en attente" value={String(MOCK.pending)} color="warning" />
        <StatCard label="Approuvés ce mois" value={String(MOCK.approved)} color="teal" />
        <StatCard label="Encours financé" value={MOCK.exposure} color="teal" />
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-navy-900 mb-4">Packages récents</h2>
        <p className="text-sm text-gray-400">Les packages de refinancement apparaîtront ici.</p>
      </div>
    </DashboardShell>
  )
}

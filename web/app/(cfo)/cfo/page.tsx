import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

const MOCK = {
  total: '€ 8 450 000',
  rents: '€ 142 000',
  defaultRate: '0.8%',
  active: 47,
}

export default function CfoDashboard() {
  return (
    <DashboardShell role="cfo" title="Tableau de bord" subtitle="Vue consolidée du portefeuille">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Encours total" value={MOCK.total} color="teal" />
        <StatCard label="Loyers ce mois" value={MOCK.rents} color="teal" />
        <StatCard label="Taux de défaut" value={MOCK.defaultRate} color="warning" />
        <StatCard label="Dossiers actifs" value={String(MOCK.active)} />
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-base font-semibold text-navy-900 mb-4">Performance du portefeuille</h2>
        <div className="h-48 flex items-center justify-center rounded-lg bg-gray-50 border border-dashed border-gray-200">
          <p className="text-sm text-gray-400">Graphique de performance (à venir)</p>
        </div>
      </div>
    </DashboardShell>
  )
}

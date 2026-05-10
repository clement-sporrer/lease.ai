import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

const MOCK = {
  tasks: 7,
  docsWaiting: 14,
  activeDeals: 23,
  pendingActivation: 3,
}

export default function OpsDashboard() {
  return (
    <DashboardShell role="ops" title="Tableau de bord" subtitle="Suivi opérationnel">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Tâches ouvertes" value={String(MOCK.tasks)} color="warning" />
        <StatCard label="Documents en attente" value={String(MOCK.docsWaiting)} color="danger" />
        <StatCard label="Dossiers actifs" value={String(MOCK.activeDeals)} color="teal" />
        <StatCard label="Activations en cours" value={String(MOCK.pendingActivation)} />
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-navy-900 mb-4">Tâches prioritaires</h2>
        <p className="text-sm text-gray-400">Les tâches apparaîtront ici.</p>
      </div>
    </DashboardShell>
  )
}

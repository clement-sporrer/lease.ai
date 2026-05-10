import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

const MOCK = {
  queue: 12,
  pendingReview: 5,
  approvedThisMonth: 8,
  rejectedThisMonth: 2,
}

export default function AdminDashboard() {
  return (
    <DashboardShell role="admin" title="Tableau de bord" subtitle="Vue opérationnelle ADV">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="File d'attente" value={String(MOCK.queue)} color="warning" />
        <StatCard label="En révision" value={String(MOCK.pendingReview)} />
        <StatCard label="Accordés ce mois" value={String(MOCK.approvedThisMonth)} color="teal" />
        <StatCard label="Refusés ce mois" value={String(MOCK.rejectedThisMonth)} color="danger" />
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-navy-900 mb-4">Dossiers récents</h2>
        <p className="text-sm text-gray-400">Les dossiers apparaîtront ici.</p>
      </div>
    </DashboardShell>
  )
}

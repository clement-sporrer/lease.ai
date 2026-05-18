import { createSupabaseServerClient } from '@/lib/supabase-server'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

export default async function OpsDashboard() {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  return (
    <DashboardShell role="ops" title="Tableau de bord" subtitle="Suivi opérationnel">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Tâches ouvertes" value="0" color="warning" />
        <StatCard label="Documents en attente" value="0" color="danger" />
        <StatCard label="Dossiers actifs" value="0" color="teal" />
        <StatCard label="Activations en cours" value="0" />
      </div>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Tâches prioritaires</h2>
        </div>
        <p className="px-6 py-8 text-center text-sm text-gray-400">
          Les tâches apparaîtront ici lorsque les workflows seront actifs.
        </p>
      </div>
    </DashboardShell>
  )
}

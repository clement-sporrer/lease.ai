import { createSupabaseServerClient } from '@/lib/supabase-server'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

export default async function CommercialDashboard() {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  return (
    <DashboardShell role="commercial" title="Tableau de bord" subtitle="Suivi commercial et pipeline">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Dossiers soumis" value="0" color="teal" />
        <StatCard label="En attente réponse" value="0" color="warning" />
        <StatCard label="Taux de conversion" value="—" />
        <StatCard label="Volume ce mois" value="—" color="teal" />
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden mb-6">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Mes dossiers en cours</h2>
        </div>
        <p className="px-6 py-8 text-center text-sm text-gray-400">
          Vos dossiers actifs apparaîtront ici.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Partenaires actifs</h2>
        </div>
        <p className="px-6 py-8 text-center text-sm text-gray-400">
          Aucun partenaire enregistré pour le moment.
        </p>
      </div>
    </DashboardShell>
  )
}

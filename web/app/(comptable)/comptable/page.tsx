import { createSupabaseServerClient } from '@/lib/supabase-server'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

export default async function ComptableDashboard() {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  return (
    <DashboardShell role="comptable" title="Tableau de bord" subtitle="Suivi comptable et facturation">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Factures ce mois" value="0" />
        <StatCard label="En attente règlement" value="0" color="warning" />
        <StatCard label="Retards de paiement" value="0" color="danger" />
        <StatCard label="Encaissé ce mois" value="—" color="teal" />
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden mb-6">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Factures récentes</h2>
        </div>
        <p className="px-6 py-8 text-center text-sm text-gray-400">
          Les factures générées apparaîtront ici.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Échéances à venir</h2>
        </div>
        <p className="px-6 py-8 text-center text-sm text-gray-400">
          Aucune échéance programmée.
        </p>
      </div>
    </DashboardShell>
  )
}

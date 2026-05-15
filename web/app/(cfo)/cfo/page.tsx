import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

interface PortfolioData {
  active_leases: number
  pipeline_deals: number
  total_commitment_eur: number
  cash_collected_month_eur: number
}

interface PortfolioResponse {
  data: PortfolioData
}

function formatEuros(eur: number): string {
  return eur.toLocaleString('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  })
}

export default async function CfoDashboard() {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  let portfolio: PortfolioData | null = null
  try {
    const result = await apiFetch<PortfolioResponse>('/dashboards/cfo/portfolio', session.access_token)
    portfolio = result.data
  } catch {
    // API unavailable — fall back to dashes rather than crashing
  }

  const totalExposure = portfolio ? formatEuros(portfolio.total_commitment_eur) : '—'
  const monthlyRent = portfolio ? formatEuros(portfolio.cash_collected_month_eur) : '—'
  const defaultRate = '—'
  const activeDeals = portfolio ? String(portfolio.active_leases) : '—'

  return (
    <DashboardShell role="cfo" title="Tableau de bord" subtitle="Vue consolidée du portefeuille">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Encours total" value={totalExposure} color="teal" />
        <StatCard label="Loyers ce mois" value={monthlyRent} color="teal" />
        <StatCard label="Taux de défaut" value={defaultRate} color="warning" />
        <StatCard label="Dossiers actifs" value={activeDeals} />
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

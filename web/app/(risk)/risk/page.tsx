import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { StatCard } from '@/components/dashboard/StatCard'

interface PortfolioData {
  active_leases: number
  pipeline_deals: number
  total_commitment_eur: number
  default_rate_pct: number | null
  risk_distribution: { band: string; count: number; exposure_eur: number }[]
}

interface PortfolioResponse {
  data: PortfolioData
}

export default async function RiskDashboard() {
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
    // API unavailable
  }

  const defaultRate = portfolio?.default_rate_pct != null
    ? `${portfolio.default_rate_pct.toFixed(1)} %`
    : '—'
  const pipeline = portfolio ? String(portfolio.pipeline_deals) : '—'
  const activeLeases = portfolio ? String(portfolio.active_leases) : '—'

  return (
    <DashboardShell role="risk" title="Tableau de bord" subtitle="Analyse et suivi du risque portefeuille">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Taux de défaut" value={defaultRate} color="danger" />
        <StatCard label="En pipeline" value={pipeline} color="warning" />
        <StatCard label="Dossiers actifs" value={activeLeases} color="teal" />
        <StatCard label="Alertes risque" value="0" />
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden mb-6">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Distribution par bande de risque</h2>
        </div>
        {portfolio?.risk_distribution && portfolio.risk_distribution.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-left bg-gray-50/60">
                <th className="px-6 py-3 pr-4">Bande</th>
                <th className="py-3 pr-4">Dossiers</th>
                <th className="py-3 pr-6">Exposition</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {portfolio.risk_distribution.map((row) => (
                <tr key={row.band} className="hover:bg-gray-50/70 transition-colors">
                  <td className="px-6 py-3 pr-4 font-mono font-semibold text-navy-900">{row.band}</td>
                  <td className="py-3 pr-4 tabular-nums text-gray-700">{row.count}</td>
                  <td className="py-3 pr-6 font-mono tabular-nums text-gray-700">
                    {new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(row.exposure_eur)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="px-6 py-8 text-center text-sm text-gray-400">
            Aucune donnée de risque disponible.
          </p>
        )}
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-50">
          <h2 className="text-sm font-semibold text-navy-900">Alertes et dépassements</h2>
        </div>
        <p className="px-6 py-8 text-center text-sm text-gray-400">
          Aucune alerte active.
        </p>
      </div>
    </DashboardShell>
  )
}

import { EmptyState } from '@/components/shared/EmptyState'
import type { Asset, PaymentScheduleEntry } from '@/lib/types/contract'

function formatCents(cents: number | null): string {
  if (cents === null) return '—'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100)
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

const SCHEDULE_STATUS_LABEL: Record<string, string> = {
  pending: 'À venir',
  paid: 'Payée',
  overdue: 'En retard',
  cancelled: 'Annulée',
}

const SCHEDULE_STATUS_COLOR: Record<string, string> = {
  pending: 'text-gray-500',
  paid: 'text-teal-600',
  overdue: 'text-red-600',
  cancelled: 'text-gray-400',
}

interface Props {
  assets: Asset[]
  schedule: PaymentScheduleEntry[]
}

export function AssetsPanel({ assets, schedule }: Props) {
  return (
    <div className="mt-6 space-y-4">
      <div className="rounded-2xl border border-gray-200 bg-white">
        <div className="border-b border-gray-100 px-6 py-4">
          <h3 className="text-sm font-semibold text-navy-900">Actifs financés</h3>
        </div>
        {assets.length === 0 ? (
          <EmptyState title="Aucun actif enregistré" />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-400">
                <th className="px-6 py-3 text-left font-medium">Désignation</th>
                <th className="px-6 py-3 text-left font-medium">Catégorie</th>
                <th className="px-6 py-3 text-right font-medium">Qté</th>
                <th className="px-6 py-3 text-right font-medium">Valeur unitaire</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {assets.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50/50">
                  <td className="px-6 py-3 font-medium text-navy-900">{a.name}</td>
                  <td className="px-6 py-3 text-gray-500">{a.category ?? '—'}</td>
                  <td className="px-6 py-3 text-right font-mono text-gray-700">{a.quantity}</td>
                  <td className="px-6 py-3 text-right font-mono text-gray-700">
                    {formatCents(a.unit_value_cents)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white">
        <div className="border-b border-gray-100 px-6 py-4">
          <h3 className="text-sm font-semibold text-navy-900">Échéancier de paiement</h3>
        </div>
        {schedule.length === 0 ? (
          <EmptyState title="Aucune échéance enregistrée" />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-400">
                <th className="px-6 py-3 text-left font-medium">Échéance</th>
                <th className="px-6 py-3 text-right font-medium">Montant</th>
                <th className="px-6 py-3 text-right font-medium">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {schedule.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50/50">
                  <td className="px-6 py-3 font-mono text-gray-700">{formatDate(entry.due_date)}</td>
                  <td className="px-6 py-3 text-right font-mono text-gray-700">
                    {formatCents(entry.amount_cents)}
                  </td>
                  <td className={`px-6 py-3 text-right text-xs font-medium ${SCHEDULE_STATUS_COLOR[entry.status] ?? 'text-gray-500'}`}>
                    {SCHEDULE_STATUS_LABEL[entry.status] ?? entry.status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

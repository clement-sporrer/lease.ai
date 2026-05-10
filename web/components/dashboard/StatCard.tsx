type Color = 'default' | 'teal' | 'warning' | 'danger'

type Props = {
  label: string
  value: string
  sublabel?: string
  trend?: 'up' | 'down' | 'neutral'
  color?: Color
}

const VALUE_COLORS: Record<Color, string> = {
  default: 'text-navy-900',
  teal: 'text-teal-500',
  warning: 'text-warning',
  danger: 'text-danger',
}

export function StatCard({ label, value, sublabel, color = 'default' }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-2xl font-bold font-mono ${VALUE_COLORS[color]}`}>{value}</p>
      {sublabel && <p className="text-xs text-gray-400 mt-1">{sublabel}</p>}
    </div>
  )
}

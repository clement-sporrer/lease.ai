type Color = 'default' | 'teal' | 'warning' | 'danger'
type Trend = 'up' | 'down' | 'neutral'

type Props = {
  label: string
  value: string
  sublabel?: string
  color?: Color
  trend?: Trend
  trendLabel?: string
}

const VALUE_COLORS: Record<Color, string> = {
  default: 'text-navy-900',
  teal: 'text-teal-500',
  warning: 'text-warning',
  danger: 'text-danger',
}

const ACCENT_BARS: Record<Color, string> = {
  default: 'bg-navy-900/10',
  teal: 'bg-teal-500/15',
  warning: 'bg-warning/15',
  danger: 'bg-danger/15',
}

const TREND_CONFIG: Record<Trend, { icon: string; className: string }> = {
  up:      { icon: '↑', className: 'text-teal-600' },
  down:    { icon: '↓', className: 'text-danger' },
  neutral: { icon: '→', className: 'text-gray-400' },
}

export function StatCard({ label, value, sublabel, color = 'default', trend, trendLabel }: Props) {
  return (
    <div className="relative overflow-hidden bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      <div className={`absolute inset-x-0 bottom-0 h-0.5 ${ACCENT_BARS[color]}`} />
      <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-2">
        {label}
      </p>
      <p className={`text-2xl font-bold font-mono tabular-nums ${VALUE_COLORS[color]}`}>
        {value}
      </p>
      <div className="mt-1.5 flex items-center gap-1.5 min-h-[1rem]">
        {trend && trendLabel && (
          <>
            <span className={`text-xs font-semibold ${TREND_CONFIG[trend].className}`}>
              {TREND_CONFIG[trend].icon}
            </span>
            <span className="text-xs text-gray-400">{trendLabel}</span>
          </>
        )}
        {sublabel && !trend && (
          <span className="text-xs text-gray-400">{sublabel}</span>
        )}
      </div>
    </div>
  )
}

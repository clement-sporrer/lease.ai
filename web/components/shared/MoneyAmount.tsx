interface Props {
  cents: number | null | undefined
  currency?: string
  className?: string
}

export function MoneyAmount({ cents, currency = 'EUR', className = '' }: Props) {
  if (cents == null) return <span className={`font-mono text-gray-400 ${className}`}>—</span>
  const formatted = new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(cents / 100)
  return (
    <span
      className={`font-mono tabular-nums ${className}`}
      style={{ fontFamily: 'IBM Plex Mono, monospace' }}
    >
      {formatted}
    </span>
  )
}

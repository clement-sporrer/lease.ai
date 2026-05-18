interface Props {
  source: string | null | undefined
  className?: string
}

const SOURCE_LABELS: Record<string, string> = {
  pappers: 'Source : Pappers',
  mistral: 'Extrait par Mistral',
  mock: 'Données de test',
}

export function ProvenanceBadge({ source, className = '' }: Props) {
  if (!source) return null
  const label = SOURCE_LABELS[source] ?? `Source : ${source}`
  const isMock = source === 'mock'
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium tracking-wide ${
        isMock
          ? 'bg-gray-100 text-gray-400'
          : 'bg-teal-50 text-teal-700 ring-1 ring-teal-200'
      } ${className}`}
    >
      {!isMock && (
        <span className="h-1.5 w-1.5 rounded-full bg-teal-500 inline-block" />
      )}
      {label}
    </span>
  )
}

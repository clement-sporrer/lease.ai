import { View, Text } from 'react-native'

type StatusConfig = {
  bg: string
  text: string
  label: string
}

const STATUS_MAP: Record<string, StatusConfig> = {
  draft: { bg: 'bg-gray-100', text: 'text-gray-600', label: 'Brouillon' },
  submitted: { bg: 'bg-blue-500', text: 'text-white', label: 'Soumis' },
  pre_approved: { bg: 'bg-teal-500', text: 'text-white', label: 'Pré-accordé' },
  missing_documents: { bg: 'bg-warning', text: 'text-white', label: 'Pièces manquantes' },
  active: { bg: 'bg-teal-500', text: 'text-white', label: 'ACTIF' },
}

type StatusBadgeProps = {
  status: string
  large?: boolean
}

export function StatusBadge({ status, large = false }: StatusBadgeProps) {
  const config = STATUS_MAP[status] ?? { bg: 'bg-gray-100', text: 'text-gray-600', label: status.replace(/_/g, ' ') }

  return (
    <View className={`${config.bg} rounded-full ${large ? 'px-8 py-3' : 'px-3 py-1'} self-start`}>
      <Text className={`${config.text} ${large ? 'text-base font-bold' : 'text-xs font-medium'}`}>
        {config.label}
      </Text>
    </View>
  )
}

import { View, Text } from 'react-native'

type KpiCardProps = {
  label: string
  value: string
  valueClassName?: string
}

export function KpiCard({ label, value, valueClassName = 'text-navy-900' }: KpiCardProps) {
  return (
    <View className="flex-1 min-w-[44%] bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      <Text className={`text-2xl font-bold font-mono ${valueClassName}`}>{value}</Text>
      <Text className="text-xs text-gray-500 mt-1">{label}</Text>
    </View>
  )
}

import { View, Text, ScrollView, TouchableOpacity } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useAuthStore } from '@/src/stores/auth'
import { StatusBadge } from '@/src/components/StatusBadge'

const MOCK_LEASE = {
  id: 'LSE-2024-001',
  startDate: '01/06/2024',
  endDate: '01/06/2027',
  totalCommitment: 145800,
}

const MOCK_NEXT_PAYMENT = {
  amount: 4050,
  dueDate: '01/06/2026',
}

const MOCK_ASSETS = [
  { id: 'a1', model: 'MacBook Pro 16" M3 Pro', quantity: 2, value: 24000 },
  { id: 'a2', model: 'iPhone 15 Pro', quantity: 5, value: 7500 },
]

export default function ClientDashboard() {
  const session = useAuthStore((s) => s.session)

  const rawName = session?.user?.user_metadata?.full_name as string | undefined
  const emailPrefix = session?.user?.email?.split('@')[0] ?? 'Client'
  const displayName = rawName ?? emailPrefix

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['top']}>
      {/* Header */}
      <View className="bg-navy-900 px-5 pt-4 pb-6">
        <Text className="text-white text-xl font-bold">{displayName}</Text>
        <Text className="text-blue-300 text-sm mt-0.5">Locataire</Text>
      </View>

      <ScrollView
        className="flex-1"
        contentContainerClassName="px-5 pt-5 pb-24"
        showsVerticalScrollIndicator={false}
      >
        {/* Contract status */}
        <View className="items-center mb-6">
          <StatusBadge status="active" large />
        </View>

        {/* Lease info card */}
        <View className="bg-white rounded-2xl p-5 mb-4 border border-gray-100 shadow-sm">
          <Text className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Contrat de location
          </Text>

          <View className="flex-row justify-between mb-2">
            <Text className="text-sm text-gray-500">Référence</Text>
            <Text className="text-sm font-bold font-mono text-navy-900">{MOCK_LEASE.id}</Text>
          </View>

          <View className="flex-row justify-between mb-2">
            <Text className="text-sm text-gray-500">Début</Text>
            <Text className="text-sm font-mono text-navy-900">{MOCK_LEASE.startDate}</Text>
          </View>

          <View className="flex-row justify-between mb-2">
            <Text className="text-sm text-gray-500">Fin</Text>
            <Text className="text-sm font-mono text-navy-900">{MOCK_LEASE.endDate}</Text>
          </View>

          <View className="h-px bg-gray-100 my-3" />

          <View className="flex-row justify-between items-center">
            <Text className="text-sm text-gray-500">Engagement total</Text>
            <Text className="text-lg font-bold font-mono text-navy-900">
              € {MOCK_LEASE.totalCommitment.toLocaleString('fr-FR')}
            </Text>
          </View>
        </View>

        {/* Next payment card */}
        <View className="bg-white rounded-2xl p-5 mb-4 border border-gray-100 shadow-sm">
          <Text className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Prochain paiement
          </Text>

          <Text className="text-3xl font-bold font-mono text-navy-900">
            € {MOCK_NEXT_PAYMENT.amount.toLocaleString('fr-FR')}
            <Text className="text-base font-normal text-gray-400">/mois</Text>
          </Text>

          <View className="flex-row items-center justify-between mt-3">
            <View className="flex-row items-center gap-2">
              <Text className="text-sm text-gray-500">Échéance :</Text>
              <Text className="text-sm font-mono text-navy-900">{MOCK_NEXT_PAYMENT.dueDate}</Text>
            </View>
            <View className="bg-warning rounded-full px-3 py-1">
              <Text className="text-white text-xs font-medium">À venir</Text>
            </View>
          </View>
        </View>

        {/* Assets section */}
        <Text className="text-base font-semibold text-navy-900 mb-3">Matériel loué</Text>
        <View className="bg-white rounded-2xl border border-gray-100 shadow-sm px-4 mb-6">
          {MOCK_ASSETS.map((asset, index) => (
            <View
              key={asset.id}
              className={`py-3 ${index < MOCK_ASSETS.length - 1 ? 'border-b border-gray-100' : ''}`}
            >
              <View className="flex-row items-center justify-between">
                <View className="flex-1 mr-3">
                  <Text className="text-sm font-medium text-navy-900">{asset.model}</Text>
                  <Text className="text-xs text-gray-400 mt-0.5">
                    Qté : {asset.quantity}
                  </Text>
                </View>
                <Text className="text-sm font-bold font-mono text-navy-900">
                  € {asset.value.toLocaleString('fr-FR')}
                </Text>
              </View>
            </View>
          ))}
        </View>
      </ScrollView>

      {/* CTA */}
      <View className="absolute bottom-0 left-0 right-0 bg-gray-50 pt-2 pb-8 px-5">
        <TouchableOpacity
          className="border-2 border-blue-500 rounded-2xl py-4 items-center"
          activeOpacity={0.85}
        >
          <Text className="text-blue-500 font-semibold text-base">Contacter mon conseiller</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  )
}

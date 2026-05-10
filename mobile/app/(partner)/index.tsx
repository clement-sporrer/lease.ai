import { Alert, View, Text, ScrollView, TouchableOpacity } from 'react-native'
import { useRouter } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { SafeAreaView } from 'react-native-safe-area-context'
import { BrandMark } from '@/src/components/BrandMark'
import { KpiCard } from '@/src/components/KpiCard'
import { StatusBadge } from '@/src/components/StatusBadge'
import { supabase } from '@/src/lib/supabase'
import { useDisplayName } from '@/src/hooks/useDisplayName'

const MOCK_KPIS = { active: 7, engagement: 142000, toComplete: 3, approved: 4 }

const MOCK_DEALS = [
  { id: '1', name: 'SIREN 823456789', status: 'submitted', date: '09/05/2026' },
  { id: '2', name: 'SIREN 712345678', status: 'missing_documents', date: '08/05/2026' },
  { id: '3', name: 'SIREN 654321098', status: 'pre_approved', date: '07/05/2026' },
]

export default function PartnerDashboard() {
  const router = useRouter()
  const displayName = useDisplayName('Partenaire')
  const HAS_PENDING = MOCK_KPIS.toComplete > 0

  const handleLogout = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) {
      Alert.alert('Déconnexion impossible', error.message)
      return
    }
    router.replace('/(auth)/login' as never)
  }

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <ScrollView
        className="flex-1"
        contentContainerClassName="px-5 pt-6 pb-24"
        showsVerticalScrollIndicator={false}
      >
        <View className="flex-row items-start justify-between gap-3">
          <View className="flex-1">
            <View className="flex-row items-center gap-3">
              <BrandMark variant="mark" style={{ width: 30, height: 30 }} />
              <View>
                <Text className="text-2xl font-bold text-navy-900">Bonjour, {displayName}</Text>
                <Text className="text-sm text-gray-500 mt-1">Tableau de bord partenaire</Text>
              </View>
            </View>
          </View>
          <TouchableOpacity
            className="flex-row items-center rounded-full border border-gray-200 bg-white px-3 py-2"
            activeOpacity={0.8}
            onPress={handleLogout}
          >
            <Ionicons name="log-out-outline" size={18} color="#0D183D" />
            <Text className="ml-2 text-sm font-medium text-navy-900">Déconnexion</Text>
          </TouchableOpacity>
        </View>

        {/* Health banner */}
        {HAS_PENDING ? (
          <View className="rounded-xl p-4 mb-6 mt-4 bg-warning">
            <Text className="text-white font-semibold text-sm">
              {MOCK_KPIS.toComplete} dossiers en attente
            </Text>
          </View>
        ) : (
          <View className="rounded-xl p-4 mb-6 mt-4 bg-teal-500">
            <Text className="text-white font-semibold text-sm">Tout est à jour</Text>
          </View>
        )}

        {/* KPI grid */}
        <View className="flex-row flex-wrap gap-3 mb-6">
          <KpiCard label="Dossiers actifs" value={String(MOCK_KPIS.active)} />
          <KpiCard
            label="Engagement total"
            value={`€ ${MOCK_KPIS.engagement.toLocaleString('fr-FR')}`}
          />
          <KpiCard
            label="À compléter"
            value={String(MOCK_KPIS.toComplete)}
            valueClassName={MOCK_KPIS.toComplete > 0 ? 'text-warning' : 'text-navy-900'}
          />
          <KpiCard
            label="Approuvés"
            value={String(MOCK_KPIS.approved)}
            valueClassName="text-teal-500"
          />
        </View>

        {/* Recent activity */}
        <Text className="text-base font-semibold text-navy-900 mb-3">Activité récente</Text>
        <View className="bg-white rounded-2xl border border-gray-100 shadow-sm px-4">
          {MOCK_DEALS.map((deal, index) => (
            <View
              key={deal.id}
              className={`flex-row items-center justify-between py-3 ${
                index < MOCK_DEALS.length - 1 ? 'border-b border-gray-100' : ''
              }`}
            >
              <View className="flex-1 mr-3">
                <Text className="text-sm font-medium text-navy-900 font-mono">{deal.name}</Text>
                <Text className="text-xs text-gray-400 mt-0.5">{deal.date}</Text>
              </View>
              <StatusBadge status={deal.status} />
            </View>
          ))}
        </View>
      </ScrollView>

      {/* CTA */}
      <View className="absolute bottom-0 left-0 right-0 bg-gray-50 pt-2 pb-8 px-5">
        <TouchableOpacity
          className="bg-blue-500 rounded-2xl py-4 items-center"
          activeOpacity={0.85}
          onPress={() => router.push('/(partner)/deals/new' as never)}
        >
          <Text className="text-white font-semibold text-base">Nouveau dossier</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  )
}

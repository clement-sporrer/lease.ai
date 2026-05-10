import { Ionicons } from '@expo/vector-icons'
import { Alert, ScrollView, Text, TouchableOpacity, View } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'

import { BrandMark } from '@/src/components/BrandMark'
import { normalizeRole } from '@/src/lib/roles'
import { useAuthStore } from '@/src/stores/auth'

const ROLE_HINTS = {
  admin: [
    'Queue de revue du jour',
    'Accès rapide aux pré-approbations',
    'Historique des décisions',
  ],
  ops: ['Documents reçus', 'Relances à envoyer', 'Pièces incomplètes'],
  risk: ['Dossiers sensibles', 'Bandes de score', 'Surveillance portefeuille'],
  financier: ['Lignes ouvertes', 'Marges par dossier', 'Décaissements à venir'],
  cfo: ['Synthèse trésorerie', 'Exposition globale', 'Rapport direction'],
} as const

type InternalRole = keyof typeof ROLE_HINTS

const INTERNAL_ROLES: InternalRole[] = ['admin', 'ops', 'risk', 'financier', 'cfo']

function toInternalRole(value: unknown): InternalRole {
  return typeof value === 'string' && INTERNAL_ROLES.includes(value as InternalRole)
    ? (value as InternalRole)
    : 'admin'
}

export default function ActionsScreen() {
  const session = useAuthStore((state) => state.session)
  const role = toInternalRole(normalizeRole(session?.user?.user_metadata?.active_role))
  const hints = ROLE_HINTS[role]

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['top']}>
      <ScrollView
        className="flex-1"
        contentContainerClassName="px-5 pt-5 pb-28"
        showsVerticalScrollIndicator={false}
      >
        <View className="flex-row items-start justify-between gap-4">
          <View className="flex-1">
            <View className="flex-row items-center gap-3">
              <BrandMark variant="mark" style={{ width: 30, height: 30 }} />
              <View>
                <Text className="text-sm font-medium uppercase tracking-[2px] text-gray-500">
                  LeaseAI interne
                </Text>
                <Text className="text-2xl font-bold text-navy-900">Actions utiles</Text>
              </View>
            </View>
            <Text className="mt-3 text-sm leading-6 text-gray-600">
              Vue rapide des sujets à traiter pour le profil {role}.
            </Text>
          </View>
          <TouchableOpacity
            className="rounded-full border border-gray-200 bg-white px-3 py-2"
            activeOpacity={0.8}
            onPress={() => Alert.alert('Raccourcis', 'La vue interne est déjà à jour.')}
          >
            <Ionicons name="refresh-outline" size={18} color="#0D183D" />
          </TouchableOpacity>
        </View>

        <View className="mt-5 rounded-3xl border border-gray-200 bg-white p-5">
          <Text className="text-base font-semibold text-navy-900">Priorités</Text>
          <View className="mt-4 gap-3">
            {hints.map((hint) => (
              <View key={hint} className="flex-row items-center gap-3">
                <View className="h-2.5 w-2.5 rounded-full bg-blue-500" />
                <Text className="flex-1 text-sm text-gray-700">{hint}</Text>
              </View>
            ))}
          </View>
        </View>

        <View className="mt-6 rounded-3xl bg-navy-900 p-5">
          <Text className="text-xs font-semibold uppercase tracking-[1.5px] text-white/65">
            Support démo
          </Text>
          <Text className="mt-3 text-lg font-bold text-white">Tout est mocké, mais la navigation est réelle.</Text>
          <Text className="mt-2 text-sm leading-6 text-white/80">
            Chaque rôle a sa propre front page et ses raccourcis. Les actions restent des démos
            tant que le back-office interne n’est pas branché.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  )
}

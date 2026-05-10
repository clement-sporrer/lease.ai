import { useRouter } from 'expo-router'
import { ActivityIndicator, Alert, ScrollView, Text, TouchableOpacity, View } from 'react-native'

import { useCreateDeal } from '@/src/hooks/useCreateDeal'
import { useDealCreationStore } from '@/src/stores/dealCreation'

function formatDate(value: string | null) {
  if (!value) return 'Non renseignée'
  return new Date(value).toLocaleDateString('fr-FR')
}

export default function EnrichmentScreen() {
  const router = useRouter()
  const company = useDealCreationStore((state) => state.company)
  const createDeal = useCreateDeal()

  if (!company) {
    return (
      <ScrollView
        className="flex-1 bg-gray-50"
        contentInsetAdjustmentBehavior="automatic"
        contentContainerStyle={{ padding: 20, gap: 16 }}
      >
        <View className="rounded-3xl border border-warning/20 bg-white p-5">
          <Text className="text-lg font-semibold text-navy-900">Enrichissement manquant</Text>
          <Text className="mt-2 text-sm text-gray-600">
            Reprenez le flow depuis la saisie du SIREN pour charger une société.
          </Text>
        </View>
        <TouchableOpacity
          className="items-center rounded-2xl bg-blue-500 py-4"
          onPress={() => router.replace('/(partner)/deals/new' as never)}
        >
          <Text className="text-base font-semibold text-white">Retour au début</Text>
        </TouchableOpacity>
      </ScrollView>
    )
  }

  const warnings: string[] = []
  if (!company.is_active) warnings.push('Société inactive')
  if (company.creation_date) {
    const ageInYears = (Date.now() - new Date(company.creation_date).getTime()) / (1000 * 60 * 60 * 24 * 365)
    if (ageInYears < 2) warnings.push('Société de moins de 2 ans')
  }

  const handleConfirm = async () => {
    try {
      await createDeal.mutateAsync({
        company_id: company.id,
        currency: 'EUR',
      })
      router.replace('/(partner)/deals/new/quote' as never)
    } catch (error) {
      Alert.alert(
        'Confirmation impossible',
        error instanceof Error ? error.message : 'Erreur inconnue',
      )
    }
  }

  return (
    <ScrollView
      className="flex-1 bg-gray-50"
      contentInsetAdjustmentBehavior="automatic"
      contentContainerStyle={{ padding: 20, gap: 20 }}
    >
      <View className="rounded-3xl bg-white p-5">
        <Text className="text-sm font-medium uppercase tracking-[2px] text-gray-500">Entreprise</Text>
        <Text className="mt-3 text-2xl font-bold text-navy-900">{company.legal_name}</Text>
        <Text className="mt-1 text-sm text-gray-500">
          SIREN {company.siren}
          {company.siret ? ` • SIRET ${company.siret}` : ''}
        </Text>
      </View>

      {warnings.length > 0 ? (
        <View className="rounded-3xl border border-warning/30 bg-warning/10 p-5">
          <Text className="text-sm font-semibold text-navy-900">Points à surveiller</Text>
          {warnings.map((warning) => (
            <Text key={warning} className="mt-2 text-sm text-gray-700">
              • {warning}
            </Text>
          ))}
        </View>
      ) : null}

      <View className="rounded-3xl border border-gray-200 bg-white p-5">
        <Text className="text-base font-semibold text-navy-900">Fiche enrichie</Text>
        <View className="mt-4 gap-4">
          <View>
            <Text className="text-xs uppercase tracking-[1px] text-gray-400">Adresse</Text>
            <Text className="mt-1 text-sm text-navy-900">
              {company.address
                ? `${company.address.street ?? ''} ${company.address.zip ?? ''} ${company.address.city ?? ''}`.trim()
                : 'Non renseignée'}
            </Text>
          </View>
          <View>
            <Text className="text-xs uppercase tracking-[1px] text-gray-400">Activité</Text>
            <Text className="mt-1 text-sm text-navy-900">{company.activity_code ?? 'Non renseignée'}</Text>
          </View>
          <View>
            <Text className="text-xs uppercase tracking-[1px] text-gray-400">Forme juridique</Text>
            <Text className="mt-1 text-sm text-navy-900">{company.legal_status ?? 'Non renseignée'}</Text>
          </View>
          <View>
            <Text className="text-xs uppercase tracking-[1px] text-gray-400">Création</Text>
            <Text className="mt-1 text-sm text-navy-900">{formatDate(company.creation_date)}</Text>
          </View>
          <View>
            <Text className="text-xs uppercase tracking-[1px] text-gray-400">Statut</Text>
            <Text className={`mt-1 text-sm font-medium ${company.is_active ? 'text-teal-500' : 'text-danger'}`}>
              {company.is_active ? 'Active' : 'Inactive'}
            </Text>
          </View>
        </View>
      </View>

      <TouchableOpacity
        className={`items-center rounded-2xl bg-blue-500 py-4 ${createDeal.isPending ? 'opacity-70' : ''}`}
        activeOpacity={0.85}
        disabled={createDeal.isPending}
        onPress={handleConfirm}
      >
        {createDeal.isPending ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <Text className="text-base font-semibold text-white">Confirmer l’entreprise</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  )
}

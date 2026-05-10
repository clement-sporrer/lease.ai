import { useEffect } from 'react'
import { useRouter } from 'expo-router'
import { ActivityIndicator, Alert, ScrollView, Text, TouchableOpacity, View } from 'react-native'

import { StatusBadge } from '@/src/components/StatusBadge'
import { useAssessRisk } from '@/src/hooks/useAssessRisk'
import { useIndicativePricing } from '@/src/hooks/useIndicativePricing'
import { useSubmitDeal } from '@/src/hooks/useSubmitDeal'
import { useDealCreationStore } from '@/src/stores/dealCreation'

function formatEuros(cents: number | null | undefined) {
  if (cents == null) return '—'
  return `${(cents / 100).toLocaleString('fr-FR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} €`
}

export default function OfferScreen() {
  const router = useRouter()
  const deal = useDealCreationStore((state) => state.deal)
  const pricingProposal = useDealCreationStore((state) => state.pricingProposal)
  const riskAssessment = useDealCreationStore((state) => state.riskAssessment)
  const indicativePricing = useIndicativePricing()
  const assessRisk = useAssessRisk()
  const submitDeal = useSubmitDeal()

  useEffect(() => {
    if (!deal?.id || !deal.amount_cents || !deal.duration_months) return

    indicativePricing.mutate({
      amount_cents: deal.amount_cents,
      duration_months: deal.duration_months,
    })

    assessRisk.mutate(deal.id)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deal?.id, deal?.amount_cents, deal?.duration_months])

  if (!deal || !deal.amount_cents || !deal.duration_months) {
    return (
      <ScrollView
        className="flex-1 bg-gray-50"
        contentInsetAdjustmentBehavior="automatic"
        contentContainerStyle={{ padding: 20, gap: 16 }}
      >
        <View className="rounded-3xl border border-warning/20 bg-white p-5">
          <Text className="text-lg font-semibold text-navy-900">Données insuffisantes</Text>
          <Text className="mt-2 text-sm text-gray-600">
            Le devis doit être complété avant de calculer l’offre indicative.
          </Text>
        </View>
        <TouchableOpacity
          className="items-center rounded-2xl bg-blue-500 py-4"
          onPress={() => router.replace('/(partner)/deals/new/quote' as never)}
        >
          <Text className="text-base font-semibold text-white">Retour au devis</Text>
        </TouchableOpacity>
      </ScrollView>
    )
  }

  const isLoading = indicativePricing.isPending || assessRisk.isPending

  const handleSubmit = () => {
    submitDeal.mutate(deal.id, {
      onSuccess: () => {
        Alert.alert('Dossier soumis', 'Le dossier a bien été envoyé pour revue.')
        router.replace('/(partner)')
      },
      onError: (error) => {
        Alert.alert('Soumission impossible', error instanceof Error ? error.message : 'Erreur inconnue')
      },
    })
  }

  return (
    <ScrollView
      className="flex-1 bg-gray-50"
      contentInsetAdjustmentBehavior="automatic"
      contentContainerStyle={{ padding: 20, gap: 20 }}
    >
      <View className="rounded-3xl bg-navy-900 p-6">
        <Text className="text-sm font-medium uppercase tracking-[2px] text-white/70">Offre indicative</Text>
        <Text className="mt-3 text-3xl font-bold text-white">{formatEuros(deal.amount_cents)}</Text>
        <Text className="mt-2 text-sm text-white/80">Sur {deal.duration_months} mois, hors validation finale.</Text>
      </View>

      {isLoading ? (
        <View className="items-center rounded-3xl bg-white p-8">
          <ActivityIndicator color="#2563EB" />
          <Text className="mt-3 text-sm text-gray-600">Calcul en cours…</Text>
        </View>
      ) : null}

      {pricingProposal ? (
        <View className="rounded-3xl border border-gray-200 bg-white p-5">
          <Text className="text-base font-semibold text-navy-900">Synthèse financière</Text>
          <View className="mt-4 gap-4">
            <View className="flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">Montant financé</Text>
              <Text className="font-mono text-sm text-navy-900">{formatEuros(pricingProposal.amount_financed_cents)}</Text>
            </View>
            <View className="flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">Mensualité</Text>
              <Text className="font-mono text-sm font-semibold text-navy-900">
                {formatEuros(pricingProposal.monthly_payment_cents)}
              </Text>
            </View>
            <View className="flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">Taux refinancement</Text>
              <Text className="font-mono text-sm text-navy-900">{(pricingProposal.refi_rate * 100).toFixed(2)}%</Text>
            </View>
            <View className="flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">Marge</Text>
              <Text className="font-mono text-sm text-navy-900">{(pricingProposal.margin_rate * 100).toFixed(2)}%</Text>
            </View>
            <View className="flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">Frais</Text>
              <Text className="font-mono text-sm text-navy-900">{formatEuros(pricingProposal.fees_cents)}</Text>
            </View>
          </View>
        </View>
      ) : null}

      {riskAssessment ? (
        <View className="rounded-3xl border border-gray-200 bg-white p-5">
          <Text className="text-base font-semibold text-navy-900">Score risque</Text>
          <View className="mt-4 flex-row items-center justify-between">
            <StatusBadge status={riskAssessment.band} large />
            <Text className="font-mono text-2xl font-bold text-navy-900">{riskAssessment.score}/100</Text>
          </View>
          <Text className="mt-4 text-sm leading-6 text-gray-600">
            {riskAssessment.recommendation ?? 'Analyse disponible.'}
          </Text>
          {riskAssessment.flags?.length ? (
            <View className="mt-4 gap-2">
              {riskAssessment.flags.map((flag) => (
                <Text key={flag} className="text-sm text-gray-600">
                  • {flag}
                </Text>
              ))}
            </View>
          ) : null}
        </View>
      ) : null}

      <View className="rounded-3xl border border-blue-100 bg-blue-50 p-5">
        <Text className="text-sm font-semibold text-blue-500">Avertissement</Text>
        <Text className="mt-2 text-sm leading-6 text-gray-700">
          Offre indicative, sous réserve d&apos;analyse du dossier et validation par un partenaire financeur.
        </Text>
      </View>

      <TouchableOpacity
        className={`items-center rounded-2xl py-4 ${submitDeal.isPending ? 'bg-blue-400' : 'bg-blue-500'}`}
        disabled={submitDeal.isPending || !pricingProposal || !riskAssessment}
        onPress={handleSubmit}
      >
        {submitDeal.isPending ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <Text className="text-base font-semibold text-white">Soumettre le dossier</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  )
}

import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'expo-router'
import { Controller, useForm } from 'react-hook-form'
import { ActivityIndicator, ScrollView, Text, TextInput, TouchableOpacity, View } from 'react-native'
import { z } from 'zod'

import { useEnrichCompany } from '@/src/hooks/useEnrichCompany'

const schema = z.object({
  sirenOrSiret: z
    .string()
    .trim()
    .regex(/^\d{9}$|^\d{14}$/, 'SIREN 9 chiffres ou SIRET 14 chiffres'),
})

type FormData = z.infer<typeof schema>

export default function NewDealIndexScreen() {
  const router = useRouter()
  const enrichCompany = useEnrichCompany()
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { sirenOrSiret: '' },
  })

  const onSubmit = ({ sirenOrSiret }: FormData) => {
    enrichCompany.mutate(sirenOrSiret, {
      onSuccess: () => router.push('/(partner)/deals/new/enrichment' as never),
    })
  }

  return (
    <ScrollView
      className="flex-1 bg-gray-50"
      contentInsetAdjustmentBehavior="automatic"
      keyboardShouldPersistTaps="handled"
      contentContainerStyle={{ padding: 20, gap: 20 }}
    >
      <View className="rounded-3xl bg-navy-900 p-6">
        <Text className="text-sm font-medium uppercase tracking-[2px] text-white/70">Phase 3</Text>
        <Text className="mt-3 text-3xl font-bold text-white">Créer un dossier de leasing</Text>
        <Text className="mt-2 text-sm leading-6 text-white/80">
          Commencez par identifier l’entreprise avec son SIREN ou son SIRET.
        </Text>
      </View>

      <View className="rounded-3xl border border-gray-200 bg-white p-5">
        <Text className="text-base font-semibold text-navy-900">Identification</Text>
        <Text className="mt-1 text-sm text-gray-500">
          L’enrichissement est mocké, mais le flow complet est celui du MVP.
        </Text>

        <View className="mt-5">
          <Text className="mb-2 text-sm font-medium text-navy-900">SIREN ou SIRET</Text>
          <Controller
            control={control}
            name="sirenOrSiret"
            render={({ field: { onChange, onBlur, value } }) => (
              <TextInput
                className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-4 text-base text-navy-900"
                keyboardType="number-pad"
                placeholder="823456789"
                placeholderTextColor="#9CA3AF"
                value={value}
                onChangeText={(text) => onChange(text.replace(/\D/g, ''))}
                onBlur={onBlur}
                maxLength={14}
              />
            )}
          />
          {errors.sirenOrSiret ? (
            <Text className="mt-2 text-sm text-danger">{errors.sirenOrSiret.message}</Text>
          ) : null}
          {enrichCompany.error instanceof Error ? (
            <Text className="mt-2 text-sm text-danger">{enrichCompany.error.message}</Text>
          ) : null}
        </View>
      </View>

      <View className="rounded-3xl border border-blue-100 bg-blue-50 p-5">
        <Text className="text-sm font-semibold text-blue-500">Étapes à venir</Text>
        <Text className="mt-2 text-sm leading-6 text-gray-600">
          1. Vérification de la société
          {'\n'}2. Upload du devis fournisseur
          {'\n'}3. Calcul de l’offre indicative
          {'\n'}4. Soumission du dossier
        </Text>
      </View>

      <TouchableOpacity
        className={`items-center rounded-2xl bg-blue-500 py-4 ${enrichCompany.isPending ? 'opacity-70' : ''}`}
        activeOpacity={0.85}
        disabled={enrichCompany.isPending}
        onPress={handleSubmit(onSubmit)}
      >
        {enrichCompany.isPending ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <Text className="text-base font-semibold text-white">Continuer</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  )
}

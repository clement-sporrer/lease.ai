import * as DocumentPicker from 'expo-document-picker'
import { useMutation } from '@tanstack/react-query'
import { useRouter } from 'expo-router'
import { useMemo, useState } from 'react'
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native'

import { useUploadDocument } from '@/src/hooks/useUploadDocument'
import { patchDeal } from '@/src/services/deals'
import { createQuote, extractQuote, patchQuote } from '@/src/services/quotes'
import { useDealCreationStore } from '@/src/stores/dealCreation'
import { Quote } from '@/src/types/quote'

function eurosToCents(value: string): number | null {
  if (!value.trim()) return null
  const normalized = Number(value.replace(',', '.'))
  if (Number.isNaN(normalized)) return null
  return Math.round(normalized * 100)
}

function centsToEuros(value: number | null | undefined): string {
  if (value == null) return ''
  return (value / 100).toFixed(2).replace('.', ',')
}

export default function QuoteScreen() {
  const router = useRouter()
  const deal = useDealCreationStore((state) => state.deal)
  const quote = useDealCreationStore((state) => state.quote)
  const setQuote = useDealCreationStore((state) => state.setQuote)
  const setDeal = useDealCreationStore((state) => state.setDeal)
  const uploadDocument = useUploadDocument()
  const [fileName, setFileName] = useState<string | null>(null)
  const [supplierName, setSupplierName] = useState(quote?.supplier_name ?? '')
  const [quoteNumber, setQuoteNumber] = useState(quote?.quote_number ?? '')
  const [amountExclTax, setAmountExclTax] = useState(centsToEuros(quote?.amount_excl_tax_cents))
  const [amountInclTax, setAmountInclTax] = useState(centsToEuros(quote?.amount_incl_tax_cents))
  const [category, setCategory] = useState(quote?.category ?? 'hardware')
  const [durationMonths, setDurationMonths] = useState(deal?.duration_months ? String(deal.duration_months) : '36')

  const createQuoteMutation = useMutation({
    mutationFn: (documentId: string | null) =>
      createQuote(deal!.id, {
        document_id: documentId,
        supplier_name: supplierName || null,
        quote_number: quoteNumber || null,
        amount_excl_tax_cents: eurosToCents(amountExclTax),
        amount_incl_tax_cents: eurosToCents(amountInclTax),
        category: category || null,
        currency: 'EUR',
      }),
    onSuccess: (newQuote) => {
      setQuote(newQuote)
      setSupplierName(newQuote.supplier_name ?? '')
      setQuoteNumber(newQuote.quote_number ?? '')
      setAmountExclTax(centsToEuros(newQuote.amount_excl_tax_cents))
      setAmountInclTax(centsToEuros(newQuote.amount_incl_tax_cents))
      setCategory(newQuote.category ?? 'hardware')
    },
  })

  const extractQuoteMutation = useMutation({
    mutationFn: (quoteId: string) => extractQuote(deal!.id, quoteId),
    onSuccess: (extractedQuote) => {
      setQuote(extractedQuote)
      setSupplierName(extractedQuote.supplier_name ?? '')
      setQuoteNumber(extractedQuote.quote_number ?? '')
      setAmountExclTax(centsToEuros(extractedQuote.amount_excl_tax_cents))
      setAmountInclTax(centsToEuros(extractedQuote.amount_incl_tax_cents))
      setCategory(extractedQuote.category ?? 'hardware')
    },
  })

  const saveQuoteMutation = useMutation({
    mutationFn: async (currentQuote: Quote) => {
      const updatedQuote = await patchQuote(deal!.id, currentQuote.id, {
        supplier_name: supplierName || null,
        quote_number: quoteNumber || null,
        amount_excl_tax_cents: eurosToCents(amountExclTax),
        amount_incl_tax_cents: eurosToCents(amountInclTax),
        category: category || null,
      })
      const updatedDeal = await patchDeal(deal!.id, {
        amount_cents: updatedQuote.amount_incl_tax_cents,
        duration_months: Number(durationMonths),
      })
      return { updatedQuote, updatedDeal }
    },
    onSuccess: ({ updatedQuote, updatedDeal }) => {
      setQuote(updatedQuote)
      setDeal(updatedDeal)
      router.push('/(partner)/deals/new/offer' as never)
    },
  })

  const busy =
    uploadDocument.isPending ||
    createQuoteMutation.isPending ||
    extractQuoteMutation.isPending ||
    saveQuoteMutation.isPending

  const canContinue = useMemo(() => {
    return !!(
      deal &&
      quote &&
      supplierName.trim() &&
      eurosToCents(amountInclTax) &&
      Number(durationMonths) > 0
    )
  }, [deal, quote, supplierName, amountInclTax, durationMonths])

  if (!deal) {
    return (
      <ScrollView
        className="flex-1 bg-gray-50"
        contentInsetAdjustmentBehavior="automatic"
        contentContainerStyle={{ padding: 20, gap: 16 }}
      >
        <View className="rounded-3xl border border-warning/20 bg-white p-5">
          <Text className="text-lg font-semibold text-navy-900">Dossier introuvable</Text>
          <Text className="mt-2 text-sm text-gray-600">
            Le dossier n’a pas encore été créé. Reprenez depuis l’étape entreprise.
          </Text>
        </View>
        <TouchableOpacity
          className="items-center rounded-2xl bg-blue-500 py-4"
          onPress={() => router.replace('/(partner)/deals/new/enrichment' as never)}
        >
          <Text className="text-base font-semibold text-white">Retour</Text>
        </TouchableOpacity>
      </ScrollView>
    )
  }

  const handlePickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'image/*'],
        copyToCacheDirectory: true,
        multiple: false,
      })

      if (result.canceled) return

      const asset = result.assets[0]
      setFileName(asset.name)

      uploadDocument.mutate(
        {
          dealId: deal.id,
          fileUri: asset.uri,
          fileName: asset.name,
          mimeType: asset.mimeType ?? 'application/pdf',
          sizeBytes: asset.size ?? 0,
        },
        {
          onSuccess: async (document) => {
            const newQuote = await createQuoteMutation.mutateAsync(document.id)
            await extractQuoteMutation.mutateAsync(newQuote.id)
          },
          onError: (error) => {
            Alert.alert('Upload impossible', error instanceof Error ? error.message : 'Erreur inconnue')
          },
        },
      )
    } catch (error) {
      Alert.alert('Fichier invalide', error instanceof Error ? error.message : 'Erreur inconnue')
    }
  }

  const handleContinue = async () => {
    if (!quote) {
      Alert.alert('Devis manquant', 'Chargez un devis avant de continuer.')
      return
    }
    if (!canContinue) {
      Alert.alert('Champs incomplets', 'Renseignez les montants, le fournisseur et la durée.')
      return
    }
    await saveQuoteMutation.mutateAsync(quote)
  }

  return (
    <ScrollView
      className="flex-1 bg-gray-50"
      contentInsetAdjustmentBehavior="automatic"
      contentContainerStyle={{ padding: 20, gap: 20 }}
      keyboardShouldPersistTaps="handled"
    >
      <View className="rounded-3xl bg-white p-5">
        <Text className="text-sm font-medium uppercase tracking-[2px] text-gray-500">Devis</Text>
        <Text className="mt-3 text-2xl font-bold text-navy-900">Upload fournisseur</Text>
        <Text className="mt-2 text-sm leading-6 text-gray-600">
          Chargez un PDF ou une image, puis corrigez si besoin les données extraites.
        </Text>
      </View>

      <TouchableOpacity
        className={`rounded-3xl border border-dashed border-blue-500 bg-blue-50 p-5 ${busy ? 'opacity-70' : ''}`}
        disabled={busy}
        onPress={handlePickDocument}
      >
        <Text className="text-sm font-semibold text-blue-500">
          {fileName ? 'Remplacer le document' : 'Choisir un document'}
        </Text>
        <Text className="mt-2 text-sm text-gray-600">
          {fileName ?? 'PDF ou image du devis fournisseur'}
        </Text>
        {busy ? <ActivityIndicator className="mt-4" color="#2563EB" /> : null}
      </TouchableOpacity>

      <View className="rounded-3xl border border-gray-200 bg-white p-5">
        <Text className="text-base font-semibold text-navy-900">Données du devis</Text>
        <View className="mt-4 gap-4">
          <View>
            <Text className="mb-2 text-sm font-medium text-navy-900">Fournisseur</Text>
            <TextInput
              className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-4 text-base text-navy-900"
              value={supplierName}
              onChangeText={setSupplierName}
              placeholder="Lenovo France"
              placeholderTextColor="#9CA3AF"
            />
          </View>
          <View>
            <Text className="mb-2 text-sm font-medium text-navy-900">Numéro de devis</Text>
            <TextInput
              className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-4 text-base text-navy-900"
              value={quoteNumber}
              onChangeText={setQuoteNumber}
              placeholder="DEV-2026-001"
              placeholderTextColor="#9CA3AF"
            />
          </View>
          <View>
            <Text className="mb-2 text-sm font-medium text-navy-900">Montant HT (€)</Text>
            <TextInput
              className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-4 text-base text-navy-900"
              value={amountExclTax}
              onChangeText={setAmountExclTax}
              keyboardType="decimal-pad"
              placeholder="99000,00"
              placeholderTextColor="#9CA3AF"
            />
          </View>
          <View>
            <Text className="mb-2 text-sm font-medium text-navy-900">Montant TTC (€)</Text>
            <TextInput
              className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-4 text-base text-navy-900"
              value={amountInclTax}
              onChangeText={setAmountInclTax}
              keyboardType="decimal-pad"
              placeholder="118800,00"
              placeholderTextColor="#9CA3AF"
            />
          </View>
          <View>
            <Text className="mb-2 text-sm font-medium text-navy-900">Catégorie</Text>
            <TextInput
              className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-4 text-base text-navy-900"
              value={category}
              onChangeText={setCategory}
              placeholder="hardware"
              placeholderTextColor="#9CA3AF"
            />
          </View>
          <View>
            <Text className="mb-2 text-sm font-medium text-navy-900">Durée (mois)</Text>
            <TextInput
              className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-4 text-base text-navy-900"
              value={durationMonths}
              onChangeText={(text) => setDurationMonths(text.replace(/\D/g, ''))}
              keyboardType="number-pad"
              placeholder="36"
              placeholderTextColor="#9CA3AF"
            />
          </View>
        </View>
      </View>

      <TouchableOpacity
        className={`items-center rounded-2xl py-4 ${canContinue ? 'bg-blue-500' : 'bg-gray-300'}`}
        disabled={!canContinue || busy}
        onPress={handleContinue}
      >
        {saveQuoteMutation.isPending ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <Text className="text-base font-semibold text-white">Calculer l’offre</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  )
}

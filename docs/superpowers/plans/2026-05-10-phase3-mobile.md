# Phase 3 Mobile — Deal Creation Flow

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the 4-screen partner deal creation wizard (SCR-PARTNER-003 → 006) with full API integration: SIREN enrichment, deal creation, PDF quote upload to Supabase Storage, indicative pricing + risk score, and deal submission.

**Architecture:** Wizard flow using Expo Router file-based navigation under `app/(partner)/deals/new/`. State persisted in `useDealCreationStore` (Zustand) so back navigation never re-creates a deal. All API calls via TanStack Query mutations. Auth token from Supabase session.

**Tech Stack:** Expo SDK 54, Expo Router 6, TypeScript strict, NativeWind (Tailwind), TanStack Query v5, Zustand v5, React Hook Form + `@hookform/resolvers` + Zod v4, `expo-document-picker`. Run `npx tsc --noEmit` from `mobile/` to verify types.

**Prerequisite — install two missing dependencies:**
```bash
cd mobile && npx expo install expo-document-picker && npm install @hookform/resolvers
```
Add `EXPO_PUBLIC_API_URL=http://localhost:8000` to `mobile/.env.local`.

---

## File Map

**New files:**
- `mobile/src/types/deal.ts`
- `mobile/src/types/company.ts`
- `mobile/src/types/quote.ts`
- `mobile/src/types/pricing.ts`
- `mobile/src/types/risk.ts`
- `mobile/src/lib/api.ts` — authenticated fetch wrapper
- `mobile/src/services/deals.ts`
- `mobile/src/services/companies.ts`
- `mobile/src/services/documents.ts`
- `mobile/src/services/pricing.ts`
- `mobile/src/stores/dealCreation.ts`
- `mobile/src/hooks/useEnrichCompany.ts`
- `mobile/src/hooks/useCreateDeal.ts`
- `mobile/src/hooks/useUploadDocument.ts`
- `mobile/src/hooks/useIndicativePricing.ts`
- `mobile/src/hooks/useAssessRisk.ts`
- `mobile/src/hooks/useSubmitDeal.ts`
- `mobile/app/(partner)/deals/new/_layout.tsx`
- `mobile/app/(partner)/deals/new/index.tsx` — SCR-PARTNER-003
- `mobile/app/(partner)/deals/new/enrichment.tsx` — SCR-PARTNER-004
- `mobile/app/(partner)/deals/new/quote.tsx` — SCR-PARTNER-005
- `mobile/app/(partner)/deals/new/offer.tsx` — SCR-PARTNER-006

**Modified files:**
- `mobile/app/(partner)/index.tsx` — wire "Nouveau dossier" CTA

---

## Task 1: Install Dependencies + Types + API Client

**Files:**
- Create: `mobile/src/types/deal.ts`
- Create: `mobile/src/types/company.ts`
- Create: `mobile/src/types/quote.ts`
- Create: `mobile/src/types/pricing.ts`
- Create: `mobile/src/types/risk.ts`
- Create: `mobile/src/lib/api.ts`

- [ ] **Step 1: Install dependencies**

```bash
cd mobile && npx expo install expo-document-picker && npm install @hookform/resolvers
```
Add to `mobile/.env.local` (create if missing):
```
EXPO_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 2: Write deal types**

```typescript
// mobile/src/types/deal.ts
export type DealStatus =
  | 'draft'
  | 'company_enriched'
  | 'quote_added'
  | 'indicative_offer_ready'
  | 'submitted'
  | 'internal_review'
  | 'missing_documents'
  | 'pre_approved'
  | 'refi_package_ready'
  | 'refi_review'
  | 'financier_approved'
  | 'financier_rejected'
  | 'firm_offer_generated'
  | 'contract_generated'
  | 'signing'
  | 'signed'
  | 'activation_pending'
  | 'active'
  | 'cancelled'

export interface Deal {
  id: string
  public_id: string
  company_id: string
  partner_org_id: string | null
  submitted_by_user_id: string | null
  status: DealStatus
  amount_cents: number | null
  currency: string
  duration_months: number | null
  risk_score: number | null
  risk_band: 'green' | 'orange' | 'red' | null
  monthly_payment_cents: number | null
  created_at: string
  updated_at: string
}

export interface DealCreatePayload {
  company_id: string
  amount_cents: number
  duration_months: number
  currency?: string
}
```

- [ ] **Step 3: Write company types**

```typescript
// mobile/src/types/company.ts
export interface Company {
  id: string
  siren: string
  siret: string | null
  legal_name: string
  trade_name: string | null
  address: {
    street?: string
    city?: string
    zip?: string
  } | null
  activity_code: string | null
  creation_date: string | null  // ISO date string
  legal_status: string | null
  is_active: boolean
  enrichment_source: string | null
  created_at: string
}
```

- [ ] **Step 4: Write quote, pricing, and risk types**

```typescript
// mobile/src/types/quote.ts
export interface Quote {
  id: string
  deal_id: string
  document_id: string | null
  supplier_name: string | null
  quote_number: string | null
  amount_excl_tax_cents: number | null
  amount_incl_tax_cents: number | null
  currency: string
  category: string | null
  extraction_status: 'pending' | 'done' | 'failed'
  created_at: string
  updated_at: string
}
```

```typescript
// mobile/src/types/pricing.ts
export interface PricingProposal {
  id?: string
  deal_id?: string
  type: 'indicative' | 'firm'
  amount_financed_cents: number
  duration_months: number
  monthly_payment_cents: number
  refi_rate: number
  margin_rate: number
  fees_cents: number
  assumptions: Record<string, unknown> | null
  version: number
  created_at?: string
}

export interface IndicativePricingRequest {
  amount_cents: number
  duration_months: number
  refi_rate?: number
  margin_rate?: number
  fees_cents?: number
}
```

```typescript
// mobile/src/types/risk.ts
export type RiskBand = 'green' | 'orange' | 'red'

export interface RiskAssessment {
  id: string
  deal_id: string
  score: number
  band: RiskBand
  flags: string[] | null
  rules_applied: string[] | null
  recommendation: string | null
  version: number
  created_at: string
}
```

- [ ] **Step 5: Write the API client**

```typescript
// mobile/src/lib/api.ts
import { supabase } from './supabase'

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000'

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (!token) throw new Error('Not authenticated')
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}${path}`, { headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw { status: res.status, error: body.error ?? body }
  }
  const body = await res.json()
  return body.data as T
}

export async function apiPost<T>(
  path: string,
  payload: unknown,
  extraHeaders: Record<string, string> = {},
): Promise<T> {
  const headers = { ...(await getAuthHeaders()), ...extraHeaders }
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw { status: res.status, error: body.error ?? body }
  }
  const body = await res.json()
  return body.data as T
}

export async function apiPatch<T>(path: string, payload: unknown): Promise<T> {
  const headers = await getAuthHeaders()
  const res = await fetch(`${API_URL}${path}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw { status: res.status, error: body.error ?? body }
  }
  const body = await res.json()
  return body.data as T
}
```

- [ ] **Step 6: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 7: Commit**

```bash
git add mobile/src/types/ mobile/src/lib/api.ts mobile/.env.local
git commit -m "feat(mobile): Phase 3 types + authenticated API client"
```

---

## Task 2: Service Layer

**Files:**
- Create: `mobile/src/services/deals.ts`
- Create: `mobile/src/services/companies.ts`
- Create: `mobile/src/services/documents.ts`
- Create: `mobile/src/services/pricing.ts`

- [ ] **Step 1: Write deals service**

```typescript
// mobile/src/services/deals.ts
import { apiGet, apiPost, apiPatch } from '@/src/lib/api'
import { Deal, DealCreatePayload } from '@/src/types/deal'

export async function createDeal(payload: DealCreatePayload, idempotencyKey: string): Promise<Deal> {
  return apiPost<Deal>('/deals', payload, { 'Idempotency-Key': idempotencyKey })
}

export async function getDeal(dealId: string): Promise<Deal> {
  return apiGet<Deal>(`/deals/${dealId}`)
}

export async function patchDeal(dealId: string, payload: Partial<DealCreatePayload>): Promise<Deal> {
  return apiPatch<Deal>(`/deals/${dealId}`, payload)
}

export async function submitDeal(dealId: string): Promise<Deal> {
  return apiPost<Deal>(`/deals/${dealId}/submit`, {})
}

export async function savePricingProposal(dealId: string, payload: {
  amount_cents: number
  duration_months: number
  refi_rate?: number
  margin_rate?: number
  fees_cents?: number
}): Promise<Deal> {
  return apiPost<Deal>(`/deals/${dealId}/pricing/recalculate`, payload)
}
```

- [ ] **Step 2: Write companies service**

```typescript
// mobile/src/services/companies.ts
import { apiPost } from '@/src/lib/api'
import { Company } from '@/src/types/company'

export async function enrichCompany(siren: string): Promise<Company> {
  return apiPost<Company>('/companies/enrich', { siren })
}
```

- [ ] **Step 3: Write documents service**

```typescript
// mobile/src/services/documents.ts
import { supabase } from '@/src/lib/supabase'
import { apiPost } from '@/src/lib/api'

export interface UploadUrlResponse {
  document_id: string
  upload_url: string
  storage_path: string
  expires_in: number
}

export interface DocumentRecord {
  id: string
  deal_id: string
  type: string
  status: string
  file_name: string
  mime_type: string | null
  size_bytes: number | null
  version: number
  created_at: string
}

export async function getUploadUrl(dealId: string): Promise<UploadUrlResponse> {
  return apiPost<UploadUrlResponse>(`/deals/${dealId}/documents/upload-url`, {})
}

export async function uploadFileDirect(uploadUrl: string, fileUri: string, mimeType: string): Promise<void> {
  const response = await fetch(fileUri)
  const blob = await response.blob()
  const uploadRes = await fetch(uploadUrl, {
    method: 'PUT',
    headers: { 'Content-Type': mimeType },
    body: blob,
  })
  if (!uploadRes.ok) {
    throw new Error(`Upload failed: ${uploadRes.status}`)
  }
}

export async function confirmUpload(
  dealId: string,
  documentId: string,
  storagePath: string,
  fileName: string,
  mimeType: string,
  sizeBytes: number,
): Promise<DocumentRecord> {
  return apiPost<DocumentRecord>(`/deals/${dealId}/documents/confirm`, {
    document_id: documentId,
    storage_key: storagePath,
    file_name: fileName,
    mime_type: mimeType,
    size_bytes: sizeBytes,
    document_type: 'quote',
  })
}
```

- [ ] **Step 4: Write pricing service**

```typescript
// mobile/src/services/pricing.ts
import { apiPost } from '@/src/lib/api'
import { PricingProposal, IndicativePricingRequest } from '@/src/types/pricing'
import { RiskAssessment } from '@/src/types/risk'

export async function getIndicativePricing(payload: IndicativePricingRequest): Promise<PricingProposal> {
  return apiPost<PricingProposal>('/pricing/indicative', payload)
}

export async function assessRisk(dealId: string): Promise<RiskAssessment> {
  return apiPost<RiskAssessment>(`/deals/${dealId}/risk/assess`, {})
}
```

- [ ] **Step 5: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 6: Commit**

```bash
git add mobile/src/services/
git commit -m "feat(mobile): service layer — deals, companies, documents, pricing"
```

---

## Task 3: useDealCreationStore

**Files:**
- Create: `mobile/src/stores/dealCreation.ts`

- [ ] **Step 1: Write the store**

```typescript
// mobile/src/stores/dealCreation.ts
import { create } from 'zustand'
import { Company } from '@/src/types/company'
import { Deal } from '@/src/types/deal'
import { Quote } from '@/src/types/quote'
import { PricingProposal } from '@/src/types/pricing'
import { RiskAssessment } from '@/src/types/risk'

interface DealCreationState {
  // Wizard data
  siren: string
  company: Company | null
  deal: Deal | null
  quote: Quote | null
  documentId: string | null
  pricingProposal: PricingProposal | null
  riskAssessment: RiskAssessment | null
  // Idempotency key — generated once per wizard session
  idempotencyKey: string

  // Actions
  setSiren: (siren: string) => void
  setCompany: (company: Company) => void
  setDeal: (deal: Deal) => void
  setQuote: (quote: Quote) => void
  setDocumentId: (id: string) => void
  setPricingProposal: (proposal: PricingProposal) => void
  setRiskAssessment: (assessment: RiskAssessment) => void
  reset: () => void
}

function generateIdempotencyKey(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

const INITIAL_STATE = {
  siren: '',
  company: null,
  deal: null,
  quote: null,
  documentId: null,
  pricingProposal: null,
  riskAssessment: null,
  idempotencyKey: generateIdempotencyKey(),
}

export const useDealCreationStore = create<DealCreationState>((set) => ({
  ...INITIAL_STATE,

  setSiren: (siren) => set({ siren }),
  setCompany: (company) => set({ company }),
  setDeal: (deal) => set({ deal }),
  setQuote: (quote) => set({ quote }),
  setDocumentId: (documentId) => set({ documentId }),
  setPricingProposal: (pricingProposal) => set({ pricingProposal }),
  setRiskAssessment: (riskAssessment) => set({ riskAssessment }),
  reset: () => set({ ...INITIAL_STATE, idempotencyKey: generateIdempotencyKey() }),
}))
```

- [ ] **Step 2: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 3: Commit**

```bash
git add mobile/src/stores/dealCreation.ts
git commit -m "feat(mobile): useDealCreationStore — wizard state with idempotency key"
```

---

## Task 4: TanStack Query Hooks

**Files:**
- Create: `mobile/src/hooks/useEnrichCompany.ts`
- Create: `mobile/src/hooks/useCreateDeal.ts`
- Create: `mobile/src/hooks/useUploadDocument.ts`
- Create: `mobile/src/hooks/useIndicativePricing.ts`
- Create: `mobile/src/hooks/useAssessRisk.ts`
- Create: `mobile/src/hooks/useSubmitDeal.ts`

- [ ] **Step 1: Write enrichment hook**

```typescript
// mobile/src/hooks/useEnrichCompany.ts
import { useMutation } from '@tanstack/react-query'
import { enrichCompany } from '@/src/services/companies'
import { useDealCreationStore } from '@/src/stores/dealCreation'

export function useEnrichCompany() {
  const setCompany = useDealCreationStore((s) => s.setCompany)
  const setSiren = useDealCreationStore((s) => s.setSiren)

  return useMutation({
    mutationFn: (siren: string) => enrichCompany(siren),
    onSuccess: (company, siren) => {
      setCompany(company)
      setSiren(siren)
    },
    retry: 1,
  })
}
```

- [ ] **Step 2: Write create deal hook**

```typescript
// mobile/src/hooks/useCreateDeal.ts
import { useMutation } from '@tanstack/react-query'
import { createDeal } from '@/src/services/deals'
import { useDealCreationStore } from '@/src/stores/dealCreation'
import { DealCreatePayload } from '@/src/types/deal'

export function useCreateDeal() {
  const setDeal = useDealCreationStore((s) => s.setDeal)
  const idempotencyKey = useDealCreationStore((s) => s.idempotencyKey)
  const deal = useDealCreationStore((s) => s.deal)

  return useMutation({
    mutationFn: (payload: DealCreatePayload) => {
      // Guard: never re-POST if deal already exists
      if (deal) return Promise.resolve(deal)
      return createDeal(payload, idempotencyKey)
    },
    onSuccess: (newDeal) => setDeal(newDeal),
    retry: 1,
  })
}
```

- [ ] **Step 3: Write document upload hook**

```typescript
// mobile/src/hooks/useUploadDocument.ts
import { useMutation } from '@tanstack/react-query'
import { getUploadUrl, uploadFileDirect, confirmUpload } from '@/src/services/documents'
import { useDealCreationStore } from '@/src/stores/dealCreation'

interface UploadPayload {
  dealId: string
  fileUri: string
  fileName: string
  mimeType: string
  sizeBytes: number
}

export function useUploadDocument() {
  const setDocumentId = useDealCreationStore((s) => s.setDocumentId)

  return useMutation({
    mutationFn: async ({ dealId, fileUri, fileName, mimeType, sizeBytes }: UploadPayload) => {
      const urlData = await getUploadUrl(dealId)
      await uploadFileDirect(urlData.upload_url, fileUri, mimeType)
      const doc = await confirmUpload(dealId, urlData.document_id, urlData.storage_path, fileName, mimeType, sizeBytes)
      return doc
    },
    onSuccess: (doc) => setDocumentId(doc.id),
    retry: 1,
  })
}
```

- [ ] **Step 4: Write pricing and risk hooks**

```typescript
// mobile/src/hooks/useIndicativePricing.ts
import { useMutation } from '@tanstack/react-query'
import { getIndicativePricing } from '@/src/services/pricing'
import { useDealCreationStore } from '@/src/stores/dealCreation'
import { IndicativePricingRequest } from '@/src/types/pricing'

export function useIndicativePricing() {
  const setPricingProposal = useDealCreationStore((s) => s.setPricingProposal)

  return useMutation({
    mutationFn: (payload: IndicativePricingRequest) => getIndicativePricing(payload),
    onSuccess: (proposal) => setPricingProposal(proposal),
  })
}
```

```typescript
// mobile/src/hooks/useAssessRisk.ts
import { useMutation } from '@tanstack/react-query'
import { assessRisk } from '@/src/services/pricing'
import { useDealCreationStore } from '@/src/stores/dealCreation'

export function useAssessRisk() {
  const setRiskAssessment = useDealCreationStore((s) => s.setRiskAssessment)

  return useMutation({
    mutationFn: (dealId: string) => assessRisk(dealId),
    onSuccess: (assessment) => setRiskAssessment(assessment),
  })
}
```

```typescript
// mobile/src/hooks/useSubmitDeal.ts
import { useMutation } from '@tanstack/react-query'
import { submitDeal, savePricingProposal } from '@/src/services/deals'
import { useDealCreationStore } from '@/src/stores/dealCreation'

export function useSubmitDeal() {
  const reset = useDealCreationStore((s) => s.reset)
  const pricingProposal = useDealCreationStore((s) => s.pricingProposal)

  return useMutation({
    mutationFn: async (dealId: string) => {
      // Save pricing proposal first to trigger indicative_offer_ready transition
      if (pricingProposal) {
        await savePricingProposal(dealId, {
          amount_cents: pricingProposal.amount_financed_cents,
          duration_months: pricingProposal.duration_months,
          refi_rate: pricingProposal.refi_rate,
          margin_rate: pricingProposal.margin_rate,
          fees_cents: pricingProposal.fees_cents,
        })
      }
      return submitDeal(dealId)
    },
    onSuccess: () => reset(),
  })
}
```

- [ ] **Step 5: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 6: Commit**

```bash
git add mobile/src/hooks/
git commit -m "feat(mobile): TanStack Query hooks for deal creation wizard"
```

---

## Task 5: SCR-PARTNER-003 — SIREN Form + Wizard Layout

**Files:**
- Create: `mobile/app/(partner)/deals/new/_layout.tsx`
- Create: `mobile/app/(partner)/deals/new/index.tsx`

- [ ] **Step 1: Write the wizard layout**

```typescript
// mobile/app/(partner)/deals/new/_layout.tsx
import { Stack } from 'expo-router'

export default function NewDealLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: '#0D183D' },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: { fontWeight: '600' },
      }}
    >
      <Stack.Screen name="index" options={{ title: 'Nouveau dossier' }} />
      <Stack.Screen name="enrichment" options={{ title: 'Entreprise' }} />
      <Stack.Screen name="quote" options={{ title: 'Devis' }} />
      <Stack.Screen name="offer" options={{ title: 'Offre indicative' }} />
    </Stack>
  )
}
```

- [ ] **Step 2: Write SCR-PARTNER-003**

```typescript
// mobile/app/(partner)/deals/new/index.tsx
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native'
import { useRouter } from 'expo-router'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useEnrichCompany } from '@/src/hooks/useEnrichCompany'

const schema = z.object({
  siren: z
    .string()
    .regex(/^\d{9}$|^\d{14}$/, 'SIREN (9 chiffres) ou SIRET (14 chiffres) uniquement'),
})

type FormData = z.infer<typeof schema>

export default function CreateDealSiren() {
  const router = useRouter()
  const { mutate: enrich, isPending, error } = useEnrichCompany()

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = ({ siren }: FormData) => {
    enrich(siren, {
      onSuccess: () => router.push('/(partner)/deals/new/enrichment'),
    })
  }

  return (
    <SafeAreaView className="flex-1 bg-white" edges={['bottom']}>
      <View className="flex-1 px-5 pt-8">
        <Text className="text-2xl font-bold text-navy-900 mb-2">Identifier l'entreprise</Text>
        <Text className="text-sm text-gray-500 mb-8">
          Entrez le SIREN (9 chiffres) ou SIRET (14 chiffres) du locataire.
        </Text>

        <Text className="text-sm font-medium text-navy-900 mb-1">SIREN / SIRET</Text>
        <Controller
          control={control}
          name="siren"
          render={({ field: { onChange, value } }) => (
            <TextInput
              className="border border-gray-200 rounded-xl px-4 py-3 text-base font-mono text-navy-900 bg-gray-50"
              placeholder="823456789"
              keyboardType="numeric"
              maxLength={14}
              value={value}
              onChangeText={onChange}
              autoFocus
            />
          )}
        />
        {errors.siren && (
          <Text className="text-danger text-sm mt-1">{errors.siren.message}</Text>
        )}

        {error && (
          <View className="bg-red-50 rounded-xl p-3 mt-4">
            <Text className="text-danger text-sm">
              Enrichissement impossible. Vérifiez le numéro et réessayez.
            </Text>
          </View>
        )}

        <TouchableOpacity
          className="bg-blue-500 rounded-xl py-4 mt-8 items-center"
          onPress={handleSubmit(onSubmit)}
          disabled={isPending}
        >
          {isPending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="text-white font-semibold text-base">Enrichir l'entreprise</Text>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  )
}
```

- [ ] **Step 3: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 4: Commit**

```bash
git add mobile/app/(partner)/deals/new/
git commit -m "feat(mobile): SCR-PARTNER-003 SIREN form + wizard layout"
```

---

## Task 6: SCR-PARTNER-004 — Company Enrichment

**Files:**
- Create: `mobile/app/(partner)/deals/new/enrichment.tsx`

- [ ] **Step 1: Write SCR-PARTNER-004**

```typescript
// mobile/app/(partner)/deals/new/enrichment.tsx
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native'
import { useRouter } from 'expo-router'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useDealCreationStore } from '@/src/stores/dealCreation'
import { useCreateDeal } from '@/src/hooks/useCreateDeal'

const AMOUNT_CENTS_DEFAULT = 10_000_000  // 100 000€ default, user can change on offer screen
const DURATION_DEFAULT = 36

function InfoRow({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <View className="flex-row justify-between py-3 border-b border-gray-100">
      <Text className="text-sm text-gray-500">{label}</Text>
      <Text className="text-sm font-medium text-navy-900 max-w-[60%] text-right">
        {value ?? '—'}
      </Text>
    </View>
  )
}

function Alert({ message }: { message: string }) {
  return (
    <View className="bg-warning/10 border border-warning rounded-xl p-3 mb-3">
      <Text className="text-warning text-sm font-medium">{message}</Text>
    </View>
  )
}

export default function CompanyEnrichment() {
  const router = useRouter()
  const company = useDealCreationStore((s) => s.company)
  const { mutate: createDeal, isPending } = useCreateDeal()

  if (!company) {
    router.replace('/(partner)/deals/new')
    return null
  }

  const ageYears = company.creation_date
    ? (Date.now() - new Date(company.creation_date).getTime()) / (1000 * 60 * 60 * 24 * 365)
    : null

  const isRecent = ageYears !== null && ageYears < 2
  const isInactive = !company.is_active

  const onConfirm = () => {
    createDeal(
      {
        company_id: company.id,
        amount_cents: AMOUNT_CENTS_DEFAULT,
        duration_months: DURATION_DEFAULT,
      },
      {
        onSuccess: () => router.push('/(partner)/deals/new/quote'),
      },
    )
  }

  return (
    <SafeAreaView className="flex-1 bg-white" edges={['bottom']}>
      <ScrollView className="flex-1 px-5 pt-6" showsVerticalScrollIndicator={false}>
        <Text className="text-xl font-bold text-navy-900 mb-1">{company.legal_name}</Text>
        <Text className="text-sm text-gray-500 mb-6">Vérifiez les informations avant de continuer.</Text>

        {isRecent && <Alert message="Société créée il y a moins de 2 ans — profil de risque élevé." />}
        {isInactive && <Alert message="Société inactive ou radiée — vérifiez avant de continuer." />}

        <View className="bg-gray-50 rounded-2xl px-4 mb-6">
          <InfoRow label="SIREN" value={company.siren} />
          <InfoRow label="SIRET" value={company.siret} />
          <InfoRow label="Forme juridique" value={company.legal_status} />
          <InfoRow label="Code activité" value={company.activity_code} />
          <InfoRow
            label="Création"
            value={
              company.creation_date
                ? new Date(company.creation_date).toLocaleDateString('fr-FR')
                : null
            }
          />
          <InfoRow
            label="Adresse"
            value={
              company.address
                ? `${company.address.street ?? ''}, ${company.address.zip ?? ''} ${company.address.city ?? ''}`.trim()
                : null
            }
          />
          <InfoRow label="Statut" value={company.is_active ? 'Active' : 'Inactive'} />
        </View>
      </ScrollView>

      <View className="px-5 pb-6 pt-2">
        <TouchableOpacity
          className="bg-blue-500 rounded-xl py-4 items-center"
          onPress={onConfirm}
          disabled={isPending}
        >
          {isPending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="text-white font-semibold text-base">Confirmer et continuer</Text>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  )
}
```

- [ ] **Step 2: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 3: Commit**

```bash
git add mobile/app/(partner)/deals/new/enrichment.tsx
git commit -m "feat(mobile): SCR-PARTNER-004 company enrichment confirmation"
```

---

## Task 7: SCR-PARTNER-005 — Quote Upload

**Files:**
- Create: `mobile/app/(partner)/deals/new/quote.tsx`

- [ ] **Step 1: Write SCR-PARTNER-005**

```typescript
// mobile/app/(partner)/deals/new/quote.tsx
import { useState } from 'react'
import { View, Text, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native'
import { useRouter } from 'expo-router'
import { SafeAreaView } from 'react-native-safe-area-context'
import * as DocumentPicker from 'expo-document-picker'
import { useDealCreationStore } from '@/src/stores/dealCreation'
import { useUploadDocument } from '@/src/hooks/useUploadDocument'

const MOCK_EXTRACTION = {
  supplier_name: 'Lenovo France',
  amount_excl_tax: '9 900,00 €',
  amount_incl_tax: '11 880,00 €',
  category: 'Matériel informatique',
  items: [
    { label: 'ThinkPad X1 Carbon Gen 12', qty: 5, unit: '1 980,00 €' },
    { label: 'Docking Station USB-C', qty: 5, unit: '120,00 €' },
  ],
}

type UploadState = 'idle' | 'uploading' | 'extracting' | 'done' | 'error'

export default function QuoteUpload() {
  const router = useRouter()
  const deal = useDealCreationStore((s) => s.deal)
  const [uploadState, setUploadState] = useState<UploadState>('idle')
  const [fileName, setFileName] = useState<string | null>(null)

  const { mutate: uploadDocument } = useUploadDocument()

  if (!deal) {
    router.replace('/(partner)/deals/new')
    return null
  }

  const handlePickFile = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: ['application/pdf', 'image/*'],
      copyToCacheDirectory: true,
    })
    if (result.canceled || !result.assets[0]) return

    const asset = result.assets[0]
    setFileName(asset.name)
    setUploadState('uploading')

    uploadDocument(
      {
        dealId: deal.id,
        fileUri: asset.uri,
        fileName: asset.name,
        mimeType: asset.mimeType ?? 'application/octet-stream',
        sizeBytes: asset.size ?? 0,
      },
      {
        onSuccess: () => {
          setUploadState('extracting')
          // Simulate mock extraction delay — set done after 1.5s
          setTimeout(() => setUploadState('done'), 1500)
        },
        onError: () => setUploadState('error'),
      },
    )
  }

  const canContinue = uploadState === 'done'

  return (
    <SafeAreaView className="flex-1 bg-white" edges={['bottom']}>
      <ScrollView className="flex-1 px-5 pt-6" showsVerticalScrollIndicator={false}>
        <Text className="text-xl font-bold text-navy-900 mb-2">Ajouter le devis</Text>
        <Text className="text-sm text-gray-500 mb-8">
          Importez le devis IT au format PDF ou image.
        </Text>

        {/* Upload zone */}
        <TouchableOpacity
          className="border-2 border-dashed border-blue-200 rounded-2xl p-8 items-center mb-6 bg-blue-50"
          onPress={handlePickFile}
          disabled={uploadState === 'uploading' || uploadState === 'extracting'}
        >
          {uploadState === 'idle' && (
            <>
              <Text className="text-3xl mb-2">📄</Text>
              <Text className="text-blue-500 font-semibold text-base">Sélectionner un fichier</Text>
              <Text className="text-gray-400 text-xs mt-1">PDF ou image</Text>
            </>
          )}
          {uploadState === 'uploading' && (
            <>
              <ActivityIndicator color="#2563EB" />
              <Text className="text-blue-500 text-sm mt-2">Upload en cours…</Text>
            </>
          )}
          {uploadState === 'extracting' && (
            <>
              <ActivityIndicator color="#2563EB" />
              <Text className="text-blue-500 text-sm mt-2">Extraction en cours…</Text>
            </>
          )}
          {(uploadState === 'done' || uploadState === 'error') && fileName && (
            <>
              <Text className="text-2xl mb-1">{uploadState === 'done' ? '✅' : '❌'}</Text>
              <Text className="text-navy-900 font-medium text-sm">{fileName}</Text>
            </>
          )}
        </TouchableOpacity>

        {/* Extraction result */}
        {uploadState === 'done' && (
          <View className="bg-gray-50 rounded-2xl px-4 py-2 mb-6">
            <Text className="text-sm font-semibold text-navy-900 py-3">Résultat extraction</Text>
            <View className="flex-row justify-between py-2 border-b border-gray-100">
              <Text className="text-sm text-gray-500">Fournisseur</Text>
              <Text className="text-sm font-medium text-navy-900">{MOCK_EXTRACTION.supplier_name}</Text>
            </View>
            <View className="flex-row justify-between py-2 border-b border-gray-100">
              <Text className="text-sm text-gray-500">Montant HT</Text>
              <Text className="text-sm font-mono font-medium text-navy-900">{MOCK_EXTRACTION.amount_excl_tax}</Text>
            </View>
            <View className="flex-row justify-between py-2 border-b border-gray-100">
              <Text className="text-sm text-gray-500">Montant TTC</Text>
              <Text className="text-sm font-mono font-medium text-navy-900">{MOCK_EXTRACTION.amount_incl_tax}</Text>
            </View>
            <View className="flex-row justify-between py-2 border-b border-gray-100">
              <Text className="text-sm text-gray-500">Catégorie</Text>
              <Text className="text-sm font-medium text-navy-900">{MOCK_EXTRACTION.category}</Text>
            </View>
            {MOCK_EXTRACTION.items.map((item, i) => (
              <View key={i} className="flex-row justify-between py-2">
                <Text className="text-xs text-gray-500 flex-1 mr-2">{item.qty}× {item.label}</Text>
                <Text className="text-xs font-mono text-navy-900">{item.unit}</Text>
              </View>
            ))}
          </View>
        )}

        {uploadState === 'error' && (
          <View className="bg-red-50 rounded-xl p-4 mb-6">
            <Text className="text-danger font-medium text-sm">Upload échoué.</Text>
            <Text className="text-danger text-xs mt-1">Vérifiez votre connexion et réessayez.</Text>
          </View>
        )}
      </ScrollView>

      <View className="px-5 pb-6 pt-2">
        <TouchableOpacity
          className={`rounded-xl py-4 items-center ${canContinue ? 'bg-blue-500' : 'bg-gray-200'}`}
          onPress={() => router.push('/(partner)/deals/new/offer')}
          disabled={!canContinue}
        >
          <Text className={`font-semibold text-base ${canContinue ? 'text-white' : 'text-gray-400'}`}>
            Continuer
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  )
}
```

- [ ] **Step 2: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 3: Commit**

```bash
git add mobile/app/(partner)/deals/new/quote.tsx
git commit -m "feat(mobile): SCR-PARTNER-005 quote upload with Supabase Storage + mock extraction"
```

---

## Task 8: SCR-PARTNER-006 — Indicative Offer + Submit

**Files:**
- Create: `mobile/app/(partner)/deals/new/offer.tsx`

- [ ] **Step 1: Write SCR-PARTNER-006**

```typescript
// mobile/app/(partner)/deals/new/offer.tsx
import { useEffect } from 'react'
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native'
import { useRouter } from 'expo-router'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useDealCreationStore } from '@/src/stores/dealCreation'
import { useIndicativePricing } from '@/src/hooks/useIndicativePricing'
import { useAssessRisk } from '@/src/hooks/useAssessRisk'
import { useSubmitDeal } from '@/src/hooks/useSubmitDeal'
import type { RiskBand } from '@/src/types/risk'

const BAND_CONFIG: Record<RiskBand, { bg: string; text: string; label: string }> = {
  green: { bg: 'bg-teal-500', text: 'text-white', label: 'Profil favorable' },
  orange: { bg: 'bg-warning', text: 'text-white', label: 'Profil à surveiller' },
  red: { bg: 'bg-danger', text: 'text-white', label: 'Profil à risque élevé' },
}

function formatEur(cents: number): string {
  return (cents / 100).toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })
}

export default function IndicativeOffer() {
  const router = useRouter()
  const deal = useDealCreationStore((s) => s.deal)
  const pricingProposal = useDealCreationStore((s) => s.pricingProposal)
  const riskAssessment = useDealCreationStore((s) => s.riskAssessment)

  const { mutate: fetchPricing, isPending: pricingLoading } = useIndicativePricing()
  const { mutate: fetchRisk, isPending: riskLoading } = useAssessRisk()
  const { mutate: submit, isPending: submitting, error: submitError } = useSubmitDeal()

  useEffect(() => {
    if (!deal) return
    if (!pricingProposal) {
      fetchPricing({
        amount_cents: deal.amount_cents ?? 10_000_000,
        duration_months: deal.duration_months ?? 36,
      })
    }
    if (!riskAssessment) {
      fetchRisk(deal.id)
    }
  }, [deal])

  if (!deal) {
    router.replace('/(partner)/deals/new')
    return null
  }

  const isLoading = pricingLoading || riskLoading
  const canSubmit = !isLoading && !!pricingProposal && !!riskAssessment

  const handleSubmit = () => {
    submit(deal.id, {
      onSuccess: () => router.replace('/(partner)'),
    })
  }

  const band = riskAssessment?.band ?? 'green'
  const bandConfig = BAND_CONFIG[band]

  return (
    <SafeAreaView className="flex-1 bg-white" edges={['bottom']}>
      <ScrollView className="flex-1 px-5 pt-6" showsVerticalScrollIndicator={false}>
        <Text className="text-xl font-bold text-navy-900 mb-2">Offre indicative</Text>
        <Text className="text-sm text-gray-500 mb-6">
          Mensualité estimée selon les conditions actuelles du marché.
        </Text>

        {isLoading && (
          <View className="items-center py-12">
            <ActivityIndicator size="large" color="#2563EB" />
            <Text className="text-gray-400 text-sm mt-3">Calcul en cours…</Text>
          </View>
        )}

        {!isLoading && pricingProposal && (
          <>
            {/* Main pricing card */}
            <View className="bg-navy-900 rounded-2xl p-6 mb-4">
              <Text className="text-blue-200 text-sm mb-1">Mensualité indicative</Text>
              <Text className="text-white text-4xl font-bold font-mono">
                {formatEur(pricingProposal.monthly_payment_cents)}
              </Text>
              <Text className="text-blue-200 text-xs mt-1">/ mois</Text>
            </View>

            {/* Details */}
            <View className="bg-gray-50 rounded-2xl px-4 py-2 mb-4">
              <View className="flex-row justify-between py-3 border-b border-gray-100">
                <Text className="text-sm text-gray-500">Montant financé</Text>
                <Text className="text-sm font-mono font-medium text-navy-900">
                  {formatEur(pricingProposal.amount_financed_cents)}
                </Text>
              </View>
              <View className="flex-row justify-between py-3 border-b border-gray-100">
                <Text className="text-sm text-gray-500">Durée</Text>
                <Text className="text-sm font-mono font-medium text-navy-900">
                  {pricingProposal.duration_months} mois
                </Text>
              </View>
              <View className="flex-row justify-between py-3 border-b border-gray-100">
                <Text className="text-sm text-gray-500">Taux total</Text>
                <Text className="text-sm font-mono font-medium text-navy-900">
                  {((pricingProposal.refi_rate + pricingProposal.margin_rate) * 100).toFixed(2)}%
                </Text>
              </View>
              <View className="flex-row justify-between py-3">
                <Text className="text-sm text-gray-500">Frais de dossier</Text>
                <Text className="text-sm font-mono font-medium text-navy-900">
                  {formatEur(pricingProposal.fees_cents)}
                </Text>
              </View>
            </View>

            {/* Risk band */}
            {riskAssessment && (
              <View className={`${bandConfig.bg} rounded-2xl p-4 mb-4`}>
                <View className="flex-row justify-between items-center">
                  <Text className={`${bandConfig.text} font-semibold text-sm`}>Score de risque</Text>
                  <Text className={`${bandConfig.text} font-bold text-lg font-mono`}>
                    {riskAssessment.score}/100
                  </Text>
                </View>
                <Text className={`${bandConfig.text} text-xs mt-1 opacity-90`}>
                  {riskAssessment.recommendation}
                </Text>
              </View>
            )}

            {/* Disclaimer */}
            <View className="bg-blue-50 rounded-xl p-4 mb-6">
              <Text className="text-blue-700 text-xs leading-5">
                Offre indicative, sous réserve d'analyse du dossier et validation par un partenaire financeur.
              </Text>
            </View>
          </>
        )}

        {submitError && (
          <View className="bg-red-50 rounded-xl p-4 mb-4">
            <Text className="text-danger text-sm font-medium">Soumission échouée.</Text>
            <Text className="text-danger text-xs mt-1">Vérifiez votre connexion et réessayez.</Text>
          </View>
        )}
      </ScrollView>

      <View className="px-5 pb-6 pt-2">
        <TouchableOpacity
          className={`rounded-xl py-4 items-center ${canSubmit ? 'bg-blue-500' : 'bg-gray-200'}`}
          onPress={handleSubmit}
          disabled={!canSubmit || submitting}
        >
          {submitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className={`font-semibold text-base ${canSubmit ? 'text-white' : 'text-gray-400'}`}>
              Soumettre le dossier
            </Text>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  )
}
```

- [ ] **Step 2: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 3: Commit**

```bash
git add mobile/app/(partner)/deals/new/offer.tsx
git commit -m "feat(mobile): SCR-PARTNER-006 indicative offer + risk band + submit"
```

---

## Task 9: Wire CTA in Partner Dashboard

**Files:**
- Modify: `mobile/app/(partner)/index.tsx`

- [ ] **Step 1: Update the "Nouveau dossier" CTA to navigate to the wizard**

In `mobile/app/(partner)/index.tsx`, find the CTA button and update its `onPress` handler:

```typescript
// Find the existing CTA button (around line 65-80) and change:
// onPress={() => {}} or any placeholder
// to:
onPress={() => router.push('/(partner)/deals/new')}
```

The button text should already be "Nouveau dossier" — just wire the navigation.

- [ ] **Step 2: Verify types compile**

```bash
cd mobile && npx tsc --noEmit
```
Expected: 0 errors

- [ ] **Step 3: Final commit**

```bash
git add mobile/app/(partner)/index.tsx
git commit -m "feat(mobile): wire Nouveau dossier CTA to deal creation wizard — Phase 3 mobile complete"
```

import { apiGet, apiPatch, apiPost } from '@/src/lib/api'
import { Deal, DealCreatePayload, DealStatus, DealStatusTransitionPayload } from '@/src/types/deal'
import { PricingProposal } from '@/src/types/pricing'

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

export async function transitionDeal(dealId: string, status: DealStatus): Promise<Deal> {
  const payload: DealStatusTransitionPayload = { status }
  return apiPost<Deal>(`/deals/${dealId}/status`, payload)
}

export async function savePricingProposal(
  dealId: string,
  payload: {
    amount_cents: number
    duration_months: number
    refi_rate?: number
    margin_rate?: number
    fees_cents?: number
  },
): Promise<PricingProposal> {
  return apiPost<PricingProposal>(`/deals/${dealId}/pricing/recalculate`, payload)
}

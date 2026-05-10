import { apiGet, apiPost } from '@/src/lib/api'
import { PricingProposal, IndicativePricingRequest } from '@/src/types/pricing'
import { RiskAssessment } from '@/src/types/risk'

export async function getIndicativePricing(payload: IndicativePricingRequest): Promise<PricingProposal> {
  return apiPost<PricingProposal>('/pricing/indicative', payload)
}

export async function getLatestPricing(dealId: string): Promise<PricingProposal | null> {
  return apiGet<PricingProposal | null>(`/deals/${dealId}/pricing`)
}

export async function assessRisk(dealId: string): Promise<RiskAssessment> {
  return apiPost<RiskAssessment>(`/deals/${dealId}/risk/assess`, {})
}

export async function getLatestRisk(dealId: string): Promise<RiskAssessment> {
  return apiGet<RiskAssessment>(`/deals/${dealId}/risk/latest`)
}

export interface PricingProposal {
  id?: string | null
  deal_id?: string | null
  type: 'indicative' | 'firm'
  amount_financed_cents: number
  duration_months: number
  monthly_payment_cents: number
  refi_rate: number
  margin_rate: number
  fees_cents: number
  assumptions: Record<string, unknown> | null
  version: number
  created_at?: string | null
}

export interface IndicativePricingRequest {
  amount_cents: number
  duration_months: number
  refi_rate?: number
  margin_rate?: number
  fees_cents?: number
}

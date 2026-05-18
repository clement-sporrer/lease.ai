export interface Offer {
  id: string
  deal_id: string
  version: number
  is_active: boolean
  amount_cents: number | null
  duration_months: number | null
  monthly_payment_cents: number | null
  risk_band: string | null
  currency: string
  valid_until: string | null
  created_at: string
}

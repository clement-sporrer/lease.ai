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
  amount_cents?: number | null
  duration_months?: number | null
  currency?: string
}

export interface DealStatusTransitionPayload {
  status: DealStatus
}

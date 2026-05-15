export interface RefiPackage {
  id: string
  deal_id: string
  status: 'draft' | 'sent' | 'financier_approved' | 'financier_rejected'
  amount_cents: number | null
  duration_months: number | null
  monthly_payment_cents: number | null
  risk_score: number | null
  risk_band: string | null
  sent_at: string | null
  created_at: string
  updated_at: string
}

export interface FinancierDecisionRequest {
  decision: 'approved' | 'rejected'
  reason?: string
}

export interface FinancierDecision {
  id: string
  refi_package_id: string
  decision: 'approved' | 'rejected'
  reason: string | null
  decided_at: string
}

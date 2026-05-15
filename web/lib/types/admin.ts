export const WRITE_ROLES = ['admin', 'ops'] as const
export type WriteRole = (typeof WRITE_ROLES)[number]

export function canWrite(role: string | undefined): boolean {
  return WRITE_ROLES.includes(role as WriteRole)
}

export type DealStatus =
  | 'draft'
  | 'company_enriched'
  | 'quote_added'
  | 'indicative_offer_ready'
  | 'submitted'
  | 'internal_review'
  | 'missing_documents'
  | 'pre_approved'
  | 'financier_rejected'
  | 'refi_package_ready'
  | 'refi_review'
  | 'financier_approved'
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
  risk_band: string | null
  monthly_payment_cents: number | null
  created_at: string
  updated_at: string
}

export interface DocumentItem {
  id: string
  type: string
  status: 'pending_upload' | 'uploaded' | 'validated' | 'rejected' | 'pending'
  file_name: string
}

export interface DealChecklist {
  deal_id: string
  status: DealStatus
  documents: DocumentItem[]
  risk_score: number | null
  risk_band: string | null
  pricing_monthly: number | null
  all_docs_validated: boolean
  checklist_complete: boolean
}

export interface AuditEvent {
  id: string
  deal_id: string
  actor_id: string | null
  actor_role: string
  action: string
  payload: Record<string, unknown> | null
  created_at: string
}

export interface QueueResponse {
  data: Deal[]
  meta: { total: number }
}

export interface TimelineResponse {
  data: AuditEvent[]
  meta: { total: number }
}

export interface QuoteItem {
  label: string
  category: string | null
  quantity: number
  unit_price_cents: number | null
  total_price_cents: number | null
}

export interface Quote {
  id: string
  deal_id: string
  supplier_name: string | null
  quote_number: string | null
  amount_excl_tax_cents: number | null
  amount_incl_tax_cents: number | null
  currency: string
  category: string | null
  extraction_status: 'pending' | 'done' | 'failed'
  extraction_source: string | null
  extraction_payload: {
    items?: QuoteItem[]
    [key: string]: unknown
  } | null
}

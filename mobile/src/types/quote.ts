export interface QuoteItem {
  id: string
  label: string
  category: string | null
  quantity: number
  unit_price_cents: number | null
  total_price_cents: number | null
}

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
  items: QuoteItem[]
  created_at: string
  updated_at: string
}

export interface QuoteCreatePayload {
  document_id?: string | null
  supplier_name?: string | null
  quote_number?: string | null
  amount_excl_tax_cents?: number | null
  amount_incl_tax_cents?: number | null
  currency?: string
  category?: string | null
}

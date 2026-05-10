export interface CompanyAddress {
  street?: string
  city?: string
  zip?: string
}

export interface Company {
  id: string
  siren: string
  siret: string | null
  legal_name: string
  trade_name: string | null
  address: CompanyAddress | null
  activity_code: string | null
  creation_date: string | null
  legal_status: string | null
  is_active: boolean
  enrichment_source: string | null
  created_at: string
}

// web/lib/types/contract.ts
export interface Contract {
  id: string
  deal_id: string
  public_id: string
  status: string
  sent_at: string | null
  signed_at: string | null
  activated_at: string | null
  total_commitment_cents: number | null
  created_at: string
}

export interface Asset {
  id: string
  contract_id: string
  name: string
  category: string | null
  quantity: number
  unit_value_cents: number | null
  created_at: string
}

export interface PaymentScheduleEntry {
  id: string
  contract_id: string
  due_date: string
  amount_cents: number
  status: string
  created_at: string
}

export interface ActivationChecklistItem {
  key: string
  label: string
  satisfied: boolean
}

export interface ActivationChecklist {
  items: ActivationChecklistItem[]
  all_satisfied: boolean
}

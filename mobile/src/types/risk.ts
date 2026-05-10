export type RiskBand = 'green' | 'orange' | 'red'

export interface RiskAssessment {
  id: string
  deal_id: string
  score: number
  band: RiskBand
  flags: string[] | null
  rules_applied: string[] | null
  recommendation: string | null
  version: number
  created_at: string
}

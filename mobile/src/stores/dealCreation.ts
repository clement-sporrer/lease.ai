import { create } from 'zustand'

import { Company } from '@/src/types/company'
import { Deal } from '@/src/types/deal'
import { PricingProposal } from '@/src/types/pricing'
import { Quote } from '@/src/types/quote'
import { RiskAssessment } from '@/src/types/risk'

interface DealCreationState {
  siren: string
  company: Company | null
  deal: Deal | null
  quote: Quote | null
  documentId: string | null
  pricingProposal: PricingProposal | null
  riskAssessment: RiskAssessment | null
  idempotencyKey: string
  setSiren: (siren: string) => void
  setCompany: (company: Company) => void
  setDeal: (deal: Deal) => void
  setQuote: (quote: Quote) => void
  setDocumentId: (documentId: string) => void
  setPricingProposal: (pricingProposal: PricingProposal) => void
  setRiskAssessment: (riskAssessment: RiskAssessment) => void
  reset: () => void
}

function generateIdempotencyKey(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function createInitialState() {
  return {
    siren: '',
    company: null,
    deal: null,
    quote: null,
    documentId: null,
    pricingProposal: null,
    riskAssessment: null,
    idempotencyKey: generateIdempotencyKey(),
  }
}

export const useDealCreationStore = create<DealCreationState>((set) => ({
  ...createInitialState(),
  setSiren: (siren) => set({ siren }),
  setCompany: (company) => set({ company }),
  setDeal: (deal) => set({ deal }),
  setQuote: (quote) => set({ quote }),
  setDocumentId: (documentId) => set({ documentId }),
  setPricingProposal: (pricingProposal) => set({ pricingProposal }),
  setRiskAssessment: (riskAssessment) => set({ riskAssessment }),
  reset: () => set(createInitialState()),
}))

import { apiGet, apiPatch, apiPost } from '@/src/lib/api'
import { Quote, QuoteCreatePayload } from '@/src/types/quote'

export async function createQuote(dealId: string, payload: QuoteCreatePayload): Promise<Quote> {
  return apiPost<Quote>(`/deals/${dealId}/quotes`, payload)
}

export async function getQuote(dealId: string, quoteId: string): Promise<Quote> {
  return apiGet<Quote>(`/deals/${dealId}/quotes/${quoteId}`)
}

export async function patchQuote(dealId: string, quoteId: string, payload: Partial<QuoteCreatePayload>): Promise<Quote> {
  return apiPatch<Quote>(`/deals/${dealId}/quotes/${quoteId}`, payload)
}

export async function extractQuote(dealId: string, quoteId: string): Promise<Quote> {
  return apiPost<Quote>(`/deals/${dealId}/quotes/${quoteId}/extract`, {})
}

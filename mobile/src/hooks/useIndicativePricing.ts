import { useMutation } from '@tanstack/react-query'

import { getIndicativePricing } from '@/src/services/pricing'
import { useDealCreationStore } from '@/src/stores/dealCreation'
import { IndicativePricingRequest } from '@/src/types/pricing'

export function useIndicativePricing() {
  const setPricingProposal = useDealCreationStore((state) => state.setPricingProposal)

  return useMutation({
    mutationFn: (payload: IndicativePricingRequest) => getIndicativePricing(payload),
    onSuccess: (proposal) => setPricingProposal(proposal),
    retry: 1,
  })
}

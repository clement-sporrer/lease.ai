import { useMutation } from '@tanstack/react-query'

import { savePricingProposal, submitDeal } from '@/src/services/deals'
import { useDealCreationStore } from '@/src/stores/dealCreation'

export function useSubmitDeal() {
  const pricingProposal = useDealCreationStore((state) => state.pricingProposal)
  const setPricingProposal = useDealCreationStore((state) => state.setPricingProposal)
  const reset = useDealCreationStore((state) => state.reset)

  return useMutation({
    mutationFn: async (dealId: string) => {
      if (pricingProposal) {
        const persistedProposal = await savePricingProposal(dealId, {
          amount_cents: pricingProposal.amount_financed_cents,
          duration_months: pricingProposal.duration_months,
          refi_rate: pricingProposal.refi_rate,
          margin_rate: pricingProposal.margin_rate,
          fees_cents: pricingProposal.fees_cents,
        })
        setPricingProposal(persistedProposal)
      }
      return submitDeal(dealId)
    },
    onSuccess: () => reset(),
    retry: 1,
  })
}

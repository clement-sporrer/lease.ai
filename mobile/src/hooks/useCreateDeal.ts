import { useMutation } from '@tanstack/react-query'

import { createDeal } from '@/src/services/deals'
import { useDealCreationStore } from '@/src/stores/dealCreation'
import { DealCreatePayload } from '@/src/types/deal'

export function useCreateDeal() {
  const deal = useDealCreationStore((state) => state.deal)
  const idempotencyKey = useDealCreationStore((state) => state.idempotencyKey)
  const setDeal = useDealCreationStore((state) => state.setDeal)

  return useMutation({
    mutationFn: (payload: DealCreatePayload) => {
      if (deal) return Promise.resolve(deal)
      return createDeal(payload, idempotencyKey)
    },
    onSuccess: (newDeal) => setDeal(newDeal),
    retry: 1,
  })
}

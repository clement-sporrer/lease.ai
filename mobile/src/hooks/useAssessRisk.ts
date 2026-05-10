import { useMutation } from '@tanstack/react-query'

import { assessRisk } from '@/src/services/pricing'
import { useDealCreationStore } from '@/src/stores/dealCreation'

export function useAssessRisk() {
  const setRiskAssessment = useDealCreationStore((state) => state.setRiskAssessment)

  return useMutation({
    mutationFn: (dealId: string) => assessRisk(dealId),
    onSuccess: (assessment) => setRiskAssessment(assessment),
    retry: 1,
  })
}

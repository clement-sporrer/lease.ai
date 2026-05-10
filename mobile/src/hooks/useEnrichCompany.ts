import { useMutation } from '@tanstack/react-query'

import { enrichCompany } from '@/src/services/companies'
import { useDealCreationStore } from '@/src/stores/dealCreation'

export function useEnrichCompany() {
  const setCompany = useDealCreationStore((state) => state.setCompany)
  const setSiren = useDealCreationStore((state) => state.setSiren)

  return useMutation({
    mutationFn: (sirenOrSiret: string) => enrichCompany(sirenOrSiret),
    onSuccess: (company, sirenOrSiret) => {
      setCompany(company)
      setSiren(sirenOrSiret)
    },
    retry: 1,
  })
}

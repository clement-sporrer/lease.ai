import { apiGet, apiPost } from '@/src/lib/api'
import { Company } from '@/src/types/company'

export async function enrichCompany(sirenOrSiret: string): Promise<Company> {
  return apiPost<Company>('/companies/enrich', { siren_or_siret: sirenOrSiret })
}

export async function getCompany(companyId: string): Promise<Company> {
  return apiGet<Company>(`/companies/${companyId}`)
}

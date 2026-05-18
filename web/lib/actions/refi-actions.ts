'use server'

import { revalidatePath } from 'next/cache'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import type { RefiPackage, FinancierDecision } from '@/lib/types/refi'

async function getToken(): Promise<string> {
  const supabase = await createSupabaseServerClient()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('Not authenticated')
  return session.access_token
}

export async function createRefiPackage(dealId: string): Promise<{ data: RefiPackage } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: RefiPackage }>(`/deals/${dealId}/refi-packages`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Failed to create refi package' }
  }
}

export async function sendRefiPackage(packageId: string, dealId: string): Promise<{ data: RefiPackage } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: RefiPackage }>(`/refi-packages/${packageId}/send`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Failed to send package' }
  }
}

export async function recordFinancierDecision(
  packageId: string,
  decision: 'approved' | 'rejected',
  reason?: string
): Promise<{ data: FinancierDecision } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: FinancierDecision }>(
      `/refi-packages/${packageId}/decision`,
      token,
      { method: 'POST', body: JSON.stringify({ decision, reason }) }
    )
    revalidatePath('/financier/packages')
    revalidatePath(`/financier/packages/${packageId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Failed to record decision' }
  }
}

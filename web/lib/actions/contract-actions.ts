// web/lib/actions/contract-actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import type { Contract } from '@/lib/types/contract'

async function getToken(): Promise<string> {
  const supabase = await createSupabaseServerClient()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('Not authenticated')
  return session.access_token
}

export async function generateContract(dealId: string): Promise<{ data: Contract } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Contract }>(`/deals/${dealId}/contracts`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Échec de la génération du contrat' }
  }
}

export async function sendSignature(contractId: string, dealId: string): Promise<{ data: Contract } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Contract }>(`/contracts/${contractId}/send-signature`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Échec de l'envoi pour signature" }
  }
}

export async function mockSign(contractId: string, dealId: string): Promise<{ data: Contract } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Contract }>(`/contracts/${contractId}/mock-sign`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Échec de la signature simulée' }
  }
}

export async function activateContract(contractId: string, dealId: string): Promise<{ data: Contract } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Contract }>(`/contracts/${contractId}/activate`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Échec de l'activation" }
  }
}

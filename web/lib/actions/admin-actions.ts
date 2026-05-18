'use server'

import { revalidatePath } from 'next/cache'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'

async function getToken(): Promise<string | null> {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()
  return session?.access_token ?? null
}

export async function requestDocument(
  dealId: string,
  documentType: string,
  reason: string
): Promise<{ error?: string }> {
  const token = await getToken()
  if (!token) return { error: 'Non authentifié' }
  try {
    await apiFetch(`/admin/deals/${dealId}/request-document`, token, {
      method: 'POST',
      body: JSON.stringify({ document_type: documentType, reason }),
    })
    revalidatePath(`/admin/deals/${dealId}`)
    return {}
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'Erreur serveur' }
  }
}

export async function preApproveDeal(
  dealId: string,
  justification: string | null
): Promise<{ error?: string }> {
  const token = await getToken()
  if (!token) return { error: 'Non authentifié' }
  try {
    await apiFetch(`/admin/deals/${dealId}/pre-approve`, token, {
      method: 'POST',
      body: JSON.stringify({ justification }),
    })
    revalidatePath(`/admin/deals/${dealId}`)
    return {}
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'Erreur serveur' }
  }
}

export async function rejectDeal(
  dealId: string,
  reason: string
): Promise<{ error?: string }> {
  const token = await getToken()
  if (!token) return { error: 'Non authentifié' }
  try {
    await apiFetch(`/admin/deals/${dealId}/reject`, token, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    })
    revalidatePath(`/admin/deals/${dealId}`)
    return {}
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'Erreur serveur' }
  }
}

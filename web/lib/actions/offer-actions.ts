'use server'

import { revalidatePath } from 'next/cache'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import type { Offer } from '@/lib/types/offer'

async function getToken(): Promise<string> {
  const supabase = await createSupabaseServerClient()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('Not authenticated')
  return session.access_token
}

export async function generateOffer(dealId: string): Promise<{ data: Offer } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Offer }>(`/deals/${dealId}/offers`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Failed to generate offer' }
  }
}

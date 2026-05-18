'use server'

import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'

export async function getDocumentViewUrl(
  documentId: string
): Promise<{ data?: { url: string; expires_in: number }; error?: string }> {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()
  if (!session) return { error: 'Non authentifié' }

  try {
    const result = await apiFetch<{ data: { url: string; expires_in: number } }>(
      `/documents/${documentId}/view-url`,
      session.access_token
    )
    return { data: result.data }
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'Erreur serveur' }
  }
}

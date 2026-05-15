import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { DealQueue } from '@/components/admin/DealQueue'
import type { QueueResponse } from '@/lib/types/admin'

export default async function AdminQueuePage() {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  let queueData: QueueResponse = { data: [], meta: { total: 0 } }
  let apiError = false
  try {
    queueData = await apiFetch<QueueResponse>('/admin/queue', session.access_token)
  } catch {
    apiError = true
  }

  return (
    <DashboardShell role="admin" title="File d'attente" subtitle={`${queueData.meta.total} dossier(s) à traiter`}>
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        {apiError && (
          <p className="text-sm text-red-500 mb-4">Impossible de charger la file d'attente.</p>
        )}
        <DealQueue deals={queueData.data} />
      </div>
    </DashboardShell>
  )
}

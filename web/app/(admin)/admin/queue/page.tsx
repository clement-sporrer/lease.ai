import { Suspense } from 'react'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { DealQueue } from '@/components/admin/DealQueue'
import { QueueFilters } from '@/components/admin/QueueFilters'
import { QueuePagination } from '@/components/admin/QueuePagination'
import type { QueueResponse } from '@/lib/types/admin'

interface Props {
  searchParams: Promise<{ status?: string; search?: string; page?: string }>
}

export default async function AdminQueuePage({ searchParams }: Props) {
  const { status, search, page: pageStr } = await searchParams
  const page = Math.max(1, parseInt(pageStr ?? '1', 10))
  const pageSize = 20

  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  const params = new URLSearchParams()
  if (status) params.set('status', status)
  if (search) params.set('search', search)
  params.set('page', String(page))
  params.set('page_size', String(pageSize))

  let queueData: QueueResponse = {
    data: [],
    meta: { total: 0, page: 1, page_size: pageSize },
  }
  let apiError = false
  try {
    queueData = await apiFetch<QueueResponse>(
      `/admin/queue?${params.toString()}`,
      session.access_token
    )
  } catch {
    apiError = true
  }

  return (
    <DashboardShell
      role="admin"
      title="File d'attente"
      subtitle={`${queueData.meta.total} dossier(s)`}
    >
      {apiError && (
        <p className="mb-4 text-sm text-red-500">Impossible de charger la file d'attente.</p>
      )}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <Suspense>
          <QueueFilters />
        </Suspense>
        <DealQueue deals={queueData.data} />
        <Suspense>
          <QueuePagination
            total={queueData.meta.total}
            page={page}
            pageSize={pageSize}
          />
        </Suspense>
      </div>
    </DashboardShell>
  )
}

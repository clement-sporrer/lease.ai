import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { DealReviewHeader } from '@/components/admin/DealReviewHeader'
import { CompanySummary } from '@/components/admin/CompanySummary'
import { QuoteSummary } from '@/components/admin/QuoteSummary'
import { RiskSummary } from '@/components/admin/RiskSummary'
import { DocumentList } from '@/components/admin/DocumentList'
import { AuditTimeline } from '@/components/admin/AuditTimeline'
import { ActionPanel } from '@/components/admin/ActionPanel'
import { canWrite } from '@/lib/types/admin'
import type { Deal, DealChecklist, TimelineResponse } from '@/lib/types/admin'

interface Props {
  params: Promise<{ id: string }>
}

export default async function DealReviewPage({ params }: Props) {
  const { id } = await params
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  const token = session.access_token
  const activeRole = session.user.user_metadata?.active_role as string | undefined
  const userCanWrite = canWrite(activeRole)

  let deal: Deal | null = null
  let checklist: DealChecklist | null = null
  let timeline: TimelineResponse = { data: [], meta: { total: 0 } }

  try {
    const [dealRes, checklistRes, timelineRes] = await Promise.all([
      apiFetch<{ data: Deal }>(`/deals/${id}`, token),
      apiFetch<{ data: DealChecklist }>(`/admin/deals/${id}/checklist`, token),
      apiFetch<TimelineResponse>(`/deals/${id}/timeline`, token),
    ])
    deal = dealRes.data
    checklist = checklistRes.data
    timeline = timelineRes
  } catch {
    // API fetch failed — deal will be null, show error state below
  }

  if (!deal) {
    return <p className="p-8 text-sm text-gray-500">Impossible de charger ce dossier.</p>
  }

  return (
    <DashboardShell role="admin" title={`Dossier ${deal.public_id}`}>
      <div className="max-w-4xl">
        <DealReviewHeader deal={deal} />
        <CompanySummary />
        <QuoteSummary deal={deal} />
        <RiskSummary deal={deal} />
        <DocumentList
          documents={checklist?.documents ?? []}
          canWrite={userCanWrite}
          token={token}
        />
        <AuditTimeline events={timeline.data} />
      </div>
      <ActionPanel dealId={id} token={token} canWrite={userCanWrite} />
    </DashboardShell>
  )
}

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
import { RefiPackagePanel } from '@/components/admin/RefiPackagePanel'
import { OfferPanel } from '@/components/admin/OfferPanel'
import { QuoteUploadZone } from '@/components/admin/QuoteUploadZone'
import { canWrite } from '@/lib/types/admin'
import type { Deal, DealChecklist, TimelineResponse } from '@/lib/types/admin'
import type { RefiPackage } from '@/lib/types/refi'
import type { Offer } from '@/lib/types/offer'

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
  let refiPackage: RefiPackage | null = null
  let activeOffer: Offer | null = null

  try {
    const [dealRes, checklistRes, timelineRes, refiRes] = await Promise.all([
      apiFetch<{ data: Deal }>(`/deals/${id}`, token),
      apiFetch<{ data: DealChecklist }>(`/admin/deals/${id}/checklist`, token),
      apiFetch<TimelineResponse>(`/deals/${id}/timeline`, token),
      apiFetch<{ data: RefiPackage[] }>(`/refi-packages?deal_id=${id}`, token),
    ])
    deal = dealRes.data
    checklist = checklistRes.data
    timeline = timelineRes
    refiPackage = refiRes.data[0] ?? null
  } catch {
    // API fetch failed — deal will be null, show error state below
  }

  // Fetch active offer separately — 404 is expected when no offer exists
  if (deal) {
    try {
      activeOffer = await apiFetch<Offer>(`/deals/${id}/offers/active`, token)
    } catch {
      activeOffer = null
    }
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
        <section className="mt-6 space-y-4">
          <QuoteUploadZone dealId={id} />
          <RefiPackagePanel
            deal={deal}
            existingPackage={refiPackage}
          />
          <OfferPanel
            dealId={id}
            activeOffer={activeOffer}
            dealStatus={deal.status}
          />
        </section>
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

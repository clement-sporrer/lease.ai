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
  let company: { name?: string; siren?: string; sector?: string; creation_date?: string } | null = null

  try {
    const [dealRes, checklistRes, timelineRes, refiRes] = await Promise.all([
      apiFetch<{ data: Deal }>(`/deals/${id}`, token),
      apiFetch<{ data: DealChecklist }>(`/admin/deals/${id}/checklist`, token),
      apiFetch<TimelineResponse>(`/deals/${id}/timeline`, token),
      apiFetch<{ data: RefiPackage[] }>(`/deals/${id}/refi-packages`, token),
    ])
    deal = dealRes.data
    checklist = checklistRes.data
    timeline = timelineRes
    refiPackage = refiRes.data[0] ?? null
  } catch {
    // API fetch failed — deal will be null, show error state below
  }

  // Fetch company and active offer separately — both depend on deal being loaded
  if (deal) {
    const [companyResult, offerResult] = await Promise.allSettled([
      apiFetch<{ data: { legal_name: string; trade_name: string | null; siren: string; naf_code: string | null; creation_date: string | null } }>(`/companies/${deal.company_id}`, token),
      apiFetch<Offer>(`/deals/${id}/offers/active`, token),
    ])

    if (companyResult.status === 'fulfilled') {
      const c = companyResult.value.data
      company = {
        name: c.trade_name ?? c.legal_name,
        siren: c.siren,
        sector: c.naf_code ?? undefined,
        creation_date: c.creation_date ?? undefined,
      }
    }

    if (offerResult.status === 'fulfilled') {
      activeOffer = offerResult.value
    }
  }

  if (!deal) {
    return <p className="p-8 text-sm text-gray-500">Impossible de charger ce dossier.</p>
  }

  return (
    <DashboardShell role="admin" title={`Dossier ${deal.public_id}`}>
      <div className="max-w-4xl">
        <DealReviewHeader deal={deal} />
        <CompanySummary enrichment={company ?? undefined} />
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

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
import { ContractPanel } from '@/components/admin/ContractPanel'
import { ActivationChecklist } from '@/components/admin/ActivationChecklist'
import { AssetsPanel } from '@/components/admin/AssetsPanel'
import { QuoteUploadZone } from '@/components/admin/QuoteUploadZone'
import { Breadcrumb } from '@/components/ui/breadcrumb'
import { canWrite } from '@/lib/types/admin'
import type { Deal, DealChecklist, TimelineResponse } from '@/lib/types/admin'
import type { RefiPackage } from '@/lib/types/refi'
import type { Offer } from '@/lib/types/offer'
import type { Contract, ActivationChecklist as ActivationChecklistType, Asset, PaymentScheduleEntry } from '@/lib/types/contract'

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
  let contract: Contract | null = null
  let activationChecklist: ActivationChecklistType | null = null
  let assets: Asset[] = []
  let paymentSchedule: PaymentScheduleEntry[] = []
  let company: { name?: string; siren?: string; sector?: string; creation_date?: string; enrichment_source?: string; is_inactive?: boolean } | null = null

  const [dealResult, checklistResult, timelineResult, refiResult, contractResult] = await Promise.allSettled([
    apiFetch<{ data: Deal }>(`/deals/${id}`, token),
    apiFetch<{ data: DealChecklist }>(`/admin/deals/${id}/checklist`, token),
    apiFetch<TimelineResponse>(`/deals/${id}/timeline`, token),
    apiFetch<{ data: RefiPackage[] }>(`/deals/${id}/refi-packages`, token),
    apiFetch<{ data: Contract | null }>(`/deals/${id}/contracts/latest`, token),
  ])

  if (dealResult.status === 'fulfilled') deal = dealResult.value.data
  if (checklistResult.status === 'fulfilled') checklist = checklistResult.value.data
  if (timelineResult.status === 'fulfilled') timeline = timelineResult.value
  if (refiResult.status === 'fulfilled') refiPackage = refiResult.value.data[0] ?? null
  if (contractResult.status === 'fulfilled') contract = contractResult.value.data

  // Fetch company and active offer separately — both depend on deal being loaded
  if (deal) {
    type CompanyApiResponse = {
      legal_name: string
      trade_name: string | null
      siren: string
      activity_code: string | null
      creation_date: string | null
      enrichment_source: string | null
      is_active: boolean
    }

    const [companyResult, offerResult] = await Promise.allSettled([
      apiFetch<{ data: CompanyApiResponse }>(`/companies/${deal.company_id}`, token),
      apiFetch<{ data: Offer }>(`/deals/${id}/offers/active`, token),
    ])

    if (companyResult.status === 'fulfilled') {
      const c = companyResult.value.data
      company = {
        name: c.trade_name ?? c.legal_name,
        siren: c.siren,
        sector: c.activity_code ?? undefined,
        creation_date: c.creation_date ?? undefined,
        enrichment_source: c.enrichment_source ?? undefined,
        is_inactive: !c.is_active,
      }
    }

    if (offerResult.status === 'fulfilled') {
      activeOffer = offerResult.value.data
    }

    if (contract && ['signed', 'activation_pending', 'active'].includes(deal.status ?? '')) {
      const checklistFetchResult = await apiFetch<{ data: ActivationChecklistType }>(
        `/contracts/${contract.id}/activation-checklist`,
        token
      ).catch(() => null)
      if (checklistFetchResult) activationChecklist = checklistFetchResult.data
    }

    if (contract && deal.status === 'active') {
      const [assetsResult, scheduleResult] = await Promise.allSettled([
        apiFetch<{ data: Asset[] }>(`/contracts/${contract.id}/assets`, token),
        apiFetch<{ data: PaymentScheduleEntry[] }>(`/contracts/${contract.id}/payment-schedule`, token),
      ])
      if (assetsResult.status === 'fulfilled') assets = assetsResult.value.data
      if (scheduleResult.status === 'fulfilled') paymentSchedule = scheduleResult.value.data
    }
  }

  if (!deal) {
    return <p className="p-8 text-sm text-gray-500">Impossible de charger ce dossier.</p>
  }

  return (
    <DashboardShell role="admin" title={`Dossier ${deal.public_id}`}>
      <div className="max-w-4xl">
        <Breadcrumb crumbs={[
          { label: 'Tableau de bord', href: '/admin' },
          { label: "File d'attente", href: '/admin/queue' },
          { label: `Dossier ${deal.public_id}` },
        ]} />
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
          <ContractPanel
            dealId={id}
            dealStatus={deal.status}
            contract={contract}
          />
          <ActivationChecklist
            dealId={id}
            dealStatus={deal.status}
            contract={contract}
            checklist={activationChecklist}
          />
        </section>
        {deal.status === 'active' && (
          <AssetsPanel assets={assets} schedule={paymentSchedule} />
        )}
        <DocumentList
          documents={checklist?.documents ?? []}
          canWrite={userCanWrite}
          token={token}
        />
        <AuditTimeline events={timeline.data} />
      </div>
      <ActionPanel dealId={id} canWrite={userCanWrite} />
    </DashboardShell>
  )
}

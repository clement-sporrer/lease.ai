'use client'

import { useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { generateContract, sendSignature, mockSign } from '@/lib/actions/contract-actions'
import { Button } from '@/components/ui/button'
import type { Contract } from '@/lib/types/contract'

const CONTRACT_VISIBLE_STATUSES = new Set([
  'firm_offer_generated',
  'contract_generated',
  'signing',
  'signed',
  'activation_pending',
  'active',
])

interface Props {
  dealId: string
  dealStatus: string
  contract: Contract | null
}

export function ContractPanel({ dealId, dealStatus, contract }: Props) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()

  if (!CONTRACT_VISIBLE_STATUSES.has(dealStatus)) return null

  function handleGenerate() {
    startTransition(async () => {
      const result = await generateContract(dealId)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        toast.success('Contrat généré')
        router.refresh()
      }
    })
  }

  function handleSendSignature() {
    if (!contract) return
    startTransition(async () => {
      const result = await sendSignature(contract.id, dealId)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        toast.success('Contrat envoyé pour signature')
        router.refresh()
      }
    })
  }

  function handleMockSign() {
    if (!contract) return
    startTransition(async () => {
      const result = await mockSign(contract.id, dealId)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        toast.success('Contrat signé')
        router.refresh()
      }
    })
  }

  return (
    <div className="rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
        <h2 className="text-sm font-semibold text-navy-900">Contrat</h2>
        {dealStatus === 'firm_offer_generated' && (
          <Button variant="primary" size="sm" onClick={handleGenerate} disabled={isPending}>
            {isPending ? 'Génération…' : 'Générer le contrat'}
          </Button>
        )}
        {contract?.status === 'draft' && dealStatus === 'contract_generated' && (
          <Button variant="primary" size="sm" onClick={handleSendSignature} disabled={isPending}>
            {isPending ? 'Envoi…' : 'Envoyer pour signature'}
          </Button>
        )}
        {contract?.status === 'sent_for_signature' && dealStatus === 'signing' && (
          <Button variant="success" size="sm" onClick={handleMockSign} disabled={isPending}>
            {isPending ? 'Signature…' : 'Simuler la signature'}
          </Button>
        )}
      </div>
      <div className="px-6 py-5">
        {contract ? (
          <div className="space-y-2.5">
            <Row label="Référence">
              <span className="font-mono text-sm">{contract.public_id}</span>
            </Row>
            <Row label="Statut">
              <ContractStatusBadge status={contract.status} />
            </Row>
            <Row label="Généré le">
              <span className="text-sm text-gray-600">
                {new Date(contract.created_at).toLocaleDateString('fr-FR')}
              </span>
            </Row>
            {contract.sent_at && (
              <Row label="Envoyé le">
                <span className="text-sm text-gray-600">
                  {new Date(contract.sent_at).toLocaleDateString('fr-FR')}
                </span>
              </Row>
            )}
            {contract.signed_at && (
              <Row label="Signé le">
                <span className="text-sm text-teal-700 font-medium">
                  {new Date(contract.signed_at).toLocaleDateString('fr-FR')}
                </span>
              </Row>
            )}
            {contract.total_commitment_cents != null && (
              <Row label="Engagement total">
                <span className="font-mono text-sm tabular-nums">
                  {(contract.total_commitment_cents / 100).toLocaleString('fr-FR', {
                    style: 'currency',
                    currency: 'EUR',
                  })}
                </span>
              </Row>
            )}
          </div>
        ) : (
          <p className="italic text-gray-400 text-sm">Aucun contrat généré</p>
        )}
      </div>
    </div>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-500">{label}</span>
      {children}
    </div>
  )
}

const CONTRACT_STATUS_LABELS: Record<string, { label: string; className: string }> = {
  draft: { label: 'Brouillon', className: 'bg-gray-100 text-gray-600' },
  sent_for_signature: { label: 'En signature', className: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200' },
  signed: { label: 'Signé', className: 'bg-teal-50 text-teal-700 ring-1 ring-teal-200' },
  active: { label: 'Actif', className: 'bg-teal-50 text-teal-700 ring-1 ring-teal-200' },
}

function ContractStatusBadge({ status }: { status: string }) {
  const config = CONTRACT_STATUS_LABELS[status] ?? { label: status, className: 'bg-gray-100 text-gray-500' }
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}

'use client'

import { useTransition, useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { recordFinancierDecision } from '@/lib/actions/refi-actions'
import { Button } from '@/components/ui/button'

interface Props {
  packageId: string
}

export function DecisionButtons({ packageId }: Props) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [notes, setNotes] = useState('')

  function handleDecision(decision: 'approved' | 'rejected') {
    startTransition(async () => {
      const result = await recordFinancierDecision(packageId, decision, notes.trim() || undefined)
      if ('error' in result) {
        toast.error(result.error)
        return
      }
      toast.success(decision === 'approved' ? 'Package approuvé' : 'Package rejeté')
      router.push('/financier')
    })
  }

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="decision-notes" className="block text-sm font-medium text-gray-700 mb-1">
          Notes de décision
        </label>
        <textarea
          id="decision-notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          disabled={isPending}
          rows={3}
          placeholder="Motif de la décision, conditions particulières…"
          className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none"
        />
      </div>

      <div className="flex gap-3">
        <Button
          variant="success"
          className="flex-1"
          onClick={() => handleDecision('approved')}
          disabled={isPending}
        >
          {isPending ? 'Enregistrement…' : 'Approuver'}
        </Button>
        <Button
          variant="danger"
          className="flex-1"
          onClick={() => handleDecision('rejected')}
          disabled={isPending}
        >
          {isPending ? 'Enregistrement…' : 'Rejeter'}
        </Button>
      </div>
    </div>
  )
}

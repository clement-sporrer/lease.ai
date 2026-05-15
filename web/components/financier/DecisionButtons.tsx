'use client'

import { useTransition, useState } from 'react'
import { useRouter } from 'next/navigation'
import { recordFinancierDecision } from '@/lib/actions/refi-actions'

interface Props {
  packageId: string
}

export function DecisionButtons({ packageId }: Props) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)

  function handleDecision(decision: 'approved' | 'rejected') {
    setError(null)
    startTransition(async () => {
      const result = await recordFinancierDecision(packageId, decision, notes.trim() || undefined)
      if ('error' in result) {
        setError(result.error)
        return
      }
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
        <button
          type="button"
          onClick={() => handleDecision('approved')}
          disabled={isPending}
          className="flex-1 rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isPending ? 'Enregistrement…' : 'Approuver'}
        </button>
        <button
          type="button"
          onClick={() => handleDecision('rejected')}
          disabled={isPending}
          className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isPending ? 'Enregistrement…' : 'Rejeter'}
        </button>
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>
      )}
    </div>
  )
}

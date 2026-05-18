import type { AuditEvent } from '@/lib/types/admin'

const ACTION_LABEL: Record<string, string> = {
  status_transition: 'Changement de statut',
  document_validated: 'Document validé',
  document_rejected: 'Document refusé',
  pre_approved: 'Pré-accordé',
  deal_rejected: 'Dossier refusé',
  document_requested: 'Pièce demandée',
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function AuditTimeline({ events }: { events: AuditEvent[] }) {
  return (
    <div className="mb-4 rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-50">
        <h3 className="text-sm font-semibold text-navy-900">Historique</h3>
      </div>
      <div className="px-6 py-5">
        {events.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4">Aucun événement.</p>
        ) : (
          <ol className="relative ml-2 space-y-5 border-l border-gray-100">
            {events.map((event) => (
              <li key={event.id} className="ml-5">
                <div className="absolute -left-1.5 mt-1 h-3 w-3 rounded-full border-2 border-white bg-gray-300" />
                <p className="text-[11px] text-gray-400 mb-0.5 tabular-nums">
                  {formatDateTime(event.created_at)}
                </p>
                <p className="text-sm font-medium text-gray-800">
                  {ACTION_LABEL[event.action] ?? event.action}
                </p>
                <p className="text-xs capitalize text-gray-400">{event.actor_role}</p>
                {event.payload && (
                  <pre className="mt-1.5 overflow-x-auto rounded-lg bg-gray-50 px-3 py-2 font-mono text-xs text-gray-400">
                    {JSON.stringify(event.payload, null, 2)}
                  </pre>
                )}
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  )
}

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
    <div className="mb-4 rounded-xl border border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-700">
        Historique
      </h3>
      {events.length === 0 ? (
        <p className="text-sm text-gray-400">Aucun événement.</p>
      ) : (
        <ol className="relative ml-2 space-y-4 border-l border-gray-200">
          {events.map((event) => (
            <li key={event.id} className="ml-4">
              <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full border border-white bg-gray-400" />
              <p className="mb-0.5 text-xs text-gray-400">{formatDateTime(event.created_at)}</p>
              <p className="text-sm font-medium text-gray-900">
                {ACTION_LABEL[event.action] ?? event.action}
              </p>
              <p className="text-xs capitalize text-gray-500">{event.actor_role}</p>
              {event.payload && (
                <pre className="mt-1 overflow-x-auto rounded bg-gray-50 px-2 py-1 font-mono text-xs text-gray-400">
                  {JSON.stringify(event.payload, null, 2)}
                </pre>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}

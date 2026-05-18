'use client'

import { useState, useTransition } from 'react'
import { getDocumentViewUrl } from '@/lib/actions/document-actions'

interface Props {
  documentId: string
  fileName: string
}

export function DocumentViewerButton({ documentId, fileName }: Props) {
  const [url, setUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  function handleOpen() {
    startTransition(async () => {
      setError(null)
      const result = await getDocumentViewUrl(documentId)
      if (result.error) {
        setError(result.error)
        return
      }
      if (!result.data?.url) {
        setError('URL de visualisation indisponible')
        return
      }
      setUrl(result.data.url)
    })
  }

  function handleClose() {
    setUrl(null)
  }

  return (
    <>
      <button
        onClick={handleOpen}
        disabled={isPending}
        className="shrink-0 text-xs text-blue-500 hover:text-blue-700 disabled:opacity-50 transition-colors"
      >
        {isPending ? '…' : 'Voir'}
      </button>

      {error && (
        <span className="text-xs text-red-500">{error}</span>
      )}

      {url && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="relative flex h-[90vh] w-[90vw] max-w-4xl flex-col rounded-xl bg-white shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
              <span className="truncate text-sm font-medium text-gray-700">{fileName}</span>
              <div className="flex items-center gap-3">
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-500 hover:text-blue-700"
                >
                  Ouvrir dans un onglet
                </a>
                <button
                  onClick={handleClose}
                  className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                  aria-label="Fermer"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <iframe
              src={url}
              className="flex-1 w-full"
              title={fileName}
            />
          </div>
        </div>
      )}
    </>
  )
}

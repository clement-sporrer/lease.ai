'use client'

import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useCallback } from 'react'

interface Props {
  total: number
  page: number
  pageSize: number
}

export function QueuePagination({ total, page, pageSize }: Props) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const totalPages = Math.ceil(total / pageSize)

  const goToPage = useCallback(
    (newPage: number) => {
      const params = new URLSearchParams(searchParams.toString())
      params.set('page', String(newPage))
      router.push(pathname + '?' + params.toString())
    },
    [router, pathname, searchParams]
  )

  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between px-6 py-3 border-t border-gray-50 text-sm text-gray-500">
      <span className="text-xs tabular-nums">
        {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} sur {total}
      </span>
      <div className="flex items-center gap-2">
        <button
          onClick={() => goToPage(page - 1)}
          disabled={page <= 1}
          className="rounded px-2 py-1 text-xs hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          ← Préc.
        </button>
        <span className="text-xs tabular-nums">{page} / {totalPages}</span>
        <button
          onClick={() => goToPage(page + 1)}
          disabled={page >= totalPages}
          className="rounded px-2 py-1 text-xs hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Suiv. →
        </button>
      </div>
    </div>
  )
}

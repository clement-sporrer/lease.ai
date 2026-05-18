'use client'

import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useCallback, useRef } from 'react'

const STATUS_OPTIONS = [
  { value: '', label: 'Tous les statuts' },
  { value: 'submitted', label: 'Soumis' },
  { value: 'internal_review', label: 'En revue' },
  { value: 'missing_documents', label: 'Documents manquants' },
]

export function QueueFilters() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const createQueryString = useCallback(
    (updates: Record<string, string>) => {
      const params = new URLSearchParams(searchParams.toString())
      for (const [key, value] of Object.entries(updates)) {
        if (value) {
          params.set(key, value)
        } else {
          params.delete(key)
        }
      }
      params.delete('page')
      return params.toString()
    },
    [searchParams]
  )

  const currentStatus = searchParams.get('status') ?? ''

  function handleSearchChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      router.push(pathname + '?' + createQueryString({ search: value }))
    }, 300)
  }

  return (
    <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-50">
      <input
        type="search"
        placeholder="Rechercher (réf…)"
        defaultValue={searchParams.get('search') ?? ''}
        onChange={handleSearchChange}
        className="h-8 w-48 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
      <select
        value={currentStatus}
        onChange={(e) => {
          router.push(pathname + '?' + createQueryString({ status: e.target.value }))
        }}
        className="h-8 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        {STATUS_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  )
}

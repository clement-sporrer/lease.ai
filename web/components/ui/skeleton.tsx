import { cn } from '@/lib/utils'

export function Skeleton({ className }: { className?: string }) {
  return (
    <div className={cn('animate-pulse rounded-md bg-gray-100', className)} />
  )
}

export function SkeletonShell({ rows = 3 }: { rows?: number }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* sidebar placeholder */}
      <div className="w-60 shrink-0 border-r border-gray-100 bg-white" />
      <div className="flex-1 flex flex-col min-w-0">
        {/* header */}
        <div className="bg-white border-b border-gray-100 px-8 py-5 space-y-2">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-3.5 w-56" />
        </div>
        {/* content */}
        <div className="p-8 space-y-6">
          {/* stat cards row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-100 p-5 space-y-3">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-7 w-24" />
              </div>
            ))}
          </div>
          {/* table card */}
          <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-50">
              <Skeleton className="h-4 w-32" />
            </div>
            <div className="divide-y divide-gray-50">
              {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="px-6 py-3 flex items-center gap-6">
                  <Skeleton className="h-3.5 w-20" />
                  <Skeleton className="h-5 w-24 rounded-full" />
                  <Skeleton className="h-3.5 w-16" />
                  <Skeleton className="h-3.5 w-12 ml-auto" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

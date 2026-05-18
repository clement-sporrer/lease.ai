import { Skeleton } from '@/components/ui/skeleton'

export default function PackageDetailLoading() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <div className="w-60 shrink-0 border-r border-gray-100 bg-white" />
      <div className="flex-1 flex flex-col min-w-0">
        <div className="bg-white border-b border-gray-100 px-8 py-5 space-y-2">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-3.5 w-28" />
        </div>
        <div className="p-8 max-w-2xl space-y-6">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-56 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    </div>
  )
}

export default function DealReviewLoading() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <div className="w-64 border-r border-gray-200 bg-white" />
      <div className="flex-1 animate-pulse space-y-4 p-8">
        <div className="h-8 w-48 rounded bg-gray-200" />
        <div className="h-32 rounded bg-gray-200" />
        <div className="h-24 rounded bg-gray-200" />
        <div className="h-48 rounded bg-gray-200" />
      </div>
    </div>
  )
}

import { redirect } from 'next/navigation'
import { createSupabaseServerClient } from '@/lib/supabase-server'

export default async function RootPage() {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    redirect('/login')
  }

  // Default to admin — role-based routing added in Phase 2
  redirect('/admin')
}

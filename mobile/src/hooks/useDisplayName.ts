import { useAuthStore } from '@/src/stores/auth'

export function useDisplayName(fallback = 'Utilisateur'): string {
  const session = useAuthStore((s) => s.session)
  const rawName = session?.user?.user_metadata?.full_name
  if (typeof rawName === 'string' && rawName.trim()) return rawName
  return session?.user?.email?.split('@')[0] ?? fallback
}

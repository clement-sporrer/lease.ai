import '../global.css'
import { Stack, useRouter } from 'expo-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
import { View } from 'react-native'
import { supabase } from '@/src/lib/supabase'
import { useAuthStore } from '@/src/stores/auth'
import { normalizeRole } from '@/src/lib/roles'

const queryClient = new QueryClient()

export default function RootLayout() {
  const router = useRouter()
  const { session, isLoading, setSession, setLoading, setActiveRole } = useAuthStore()

  useEffect(() => {
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setActiveRole(session?.user?.user_metadata?.active_role ?? null)
      setLoading(false)
    })

    return () => listener.subscription.unsubscribe()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (isLoading) return
    if (!session) {
      router.replace('/(auth)/login')
      return
    }
    const role = normalizeRole(session.user.user_metadata?.active_role)
    if (role === 'partner') router.replace('/(partner)')
    else if (role === 'client') router.replace('/(client)')
    else router.replace('/(auth)/login')
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoading, session])

  if (isLoading) return <View className="flex-1 bg-white" />

  return (
    <QueryClientProvider client={queryClient}>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(partner)" />
        <Stack.Screen name="(client)" />
      </Stack>
    </QueryClientProvider>
  )
}

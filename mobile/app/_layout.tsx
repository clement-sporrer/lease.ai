import '../global.css'
import { Redirect, Stack } from 'expo-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
import { View } from 'react-native'
import { supabase } from '@/src/lib/supabase'
import { useAuthStore } from '@/src/stores/auth'

const queryClient = new QueryClient()

export default function RootLayout() {
  const { session, isLoading, setSession, setLoading, setActiveRole } = useAuthStore()

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session: s } }) => {
      setSession(s)
      setActiveRole(s?.user?.user_metadata?.active_role ?? null)
      setLoading(false)
    })

    const { data: listener } = supabase.auth.onAuthStateChange((_event, s) => {
      setSession(s)
      setActiveRole(s?.user?.user_metadata?.active_role ?? null)
    })

    return () => listener.subscription.unsubscribe()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (isLoading) {
    return <View className="flex-1 bg-white" />
  }

  if (!session) {
    return (
      <QueryClientProvider client={queryClient}>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(auth)" />
        </Stack>
        <Redirect href="/(auth)/login" />
      </QueryClientProvider>
    )
  }

  const role = session.user.user_metadata?.active_role as string | undefined

  return (
    <QueryClientProvider client={queryClient}>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(partner)" />
        <Stack.Screen name="(client)" />
      </Stack>
      {role === 'partner_user' && <Redirect href="/(partner)/" />}
      {role === 'client_user' && <Redirect href="/(client)/" />}
      {!role && <Redirect href="/(auth)/login" />}
    </QueryClientProvider>
  )
}

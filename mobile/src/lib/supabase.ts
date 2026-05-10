import { createClient } from '@supabase/supabase-js'
import * as SecureStore from 'expo-secure-store'
import { Platform } from 'react-native'

// expo-secure-store has no web implementation (exports empty object).
// On web browser: use localStorage. On SSR (Node.js): no-op (window undefined).
// On native: use SecureStore (iOS Keychain / Android Keystore).
const isBrowser = Platform.OS === 'web' && typeof window !== 'undefined'

const ExpoSecureStoreAdapter = {
  getItem: (key: string): Promise<string | null> => {
    if (isBrowser) return Promise.resolve(localStorage.getItem(key))
    if (Platform.OS === 'web') return Promise.resolve(null)
    return SecureStore.getItemAsync(key)
  },
  setItem: (key: string, value: string): Promise<void> => {
    if (isBrowser) localStorage.setItem(key, value)
    if (Platform.OS !== 'web') return SecureStore.setItemAsync(key, value)
    return Promise.resolve()
  },
  removeItem: (key: string): Promise<void> => {
    if (isBrowser) localStorage.removeItem(key)
    if (Platform.OS !== 'web') return SecureStore.deleteItemAsync(key)
    return Promise.resolve()
  },
}

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing required env vars: EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY',
  )
}

export const supabase = createClient(
  supabaseUrl,
  supabaseAnonKey,
  {
    auth: {
      storage: ExpoSecureStoreAdapter,
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: false,
    },
  }
)

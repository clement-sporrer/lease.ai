import { create } from 'zustand'
import { Session } from '@supabase/supabase-js'

type AuthState = {
  session: Session | null
  isLoading: boolean
  activeRole: string | null
  setSession: (session: Session | null) => void
  setLoading: (loading: boolean) => void
  setActiveRole: (role: string | null) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  session: null,
  isLoading: true,
  activeRole: null,
  setSession: (session) => set({ session }),
  setLoading: (isLoading) => set({ isLoading }),
  setActiveRole: (activeRole) => set({ activeRole }),
}))

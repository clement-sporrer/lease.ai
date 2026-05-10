import { useState } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native'
import { useRouter } from 'expo-router'
import { z } from 'zod'
import { supabase } from '@/src/lib/supabase'

const ROLE_ROUTES = {
  partner_user: '/(partner)/' as const,
  client_user: '/(client)/' as const,
}

type KnownRole = keyof typeof ROLE_ROUTES

const loginSchema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(1, 'Mot de passe requis'),
})

type FieldErrors = Partial<Record<'email' | 'password' | 'root', string>>

export default function LoginScreen() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [focusedField, setFocusedField] = useState<'email' | 'password' | null>(null)
  const [errors, setErrors] = useState<FieldErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit() {
    setErrors({})

    const parsed = loginSchema.safeParse({ email, password })
    if (!parsed.success) {
      const fieldErrors: FieldErrors = {}
      for (const issue of parsed.error.issues) {
        const field = issue.path[0] as 'email' | 'password'
        if (!fieldErrors[field]) fieldErrors[field] = issue.message
      }
      setErrors(fieldErrors)
      return
    }

    setIsSubmitting(true)
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: parsed.data.email,
        password: parsed.data.password,
      })

      if (error) {
        setErrors({ root: error.message })
        return
      }

      const role = data.session?.user?.user_metadata?.active_role as string | undefined

      if (role && role in ROLE_ROUTES) {
        router.replace(ROLE_ROUTES[role as KnownRole])
      } else {
        setErrors({ root: 'Aucun rôle assigné. Contactez votre administrateur.' })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <KeyboardAvoidingView
      className="flex-1 bg-white"
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={{ flexGrow: 1 }} keyboardShouldPersistTaps="handled">
        <View className="flex-1 justify-center px-6">
          <View className="items-center mb-12">
            <Text className="text-4xl font-bold text-navy-900">LeaseAI</Text>
          </View>

          <View>
            {errors.root ? (
              <Text className="text-danger text-sm mb-3">{errors.root}</Text>
            ) : null}

            <TextInput
              className={[
                'border rounded-xl px-4 py-3 mb-1 text-base text-gray-900 bg-gray-50',
                focusedField === 'email' ? 'border-blue-500' : 'border-gray-200',
              ].join(' ')}
              placeholder="Email"
              placeholderTextColor="#9CA3AF"
              autoCapitalize="none"
              keyboardType="email-address"
              autoComplete="email"
              value={email}
              onChangeText={setEmail}
              onFocus={() => setFocusedField('email')}
              onBlur={() => setFocusedField(null)}
            />
            {errors.email ? (
              <Text className="text-danger text-xs mb-3 ml-1">{errors.email}</Text>
            ) : (
              <View className="mb-3" />
            )}

            <TextInput
              className={[
                'border rounded-xl px-4 py-3 mb-1 text-base text-gray-900 bg-gray-50',
                focusedField === 'password' ? 'border-blue-500' : 'border-gray-200',
              ].join(' ')}
              placeholder="Mot de passe"
              placeholderTextColor="#9CA3AF"
              secureTextEntry
              autoComplete="password"
              value={password}
              onChangeText={setPassword}
              onFocus={() => setFocusedField('password')}
              onBlur={() => setFocusedField(null)}
            />
            {errors.password ? (
              <Text className="text-danger text-xs mb-3 ml-1">{errors.password}</Text>
            ) : (
              <View className="mb-3" />
            )}

            <TouchableOpacity
              className="bg-blue-500 rounded-xl py-4 items-center mt-2"
              onPress={handleSubmit}
              disabled={isSubmitting}
              activeOpacity={0.85}
            >
              <Text className="text-white font-semibold text-base">
                {isSubmitting ? 'Connexion...' : 'Log in'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

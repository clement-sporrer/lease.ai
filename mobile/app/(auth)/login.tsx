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
import { BrandMark } from '@/src/components/BrandMark'
import { supabase } from '@/src/lib/supabase'
import { normalizeRole } from '@/src/lib/roles'

const loginSchema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(1, 'Mot de passe requis'),
})

type FieldErrors = Partial<Record<'email' | 'password' | 'root', string>>

const partnerClientDemoAccounts = [
  { label: 'Partner demo', email: 'demo-partner@lease.ai', password: 'demo1234' },
  { label: 'Client demo', email: 'demo-client@lease.ai', password: 'demo1234' },
]

const stakeholderDemoRoles = [
  { label: 'Admin demo', role: 'admin' },
  { label: 'Ops demo', role: 'ops' },
  { label: 'Risk demo', role: 'risk' },
  { label: 'Financier demo', role: 'financier' },
  { label: 'CFO demo', role: 'cfo' },
] as const

type StakeholderRole = (typeof stakeholderDemoRoles)[number]['role']

export default function LoginScreen() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [focusedField, setFocusedField] = useState<'email' | 'password' | null>(null)
  const [errors, setErrors] = useState<FieldErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [pendingStakeholderRole, setPendingStakeholderRole] = useState<StakeholderRole | null>(
    null,
  )

  function fillDemoAccount(emailValue: string, passwordValue: string, role: StakeholderRole | null) {
    setErrors({})
    setEmail(emailValue)
    setPassword(passwordValue)
    setPendingStakeholderRole(role)
  }

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

      const currentRole = normalizeRole(data.session?.user?.user_metadata?.active_role)
      const targetRole = pendingStakeholderRole ?? currentRole

      if (targetRole && targetRole !== 'partner' && targetRole !== 'client') {
        const { error: updateError } = await supabase.auth.updateUser({
          data: { active_role: targetRole },
        })
        if (updateError) {
          setErrors({ root: updateError.message })
          return
        }
        router.replace('/(tabs)')
        return
      }

      if (targetRole === 'partner') router.replace('/(partner)')
      else if (targetRole === 'client') router.replace('/(client)')
      else setErrors({ root: 'Aucun rôle assigné. Contactez votre administrateur.' })
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
            <BrandMark variant="logo" style={{ width: 240, height: 72 }} />
          </View>

          <View>
            {__DEV__ ? (
              <View className="mb-6 rounded-2xl border border-gray-200 bg-gray-50 p-4">
                <Text className="text-sm font-semibold text-navy-900 mb-2">Comptes de démo</Text>
                <Text className="text-xs text-gray-500 mb-3">
                  Partenaire et client utilisent `demo1234`.
                </Text>
                <View className="flex-row gap-3">
                  {partnerClientDemoAccounts.map((account) => (
                    <TouchableOpacity
                      key={account.label}
                      className="flex-1 rounded-xl bg-white border border-gray-200 py-3 items-center"
                      onPress={() => fillDemoAccount(account.email, account.password, null)}
                      activeOpacity={0.85}
                    >
                      <Text className="text-sm font-medium text-gray-900">{account.label}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
                <Text className="mt-4 mb-2 text-sm font-semibold text-navy-900">Autres rôles</Text>
                <View className="flex-row flex-wrap gap-2">
                  {stakeholderDemoRoles.map((account) => (
                    <TouchableOpacity
                      key={account.role}
                      className={`rounded-xl border px-3 py-3 ${
                        pendingStakeholderRole === account.role
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 bg-white'
                      }`}
                      onPress={() =>
                        fillDemoAccount('demo-admin@lease.ai', 'demo1234', account.role)
                      }
                      activeOpacity={0.85}
                    >
                      <Text className="text-sm font-medium text-gray-900">{account.label}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
                <Text className="mt-3 text-xs text-gray-500">
                  Les rôles internes utilisent le compte `demo-admin` et changent de rôle après
                  connexion.
                </Text>
              </View>
            ) : null}

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
              className={`bg-blue-500 rounded-xl py-4 items-center mt-2 ${isSubmitting ? 'opacity-50' : ''}`}
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

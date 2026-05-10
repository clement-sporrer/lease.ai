import { Ionicons } from '@expo/vector-icons'
import { Stack, useRouter } from 'expo-router'
import { Text, TouchableOpacity } from 'react-native'

export default function NewDealLayout() {
  const router = useRouter()

  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: '#0D183D' },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: { fontWeight: '600' },
        contentStyle: { backgroundColor: '#F9FAFB' },
      }}
    >
      <Stack.Screen
        name="index"
        options={{
          title: 'Nouveau dossier',
          headerLeft: () => (
            <TouchableOpacity
              onPress={() => router.replace('/(partner)' as never)}
              activeOpacity={0.8}
              className="flex-row items-center rounded-full border border-white/15 px-3 py-2"
            >
              <Ionicons name="chevron-back" size={18} color="#FFFFFF" />
              <Text className="ml-1 text-sm font-medium text-white">Menu</Text>
            </TouchableOpacity>
          ),
        }}
      />
      <Stack.Screen name="enrichment" options={{ title: 'Entreprise' }} />
      <Stack.Screen name="quote" options={{ title: 'Devis' }} />
      <Stack.Screen name="offer" options={{ title: 'Offre indicative' }} />
    </Stack>
  )
}

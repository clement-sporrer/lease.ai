import { Stack } from 'expo-router'

export default function NewDealLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: '#0D183D' },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: { fontWeight: '600' },
        contentStyle: { backgroundColor: '#F9FAFB' },
      }}
    >
      <Stack.Screen name="index" options={{ title: 'Nouveau dossier' }} />
      <Stack.Screen name="enrichment" options={{ title: 'Entreprise' }} />
      <Stack.Screen name="quote" options={{ title: 'Devis' }} />
      <Stack.Screen name="offer" options={{ title: 'Offre indicative' }} />
    </Stack>
  )
}

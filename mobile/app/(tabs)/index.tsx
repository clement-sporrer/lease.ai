import { Ionicons } from '@expo/vector-icons'
import { useRouter } from 'expo-router'
import { useMemo } from 'react'
import { Alert, ScrollView, Text, TouchableOpacity, View } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'

import { BrandMark } from '@/src/components/BrandMark'
import { StatusBadge } from '@/src/components/StatusBadge'
import { normalizeRole } from '@/src/lib/roles'
import { useAuthStore } from '@/src/stores/auth'

type InternalRole = 'admin' | 'ops' | 'risk' | 'financier' | 'cfo'

type RoleCard = {
  label: string
  value: string
  caption: string
}

type RoleAction = {
  label: string
  icon: keyof typeof Ionicons.glyphMap
  message: string
}

type RoleFront = {
  title: string
  subtitle: string
  badge: string
  accent: string
  cards: RoleCard[]
  focus: string[]
  actions: RoleAction[]
}

const ROLE_FRONTS: Record<InternalRole, RoleFront> = {
  admin: {
    title: 'Pilotage de la revue',
    subtitle: 'Vision de la file, arbitrage des dossiers et décisions rapides.',
    badge: 'Administration',
    accent: 'bg-indigo-600',
    cards: [
      { label: 'Dossiers en file', value: '18', caption: '6 prioritaires' },
      { label: 'Décisions du jour', value: '7', caption: '4 pré-accords' },
      { label: 'Temps moyen', value: '14 min', caption: 'par dossier' },
    ],
    focus: ['Dossiers soumis', 'Documents manquants', 'Pré-approbations à valider'],
    actions: [
      { label: 'Ouvrir la file', icon: 'list-outline', message: 'File de revue interne.' },
      { label: 'Pré-approuver', icon: 'checkmark-circle-outline', message: 'Action de pré-approbation.' },
    ],
  },
  ops: {
    title: 'Suivi documentaire',
    subtitle: 'Contrôler les pièces, relancer les manquants et tenir le rythme.',
    badge: 'Opérations',
    accent: 'bg-teal-600',
    cards: [
      { label: 'Pièces à relancer', value: '9', caption: '4 aujourd’hui' },
      { label: 'PDF en attente', value: '5', caption: 'depuis moins de 24 h' },
      { label: 'Taux de complétion', value: '92%', caption: 'sur la semaine' },
    ],
    focus: ['Uploads récents', 'Documents incomplets', 'Relances à envoyer'],
    actions: [
      { label: 'Voir les pièces', icon: 'document-text-outline', message: 'Liste documentaire.' },
      { label: 'Relancer', icon: 'mail-outline', message: 'Relance documentaire simulée.' },
    ],
  },
  risk: {
    title: 'Lecture du risque',
    subtitle: 'Prioriser les dossiers sensibles et garder le portefeuille sous contrôle.',
    badge: 'Risque',
    accent: 'bg-amber-500',
    cards: [
      { label: 'Dossiers à revoir', value: '4', caption: '2 seuils élevés' },
      { label: 'Bandes critiques', value: '2', caption: 'à surveiller' },
      { label: 'Score moyen', value: '78/100', caption: 'portefeuille sain' },
    ],
    focus: ['Dossiers à fort risque', 'Bandes faibles', 'Recommandations de score'],
    actions: [
      { label: 'Voir le scoring', icon: 'shield-checkmark-outline', message: 'Détail du scoring.' },
      { label: 'Afficher les alertes', icon: 'alert-circle-outline', message: 'Alertes de risque simulées.' },
    ],
  },
  financier: {
    title: 'Bouclage financier',
    subtitle: 'Suivre les marges, la capacité et les besoins de financement.',
    badge: 'Financement',
    accent: 'bg-emerald-600',
    cards: [
      { label: 'Engagements ouverts', value: '€ 1.42M', caption: '13 lignes' },
      { label: 'Marge moyenne', value: '3.8%', caption: 'en ligne avec le plan' },
      { label: 'Capacité restante', value: '€ 620k', caption: 'après stress' },
    ],
    focus: ['Lignes de financement', 'Marge par dossier', 'Décaissements à venir'],
    actions: [
      { label: 'Lignes ouvertes', icon: 'calculator-outline', message: 'Vue des lignes ouvertes.' },
      { label: 'Exporter', icon: 'download-outline', message: 'Export financier simulé.' },
    ],
  },
  cfo: {
    title: 'Vue direction',
    subtitle: 'Lire la trésorerie, l’exposition et les arbitrages de portefeuille.',
    badge: 'Direction financière',
    accent: 'bg-rose-600',
    cards: [
      { label: 'Cash engagé', value: '€ 1.9M', caption: 'contre € 2.4M planifiés' },
      { label: 'Exposition max', value: '63%', caption: 'sous le seuil' },
      { label: 'Prévision 90 j', value: 'Stable', caption: 'tendance maîtrisée' },
    ],
    focus: ['Cash burn', 'Taux d’occupation des lignes', 'Points de vigilance'],
    actions: [
      { label: 'Synthèse', icon: 'analytics-outline', message: 'Synthèse direction.' },
      { label: 'Rapport', icon: 'document-attach-outline', message: 'Rapport CFO simulé.' },
    ],
  },
}

const INTERNAL_ROLES: InternalRole[] = ['admin', 'ops', 'risk', 'financier', 'cfo']

function toInternalRole(value: unknown): InternalRole {
  return typeof value === 'string' && INTERNAL_ROLES.includes(value as InternalRole)
    ? (value as InternalRole)
    : 'admin'
}

function InternalCard({ card }: { card: RoleCard }) {
  return (
    <View className="flex-1 min-w-[100px] rounded-2xl border border-gray-200 bg-white p-4">
      <Text className="text-xs font-medium uppercase tracking-[1.2px] text-gray-500">
        {card.label}
      </Text>
      <Text className="mt-2 text-2xl font-bold text-navy-900">{card.value}</Text>
      <Text className="mt-1 text-xs text-gray-500">{card.caption}</Text>
    </View>
  )
}

function ActionButton({ action }: { action: RoleAction }) {
  return (
    <TouchableOpacity
      className="flex-row items-center justify-between rounded-2xl border border-gray-200 bg-white px-4 py-4"
      activeOpacity={0.85}
      onPress={() => Alert.alert(action.label, action.message)}
    >
      <View className="flex-row items-center gap-3">
        <View className="h-10 w-10 items-center justify-center rounded-full bg-gray-100">
          <Ionicons name={action.icon} size={20} color="#0D183D" />
        </View>
        <Text className="text-sm font-medium text-navy-900">{action.label}</Text>
      </View>
      <Ionicons name="chevron-forward" size={18} color="#94A3B8" />
    </TouchableOpacity>
  )
}

export default function InternalDashboard() {
  const router = useRouter()
  const session = useAuthStore((state) => state.session)
  const role = toInternalRole(normalizeRole(session?.user?.user_metadata?.active_role))
  const front = useMemo(() => ROLE_FRONTS[role], [role])

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['top']}>
      <ScrollView
        className="flex-1"
        contentContainerClassName="px-5 pt-5 pb-28"
        showsVerticalScrollIndicator={false}
      >
        <View className="flex-row items-start justify-between gap-4">
          <View className="flex-1 gap-3">
            <View className="flex-row items-center gap-3">
              <BrandMark variant="mark" style={{ width: 32, height: 32 }} />
              <View>
                <Text className="text-sm font-medium uppercase tracking-[2px] text-gray-500">
                  LeaseAI interne
                </Text>
                <Text className="text-2xl font-bold text-navy-900">{front.title}</Text>
              </View>
            </View>
            <Text className="text-sm leading-6 text-gray-600">{front.subtitle}</Text>
          </View>
          <TouchableOpacity
            className="rounded-full bg-navy-900 px-3 py-2"
            activeOpacity={0.85}
            onPress={() => router.push('/(auth)/login' as never)}
          >
            <Text className="text-xs font-semibold uppercase tracking-[1px] text-white">
              Retour login
            </Text>
          </TouchableOpacity>
        </View>

        <View className={`mt-5 rounded-3xl px-5 py-5 ${front.accent}`}>
          <Text className="text-xs font-semibold uppercase tracking-[1.5px] text-white/75">
            {front.badge}
          </Text>
          <View className="mt-3 flex-row items-end justify-between gap-4">
            <View className="flex-1">
              <Text className="text-3xl font-bold leading-9 text-white">{front.title}</Text>
              <Text className="mt-2 text-sm leading-6 text-white/85">{front.subtitle}</Text>
            </View>
            <StatusBadge status="active" large />
          </View>
        </View>

        <View className="mt-5 flex-row flex-wrap gap-3">
          {front.cards.map((card) => (
            <InternalCard key={card.label} card={card} />
          ))}
        </View>

        <View className="mt-6 rounded-3xl border border-gray-200 bg-white p-5">
          <Text className="text-base font-semibold text-navy-900">Focus du jour</Text>
          <View className="mt-4 gap-3">
            {front.focus.map((item) => (
              <View key={item} className="flex-row items-center gap-3">
                <View className="h-2.5 w-2.5 rounded-full bg-blue-500" />
                <Text className="flex-1 text-sm text-gray-700">{item}</Text>
              </View>
            ))}
          </View>
        </View>

        <View className="mt-6 gap-3">
          <Text className="text-base font-semibold text-navy-900">Actions rapides</Text>
          {front.actions.map((action) => (
            <ActionButton key={action.label} action={action} />
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  )
}

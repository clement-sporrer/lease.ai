# LeaseAI — Strategic Roadmap & Complete Task Breakdown
**Date :** 2026-05-16  
**Statut :** Document de travail — source de vérité pour les sprints à venir  

---

## Priorités

| Code | Signification |
|---|---|
| **P1** | Critique démo — bloquant pour la présentation |
| **P2** | Phase 2 — cycle complet, CRM, e-signature |
| **P3** | Phase 3 — opérationnel réel (billing, paiements) |
| **P4** | Phase 4 — intelligence ambiante, AI, fine-tuning |

L'ordre (1→N) est l'ordre **logique de développement**, pas uniquement la priorité. Un item P3 peut être en position 15 parce qu'il dépend d'items P1 en positions 1–14.

---

## Audit par persona — état actuel

### Admin (`admin@lease-ai.fr`) — `/admin`
| Élément | État | Note |
|---|---|---|
| Dashboard stats (queue, en révision, approuvés) | ✅ Fonctionne | Données réelles |
| File d'attente `/admin/queue` | ✅ Fonctionne | Données réelles |
| Deal detail `/admin/deals/[id]` | ✅ Fonctionne | Panels tous wired |
| CompanySummary + badge Pappers | ✅ Fonctionne | enrichment_source en base |
| RiskSummary (A/B/C/D/E) | ✅ Fonctionne | |
| DocumentList | ✅ Fonctionne | |
| Checklist | ✅ Affiche | ❌ Pas de checkbox cliquable |
| Timeline | ✅ Affiche | |
| ActionPanel (Pré-accorder / Refuser / Demander pièce) | ✅ Fonctionne | Token passé en prop |
| RefiPackagePanel (create + send) | ✅ Fonctionne | |
| OfferPanel (generate avec versioning) | ✅ Fonctionne | |
| QuoteUploadZone (PDF → Mistral) | ✅ Fonctionne | Mock si `USE_REAL_MISTRAL=false` |
| Guard de rôle sur `/admin` | ❌ Absent | N'importe qui peut accéder |
| Nom utilisateur dans sidebar | ❌ Absent | Hardcodé "Administrateur" |
| Bouton logout | ❌ Absent | |
| Recherche / filtre sur la queue | ❌ Absent | |
| Pagination queue | ❌ Absent | Limité à 10 |
| Viewer de document (PDF in-browser) | ❌ Absent | Lien download seulement |
| Toast de succès | ❌ Absent | Erreurs inline seulement |

### Financier (`financier@lease-ai.fr`) — `/financier`
| Élément | État | Note |
|---|---|---|
| Dashboard (total, pending, approved, rejected) | ✅ Fonctionne | |
| Liste packages (10 récents) | ✅ Fonctionne | |
| Package detail `/financier/packages/[id]` | ✅ Fonctionne | |
| DecisionButtons (Approuver / Refuser + notes) | ✅ Fonctionne | |
| Nom société visible dans la liste | ❌ Absent | Seulement UUID tronqué |
| Guard de rôle | ❌ Absent | |
| Nom utilisateur / logout | ❌ Absent | |
| Lien retour vers liste depuis détail | ❌ Absent | |
| Nom deal public_id dans le détail | ❌ Absent | Seulement package UUID |

### CFO (`cfo@lease-ai.fr`) — `/cfo`
| Élément | État | Note |
|---|---|---|
| Dashboard stats (actif, pipeline, engagement, cash) | ✅ Fonctionne | Données réelles |
| Taux de défaut (`defaultRate`) | ⚠️ Affiche `—` | Backend ne le retourne pas encore |
| Guard de rôle | ❌ Absent | |
| Nom utilisateur / logout | ❌ Absent | |
| Graphiques / courbes | ❌ Absent | Chiffres seulement |
| Tableau breakdown deals actifs | ❌ Absent | |
| Filtre par période | ❌ Absent | Mois courant hardcodé |
| Export CSV/Excel | ❌ Absent | |

### Ops (`ops@lease-ai.fr`) — `/ops`
| Élément | État | Note |
|---|---|---|
| Page existe | ✅ | |
| Contenu réel | ❌ Absent | Toutes les stats à 0 |
| Queue activation | ❌ Absent | Phase 2 |
| Gestion contrats | ❌ Absent | Phase 2 |
| Suivi assets | ❌ Absent | Phase 2 |

### Risk (`risk@lease-ai.fr`) — `/risk`
| Élément | État | Note |
|---|---|---|
| Page | ❌ N'existe pas | 404 |
| Dashboard risque | ❌ Absent | |
| Vue dossiers à analyser | ❌ Absent | |
| Scoring détaillé | ❌ Absent | |

### Commercial (`commercial@lease-ai.fr`) — `/commercial`
| Élément | État | Note |
|---|---|---|
| Page | ❌ N'existe pas | 404 |
| Pipeline deals | ❌ Absent | |
| Création dossier | ❌ Absent | (via web, Phase 2) |

### Comptable (`comptable@lease-ai.fr`) — `/comptable`
| Élément | État | Note |
|---|---|---|
| Page | ❌ N'existe pas | 404 |
| Vue facturation | ❌ Absent | Phase 3 |
| Réconciliation | ❌ Absent | Phase 3 |

### Partenaire (`partenaire@techpro-solutions.fr`) — Mobile
| Élément | État | Note |
|---|---|---|
| App Expo | ❌ Hors scope démo | |

### Client (`client@globex-corp.fr`) — Mobile
| Élément | État | Note |
|---|---|---|
| App Expo | ❌ Hors scope démo | |

---

## Problèmes transversaux

### Sécurité — Critique
- Aucun middleware Next.js → toutes les routes accessibles sans auth
- Aucun RBAC sur les routes (un comptable peut voir `/admin`)
- Token JWT passé en prop dans `ActionPanel` (XSS risk si compromis)
- Pas de refresh de session (token expire, user bloqué silencieusement)
- CORS non configuré pour la production Railway
- Pas de rate limiting sur l'API

### UX/UI — Gaps
- Sidebar affiche un label hardcodé, pas le vrai nom utilisateur
- Pas de logout
- Pas de feedback succès (toasts) — seulement erreurs inline
- Pas de loading skeletons (flash de contenu vide)
- Pas de design responsive (back-office web only, mais quand même)
- Fonts : Geist (default Next.js) au lieu de Satoshi + IBM Plex Mono comme spécifié
- Pas de favicon ni app icon
- Pas d'illustrations empty state
- Pas de breadcrumbs sur les pages de détail

### Infrastructure — Gaps
- Backend non déployé (Railway)
- Pas de CI/CD (GitHub Actions)
- Pas de monitoring erreurs (Sentry)
- Pas de logging structuré backend en prod
- Variables d'environnement non validées au démarrage (app plante silencieusement)

### Data — Gaps
- Seed data pas encore en Supabase (script à lancer)
- Nom société pas visible dans la liste packages financier
- Pas de données réelles Pappers (`USE_REAL_PAPPERS=false`)
- Pas de données réelles Mistral (`USE_REAL_MISTRAL=false`)

---

## Roadmap stratégique — Tasks 1 à 47

---

### 🔴 BLOC 1 — Demo Readiness (P1 — Cette semaine)

**Objectif :** La démo de 10 minutes tourne sans accroc, sans 404, sans erreur visible.

---

**#1 — P1 | Auth | Middleware Next.js**  
Ajouter `middleware.ts` à la racine de `web/`. Routes protégées redirigent vers `/login`. Lecture du cookie Supabase SSR pour vérifier la session côté Edge.

```ts
// web/middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const PUBLIC_ROUTES = ['/login']

export async function middleware(request: NextRequest) {
  const response = NextResponse.next()
  const supabase = createServerClient(url, anon_key, { cookies: ... })
  const { data: { session } } = await supabase.auth.getSession()
  if (!session && !PUBLIC_ROUTES.includes(request.nextUrl.pathname)) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return response
}

export const config = { matcher: ['/((?!_next|api|favicon).*)'] }
```

---

**#2 — P1 | Auth | RBAC route guard**  
Middleware étendu : après vérification session, vérifier `user_metadata.active_role` et autoriser seulement les préfixes de routes correspondants. Admin ne peut pas accéder à `/cfo`, etc.

Route → Rôles autorisés :
- `/admin/*` → `admin`, `ops`
- `/financier/*` → `financier`
- `/cfo/*` → `cfo`
- `/ops/*` → `ops`
- `/risk/*` → `risk`
- `/commercial/*` → `commercial`
- `/comptable/*` → `comptable`

---

**#3 — P1 | Data | Lancer seed_demo.py**  
Exécuter `python backend/scripts/seed_demo.py` pour créer les 3 dossiers démo dans Supabase. Vérifier que Globex est en `internal_review` avec risk_band A, 3 documents validés.

---

**#4 — P1 | Backend | Lancer le backend local**  
Vérifier que `uvicorn app.main:app --reload` démarre proprement avec les env vars du root `.env.local`. Documenter la commande de lancement dans README.

---

**#5 — P1 | UX | Sidebar : nom utilisateur + logout**  
Le `Sidebar` est un client component. Utiliser `createBrowserClient` pour lire `supabase.auth.getUser()` et afficher `user.user_metadata.full_name`. Ajouter un bouton logout qui appelle `supabase.auth.signOut()` puis `router.push('/login')`.

---

**#6 — P1 | UX | Toasts de succès**  
Intégrer `react-hot-toast` ou `sonner` (déjà dans shadcn). Sur chaque action (pré-approuver, envoyer refi, approuver, générer offre), afficher un toast vert. Sur erreur, toast rouge. Remplacer les erreurs inline dans les modales par des toasts.

---

**#7 — P1 | UX | Loading states**  
Ajouter des skeletons sur les pages qui fetchent des données (admin dashboard, deal detail, financier queue). Utiliser `loading.tsx` Next.js App Router pour chaque route. Eviter le flash de contenu vide.

---

**#8 — P1 | UX | Fonts Satoshi + IBM Plex Mono**  
Remplacer Geist par Satoshi (variable font). IBM Plex Mono pour toutes les valeurs numériques et financières (déjà `font-mono` dans certains endroits mais pas cohérent). Configurer dans `layout.tsx` et `globals.css`.

---

**#9 — P1 | UX | Favicon + metadata**  
Créer `web/app/favicon.ico` et `web/app/icon.png` (logo L). Compléter le metadata de chaque layout de route group avec des titres contextuels (ex: "LeaseAI — Financier").

---

**#10 — P1 | Bug | Financier : afficher nom société dans liste packages**  
Le package refi n'a pas de champ `company_name`. Il faut soit : (a) joindre le nom société dans l'endpoint `GET /refi-packages`, soit (b) l'ajouter en réponse. Afficher "Globex Corporation" au lieu de l'UUID tronqué.

---

**#11 — P1 | Bug | Financier : lien retour + deal public_id dans détail**  
Page `/financier/packages/[id]` : ajouter un lien "← Retour" vers `/financier`. Afficher `deal.public_id` et `company_name` en en-tête du détail.

---

**#12 — P1 | Bug | CFO : ajouter defaultRate au backend**  
Endpoint `GET /cfo/portfolio` : calculer et retourner `default_rate` (deals en `financier_rejected` / total deals). Le frontend l'affiche déjà, il attend juste la valeur.

---

**#13 — P1 | UX | Breadcrumbs sur pages de détail**  
Ajouter un fil d'Ariane sur `/admin/deals/[id]` (Tableau de bord → Dossiers → D-2026-0001) et `/financier/packages/[id]` (Tableau de bord → Packages → UUID). Composant `Breadcrumbs` réutilisable.

---

**#14 — P1 | UX | Empty states avec illustration**  
Quand la queue est vide, le dashboard financier vide, le CFO sans deals — afficher une illustration SVG simple + message contextuel + CTA. Pas un simple texte gris.

---

**#15 — P1 | Infra | Déployer backend sur Railway**  
Configurer Railway project, ajouter les env vars (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, DATABASE_URL, MISTRAL_API_KEY, PAPPERS_API_KEY). Mettre à jour `NEXT_PUBLIC_API_URL` sur Vercel pour pointer vers Railway.

---

**#16 — P1 | Infra | Déployer web sur Vercel**  
Vérifier que le build Vercel passe avec les env vars correctes. Configurer le domaine custom si disponible.

---

### 🟠 BLOC 2 — Pages manquantes + UX (P1/P2 — Semaine 2-3)

**Objectif :** Chaque persona a une page fonctionnelle. L'expérience est cohérente partout.

---

**#17 — P1 | Page | Risk dashboard**  
Créer `/risk/page.tsx` avec `DashboardShell role="risk"`. Afficher :
- Dossiers en `internal_review` avec score de risque
- Distribution des risk bands (A/B/C/D/E) sous forme de barres
- Dossiers les plus risqués en haut
- Lien vers le deal detail (lecture seule pour risk)

Backend : endpoint `GET /risk/queue` qui filtre les deals en `internal_review`.

---

**#18 — P1 | Page | Commercial dashboard**  
Créer `/commercial/page.tsx`. Vue pipeline :
- Deals en `draft`, `company_enriched`, `quote_added`
- Possibilité de créer un nouveau deal depuis le web (Phase 2 pour la version complète)
- Métriques : deals en cours, taux de conversion, volume en pipeline

---

**#19 — P2 | Page | Comptable dashboard**  
Créer `/comptable/page.tsx`. Vue facturation :
- Factures émises (Phase 3)
- Paiements reçus / en retard
- Export comptable
- Pour l'instant : message "Disponible en Phase 3 — synchronisation Pennylane"

---

**#20 — P1 | UX | Checklist interactive admin**  
Les items de checklist sur la page deal doivent être cliquables. Endpoint `PATCH /admin/deals/{id}/checklist/{item}` pour marquer un item comme vérifié. Mise à jour optimiste côté client.

---

**#21 — P1 | UX | Document viewer in-browser**  
Sur la page deal, cliquer sur un document ouvre une modale avec un PDF viewer (iframe avec signed URL Supabase Storage). Pas de redirect vers une nouvelle page. Utiliser `react-pdf` ou iframe simple.

---

**#22 — P2 | UX | Server actions pour ActionPanel**  
Migrer `ActionPanel` de fetch client-side (token en prop) vers des server actions. Comme `OfferPanel` et `RefiPackagePanel`. Élimine le token passé en prop.

---

**#23 — P2 | Feature | Création de deal depuis le web**  
Formulaire admin/commercial pour créer un deal :
- Recherche SIREN → enrichissement Pappers auto
- Upload devis PDF → extraction Mistral
- Assignation partenaire optionnelle
- Crée le deal en `draft` → `company_enriched` → `quote_added` en une flow

---

**#24 — P1 | UX | Pagination sur les listes**  
Queue admin et liste packages financier : pagination côté serveur. Paramètres `?page=1&per_page=20`. Composant `Pagination` réutilisable avec prev/next + numéros de page.

---

**#25 — P1 | UX | Recherche et filtres queue admin**  
Barre de recherche sur la queue (par `public_id`, nom société). Filtres : statut, risk_band, date. Paramètres URL persistants (`?status=internal_review&risk=A`).

---

**#26 — P2 | Branding | Design system complet**  
Audit de toutes les classes Tailwind utilisées. Extraire un design system cohérent :
- Tokens : couleurs, spacing, radius, shadows, typography
- Composants : Button (primary/secondary/danger), Badge, Card, Table, Modal, Input, Select, Textarea
- Storybook ou doc page simple pour référencer les composants

---

**#27 — P2 | UX | Notifications in-app**  
Centre de notifications dans la sidebar (cloche). Nouvelles notifications quand :
- Un package refi est reçu (pour le financier)
- Une décision financier est prise (pour l'admin)
- Un document est manquant
Stocké en base, marqué "lu" au clic. Backend : `GET /notifications` et `PATCH /notifications/{id}/read`.

---

### 🟡 BLOC 3 — Cycle Complet Phase 2 (P2 — Semaines 5-8)

**Objectif :** De la création à l'activation, tout est connecté. Intégrations externes réelles.

---

**#28 — P2 | Backend | Modèles Contract, Asset, Signature**  
SQLAlchemy models + Alembic migration :
- `Contract` : deal_id, offer_id, content_url, status (draft/sent/signed), signed_at
- `Asset` : contract_id, description, serial_number, quantity, unit_price_cents, category
- `Signature` : contract_id, signatory_email, provider (yousign), external_id, signed_at, status

---

**#29 — P2 | Backend | Endpoints contrat + activation**  
- `POST /deals/{id}/contracts` → génère le contrat PDF (template Jinja2)
- `POST /contracts/{id}/send` → envoie pour signature (Yousign ou mock)
- `POST /contracts/{id}/activate` → active le deal, crée les assets
- `GET /deals/{id}/contract` → détail contrat

---

**#30 — P2 | Integration | Yousign e-signature**  
Service `YousignService` avec feature flag `USE_REAL_YOUSIGN`. 
- Crée une "signature request" avec le PDF
- Webhook Yousign → `POST /webhooks/yousign` → met à jour `Signature.status`
- Deal passe en `signed` automatiquement sur confirmation

---

**#31 — P2 | Integration | Resend — Emails transactionnels**  
Service `ResendService` avec templates HTML :
- Email offre ferme (avec PDF en pièce jointe)
- Email contrat à signer (lien Yousign)
- Relance document manquant (avec liste des docs)
- Confirmation activation

---

**#32 — P2 | Integration | Attio CRM**  
Service `AttioService` :
- Deal créé → crée contact + deal dans Attio automatiquement
- Sync statuts clés (pre_approved, signed, active)
- Évite la double saisie commercial/ADV

---

**#33 — P2 | Integration | Claude API — Résumé risque narratif**  
Dans la sidebar de la page deal admin : un paragraphe généré par Claude API résumant le risque du dossier (risk_band, score, anomalies détectées, recommandation). Mis en cache en base, régénéré sur demande.

---

**#34 — P2 | Web | Vue contrat + ops activation checklist**  
- Page `/ops/contracts` : liste des contrats en cours
- Page `/ops/contracts/[id]` : détail + checklist activation (assets reçus, installation confirmée)
- Bouton "Activer" → `POST /contracts/{id}/activate`

---

**#35 — P2 | Web | Vue assets créés après activation**  
Sur la page deal (admin + ops) : section "Assets" visible après activation. Liste des équipements avec numéro de série, état, date d'installation.

---

**#36 — P2 | Security | Audit log viewer**  
Page `/admin/audit` : liste des événements sensibles (login admin+, changement statut, décision, override, activation). Filtrable par user, action, date. Backend : `GET /admin/audit` avec pagination.

---

### 🟡 BLOC 4 — Opérationnel Phase 3 (P3 — Semaines 9-12)

**Objectif :** La boite tourne sur l'outil. Billing, paiements, comptabilité automatisée.

---

**#37 — P3 | Backend | Modèles PaymentSchedule, Invoice, Payment**  
- `PaymentSchedule` : contract_id, monthly_payment_cents, start_date, end_date, nb_payments
- `Invoice` : schedule_id, due_date, amount_cents, status (pending/paid/late), paid_at
- `Payment` : invoice_id, amount_cents, received_at, source (qonto/manual), reference

---

**#38 — P3 | Backend | Génération échéancier à l'activation**  
À l'activation du contrat → générer automatiquement toutes les `Invoice` du `PaymentSchedule`. Ex: 36 mois → 36 factures créées avec les dates d'échéance.

---

**#39 — P3 | Integration | Qonto — Réconciliation paiements**  
Service `QontoService` avec webhook :
- Virement reçu → match avec facture par référence
- `Invoice.status` → `paid`, `Payment` créé
- Alertes si montant ne correspond pas (écart > 1€)

---

**#40 — P3 | Integration | Pennylane — Comptabilité**  
Service `PennylaneService` :
- Chaque facture émise → écriture comptable générée (compte produit, TVA)
- Chaque paiement reçu → écriture lettrée
- Export mensuel automatique

---

**#41 — P3 | Web | Comptable — Vue facturation complète**  
- Page `/comptable` : tableau de bord (CA mois, encaissements, retards)
- Liste factures avec filtres (status, période, client)
- Actions : marquer payé manuellement, générer avoir
- Export CSV pour intégration comptable externe

---

**#42 — P3 | Web | CFO — Cash dashboard enrichi**  
Compléter le dashboard CFO :
- Courbe trésorerie (loyers attendus vs reçus, M-6 → M+6)
- Tableau deals actifs avec échéancier
- Alertes retards (badge rouge si > 30 jours)
- Export Excel one-click

---

**#43 — P3 | Web | Client — Espace client mobile**  
App Expo côté client :
- Login → voir ses contrats actifs
- Échéancier et historique de paiements
- Télécharger ses factures
- Signalement de problème (asset défectueux)

---

### 🟢 BLOC 5 — Intelligence Ambiante Phase 4 (P4 — Mois 3-4)

**Objectif :** Le produit pense avec vous. AI contextuelle, suggestions, détection d'anomalies.

---

**#44 — P4 | AI | Agent contextuel Claude avec RAG**  
Sidebar AI dans chaque vue rôle :
- Context : deal actif, historique dossiers similaires, KPIs
- Répond à des questions métier ("quel est le risque de ce dossier ?")
- Suggère des actions ("ce dossier ressemble à un qui a defaulté en mois 8")
- RAG sur la base de dossiers (embeddings via `pgvector`)

---

**#45 — P4 | AI | Détection d'anomalies paiements**  
Job scheduled (cron) qui analyse les paiements :
- Retard récurrent → alerte ops + comptable
- Pattern inhabituel (paiement partiel, double) → alerte CFO
- Score de risque de défaut mis à jour dynamiquement

---

**#46 — P4 | Integration | Granola — Notes réunion → dossier**  
Webhook Granola → `POST /deals/from-notes` :
- Transcript de réunion → Claude extrait les éléments clés (société, montant, durée, type matériel)
- Deal créé en `draft` avec les champs pré-remplis
- Commercial reçoit une notification pour valider

---

**#47 — P4 | AI | Fine-tuning extraction documents**  
- Dataset : tous les devis extraits avec corrections manuelles
- Fine-tuning Mistral sur l'extraction de devis IT leasing
- A/B test : fine-tuné vs base model sur précision des line items
- Fallback automatique si modèle fine-tuné dépasse p95 latency

---

## Synthèse par bloc

| # Tâches | Bloc | Priorité | Deadline |
|---|---|---|---|
| 1–16 | Demo readiness | P1 | Semaine 1 |
| 17–27 | Pages manquantes + UX | P1/P2 | Semaines 2–3 |
| 28–36 | Cycle complet Phase 2 | P2 | Semaines 5–8 |
| 37–43 | Opérationnel Phase 3 | P3 | Semaines 9–12 |
| 44–47 | Intelligence Phase 4 | P4 | Mois 3–4 |

---

## Stack décisions à confirmer

| Décision | Option A | Option B | Recommandation |
|---|---|---|---|
| Toast library | `sonner` (déjà shadcn) | `react-hot-toast` | **sonner** — déjà dans le projet |
| PDF viewer | `react-pdf` | iframe + signed URL | **iframe** — zéro dépendance |
| Charts CFO | `recharts` | `tremor` | **recharts** — plus flexible |
| Notifs in-app | polling | Supabase Realtime | **Realtime** — déjà en stack |
| Email templates | HTML string | React Email | **React Email** — maintenable |

---

## Ce qui est hors scope (pour l'instant)

- App mobile partenaire + client (Expo) — hors focus web démo
- Multi-refinanceur (sélection du meilleur taux entre plusieurs financeurs)
- Scoring ML (règle-based pour MVP, ML en Phase 4+)
- Marketplace fournisseurs
- Gestion résiduelle / rachat anticipé
- API publique pour intégrations partenaires

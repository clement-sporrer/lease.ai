# lease.ai — Phases de build

> Document de référence pour suivre la progression du MVP.  
> Mis à jour au fil des sessions.

---

## Phase 1 — Scaffold & Auth ✅

**Objectif :** Poser l'infrastructure de base. Tout le monde peut se connecter et être redirigé vers le bon espace.

**Livraisons :**
- Monorepo initialisé (`mobile/`, `web/`, `backend/`)
- FastAPI avec config, SQLAlchemy async, Supabase Auth (JWKS ES256)
- Middleware `verify_token` + extraction `active_role` depuis JWT
- `GET /me` + `POST /me/active-role`
- Mobile : Expo Router + login screen + redirection par rôle
- Web : Next.js App Router + shells `/admin`, `/ops`, `/financier`, `/cfo`
- Supabase : tables `organizations`, `profiles`, `user_roles`

---

## Phase 2 — Schema core + Dashboard shells ✅

**Objectif :** Avoir les entités métier principales en base et un dashboard fonctionnel pour chaque rôle.

**Livraisons :**
- 5 tables Supabase : `organizations`, `profiles`, `user_roles`, `companies`, `deals`
- Auth router complet : login Supabase proxy, set_active_role Admin API
- Mobile : flux auth complet (signInWithPassword → SecureStore/localStorage → Zustand → redirect rôle)
- Mobile : Partner dashboard SCR-PARTNER-001 (KPI cards, pipeline) + Client dashboard SCR-CLIENT-002
- Web : DashboardShell + Sidebar + StatCard pour admin/ops/financier/cfo
- Bug fixes : expo-secure-store web crash, SSR localStorage guard, trailing slashes typed routes
- 38 tests backend, 0 erreurs tsc mobile + web

---

## Phase 3 — Deal creation flow 🔄 (en cours)

**Objectif :** Un partenaire peut créer un dossier complet depuis l'app mobile : SIREN → enrichissement entreprise → devis → mensualité indicative → soumission.

**Status transitions couvertes :** `draft → company_enriched → quote_added → indicative_offer_ready → submitted`

**Backend :**
- Migration `002` : tables `quotes`, `quote_items`, `documents`, `risk_assessments`, `pricing_proposals`
- Routers : `/deals` (CRUD + submit), `/companies` (enrich mock), `/pricing` (indicatif), `/deals/{id}/quotes`, `/deals/{id}/documents`, `/deals/{id}/risk`
- Services : `DealService` (transitions), `EnrichmentService` (mock Pappers), `PricingService` (annuité financière), `RiskService` (rule-based score 0–100)
- Normalisation API : envelope `{"data": ...}`, erreurs `{"error": {"code": ...}}`

**Mobile :**
- SCR-PARTNER-003 : formulaire SIREN/SIRET avec validation Zod
- SCR-PARTNER-004 : confirmation enrichissement entreprise + alertes (société récente, inactive)
- SCR-PARTNER-005 : upload devis PDF → Supabase Storage (signed URL) → extraction mock
- SCR-PARTNER-006 : mensualité indicative + risk band + soumission
- `useDealCreationStore` Zustand pour persister l'état entre les écrans

---

## Phase 4 — Revue interne + documents

**Objectif :** L'équipe ADV/risk peut recevoir un dossier soumis, vérifier les pièces et prendre une décision.

**Status transitions :** `submitted → internal_review → [missing_documents | pre_approved | financier_rejected]`

**Backend :**
- Router `/admin` : queue ADV, pre-approve, reject, request-document
- Router `/deals/{id}/documents` : validate, reject
- Audit events sur chaque action sensible

**Web back-office :**
- SCR-ADMIN-003 : deal review (statut, entreprise, devis, score, docs, timeline, checklist, actions)
- Dashboard admin : queue de dossiers à traiter

---

## Phase 5 — Package refinanceur + décision financeur

**Objectif :** Générer le dossier de refi, l'envoyer au financeur, récupérer sa décision.

**Status transitions :** `pre_approved → refi_package_ready → refi_review → [financier_approved | financier_rejected]`

**Backend :**
- Router `/refi-packages` : génération PDF/ZIP, envoi, décision
- `RefiPackageService` : assemblage du dossier

**Web back-office :**
- Espace financeur : liste packages reçus, décision approve/reject/clarification

---

## Phase 6 — Offre ferme + contrat + signature

**Objectif :** Générer l'offre ferme, le contrat, et simuler la signature.

**Status transitions :** `financier_approved → firm_offer_generated → contract_generated → signing → signed`

**Backend :**
- Routers `/offers`, `/contracts`
- Mock signature (`POST /contracts/{id}/mock-sign`)
- Génération PDF offre + contrat

**Mobile :**
- Partenaire reçoit l'offre ferme et peut la transmettre au client

---

## Phase 7 — Activation

**Objectif :** Activer le contrat après conformité minimale vérifiée.

**Status transitions :** `signed → activation_pending → active`

**Backend :**
- `GET /contracts/{id}/activation-checklist`
- `POST /contracts/{id}/activate`
- Checklist : accord financeur, offre ferme, contrat signé, mandat SEPA simulé, PV livraison, actif créé, échéancier généré

**Web back-office :**
- SCR-ADMIN-011 : activation checklist avec blockers explicites

---

## Phase 8 — Actif + échéancier + paiements

**Objectif :** Gérer le cycle de vie du contrat actif côté client et CFO.

**Backend :**
- Routers `/assets`, `/schedule`, `/invoices`, `/payments`
- Génération échéancier, facturation, marquage paiements

**Mobile (client) :**
- SCR-CLIENT-002 enrichi : actifs, prochain paiement, documents, health score

**Web (CFO) :**
- SCR-CFO-001 : portfolio dashboard (production, commitment, cash, retards, rejets, renouvellements)

---

## Phase 9 — AI assistant contextuel

**Objectif :** Répondre à des questions contextuelles sur un dossier ou un contrat, sans décision autonome.

**Backend :**
- `POST /ai/assistant/query`
- `POST /ai/deals/{id}/summary`
- `POST /ai/documents/{id}/extract` (vraie extraction OCR)

**Mobile + Web :**
- SCR-SHARED-002 : assistant flottant sur les écrans deal/contract

---

## Récapitulatif

| Phase | Scope | Status |
|---|---|---|
| 1 | Scaffold, auth, roles, shells | ✅ Done |
| 2 | Schema core, auth flow, dashboards | ✅ Done |
| 3 | Deal creation (SIREN → submit) | 🔄 En cours |
| 4 | Revue interne ADV/risk | ⬜ À faire |
| 5 | Package refi + décision financeur | ⬜ À faire |
| 6 | Offre ferme + contrat + signature | ⬜ À faire |
| 7 | Activation | ⬜ À faire |
| 8 | Actif + échéancier + paiements | ⬜ À faire |
| 9 | AI assistant | ⬜ À faire |

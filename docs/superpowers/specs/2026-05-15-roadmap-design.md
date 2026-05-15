# LeaseAI — Roadmap & Design Spec
**Date :** 2026-05-15
**Auteur :** Clément Sporrer + Claude
**Statut :** Approuvé pour implémentation

---

## Contexte & objectif

LeaseAI est la plateforme opérationnelle d'une société de financement IT leasing **AI-native**. Ce n'est pas un simple outil de gestion — c'est le système d'exploitation de la boite. Chaque intégration est un nerf du système, pas un plugin.

**Objectif à court terme :** être démo-ready en 2–4 semaines pour une présentation à des experts secteur (revendeurs IT, établissements financiers, opérateurs leasing, dirigeants). La démo est guidée (on drive l'écran). Le message central : *"C'est complet — tout le cycle en un seul outil, aucun angle mort."*

**Principe directeur :** Backend-first, données réelles. Pas de décor. Les boutons écrivent en base, les statuts voyagent entre les rôles, les vues lisent de la vraie donnée.

---

## Architecture cible

```
Supabase (Auth JWT ES256 + Postgres + Storage)
       │
       ▼
FastAPI (Railway) ── services métier ── intégrations externes
       │
       ├── Web back-office (Vercel / Next.js 16)
       │     admin · ops · risk · financier · cfo
       │
       └── Mobile (Expo EAS) — hors scope démo
```

**Règle d'or :** tout ce qui est logique métier vit dans les services FastAPI. La web app est affichage + actions. Aucune décision dans les composants React.

---

## Carte des intégrations

### Tier 1 — Critique (Phase 1, semaines 1–4)

| Intégration | Usage | Justification |
|---|---|---|
| **Pappers API** | Enrichissement SIREN réel | Remplace le mock, données officielles |
| **Mistral API** | OCR + extraction structurée des devis PDF | Moins cher que OpenAI, souveraineté européenne — critique pour données financières sensibles |
| **Supabase Storage** | Upload documents, signed URLs | Déjà partiellement intégré |

### Tier 2 — Démo-impactant (Phase 2, semaines 5–8)

| Intégration | Usage | Justification |
|---|---|---|
| **Yousign** | E-signature réelle sur contrats | Rend le cycle complet, souverain EU |
| **Attio CRM** | Deal créé → contact/deal Attio auto-sync | La boite a une vue CRM sans double saisie |
| **Resend** | Emails transactionnels (offre, contrat, relance) | Pro, délivrabilité, templates HTML |
| **Claude API** | Résumé risque narratif, AI assistant contextuel | Raisonnement de haut niveau, pas OCR |

### Tier 3 — Opérationnel (Phase 3, semaines 9–12)

| Intégration | Usage | Justification |
|---|---|---|
| **Qonto** | Relevés bancaires + réconciliation paiements | Loyers reçus confirmés automatiquement |
| **Pennylane** | Sync comptabilité (écritures automatiques) | La CFO n'a pas à ressaisir |
| **Google Workspace** | Drive (documents partagés), Gmail (envois) | Interopérabilité avec l'écosystème client |

### Tier 4 — Intelligence ambiante (Phase 4, mois 3–4)

| Intégration | Usage | Justification |
|---|---|---|
| **Granola** | Notes de réunion → brouillon de dossier | C'est comme ça qu'une boite AI-native commence un deal |
| **Cal.com** | Scheduling ops/client lié à un dossier | RDV traçable dans le cycle |
| **OpenAI / Mistral fine-tuné** | Fallback LLM + A/B extraction docs | Résilience + optimisation continue |

---

## Principe d'intégration (test-first)

Chaque intégration suit ce protocole avant de passer en production :

1. **Mock stable défini** — contrat d'interface codifié, les tests unitaires s'appuient dessus
2. **Test d'intégration isolé** — script qui appelle l'API réelle en sandbox, CI séparé (ne bloque pas le pipeline principal)
3. **Feature flag** — env var `USE_REAL_<SERVICE>=true/false`, bascule en 30 secondes sans redéploiement
4. **Monitoring actif** — chaque appel externe loggé (latence, statut, erreur), alerte si taux d'erreur > 5% ou p95 > 3s

---

## Phases de développement

### Phase 1 — Premier étage + IA réelle (semaines 1–4)
**Livrable :** démo experts opérationnelle, backend-first, données réelles

#### Semaine 1 — Backend refi + financier
- Modèles SQLAlchemy : `RefiPackage`, `FinancierDecision`, `Offer`
  - `Offer` doit supporter nativement le versioning : champs `version: int` (incrémental) + `is_active: bool`. Générer une V2 ne touche pas la V1 — on désactive l'ancienne, on crée la nouvelle. Critique en leasing où le broker demande souvent un ajustement de loyer post-offre.
- Migrations Alembic
- Endpoints :
  - `POST /deals/{id}/refi-packages` — crée et associe le package
  - `POST /refi-packages/{id}/send` — passe le deal en `refi_package_ready`
  - `POST /refi-packages/{id}/decision` — approve (→ `financier_approved`) ou reject (→ `financier_rejected`)
  - `POST /deals/{id}/offers` — génère l'offre ferme (→ `firm_offer_generated`) ; si une offre active existe déjà, la désactive et crée version+1
- Tests unitaires sur chaque service (transitions validées, versioning offre inclus)

#### Semaine 2 — Web admin polish + refi
- Admin deal detail — polish complet (typography, spacing, status badge, timeline)
- Bouton "Générer package refi" → appel API réel → statut change en base
- Vue package refi (récapitulatif assets, risk score, pricing)
- Timeline enrichie avec chaque transition

#### Semaine 3 — Web financier
- Financier queue : liste des packages reçus, triés par date, avec statut
- Financier deal view : assets, risk band, pricing, documents
- Bouton "Approuver" / "Refuser" (avec champ motif si refus) → API réelle
- Statut mis à jour visible immédiatement pour l'admin

#### Semaine 4 — Web CFO + intégrations critiques + polish
- CFO dashboard sur vraies données (encours, loyers mois, taux défaut, distribution risque)
- **Pappers API** branché sur enrichissement SIREN (avec fallback mock si timeout)
- **Mistral API** branché sur extraction devis PDF (champs structurés : items, montants, fournisseur)
- **Badges de provenance** sur toutes les données enrichies : badge "Source : Pappers" sur les champs company enrichis, badge "Extrait par Mistral" sur chaque line-item du devis. Stocké en base (`enrichment_source`, `extraction_source`) — pas affiché depuis une constante. Les experts secteur font confiance aux données quand ils savent d'où elles viennent.
- Seed data réaliste : 3 dossiers à stades différents (draft, refi_package_ready, financier_approved)
- Répétition du script démo (10 min chrono)

**Checkpoint démo :** Admin "Approuver" → tab Financier → package visible → "Approuver" → tab Admin → statut `financier_approved` → "Générer offre" → tab CFO → deal dans le pipeline. Tout en base réelle.

---

### Phase 2 — Cycle complet + CRM (semaines 5–8)
**Livrable :** de la création à l'activation, tout est connecté

- Backend : `Contract`, `Asset`, `Signature` (SQLAlchemy + migrations)
- Endpoints contrat + activation
- **Yousign** — e-signature réelle (webhook confirmation → statut `signed`)
- **Attio CRM** — deal créé → contact + deal Attio, sync statuts clés
- **Resend** — email offre ferme, email contrat à signer, relance document manquant
- **Claude API** — résumé risque narratif dans la sidebar admin (1 paragraphe généré)
- Web : vue contrat, ops activation checklist, asset créé visible

---

### Phase 3 — Opérationnel réel (semaines 9–12)
**Livrable :** la boite tourne sur l'outil

- Backend : `PaymentSchedule`, `Invoice`, `Payment`
- Génération échéancier à l'activation
- **Qonto** — webhook paiement reçu → `Invoice` marquée payée automatiquement
- **Pennylane** — écriture comptable générée à chaque facture émise
- **Google Workspace** — documents partagés via Drive, emails via Gmail API
- Web : vue échéancier + factures, retards + alertes, CFO cash dashboard

---

### Phase 4 — Intelligence ambiante (mois 3–4)
**Livrable :** le produit pense avec vous

- Agent AI contextuel (Claude) avec RAG sur historique dossiers
- Suggestions de décision (risk, pricing outliers, documents manquants)
- Détection anomalies paiement
- **Granola** — notes de réunion → brouillon de dossier (draft deal pré-rempli)
- **Cal.com** — RDV planifié depuis la fiche deal, visible dans le timeline
- **OpenAI / Mistral fine-tuné** — A/B extraction docs, fallback LLM
- Sidebar AI dans chaque vue rôle (contexte deal actif)

---

## Script démo (10 minutes)

| Étape | Rôle | Action | Ce que l'expert voit |
|---|---|---|---|
| 1 | Admin | Ouvre la queue | Liste des dossiers avec statuts, risk bands, priorités |
| 2 | Admin | Ouvre Globex Inc. | Fiche company (badge "Source : Pappers"), risk score A, documents validés |
| 2b | Admin | Drag-and-drop PDF devis en direct | Mistral extrait les items (désignations, quantités, montants) en < 5s — badge "Extrait par Mistral" apparaît sur chaque ligne. Zéro saisie visible. |
| 3 | Admin | Clique "Pré-approuver" | Statut passe à `pre_approved`, timeline s'enrichit |
| 4 | Admin | Clique "Générer package refi" | Package créé, deal passe à `refi_package_ready` |
| 5 | Financier | Ouvre sa queue | Le package Globex apparaît, avec assets, risk, pricing |
| 6 | Financier | Clique "Approuver" | Deal passe à `financier_approved` — en base, en temps réel |
| 7 | Admin | Retour sur le dossier | Statut mis à jour, bouton "Générer offre ferme" disponible |
| 8 | Admin | Génère l'offre | Offre ferme créée, deal passe à `firm_offer_generated` |
| 9 | CFO | Ouvre le dashboard | Pipeline actif, deal Globex visible, encours mis à jour |

**Durée totale :** 8–10 minutes. L'upload devis en direct est le moment "Wahou" — il prouve que l'IA travaille en live, pas sur du hardcodé. Chaque action change la base.

---

## Ce qui est hors scope démo (mais sur les plans)

- Contrat + e-signature (Phase 2)
- Activation + actifs (Phase 2)
- Billing + paiements (Phase 3)
- Mobile (partner + client) — hors focus web
- AI assistant sidebar (Phase 4)
- Multi-refinanceur (après Phase 2)

---

## Conventions techniques

- **Argent :** toujours en centimes, jamais en float (`amount_cents: int`)
- **Statuts :** snake_case, machine-readable, jamais de string libre
- **Intégrations externes :** toujours via une classe service dédiée, jamais d'appel HTTP dans un router
- **Feature flags :** `USE_REAL_PAPPERS`, `USE_REAL_MISTRAL` dans `.env` — défaut `false` en test
- **Tests d'intégration :** dans `tests/integration/`, marqués `@pytest.mark.integration`, exclus du CI principal
- **Monitoring :** chaque appel externe wrappé avec log structuré (service, latency_ms, status_code, error)

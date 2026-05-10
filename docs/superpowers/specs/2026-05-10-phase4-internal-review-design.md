# Phase 4 — Revue interne : Design Spec

> Date: 2026-05-10  
> Scope: submitted → internal_review → [missing_documents | pre_approved | financier_rejected]  
> Approche retenue: Backend-first, UI fonctionnelle

---

## 1. Status transitions

```
submitted          → internal_review      POST /admin/deals/{id}/start-review
internal_review    → missing_documents    POST /admin/deals/{id}/request-document
internal_review    → pre_approved         POST /admin/deals/{id}/pre-approve
internal_review    → financier_rejected   POST /admin/deals/{id}/reject
missing_documents  → internal_review      automatique au prochain upload partenaire
```

**Règles métier :**
- `reject` : champ `reason` obligatoire (422 si absent)
- `pre-approve` : `justification` optionnel (pas de hard block sur les docs)
- Seuls `ops_user` et `admin_user` peuvent déclencher les transitions en écriture
- `risk_user` accède en lecture à tout le dossier

---

## 2. Base de données

### Migration 003 — table `audit_events`

```sql
CREATE TABLE audit_events (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deal_id     UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  actor_id    UUID NOT NULL REFERENCES profiles(id),
  actor_role  TEXT NOT NULL,
  action      TEXT NOT NULL,  -- enum ci-dessous
  payload     JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_events_deal_id ON audit_events(deal_id);
CREATE INDEX idx_audit_events_created_at ON audit_events(created_at);
```

**Actions auditées :**
- `status_transition` — payload: `{from, to}`
- `document_validated` — payload: `{document_id, document_type}`
- `document_rejected` — payload: `{document_id, document_type, reason}`
- `pre_approved` — payload: `{justification?}`
- `deal_rejected` — payload: `{reason}`
- `document_requested` — payload: `{document_type, reason}`

---

## 3. Backend

### Services

**`AuditService`** (`app/services/audit_service.py`)
- `async def log(db, deal_id, actor_id, actor_role, action, payload=None)`
- Appelé par tous les services qui déclenchent des actions sensibles

**`AdminService`** (`app/services/admin_service.py`)
- `get_queue(db)` → deals en statut `submitted` ou `internal_review`, triés par date
- `get_checklist(db, deal_id)` → agrège état docs, risk score, pricing
- `start_review(db, deal_id, actor)` → `submitted → internal_review` + audit
- `request_document(db, deal_id, actor, document_type, reason)` → `internal_review → missing_documents` + audit
- `pre_approve(db, deal_id, actor, justification=None)` → `internal_review → pre_approved` + audit
- `reject(db, deal_id, actor, reason)` → `internal_review → financier_rejected` + audit (reason obligatoire)

**`DocumentService`** (extension)
- `validate_document(db, document_id, actor)` → statut doc → `validated` + audit
- `reject_document(db, document_id, actor, reason)` → statut doc → `rejected` + audit

### Routers

**`/admin`** (`app/routers/admin.py`)
```
GET  /admin/queue                         → ops + admin + risk (lecture)
GET  /admin/deals/{deal_id}/checklist     → ops + admin + risk (lecture)
POST /admin/deals/{deal_id}/start-review  → ops + admin seulement
POST /admin/deals/{deal_id}/request-document   → ops + admin seulement
POST /admin/deals/{deal_id}/pre-approve   → ops + admin seulement
POST /admin/deals/{deal_id}/reject        → ops + admin seulement
```

**`/documents`** (extension de `app/routers/documents.py`)
```
POST /documents/{document_id}/validate    → ops + admin seulement
POST /documents/{document_id}/reject      → ops + admin seulement
```

**`/deals/{id}/timeline`** (implémenté maintenant)
```
GET /deals/{deal_id}/timeline             → audit_events triés DESC, tous rôles internes
```

### Schemas Pydantic

```python
# Requêtes
class StartReviewRequest(BaseModel): pass  # body vide

class RequestDocumentRequest(BaseModel):
    document_type: str
    reason: str

class PreApproveRequest(BaseModel):
    justification: str | None = None

class RejectRequest(BaseModel):
    reason: str  # obligatoire

class ValidateDocumentRequest(BaseModel): pass

class RejectDocumentRequest(BaseModel):
    reason: str

# Réponse checklist
class DealChecklistResponse(BaseModel):
    deal_id: str
    status: str
    documents: list[DocumentStatus]
    risk_score: int | None
    risk_band: str | None
    pricing_monthly: float | None
    all_docs_validated: bool
```

### Codes d'erreur

| Code | HTTP | Description |
|---|---|---|
| `INVALID_TRANSITION` | 409 | Transition non autorisée depuis statut actuel |
| `JUSTIFICATION_REQUIRED` | 422 | Reject sans reason |
| `INSUFFICIENT_ROLE` | 403 | Action réservée ops/admin tentée par risk |
| `DOCUMENT_NOT_FOUND` | 404 | Document inexistant |
| `DEAL_NOT_IN_REVIEW` | 409 | Action admin sur deal pas en internal_review |

---

## 4. Web back-office

### Structure fichiers

```
web/app/(admin)/
  page.tsx                          → queue listing
  deals/[id]/page.tsx               → SCR-ADMIN-003 deal review
  deals/[id]/loading.tsx            → skeleton

web/src/
  components/admin/
    DealQueue.tsx                   → table filtrable (statut, date, score band)
    DealReviewHeader.tsx            → statut badge + deal ID + date + partner
    CompanySummary.tsx              → enrichissement entreprise
    QuoteSummary.tsx                → montant, durée, mensualité
    RiskSummary.tsx                 → score + band + facteurs
    DocumentList.tsx                → docs avec validate/reject (ops+admin only)
    AuditTimeline.tsx               → events chronologiques
    ActionPanel.tsx                 → 3 boutons d'action + modales
  services/admin.ts                 → appels API /admin/*
  services/documents.ts             → validate / reject
  hooks/useAdminQueue.ts            → TanStack Query
  hooks/useDealReview.ts            → deal + checklist + docs + timeline
  types/admin.ts
```

### SCR-ADMIN-003 — Sections

1. **Header** — badge statut coloré, deal ID, date soumission, nom partenaire, organisation
2. **Entreprise** — nom, SIREN, secteur, date création, alertes enrichissement (société récente, inactive)
3. **Devis** — montant total, durée, taux, mensualité indicative calculée
4. **Score** — band (Low/Medium/High/Very High), score brut /100, facteurs contributeurs
5. **Documents** — liste avec statut badge (pending/validated/rejected), boutons validate/reject per doc (ops+admin only)
6. **Timeline** — audit events chronologiques (qui a fait quoi, quand)
7. **Action panel** (fixe en bas) — 3 boutons :
   - "Demander pièce" → modale: type de pièce + raison
   - "Pré-accorder" → modale: justification optionnelle + confirmation
   - "Refuser" → modale: raison obligatoire + confirmation

### Permissions UI

- `risk_user` : voit toutes les sections, boutons d'action absents du DOM
- `ops_user` + `admin_user` : accès complet avec boutons d'action

---

## 5. Tests

### Backend (~25 nouveaux tests)

- `test_admin_router.py`
  - Queue retourne bons statuts
  - start-review : submitted → internal_review
  - start-review : deal en draft → 409 INVALID_TRANSITION
  - request-document : → missing_documents + audit créé
  - pre-approve : → pre_approved, justification optionnelle
  - reject : sans reason → 422 JUSTIFICATION_REQUIRED
  - reject : → financier_rejected + audit créé
  - risk_user sur POST → 403 INSUFFICIENT_ROLE

- `test_audit_service.py`
  - Log créé sur chaque action sensible
  - Timeline retourne events triés DESC

- `test_admin_service.py`
  - Transitions valides et invalides
  - Justification obligatoire sur reject

- `test_documents_router.py` (extension)
  - validate : ops → 200, risk → 403
  - reject : sans reason → 422
  - reject : ops → doc statut rejected + audit

### Web

Pas de test suite établie dans le projet — on n'en ajoute pas.

---

## 6. Décisions clés

| Décision | Choix | Raison |
|---|---|---|
| Hard block pre-approve | Non | Override avec justification optionnelle — ops/admin responsables |
| Doc validate/reject | ops + admin seulement | risk = lecture seule sur les actions |
| Audit storage | Table `audit_events` Supabase | Timeline dans l'UI, queryable |
| Push notifs mobile | Non MVP | Poll TanStack Query suffit |
| missing_documents → internal_review | Auto au prochain upload | Simplifie le flow partenaire |

---

## 7. Hors scope Phase 4

- Refi package (Phase 5)
- Notifications push Expo
- Assignation individuelle d'un dossier à un ops
- SLA / deadline sur la revue

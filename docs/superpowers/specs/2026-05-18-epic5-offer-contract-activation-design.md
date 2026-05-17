# Epic 5 — Offer, Contract, Activation

**Date:** 2026-05-18  
**Scope:** lease.ai web back-office + FastAPI backend  
**Branch:** feat/phase1-web  
**Status transitions covered:** `firm_offer_generated → contract_generated → signing → signed → activation_pending → active`

---

## Context

The financier has approved the deal. An active offer exists. Epic 5 closes the loop: generate a contract, collect a mock signature, run a blocking activation checklist, then activate — creating assets and a payment schedule automatically from the quote data.

No new DB migration needed. Tables `contracts`, `assets`, `payment_schedules` already exist in schema.

---

## Backend

### New files
- `backend/app/routers/contracts.py`
- `backend/app/services/contract_service.py`
- `backend/app/schemas/contract.py`

### Endpoints

| Method | Path | Transition | Role |
|--------|------|------------|------|
| POST | `/deals/{deal_id}/contracts` | `firm_offer_generated → contract_generated` | admin, ops |
| POST | `/contracts/{contract_id}/send-signature` | `contract_generated → signing` | admin, ops |
| POST | `/contracts/{contract_id}/mock-sign` | `signing → signed` | admin, ops |
| GET | `/contracts/{contract_id}/activation-checklist` | — | admin, ops, risk |
| POST | `/contracts/{contract_id}/activate` | `signed → activation_pending → active` | admin, ops |

### ContractService methods

**`generate_contract(db, deal_id, actor_id, actor_role)`**
- Idempotent: if a contract already exists for this deal, return it (no error, no duplicate)
- Creates `contracts` row with `status = draft`, `public_id` generated
- Transitions deal to `contract_generated`
- Writes audit event `CONTRACT_GENERATED`

**`send_signature(db, contract_id, actor_id, actor_role)`**
- Sets `contracts.sent_at = now()`
- Transitions deal to `signing`
- Audit event `CONTRACT_SENT_FOR_SIGNATURE`

**`mock_sign(db, contract_id, actor_id, actor_role)`**
- Sets `contracts.signed_at = now()`, `contracts.status = signed`
- Transitions deal to `signed`
- Audit event `CONTRACT_SIGNED`

**`activation_checklist(db, contract_id)`**
Returns list of 6 conditions, each `{ key, label, satisfied: bool }`:

1. `contract_generated` — contract row exists
2. `contract_sent` — `sent_at IS NOT NULL`
3. `contract_signed` — `signed_at IS NOT NULL`
4. `financier_decision_received` — `financier_decisions` row with `decision = approved` exists for this deal
5. `active_offer_present` — active offer exists for this deal
6. `quote_validated` — at least one document with `type = quote` and `status = validated` exists for this deal

**`activate(db, contract_id, actor_id, actor_role)`**
- Calls `activation_checklist()` — if any condition is `satisfied = False`, raises `AppError(400, "ACTIVATION_BLOCKED", ..., details={"failed_conditions": [...]})`
- Creates `Asset` rows from `quote_items` of the active quote: `name`, `category`, `unit_value_cents`, `quantity` copied directly
- Generates `payment_schedules`: `duration_months` rows, `due_date = activation_date + n months`, `amount_cents = monthly_payment_cents` from active `pricing_proposal`
- Sets `contracts.activated_at = now()`, `contracts.status = active`
- Transitions deal to `activation_pending` then `active` (two sequential transitions per state machine)
- Audit event `CONTRACT_ACTIVATED`

### Error handling
- Unauthorized transition → existing `AppError` pattern from `transitions.py`
- `ACTIVATION_BLOCKED` → 400 with `details.failed_conditions` list
- Missing pricing proposal at activation → `AppError(409, "PRICING_PROPOSAL_MISSING", ...)`

### Schema (Pydantic)

```python
class ContractResponse(BaseModel):
    id: UUID
    deal_id: UUID
    public_id: str
    status: str
    sent_at: datetime | None
    signed_at: datetime | None
    activated_at: datetime | None
    total_commitment_cents: int | None
    created_at: datetime

class ActivationChecklistItem(BaseModel):
    key: str
    label: str
    satisfied: bool

class ActivationChecklistResponse(BaseModel):
    items: list[ActivationChecklistItem]
    all_satisfied: bool
```

---

## Web

### New components
- `web/src/components/admin/ContractPanel.tsx`
- `web/src/components/admin/ActivationChecklist.tsx`

### New server actions
- `web/app/actions/contracts.ts`: `generateContract`, `sendSignature`, `mockSign`, `activateContract`

### ContractPanel

Visible when `deal.status` is in `['firm_offer_generated', 'contract_generated', 'signing', 'signed', 'activation_pending', 'active']`.

States it renders:

| Deal status | What shows |
|-------------|------------|
| `firm_offer_generated` | Button "Générer le contrat" |
| `contract_generated` | Contract info (public_id, date) + Button "Envoyer pour signature" |
| `signing` | Contract info + Button "Simuler la signature" |
| `signed` and beyond | Contract info + "Signé le [date]" badge |

Each action: toast success/error + `revalidatePath`.

### ActivationChecklist

Visible when `deal.status` is in `['signed', 'activation_pending', 'active']`.

- Fetches `GET /contracts/{contract_id}/activation-checklist`
- Renders each condition as a row: green checkmark if satisfied, red X if not
- Button "Activer le contrat" — disabled if `all_satisfied = false`, with tooltip "X conditions manquantes"
- On success: toast "Contrat activé — dossier actif" 
- If `ACTIVATION_BLOCKED` error: display list of failed conditions inline (not just a toast)

### Integration in `deals/[id]/page.tsx`

- Add contract fetch to the initial `Promise.allSettled` block: `GET /deals/{id}/contracts/latest` (new endpoint returning most recent contract for a deal, or null)
- Pass `contract` prop to `ContractPanel` and `ActivationChecklist`
- Both components render conditionally based on `deal.status`

### New endpoint (addition to contracts router)
```
GET /deals/{deal_id}/contracts/latest   → returns most recent contract or null (200 with data: null)
```

---

## What is NOT built

- Real PDF contract generation (contract is a DB record only at MVP)
- Manual asset form (assets created automatically from quote lines)
- SEPA mock
- Client-facing contract view (Epic 6)
- Email notifications

---

## File list

**Backend (new)**
- `backend/app/routers/contracts.py`
- `backend/app/services/contract_service.py`
- `backend/app/schemas/contract.py`
- `backend/tests/test_contracts.py`

**Backend (modified)**
- `backend/main.py` — register contracts router

**Web (new)**
- `web/src/components/admin/ContractPanel.tsx`
- `web/src/components/admin/ActivationChecklist.tsx`
- `web/app/actions/contracts.ts`
- `web/src/lib/types/contract.ts`

**Web (modified)**
- `web/app/(admin)/admin/deals/[id]/page.tsx` — add contract fetch + render new panels

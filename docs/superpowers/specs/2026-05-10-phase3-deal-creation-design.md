# Phase 3 — Deal Creation Flow : Design Spec

**Date:** 2026-05-10  
**Branch:** feat/phase1-scaffold  
**Status:** Approved

---

## Scope

Full deal creation flow from partner mobile app: SIREN entry → company enrichment → quote upload → indicative pricing + risk score → deal submission.

**Status transitions covered:** `draft` → `company_enriched` → `quote_added` → `indicative_offer_ready` → `submitted`

**Out of scope:** real ML scoring, real Pappers API, real document OCR, admin review flow (Phase 4+).

---

## Backend

### Migrations (Alembic)

5 new tables added in a single migration `002_phase3_deal_creation.py`:

**`quotes`**
- `id`, `deal_id` (FK deals), `document_id` nullable (FK documents.id — source PDF du devis)
- `supplier_name`, `quote_number`
- `amount_excl_tax_cents`, `amount_incl_tax_cents`, `currency`
- `category`, `extraction_status` (pending/done/failed), `extraction_payload_json`
- `created_at`, `updated_at`

**`quote_items`**
- `id`, `quote_id` (FK quotes), `label`, `category`
- `quantity`, `unit_price_cents`, `total_price_cents`

**`documents`**
- `id`, `deal_id` (FK deals), `contract_id` (nullable), `organization_id` (nullable)
- `type`, `status` (required/uploaded/extracting/validated/rejected/missing/expired)
- `file_name`, `storage_key`, `mime_type`, `size_bytes`, `version`
- `uploaded_by_user_id`, `validated_by_user_id` (nullable)
- `created_at`

**`risk_assessments`**
- `id`, `deal_id` (FK deals)
- `score` (0–100), `band` (green/orange/red)
- `flags_json`, `rules_applied_json`, `recommendation`
- `created_by`, `version`, `created_at`

**`pricing_proposals`**
- `id`, `deal_id` (FK deals)
- `type` (indicative/firm)
- `amount_financed_cents`, `duration_months`, `monthly_payment_cents`
- `residual_value_cents`, `refi_rate`, `margin_rate`, `fees_cents`
- `assumptions_json`, `version`, `created_at`

### API — Normalized conventions

All responses use:
```json
{ "data": { ... } }
// or for lists:
{ "data": [...], "meta": { "total": 0, "page": 1, "per_page": 20 } }
```

All errors use:
```json
{ "error": { "code": "SNAKE_CASE_CODE", "message": "Human readable", "details": {} } }
```

HTTP status codes: 200 GET/PATCH success, 201 POST creation, 400 validation, 401 no auth, 403 wrong role, 404 not found, 409 conflict/invalid transition, 422 schema error.

### Routers

**`/deals`**
```
POST   /deals                          → create deal: accepts company_id, triggers draft → company_enriched
                                          idempotency: Idempotency-Key header (UUID from mobile),
                                          duplicate key within 24h returns existing deal (200, not 201)
GET    /deals                          → list deals (scoped to org, paginated)
GET    /deals/{deal_id}                → get deal detail
PATCH  /deals/{deal_id}                → update deal fields
POST   /deals/{deal_id}/submit         → transition: indicative_offer_ready → submitted
POST   /deals/{deal_id}/status         → explicit status transition (internal use)
GET    /deals/{deal_id}/timeline       → stub Phase 4-ready: returns [] in Phase 3, wired to audit_events in Phase 4
```

**`/companies`**
```
POST   /companies/enrich               → mock Pappers enrichment by SIREN/SIRET
GET    /companies/{company_id}         → get enriched company
```
Note: `POST /deals/{deal_id}/company` removed — deal creation and company linking are unified in `POST /deals` (single flow, no ambiguity).

**`/quotes`** (nested under deals)
```
POST   /deals/{deal_id}/quotes                    → create quote + trigger quote_added transition
GET    /deals/{deal_id}/quotes/{quote_id}          → get quote with items
PATCH  /deals/{deal_id}/quotes/{quote_id}          → update quote fields manually
POST   /deals/{deal_id}/quotes/{quote_id}/extract  → trigger mock extraction
```

**`/documents`** (nested under deals)
```
POST   /deals/{deal_id}/documents/upload-url       → generate signed Supabase Storage upload URL
POST   /deals/{deal_id}/documents/confirm          → confirm upload, save storage_key to DB
GET    /deals/{deal_id}/documents                  → list documents for deal
```

**`/pricing`**
```
POST   /pricing/indicative             → stateless compute, returns pricing_proposal without saving to DB
POST   /deals/{deal_id}/pricing/recalculate → saves pricing_proposal + triggers quote_added → indicative_offer_ready transition
GET    /deals/{deal_id}/pricing        → latest pricing_proposal for deal
```

**`/risk`** (nested under deals)
```
POST   /deals/{deal_id}/risk/assess    → run rule-based scoring, save risk_assessment
GET    /deals/{deal_id}/risk/latest    → latest risk_assessment for deal
```

### Services

**`PricingService`**

Financial annuity formula:
```python
r = (refi_rate + margin_rate) / 12
monthly_payment = amount * r / (1 - (1 + r) ** -duration_months)
monthly_payment += fees_cents / duration_months
```

Default assumptions: `refi_rate=0.045`, `margin_rate=0.025`, `fees_cents=50_000` (€500).  
Stored in `assumptions_json` for full traceability.

**`RiskService`** (rule-based, no ML)

Score starts at 75 (default band: green). Rules applied:
- Company age < 2 years → −30
- Amount > €100k → −10
- Sector risk (NAF code list) → −15
- Company inactive/radiation → −50

Band thresholds: `green` ≥ 60, `orange` 30–59, `red` < 30.  
Flags and rules stored in `flags_json` / `rules_applied_json` for audit.

**`EnrichmentService`** (mock Pappers)

SIREN → deterministic mock data based on SIREN hash. Always returns plausible data. `enrichment_source: "mock"`. Unknown SIREN → returns partial data with `active_status: unknown`, no blocking error.

**`DealService`**

Owns all status transitions. Validates against `allowedDealTransitions` map. Rejects invalid transitions with:
```json
{
  "error": {
    "code": "INVALID_TRANSITION",
    "message": "Cannot transition from quote_added to submitted",
    "details": {
      "current_status": "quote_added",
      "allowed_next": ["indicative_offer_ready", "cancelled"]
    }
  }
}
```

### Tests (pytest + respx + ASGI)

- `test_deals_router.py`: CRUD, submit flow, invalid transitions
- `test_companies_router.py`: enrich known/unknown SIREN, link to deal
- `test_pricing_service.py`: annuity formula with known values, edge cases
- `test_risk_service.py`: each rule independently + combinations

---

## Mobile

### Navigation structure

```
mobile/app/(partner)/deals/new/
  index.tsx        ← SCR-PARTNER-003 : SIREN form
  enrichment.tsx   ← SCR-PARTNER-004 : company confirmation
  quote.tsx        ← SCR-PARTNER-005 : quote upload
  offer.tsx        ← SCR-PARTNER-006 : indicative offer + submit
```

Deal created at SCR-004 confirm (`POST /deals` with `company_id` + `Idempotency-Key` header — UUID generated once and stored in the store). `deal_id` flows via Zustand `useDealCreationStore`. Back navigation never re-POSTs: `dealId` already set in store → uses existing deal.

### State

`useDealCreationStore` (Zustand):
```ts
{
  siren: string
  company: CompanyData | null
  dealId: string | null
  quoteId: string | null
  documentId: string | null
  pricingProposal: PricingProposal | null
  riskAssessment: RiskAssessment | null
  reset: () => void
}
```

TanStack Query hooks: `useEnrichCompany`, `useCreateDeal`, `useUploadQuote`, `useIndicativePricing`, `useAssessRisk`, `useSubmitDeal`.

### Screens

**SCR-PARTNER-003 — SIREN form**
- React Hook Form + Zod: SIREN (9 digits) or SIRET (14 digits), optional trade_name + contact
- Validation: numeric only, correct length
- On submit: `POST /companies/enrich` → navigate to enrichment.tsx with company data

**SCR-PARTNER-004 — Company enrichment**
- Display: legal_name, SIREN/SIRET, address, activity, creation date, active status
- Alerts: company < 2 years old, inactive status, missing data
- On confirm: `POST /deals` (creates draft, links company_id) → navigate to quote.tsx

**SCR-PARTNER-005 — Quote upload**
- Expo Document Picker: PDF or image
- Flow: `POST /deals/{id}/documents/upload-url` → upload to Supabase Storage → `POST confirm`
- `POST /deals/{id}/quotes/{id}/extract` → show mock extraction result
- Fields editable if extraction incorrect (supplier, amount HT/TTC, category)
- On continue: navigate to offer.tsx (pricing + risk called here)

**SCR-PARTNER-006 — Indicative offer**
- On screen entry: `POST /pricing/indicative` (stateless preview) + `POST /deals/{id}/risk/assess` in parallel
- On submit: `POST /deals/{id}/pricing/recalculate` (saves + triggers indicative_offer_ready) then `POST /deals/{id}/submit`
- Display: amount financed, duration, monthly payment, rate, assumptions
- Risk band badge: green/orange/red with short explanation
- Disclaimer: "Offre indicative, sous réserve d'analyse du dossier et validation par un partenaire financeur."
- CTA `Soumettre le dossier`: `POST /deals/{id}/submit` → redirect to partner dashboard + success toast
- Store reset on success

### Upload flow (document)

```
mobile → POST /deals/{id}/documents/upload-url
backend → returns { upload_url, document_id, expires_in }
mobile → PUT {upload_url} with file binary (direct to Supabase Storage)
mobile → POST /deals/{id}/documents/confirm { document_id, storage_key, file_name, mime_type, size_bytes }
backend → saves record, returns document
```

### Error handling

- Invalid transition → toast "Étape manquante" + block CTA
- Upload URL expired → auto-retry get new URL (max 1 retry)
- Enrichment partial data → warn banner, not blocking
- Offline → TanStack Query retry: 2, toast on final failure
- Back navigation → deal already created, PATCH to update (no new POST)

---

## Checklist

- [ ] All 5 tables migrated + alembic_version stamped to 002
- [ ] All API responses follow normalized envelope format
- [ ] DealService enforces all status transitions
- [ ] PricingService formula unit tested with known values
- [ ] RiskService rules unit tested independently
- [ ] Mobile: useDealCreationStore resets on successful submission
- [ ] POST /deals is idempotent via Idempotency-Key header (duplicate within 24h returns existing deal)
- [ ] Mobile: useDealCreationStore generates idempotency key once per wizard session, never re-POSTs if dealId already set
- [ ] Documents upload via signed URL (never proxied through backend)
- [ ] No storage_key exposed in any API response to frontend

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Before implementing anything

Read the relevant source-of-truth docs in `.claude/docs/` before touching code:

| What you're building | Doc to read first |
|---|---|
| A screen or flow | `product/screen_specs.md`, `product/navigation_map.md` |
| Data entities or DB schema | `backend/data_model.md` |
| Status transitions | `backend/status_machine.md` |
| API endpoint | `api/endpoints.md`, `api/errors.md` |
| UI component | `design/component_library.md`, `design/design_tokens.md` |
| Permissions / access control | `product/permissions_matrix.md` |
| AI assistant feature | `agents/agent_architecture.md`, `agents/decision_boundaries.md` |

Condensed context for the whole project: `.claude/docs/01_AI_DEVELOPMENT_CONTEXT.md` — start here on every new session.

---

## Architecture

```
lease.ai/                     # monorepo
├── mobile/                   # Expo React Native — partner_user, client_user
├── web/                      # Next.js App Router — admin, ops, risk, financier, cfo
└── backend/                  # FastAPI — single API for both frontends

Deploy:
  mobile  → Expo EAS (TestFlight / Play Console)
  web     → Vercel
  backend → Railway
  db+auth → Supabase
```

**Role split by interface:**

| Interface | Roles |
|---|---|
| Mobile (Expo) | `partner_user`, `client_user` |
| Web back-office (Next.js) | `admin_user`, `ops_user`, `risk_user`, `financier_user`, `cfo_user` |

Both frontends call the same FastAPI. Supabase Auth issues the JWT — both frontends use the same token, FastAPI verifies it.

---

## Stack

**Mobile** (`mobile/`):
- Expo SDK 52 + Expo Router 4 (file-based navigation)
- TypeScript strict
- NativeWind (Tailwind for React Native)
- TanStack Query (server state)
- Zustand (client state)
- React Hook Form + Zod (forms + validation)
- `@supabase/supabase-js` (auth client)
- Expo SecureStore (token storage)

**Web back-office** (`web/`):
- Next.js 15 App Router
- TypeScript strict
- Tailwind CSS
- TanStack Query
- `@supabase/supabase-js` + `@supabase/ssr`
- shadcn/ui (component library)

**Backend** (`backend/`):
- FastAPI + Python 3.12
- Supabase Auth — JWT verified via `python-jose` (no auth logic built from scratch)
- SQLAlchemy 2.0 async + Alembic (ORM + migrations)
- Pydantic v2 (request/response schemas)
- FastAPI BackgroundTasks (async jobs for PDF, email, notifications)
- Supabase Storage (documents via signed URLs)

---

## Project structure

```
mobile/
  app/
    (auth)/login.tsx
    (role-switch)/index.tsx
    (partner)/
    (client)/
    shared/
  src/
    components/     # Design system components
    services/       # API call layer (axios/fetch wrappers)
    stores/         # Zustand stores
    hooks/          # TanStack Query hooks
    constants/      # Design tokens, status maps, routes
    types/          # Shared TypeScript types

web/
  app/
    (auth)/
    (admin)/
    (ops)/
    (financier)/
    (cfo)/
    api/            # Next.js API routes (proxies only — no business logic)
  src/
    components/
    hooks/
    services/
    types/

backend/
  app/
    routers/        # FastAPI route handlers — thin, no logic
    services/       # All business logic (DealService, PricingService, etc.)
    models/         # SQLAlchemy ORM models
    schemas/        # Pydantic request/response schemas
    core/           # config, auth middleware, db session, supabase client
    jobs/           # BackgroundTasks handlers
  alembic/          # Migrations
  main.py
```

---

## Auth — Supabase Auth

- Login handled by Supabase client SDK (mobile: `@supabase/supabase-js`, web: `@supabase/ssr`)
- Supabase now signs JWTs with **ECC P-256** (asymmetric). FastAPI must verify via JWKS, not a shared secret.
- JWKS endpoint: `https://conxwmnjhntbzftwgxig.supabase.co/auth/v1/.well-known/jwks.json`
- Algorithm: `ES256` (not HS256)
- On every FastAPI request: extract Bearer → fetch JWKS (cached) → verify with `python-jose[cryptography]` → extract `sub` (user_id) + `user_metadata.active_role`
- Active role stored in Supabase user metadata (`user_metadata.active_role`)
- Role switch: `POST /me/active-role` updates metadata via Supabase Admin API, client refreshes token

```python
# backend/app/core/auth.py — pattern à suivre
from jose import jwt
import httpx, functools

JWKS_URL = "https://conxwmnjhntbzftwgxig.supabase.co/auth/v1/.well-known/jwks.json"

@functools.lru_cache(maxsize=1)
def get_jwks(): ...  # fetch + cache, refresh toutes les heures

def verify_token(token: str) -> dict:
    keys = get_jwks()
    return jwt.decode(token, keys, algorithms=["ES256"], audience="authenticated")
```

---

## Architecture rules

- **API-first**: all business logic in FastAPI services. Both frontends are display + input only.
- **No decision logic in frontends**: status transitions, risk scores, pricing, permissions — all server-side.
- **Thin routers**: FastAPI routers validate input, call one service method, return response. Nothing else.
- **RBAC check order** on every protected endpoint: 1) authenticated, 2) active role, 3) organization scope, 4) entity permission, 5) action allowed for current status.
- **Audit everything sensitive**: login (admin+), document view/download, status change, decision, override, activation, payment marking.

---

## Deal lifecycle

```
draft → company_enriched → quote_added → indicative_offer_ready → submitted
  → internal_review → [missing_documents | pre_approved | financier_rejected]
  → refi_package_ready → refi_review → [financier_approved | financier_rejected]
  → firm_offer_generated → contract_generated → signing → signed
  → activation_pending → active
```

Backend rejects unauthorized transitions with: error code, current status, allowed next statuses, reason.

---

## Design tokens (never hardcode)

Colors: `navy.900` (#0D183D) · `blue.500` (#2563EB) · `teal.500` (#10B981) · `danger` (#EF4444) · `warning` (#F59E0B)

Typography: **Satoshi** for UI text · **IBM Plex Mono** for all numbers and financial data

Status badge colors defined in `statusColors` (`design/design_tokens.md`) — use on every status display.

---

## MVP build order

1. Auth + roles (Supabase Auth, role switch)
2. Dashboard shells per role (mobile + web)
3. Deal creation (partner mobile)
4. Company enrichment (SIREN / mock via Pappers)
5. Quote + document upload
6. Indicative pricing + risk score (rule-based, no ML)
7. Submission + internal review (admin web)
8. Refi package + financier decision (financier web)
9. Firm offer + contract + simulated signature
10. Activation
11. Assets, schedule, invoices, payments (client mobile)
12. Portfolio dashboard (CFO web)
13. AI assistant (contextual only, no autonomous decisions)

---

## What NOT to build at MVP

- Real ML scoring, real SEPA, real multi-refinancer automation
- AI making autonomous financial decisions
- Supplier marketplace, advanced residual value engine

---

## Key security rules

- Never expose `storage_key` in any frontend
- Mask IBAN partially in all UI
- Risk/pricing overrides require a justification field
- Documents (ID, RIB, SEPA, contracts): explicit permission check before generating signed URL
- No secrets in Next.js `NEXT_PUBLIC_*` vars except Supabase anon key and Stripe publishable key

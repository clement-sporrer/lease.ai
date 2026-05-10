# LeaseAI

AI-native IT leasing operator. Monorepo: mobile (Expo), web back-office (Next.js), backend (FastAPI), Supabase (auth + Postgres + storage).

End-to-end deal lifecycle: partner creates deal → SIREN enrichment → quote upload → indicative pricing → risk scoring → admin review → refi package → financier decision → firm offer → contract → signature → activation → schedule → invoice → payment → CFO portfolio.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│              Supabase (hosted)                          │
│   Auth (JWT ES256) · Postgres · Storage                │
└────────────────────────────────────────────────────────┘
       │ JWKS              │ DSN          │ signed URLs
       ▼                   ▼              ▼
┌──────────────┐       ┌─────────────────────────┐
│  mobile/     │       │      backend/           │
│  Expo SDK 54 │──────▶│      FastAPI            │
│  partner     │       │                         │
│  client      │       │  ┌─ DB-backed routers ─┐│
└──────────────┘       │  │ deals, companies,   ││
                       │  │ quotes, documents,  ││
┌──────────────┐       │  │ pricing, risk,      ││
│  web/        │──────▶│  │ admin, me, auth     ││
│  Next.js 16  │       │  └─────────────────────┘│
│  admin, ops, │       │  ┌─ Demo extras ───────┐│
│  financier,  │       │  │ refi, offers,       ││
│  cfo, risk   │       │  │ contracts, assets,  ││
└──────────────┘       │  │ billing, dashboards,││
                       │  │ ai, demo            ││
                       │  └─────────────────────┘│
                       └─────────────────────────┘
```

## Stack

| Surface | Stack |
|---|---|
| `mobile/` | Expo SDK 54 · Expo Router 6 · NativeWind · TanStack Query · Zustand · React Hook Form + Zod · `@supabase/supabase-js` |
| `web/` | Next.js 16 App Router · Tailwind · shadcn/ui · TanStack Query · `@supabase/ssr` |
| `backend/` | FastAPI · Python 3.12 · SQLAlchemy 2.0 async · Alembic · Pydantic v2 · `python-jose` · `httpx` |
| Infra | Supabase (auth + Postgres + storage) · Railway (backend deploy) · Vercel (web deploy) · Expo EAS (mobile deploy) |

## Roles

| Interface | Roles |
|---|---|
| Mobile | `partner`, `client` |
| Web back-office | `admin`, `ops`, `risk`, `financier`, `cfo` |

Both frontends share the same JWT issued by Supabase Auth. FastAPI verifies via JWKS.

## Quickstart

### Backend

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

- `GET /` — service banner with route map
- `GET /docs` — Swagger UI (all 70+ endpoints)
- `GET /health` — liveness
- `GET /demo/users` — list seeded demo users

### Mobile

```bash
cd mobile
npm install
npx expo start
```

Open Expo Go on phone or run in iOS/Android simulator.

### Web

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000.

### Tests

```bash
cd backend
pytest tests/                    # 116 tests
```

## Backend layers

Two coexisting layers, separated by route prefix and auth method:

**Real, DB-backed (production-shaped)** — covers steps 1–11 of the demo script:

| Routes | Purpose |
|---|---|
| `/auth`, `/me` | Login, current user, role switch |
| `/deals` | Create, list, get, patch, submit, status transition, timeline |
| `/companies/enrich`, `/companies/{id}` | SIREN enrichment, lookup |
| `/deals/{id}/quotes`, `/quotes/{id}/extract` | Quote upload + extraction |
| `/deals/{id}/documents/upload-url`, `/confirm` | Document upload via signed URL |
| `/documents/{id}/validate`, `/reject` | Doc validation |
| `/pricing/indicative`, `/deals/{id}/pricing/recalculate` | Pricing |
| `/deals/{id}/risk/assess`, `/risk/latest` | Risk scoring |
| `/admin/queue`, `/admin/deals/{id}/start-review`, `/pre-approve`, `/reject`, `/checklist`, `/request-document` | Admin operations |

Auth: real Supabase JWT (`Authorization: Bearer <token>`). Persistence: Postgres via SQLAlchemy. Audit log: `audit_events` table. Idempotency: `Idempotency-Key` header.

**Demo extras (in-memory, mock)** — covers steps 12–17:

| Routes | Purpose |
|---|---|
| `/deals/{id}/refi-package`, `/refi-packages/{id}/send`, `/decision` | Refi package + financier decision |
| `/deals/{id}/offers`, `/offers/{id}/send` | Firm offer |
| `/deals/{id}/contracts`, `/contracts/{id}/mock-sign`, `/send-signature`, `/activation-checklist`, `/activate` | Contract + mock signature + activation |
| `/contracts/{id}/assets`, `/assets/{id}` | Assets |
| `/contracts/{id}/schedule`, `/invoices`, `/invoices/{id}/mark-paid`, `/payments` | Billing |
| `/dashboards/{partner,client,admin,cfo/portfolio,cfo/cash,cfo/risk}` | Dashboards |
| `/ai/assistant/query`, `/ai/deals/{id}/summary`, `/ai/documents/{id}/extract` | AI assistant (keyword-matched mock) |
| `/demo/reset`, `/demo/snapshot`, `/demo/users` | Demo control |

Auth: `X-Demo-Email: <role>@leaseai.demo` header in demo mode, falls back to real JWT if `DEMO_MODE=false`. State: in-memory dict seeded at boot. PDFs: hand-generated at `static/*.pdf`.

## Demo users (in-memory seed)

```
partner@leaseai.demo    — Emma Martin (Tech Solutions Partner)
admin@leaseai.demo      — Clara Ops (LeaseAI)
ops@leaseai.demo        — Paul Ops (LeaseAI)
risk@leaseai.demo       — Hugo Risk (LeaseAI)
financier@leaseai.demo  — Martin Finance (Blue Capital Finance)
client@leaseai.demo     — Sophie Client (Globex Inc.)
cfo@leaseai.demo        — Lea CFO (LeaseAI)
```

Seeded deal: `D-2026-0001` — Globex Inc., 85 500 €, 36 months, Laptops & Accessories.

## Demo mode

`DEMO_MODE=true` (default in dev) enables the `X-Demo-Email` header bypass for the demo extras routers. Set `DEMO_MODE=false` for production — only real Supabase JWT accepted.

Demo PDFs regenerated on every boot (`backend/static/{refi,contract,offer,invoice,sepa,delivery}_demo.pdf`).

## Project structure

```
lease.ai/
├── backend/                FastAPI · 116 tests · 74 routes
│   ├── app/
│   │   ├── core/           config, auth, db, errors, idempotency, roles
│   │   ├── models/         SQLAlchemy ORM (10 entities)
│   │   ├── schemas/        Pydantic request/response
│   │   ├── services/       DealService, AdminService, ... + pricing_calc, risk_calc, transitions, pdf
│   │   ├── routers/        DB-backed + demo extras
│   │   ├── state.py        In-memory store for demo extras
│   │   └── main.py         Entrypoint
│   ├── alembic/            3 migrations
│   ├── static/             6 demo PDFs
│   └── tests/              92 main + 22 demo + 2 brand
├── mobile/                 Expo · partner + client roles
│   ├── app/                file-based routes
│   └── src/                services, hooks, stores, components
├── web/                    Next.js · admin, ops, risk, financier, cfo
│   ├── app/                App Router routes by role group
│   └── lib/                API client, Supabase client
└── .claude/docs/           36 spec docs (vision, product, design, flows, backend, api, demo)
```

## Documentation

Source-of-truth specs live in `.claude/docs/`. Read the relevant doc before implementing.

| What you're building | Doc to read first |
|---|---|
| A screen or flow | `product/screen_specs.md`, `product/navigation_map.md` |
| Data entities or DB schema | `backend/data_model.md` |
| Status transitions | `backend/status_machine.md` |
| API endpoint | `api/endpoints.md`, `api/errors.md` |
| UI component | `design/component_library.md`, `design/design_tokens.md` |
| Permissions | `product/permissions_matrix.md` |
| AI assistant | `agents/agent_architecture.md`, `agents/decision_boundaries.md` |
| Demo script | `demo/demo_script.md`, `demo/demo_seed_data.md` |

Condensed bootstrap doc: `.claude/docs/01_AI_DEVELOPMENT_CONTEXT.md`.

## Status

| Layer | Status |
|---|---|
| Backend real path (deals → admin review) | DB-backed, tested |
| Backend demo extras (refi → CFO) | In-memory, tested |
| Backend integrations (Pappers, Yousign, Stripe, Resend, Anthropic) | Not wired |
| Mobile partner flow | Login + dashboards + create deal screens scaffolded |
| Mobile client flow | Login + dashboard scaffolded |
| Web admin queue + deal review | Implemented |
| Web ops, financier, cfo | Scaffolded (placeholders) |
| Mobile branding | Logo, mark, wordmark, icons applied |
| RBAC enforcement | Partial — matrix codified in docs, enforced ad hoc per endpoint |
| Audit log | Implemented (`audit_events` table) |
| Background jobs | Inline + `BackgroundTasks` only |

## Env variables

Copy `.env.example` to `.env.local`. Required for backend:

```
DATABASE_URL=postgresql+asyncpg://postgres:<pwd>@<host>:5432/postgres
SUPABASE_URL=https://<project_ref>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
SUPABASE_JWKS_URL=https://<project_ref>.supabase.co/auth/v1/.well-known/jwks.json
DEMO_MODE=true                # set to false in prod
```

## Conventions

- **API response envelope**: `{"data": ..., "meta": {...}, "errors": [...]}` (success has empty errors; failure has empty data)
- **Money in cents**, currency in ISO 4217 (`EUR`)
- **Dates** ISO 8601 UTC at API, local formatting at UI
- **IDs** UUID internal + readable `public_id` (e.g. `D-2026-0001`)
- **Status badges** colors from `design/design_tokens.md`
- **Fonts** Satoshi for UI, IBM Plex Mono for numbers
- **Colors** `navy.900 #0D183D` · `blue.500 #2563EB` · `teal.500 #10B981`

## Deploy

- Mobile → Expo EAS (TestFlight / Play Console)
- Web → Vercel
- Backend → Railway
- DB + Auth → Supabase

## License

See `LICENSE`.

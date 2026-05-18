# LeaseAI

AI-native IT leasing operator. Monorepo: mobile (Expo), web back-office (Next.js), backend (FastAPI), Supabase (auth + Postgres + storage).

End-to-end deal lifecycle: partner creates deal → SIREN enrichment → quote upload → indicative pricing → risk scoring → admin review → refi package → financier decision → firm offer → contract → signature → activation → schedule → invoice → payment → CFO portfolio.

## Demo

[Watch the demo video](https://drive.google.com/file/d/1ESDXW7RShyQ8dmkSAT62xv5SAxlVALXp/view?usp=sharing)

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
│  client      │       │  deals, companies,      │
└──────────────┘       │  quotes, documents,     │
                       │  pricing, risk,         │
┌──────────────┐       │  admin, me, auth        │
│  web/        │──────▶│                         │
│  Next.js 16  │       └─────────────────────────┘
│  admin, ops, │
│  financier,  │
│  cfo, risk   │
└──────────────┘
```

## Stack

| Surface | Stack |
|---|---|
| `web/` | Next.js 16 App Router · Tailwind · shadcn/ui · TanStack Query · `@supabase/ssr` |
| `backend/` | FastAPI · Python 3.12 · SQLAlchemy 2.0 async · Alembic · Pydantic v2 · `python-jose` · `httpx` |
| Infra | Supabase (auth + Postgres + storage) · Railway (backend deploy) · Vercel (web deploy) |

## Roles

| Interface | Roles |
|---|---|
| Mobile | `partner`, `client` |
| Web back-office | `admin`, `ops`, `risk`, `financier`, `cfo` |

Both frontends share the same JWT issued by Supabase Auth. FastAPI verifies via JWKS (ES256).

## Quickstart

### Backend

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

- `GET /docs` — Swagger UI
- `GET /health` — liveness

### Web

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000. Set `API_INTERNAL_URL` in `web/.env.local` to point at the backend (default: `http://localhost:8000`).

### Tests

```bash
cd backend
pytest tests/
```

## Backend routes

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
| `/admin/queue`, `/admin/deals/{id}/...` | Admin operations |

Auth: Supabase JWT (`Authorization: Bearer <token>`). Persistence: Postgres via SQLAlchemy. Audit log: `audit_events` table. Idempotency: `Idempotency-Key` header.

## Project structure

```
lease.ai/
├── backend/                FastAPI
│   ├── app/
│   │   ├── core/           config, auth, db, errors, idempotency, roles
│   │   ├── models/         SQLAlchemy ORM (10 entities)
│   │   ├── schemas/        Pydantic request/response
│   │   ├── services/       DealService, AdminService, pricing_calc, risk_calc, transitions
│   │   ├── routers/        Route handlers (thin, no logic)
│   │   └── main.py         Entrypoint
│   ├── alembic/            Migrations
│   └── tests/
├── mobile/                 Expo · partner + client roles
│   ├── app/                file-based routes
│   └── src/                services, hooks, stores, components
├── web/                    Next.js · admin, ops, risk, financier, cfo
│   ├── app/                App Router routes by role group
│   └── lib/                API client, Supabase client
└── .claude/docs/           Spec docs (vision, product, design, flows, backend, api)
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

Condensed bootstrap doc: `.claude/docs/01_AI_DEVELOPMENT_CONTEXT.md`.

## Status

| Layer | Status |
|---|---|
| Backend (deals → admin review) | DB-backed, tested |
| Backend (refi → CFO) | To build |
| Backend integrations (Pappers, Yousign, Stripe, Resend, Anthropic) | Not wired |
| Web admin queue + deal review | Implemented |
| Web ops, financier, cfo | Scaffolded (placeholders) |
| RBAC enforcement | Partial — matrix in docs, enforced per endpoint |
| Audit log | Implemented (`audit_events` table) |

## Env variables

Copy `.env.example` to `.env.local`. Required for backend:

```
DATABASE_URL=postgresql+asyncpg://postgres:<pwd>@<host>:5432/postgres
SUPABASE_URL=https://<project_ref>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
JWKS_URL=https://<project_ref>.supabase.co/auth/v1/.well-known/jwks.json
```

For web (`web/.env.local`):

```
NEXT_PUBLIC_SUPABASE_URL=https://<project_ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
API_INTERNAL_URL=http://localhost:8000
```

## Conventions

- **API response envelope**: `{"data": ..., "meta": {...}, "errors": []}` (success has empty errors; failure has empty data)
- **Money in cents**, currency ISO 4217 (`EUR`)
- **Dates** ISO 8601 UTC at API, local formatting at UI
- **IDs** UUID internal + readable `public_id` (e.g. `D-2026-0001`)
- **Status badge colors** from `design/design_tokens.md`
- **Fonts** Satoshi for UI, IBM Plex Mono for numbers
- **Colors** `navy.900 #0D183D` · `blue.500 #2563EB` · `teal.500 #10B981`

## Deploy

- Web → Vercel
- Backend → Railway
- DB + Auth → Supabase

## License

See `LICENSE`.

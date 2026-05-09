# Phase 1 — Monorepo Scaffold + Auth Foundation

**Date:** 2026-05-09  
**Approach:** CLI-first scaffold (A)  
**Scope:** Scaffold all three sub-projects + FastAPI JWKS auth middleware  

---

## What Gets Built

```
lease.ai/
├── mobile/          # Expo SDK 52 + Router 4, TS strict, NativeWind
├── web/             # Next.js 15 App Router, TS strict, Tailwind, shadcn
└── backend/         # FastAPI skeleton, JWKS auth, SQLAlchemy async, Alembic
```

---

## Backend

### Dependencies

```
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
alembic
pydantic-settings
python-jose[cryptography]
httpx
```

### Structure

```
backend/
  app/
    core/
      auth.py       # JWKS fetch+cache, ES256 verify, role validation, get_current_user
      config.py     # Pydantic Settings (reads .env)
      db.py         # SQLAlchemy async engine + session factory
      roles.py      # UserRole enum + VALID_ROLES set
    routers/
      me.py         # GET /me — protected test route
    services/       # placeholder __init__.py
    models/         # placeholder __init__.py
    schemas/        # placeholder __init__.py
    main.py         # FastAPI app, CORS, /health, includes me router
  alembic/
  alembic.ini
  requirements.txt
```

### Roles model

```python
# backend/app/core/roles.py
from enum import Enum

class UserRole(str, Enum):
    partner = "partner"
    client = "client"
    admin = "admin"
    ops = "ops"
    financier = "financier"
    cfo = "cfo"
```

`active_role` extracted from the JWT is validated against `UserRole` — invalid role raises `401`.

### Auth pattern

- JWKS URL: `https://conxwmnjhntbzftwgxig.supabase.co/auth/v1/.well-known/jwks.json`
- Algorithm: `ES256` (not HS256 — Supabase migrated to ECC P-256)
- Flow: extract Bearer → fetch JWKS (lru_cache, hourly TTL) → `jwt.decode` with `python-jose` → validate `active_role` against `UserRole` → return `{user_id, active_role}`
- FastAPI dependency: `get_current_user` → injected into protected routes via `Depends`

### Protected test route

```
GET /me
→ 401 if no token or invalid token
→ 200 { "user_id": "...", "active_role": "..." } if valid
```

---

## Mobile

### Dependencies added on top of Expo scaffold

```
nativewind
zustand
@tanstack/react-query
react-hook-form
zod
@supabase/supabase-js
expo-secure-store
```

### Route structure

```
mobile/app/
  (auth)/login.tsx
  (partner)/index.tsx          # stub
  (client)/index.tsx           # stub
  _layout.tsx
```

---

## Web

### Dependencies added on top of Next.js scaffold

```
@tanstack/react-query
@supabase/supabase-js
@supabase/ssr
shadcn/ui (init)
```

### Route structure

```
web/app/
  (auth)/login/page.tsx        # stub
  (admin)/page.tsx             # stub
  (ops)/page.tsx               # stub
  (financier)/page.tsx         # stub
  (cfo)/page.tsx               # stub
  layout.tsx
```

---

## Out of Scope

- Supabase DB schema / Alembic migrations (Phase 2)
- Real screens with business logic (Phase 3+)
- SEPA, ML scoring, multi-refinancer automation

---

## Success Criteria

- `cd backend && uvicorn app.main:app --reload` starts with no errors
- `GET /health` returns `{"status": "ok"}`
- `cd mobile && npx expo start` launches without errors
- `cd web && npm run dev` launches without errors
- Auth middleware correctly rejects a request without a valid Bearer token

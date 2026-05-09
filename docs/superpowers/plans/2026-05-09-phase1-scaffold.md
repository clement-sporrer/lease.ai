# Phase 1 — Monorepo Scaffold + Auth Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the three sub-projects (mobile/, web/, backend/) and implement FastAPI JWKS-based auth middleware with a verified `/me` test route.

**Architecture:** CLI-generated scaffolds for Expo and Next.js; hand-crafted FastAPI skeleton with async SQLAlchemy. Auth uses ES256 JWT verification via Supabase's JWKS endpoint — no shared secret, no custom auth logic. All business role validation happens in a single `roles.py` enum referenced by both auth and routes.

**Tech Stack:** Expo SDK 52 + Router 4, Next.js 15 App Router, FastAPI + SQLAlchemy 2 async, python-jose[cryptography], Pydantic Settings v2, pytest + httpx TestClient

---

## File Map

```
lease.ai/
├── mobile/                          # created by: npx create-expo-app
│   └── app/
│       ├── _layout.tsx
│       ├── (auth)/login.tsx         # stub
│       ├── (partner)/index.tsx      # stub
│       └── (client)/index.tsx       # stub
│
├── web/                             # created by: create-next-app
│   └── app/
│       ├── layout.tsx
│       ├── (auth)/login/page.tsx    # stub
│       ├── (admin)/page.tsx         # stub
│       ├── (ops)/page.tsx           # stub
│       ├── (financier)/page.tsx     # stub
│       └── (cfo)/page.tsx           # stub
│
└── backend/
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── alembic.ini                  # created by: alembic init
    ├── alembic/
    │   └── env.py                   # modified to use async engine
    ├── app/
    │   ├── __init__.py
    │   ├── main.py                  # FastAPI app, CORS, /health, includes routers
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py            # Pydantic Settings
    │   │   ├── roles.py             # UserRole enum
    │   │   ├── auth.py              # JWKS cache, verify_token, get_current_user
    │   │   └── db.py                # async engine + session factory
    │   └── routers/
    │       ├── __init__.py
    │       └── me.py                # GET /me
    └── tests/
        ├── conftest.py              # EC key fixture, token factory, TestClient
        ├── test_roles.py
        ├── test_auth.py
        └── test_me.py
```

---

## Task 1: Feature branch

**Files:** none

- [ ] **Step 1: Create and switch to feature branch**

  ```bash
  cd /Users/clementsporrer/.superset/projects/lease.ai
  git checkout -b feat/phase1-scaffold
  ```

  Expected: `Switched to a new branch 'feat/phase1-scaffold'`

---

## Task 2: Backend — directory skeleton + dependencies

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/tests/__init__.py`

- [ ] **Step 1: Create directory structure**

  ```bash
  mkdir -p backend/app/core backend/app/routers backend/app/services \
            backend/app/models backend/app/schemas backend/tests
  touch backend/app/__init__.py backend/app/core/__init__.py \
        backend/app/routers/__init__.py backend/app/services/__init__.py \
        backend/app/models/__init__.py backend/app/schemas/__init__.py \
        backend/tests/__init__.py
  ```

- [ ] **Step 2: Write `backend/requirements.txt`**

  ```
  fastapi>=0.115
  uvicorn[standard]>=0.32
  sqlalchemy[asyncio]>=2.0
  asyncpg>=0.30
  alembic>=1.14
  pydantic-settings>=2.6
  python-jose[cryptography]>=3.3
  httpx>=0.27
  ```

- [ ] **Step 3: Write `backend/requirements-dev.txt`**

  ```
  -r requirements.txt
  pytest>=8.0
  pytest-asyncio>=0.24
  respx>=0.21
  cryptography>=43.0
  ```

- [ ] **Step 4: Create Python virtual environment and install**

  ```bash
  cd backend
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements-dev.txt
  ```

  Expected: all packages install without errors.

- [ ] **Step 5: Commit**

  ```bash
  git add backend/
  git commit -m "chore(backend): init directory skeleton and dependencies"
  ```

---

## Task 3: Backend — `config.py`

**Files:**
- Create: `backend/app/core/config.py`

- [ ] **Step 1: Write `backend/app/core/config.py`**

  ```python
  from pydantic_settings import BaseSettings, SettingsConfigDict


  class Settings(BaseSettings):
      model_config = SettingsConfigDict(env_file=".env", extra="ignore")

      database_url: str = "postgresql+asyncpg://localhost/leaseai"
      supabase_url: str = ""
      supabase_anon_key: str = ""
      supabase_service_role_key: str = ""
      jwks_url: str = "https://conxwmnjhntbzftwgxig.supabase.co/auth/v1/.well-known/jwks.json"
      cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8081"]


  settings = Settings()
  ```

- [ ] **Step 2: Verify import works**

  ```bash
  cd backend && source .venv/bin/activate
  python -c "from app.core.config import settings; print(settings.jwks_url)"
  ```

  Expected: prints the JWKS URL.

- [ ] **Step 3: Commit**

  ```bash
  git add backend/app/core/config.py
  git commit -m "feat(backend): add Settings config via pydantic-settings"
  ```

---

## Task 4: Backend — `roles.py` + tests

**Files:**
- Create: `backend/app/core/roles.py`
- Create: `backend/tests/test_roles.py`

- [ ] **Step 1: Write failing tests in `backend/tests/test_roles.py`**

  ```python
  import pytest
  from app.core.roles import UserRole


  def test_all_roles_defined():
      assert {r.value for r in UserRole} == {
          "partner", "client", "admin", "ops", "financier", "cfo"
      }


  def test_role_is_string_enum():
      assert UserRole.admin == "admin"
      assert isinstance(UserRole.partner, str)


  def test_invalid_role_raises():
      with pytest.raises(ValueError):
          UserRole("superadmin")
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  cd backend && source .venv/bin/activate
  python -m pytest tests/test_roles.py -v
  ```

  Expected: `ModuleNotFoundError` or `ImportError` — `roles` not defined yet.

- [ ] **Step 3: Write `backend/app/core/roles.py`**

  ```python
  from enum import Enum


  class UserRole(str, Enum):
      partner = "partner"
      client = "client"
      admin = "admin"
      ops = "ops"
      financier = "financier"
      cfo = "cfo"
  ```

- [ ] **Step 4: Run tests to verify they pass**

  ```bash
  python -m pytest tests/test_roles.py -v
  ```

  Expected: 3 PASSED.

- [ ] **Step 5: Commit**

  ```bash
  git add backend/app/core/roles.py backend/tests/test_roles.py
  git commit -m "feat(backend): add UserRole enum with 6 roles"
  ```

---

## Task 5: Backend — `auth.py` + tests

**Files:**
- Create: `backend/app/core/auth.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Write `backend/tests/conftest.py`** (shared EC key fixtures)

  ```python
  import base64
  import time
  import pytest
  from cryptography.hazmat.backends import default_backend
  from cryptography.hazmat.primitives import serialization
  from cryptography.hazmat.primitives.asymmetric import ec
  from jose import jwt


  def _int_to_b64url(n: int, length: int = 32) -> str:
      data = n.to_bytes(length, "big")
      return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


  @pytest.fixture(scope="session")
  def test_ec_key():
      private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
      pub_numbers = private_key.public_key().public_numbers()
      jwks = {
          "keys": [
              {
                  "kty": "EC",
                  "crv": "P-256",
                  "x": _int_to_b64url(pub_numbers.x),
                  "y": _int_to_b64url(pub_numbers.y),
                  "kid": "test-key-1",
                  "use": "sig",
                  "alg": "ES256",
              }
          ]
      }
      private_pem = private_key.private_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PrivateFormat.TraditionalOpenSSL,
          encryption_algorithm=serialization.NoEncryption(),
      ).decode()
      return {"private_pem": private_pem, "jwks": jwks}


  @pytest.fixture(scope="session")
  def make_token(test_ec_key):
      def _make(sub: str, active_role: str, expired: bool = False) -> str:
          now = int(time.time())
          payload = {
              "sub": sub,
              "aud": "authenticated",
              "iat": now,
              "exp": now + (-10 if expired else 3600),
              "user_metadata": {"active_role": active_role},
          }
          return jwt.encode(payload, test_ec_key["private_pem"], algorithm="ES256")

      return _make
  ```

- [ ] **Step 2: Write failing tests in `backend/tests/test_auth.py`**

  ```python
  from unittest.mock import patch
  import pytest
  from jose import JWTError
  from app.core.auth import verify_token, AuthError


  def test_verify_token_valid(test_ec_key, make_token):
      token = make_token("user-abc", "admin")
      with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
          result = verify_token(token)
      assert result["user_id"] == "user-abc"
      assert result["active_role"] == "admin"


  def test_verify_token_expired(test_ec_key, make_token):
      token = make_token("user-abc", "admin", expired=True)
      with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
          with pytest.raises(AuthError, match="expired"):
              verify_token(token)


  def test_verify_token_garbage():
      with pytest.raises(AuthError):
          verify_token("not.a.token")


  def test_verify_token_invalid_role(test_ec_key, make_token):
      token = make_token("user-abc", "superadmin")
      with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
          with pytest.raises(AuthError, match="role"):
              verify_token(token)
  ```

- [ ] **Step 3: Run tests to verify they fail**

  ```bash
  python -m pytest tests/test_auth.py -v
  ```

  Expected: `ImportError` — `auth` not defined yet.

- [ ] **Step 4: Write `backend/app/core/auth.py`**

  ```python
  import time
  from typing import Any

  import httpx
  from fastapi import Depends, HTTPException
  from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
  from jose import ExpiredSignatureError, JWTError, jwt

  from app.core.config import settings
  from app.core.roles import UserRole

  _JWKS_TTL = 3600
  _jwks_cache: dict[str, Any] = {"keys": None, "fetched_at": 0.0}

  _bearer = HTTPBearer()


  class AuthError(Exception):
      pass


  def _get_jwks() -> dict:
      now = time.time()
      if _jwks_cache["keys"] is None or now - _jwks_cache["fetched_at"] > _JWKS_TTL:
          response = httpx.get(settings.jwks_url, timeout=5)
          response.raise_for_status()
          _jwks_cache["keys"] = response.json()
          _jwks_cache["fetched_at"] = now
      return _jwks_cache["keys"]


  def verify_token(token: str) -> dict:
      try:
          jwks = _get_jwks()
          payload = jwt.decode(
              token, jwks, algorithms=["ES256"], audience="authenticated"
          )
      except ExpiredSignatureError:
          raise AuthError("Token expired")
      except JWTError as exc:
          raise AuthError(f"Invalid token: {exc}") from exc

      user_id: str = payload.get("sub", "")
      raw_role: str = payload.get("user_metadata", {}).get("active_role", "")

      try:
          active_role = UserRole(raw_role)
      except ValueError:
          raise AuthError(f"Invalid role in token: {raw_role!r}")

      return {"user_id": user_id, "active_role": active_role}


  def get_current_user(
      credentials: HTTPAuthorizationCredentials = Depends(_bearer),
  ) -> dict:
      try:
          return verify_token(credentials.credentials)
      except AuthError as exc:
          raise HTTPException(status_code=401, detail=str(exc)) from exc
  ```

- [ ] **Step 5: Run tests to verify they pass**

  ```bash
  python -m pytest tests/test_auth.py -v
  ```

  Expected: 4 PASSED.

- [ ] **Step 6: Commit**

  ```bash
  git add backend/app/core/auth.py backend/tests/conftest.py backend/tests/test_auth.py
  git commit -m "feat(backend): add JWKS auth middleware with ES256 + role validation"
  ```

---

## Task 6: Backend — `db.py`

**Files:**
- Create: `backend/app/core/db.py`

- [ ] **Step 1: Write `backend/app/core/db.py`**

  ```python
  from collections.abc import AsyncGenerator

  from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
  from sqlalchemy.orm import DeclarativeBase

  from app.core.config import settings

  engine = create_async_engine(settings.database_url, echo=False)
  AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


  class Base(DeclarativeBase):
      pass


  async def get_db() -> AsyncGenerator[AsyncSession, None]:
      async with AsyncSessionLocal() as session:
          yield session
  ```

- [ ] **Step 2: Verify import**

  ```bash
  python -c "from app.core.db import engine, Base; print('ok')"
  ```

  Expected: `ok`

- [ ] **Step 3: Commit**

  ```bash
  git add backend/app/core/db.py
  git commit -m "feat(backend): add async SQLAlchemy engine and session factory"
  ```

---

## Task 7: Backend — `main.py` + `routers/me.py` + tests

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/routers/me.py`
- Create: `backend/tests/test_me.py`

- [ ] **Step 1: Write failing tests in `backend/tests/test_me.py`**

  ```python
  from unittest.mock import patch
  import pytest
  from fastapi.testclient import TestClient
  from app.main import app


  @pytest.fixture()
  def client():
      return TestClient(app)


  def test_health(client):
      response = client.get("/health")
      assert response.status_code == 200
      assert response.json() == {"status": "ok"}


  def test_me_no_token(client):
      response = client.get("/me")
      assert response.status_code == 403  # HTTPBearer returns 403 when no header


  def test_me_invalid_token(client):
      response = client.get("/me", headers={"Authorization": "Bearer not.a.real.token"})
      assert response.status_code == 401


  def test_me_valid_token(client, test_ec_key, make_token):
      token = make_token("user-xyz", "partner")
      with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
          response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
      assert response.status_code == 200
      data = response.json()
      assert data["user_id"] == "user-xyz"
      assert data["active_role"] == "partner"
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```bash
  python -m pytest tests/test_me.py -v
  ```

  Expected: `ImportError` — `main` not defined yet.

- [ ] **Step 3: Write `backend/app/routers/me.py`**

  ```python
  from fastapi import APIRouter, Depends
  from app.core.auth import get_current_user

  router = APIRouter()


  @router.get("/me")
  def me(current_user: dict = Depends(get_current_user)) -> dict:
      return {
          "user_id": current_user["user_id"],
          "active_role": current_user["active_role"],
      }
  ```

- [ ] **Step 4: Write `backend/app/main.py`**

  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware

  from app.core.config import settings
  from app.routers import me

  app = FastAPI(title="LeaseAI API", version="0.1.0")

  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.cors_origins,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

  app.include_router(me.router)


  @app.get("/health")
  def health() -> dict:
      return {"status": "ok"}
  ```

- [ ] **Step 5: Run all backend tests**

  ```bash
  python -m pytest tests/ -v
  ```

  Expected: all PASSED (test_roles: 3, test_auth: 4, test_me: 4 = 11 total).

- [ ] **Step 6: Verify server starts**

  ```bash
  uvicorn app.main:app --reload &
  sleep 2
  curl http://localhost:8000/health
  kill %1
  ```

  Expected: `{"status":"ok"}`

- [ ] **Step 7: Commit**

  ```bash
  git add backend/app/main.py backend/app/routers/me.py backend/tests/test_me.py
  git commit -m "feat(backend): add /health and GET /me protected route"
  ```

---

## Task 8: Backend — Alembic init

**Files:**
- Create: `backend/alembic.ini` (via alembic init)
- Modify: `backend/alembic/env.py`

- [ ] **Step 1: Run alembic init**

  ```bash
  cd backend && source .venv/bin/activate
  alembic init alembic
  ```

  Expected: creates `alembic/` directory and `alembic.ini`.

- [ ] **Step 2: Update `alembic.ini` to use env var for DB URL**

  Find the line `sqlalchemy.url = driver://user:pass@localhost/dbname` and replace it:

  ```ini
  sqlalchemy.url = %(DATABASE_URL)s
  ```

  Actually, it's cleaner to configure the URL in env.py. Replace the `sqlalchemy.url` line with:

  ```ini
  # URL is configured in alembic/env.py via app.core.config
  sqlalchemy.url =
  ```

- [ ] **Step 3: Replace `backend/alembic/env.py` with async-aware version**

  ```python
  import asyncio
  from logging.config import fileConfig

  from alembic import context
  from sqlalchemy.ext.asyncio import async_engine_from_config

  from app.core.config import settings
  from app.core.db import Base

  config = context.config
  config.set_main_option("sqlalchemy.url", settings.database_url)

  if config.config_file_name is not None:
      fileConfig(config.config_file_name)

  target_metadata = Base.metadata


  def run_migrations_offline() -> None:
      context.configure(
          url=settings.database_url,
          target_metadata=target_metadata,
          literal_binds=True,
          dialect_opts={"paramstyle": "named"},
      )
      with context.begin_transaction():
          context.run_migrations()


  def do_run_migrations(connection):
      context.configure(connection=connection, target_metadata=target_metadata)
      with context.begin_transaction():
          context.run_migrations()


  async def run_async_migrations() -> None:
      connectable = async_engine_from_config(
          config.get_section(config.config_ini_section, {}),
          prefix="sqlalchemy.",
      )
      async with connectable.connect() as connection:
          await connection.run_sync(do_run_migrations)
      await connectable.dispose()


  def run_migrations_online() -> None:
      asyncio.run(run_async_migrations())


  if context.is_offline_mode():
      run_migrations_offline()
  else:
      run_migrations_online()
  ```

- [ ] **Step 4: Verify alembic can read config**

  ```bash
  alembic current
  ```

  Expected: no error (may warn about empty DB URL if no DB running — that's fine at this stage).

- [ ] **Step 5: Commit**

  ```bash
  git add backend/alembic/ backend/alembic.ini
  git commit -m "chore(backend): init alembic with async SQLAlchemy env"
  ```

---

## Task 9: Mobile — Expo scaffold

**Files:** All created by `create-expo-app`, then stubs added.

- [ ] **Step 1: Scaffold with Expo Router template**

  ```bash
  cd /Users/clementsporrer/.superset/projects/lease.ai
  npx create-expo-app@latest mobile --template default
  ```

  When prompted for a project name, accept the default or type `mobile`.
  Expected: `mobile/` directory with Expo Router + TypeScript pre-configured.

- [ ] **Step 2: Install additional dependencies**

  ```bash
  cd mobile
  npx expo install nativewind@^4 tailwindcss react-native-reanimated react-native-safe-area-context
  npm install zustand @tanstack/react-query react-hook-form zod @supabase/supabase-js
  npx expo install expo-secure-store
  ```

- [ ] **Step 3: Init NativeWind**

  Follow the NativeWind v4 setup for Expo Router. Create `tailwind.config.js` at `mobile/`:

  ```js
  /** @type {import('tailwindcss').Config} */
  module.exports = {
    content: ["./app/**/*.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"],
    presets: [require("nativewind/preset")],
    theme: {
      extend: {
        colors: {
          navy: { 900: "#0D183D" },
          blue: { 500: "#2563EB" },
          teal: { 500: "#10B981" },
          danger: "#EF4444",
          warning: "#F59E0B",
        },
      },
    },
    plugins: [],
  };
  ```

  Add to `mobile/babel.config.js` plugins array: `"nativewind/babel"`

- [ ] **Step 4: Add route group stubs**

  Create `mobile/app/(auth)/login.tsx`:

  ```tsx
  import { Text, View } from "react-native";

  export default function LoginScreen() {
    return (
      <View className="flex-1 items-center justify-center bg-white">
        <Text className="text-navy-900 text-xl font-semibold">Login</Text>
      </View>
    );
  }
  ```

  Create `mobile/app/(partner)/index.tsx`:

  ```tsx
  import { Text, View } from "react-native";

  export default function PartnerHome() {
    return (
      <View className="flex-1 items-center justify-center bg-white">
        <Text className="text-navy-900 text-xl font-semibold">Partner Dashboard</Text>
      </View>
    );
  }
  ```

  Create `mobile/app/(client)/index.tsx`:

  ```tsx
  import { Text, View } from "react-native";

  export default function ClientHome() {
    return (
      <View className="flex-1 items-center justify-center bg-white">
        <Text className="text-navy-900 text-xl font-semibold">Client Dashboard</Text>
      </View>
    );
  }
  ```

- [ ] **Step 5: Verify Expo starts**

  ```bash
  npx expo start --no-dev-client
  ```

  Expected: Metro bundler starts, QR code displayed, no TypeScript errors.
  Press `Ctrl+C` to stop.

- [ ] **Step 6: Commit**

  ```bash
  cd ..
  git add mobile/
  git commit -m "feat(mobile): scaffold Expo SDK 52 + Router 4 with NativeWind and role stubs"
  ```

---

## Task 10: Web — Next.js scaffold

**Files:** All created by `create-next-app`, then stubs added.

- [ ] **Step 1: Scaffold Next.js 15 with App Router**

  ```bash
  cd /Users/clementsporrer/.superset/projects/lease.ai
  npx create-next-app@latest web \
    --typescript \
    --tailwind \
    --eslint \
    --app \
    --no-src-dir \
    --import-alias "@/*"
  ```

  When prompted, accept defaults.

- [ ] **Step 2: Install additional dependencies**

  ```bash
  cd web
  npm install @tanstack/react-query @supabase/supabase-js @supabase/ssr
  ```

- [ ] **Step 3: Init shadcn/ui**

  ```bash
  npx shadcn@latest init
  ```

  When prompted:
  - Style: Default
  - Base color: Slate
  - CSS variables: Yes

- [ ] **Step 4: Add role route stubs**

  Create `web/app/(auth)/login/page.tsx`:

  ```tsx
  export default function LoginPage() {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <h1 className="text-2xl font-semibold text-slate-900">Login</h1>
      </main>
    );
  }
  ```

  Create `web/app/(admin)/page.tsx`:

  ```tsx
  export default function AdminDashboard() {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-semibold text-slate-900">Admin Dashboard</h1>
      </main>
    );
  }
  ```

  Create `web/app/(ops)/page.tsx`:

  ```tsx
  export default function OpsDashboard() {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-semibold text-slate-900">Ops Dashboard</h1>
      </main>
    );
  }
  ```

  Create `web/app/(financier)/page.tsx`:

  ```tsx
  export default function FinancierDashboard() {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-semibold text-slate-900">Financier Dashboard</h1>
      </main>
    );
  }
  ```

  Create `web/app/(cfo)/page.tsx`:

  ```tsx
  export default function CfoDashboard() {
    return (
      <main className="p-8">
        <h1 className="text-2xl font-semibold text-slate-900">CFO Dashboard</h1>
      </main>
    );
  }
  ```

- [ ] **Step 5: Verify dev server starts**

  ```bash
  npm run dev
  ```

  Expected: server starts at `http://localhost:3000`, no TypeScript errors.
  Press `Ctrl+C` to stop.

- [ ] **Step 6: Commit**

  ```bash
  cd ..
  git add web/
  git commit -m "feat(web): scaffold Next.js 15 App Router with Tailwind, shadcn, role stubs"
  ```

---

## Task 11: Final integration check + branch summary

- [ ] **Step 1: Run full backend test suite one last time**

  ```bash
  cd backend && source .venv/bin/activate
  python -m pytest tests/ -v
  ```

  Expected: 11 PASSED, 0 FAILED.

- [ ] **Step 2: Confirm all three projects start**

  Each in a separate terminal:

  ```bash
  # Terminal 1
  cd backend && uvicorn app.main:app --reload
  curl http://localhost:8000/health   # → {"status":"ok"}

  # Terminal 2
  cd mobile && npx expo start

  # Terminal 3
  cd web && npm run dev
  curl http://localhost:3000          # → HTML response
  ```

- [ ] **Step 3: Final commit with scope summary**

  ```bash
  git add .
  git commit -m "chore: phase 1 scaffold complete — backend auth + mobile + web stubs"
  ```

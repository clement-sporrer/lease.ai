# LeaseAI on Replit

Demo deployment guide. Replit runs the **backend (FastAPI)** and **web (Next.js)** in one Repl. Mobile (Expo) is not started in Replit — it needs a phone or simulator.

## What runs

| Service | Port (local) | Port (external) | Purpose |
|---|---|---|---|
| Web (Next.js) | 3000 | 80 | Public preview URL |
| Backend (FastAPI) | 8000 | 8000 (internal) | API |

The web app proxies `/api/*` → backend at `127.0.0.1:8000` via Next.js rewrites. Browsers only ever see the web origin.

## Setup (first time)

1. **Import the `replit-submit` branch** at https://replit.com/import (paste GitHub URL, pick branch `replit-submit`).
2. **Do not use Agent.** Stick to Shell / Run / Secrets / Workflows.
3. **Add Secrets** (Tools → Secrets) — minimum:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `DATABASE_URL` (if backend should hit a real Supabase Postgres)
   - `SUPABASE_JWKS_URL` (defaults to the seeded URL in `config.py`)
   - `DEMO_MODE=true` (already set in `.replit [env]`, override here if needed)
4. **Click Run.** The script will:
   - `pip install` backend deps
   - start uvicorn on 127.0.0.1:8000
   - wait for `/health`
   - `npm install` web deps
   - start Next.js on 0.0.0.0:3000

Open the preview tab — Next.js homepage. Click through to login, then admin/cfo/etc.

## Verify it works

In Repl Shell:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/demo/snapshot -H "X-Demo-Email: admin@leaseai.demo"
curl http://127.0.0.1:8000/dashboards/cfo/portfolio -H "X-Demo-Email: cfo@leaseai.demo"
```

In browser (replace `<repl-url>` with your repl public URL):

```
https://<repl-url>/                    # Next.js homepage
https://<repl-url>/api/health          # proxied to backend
https://<repl-url>/api/demo/users      # demo users list
```

If `/api/...` returns Next 404 or HTML, the rewrite didn't kick in — restart the repl.

## Demo flow

Demo users (no password needed when `DEMO_MODE=true`):

```
partner@leaseai.demo
admin@leaseai.demo
financier@leaseai.demo
client@leaseai.demo
cfo@leaseai.demo
```

Seeded deal: `D-2026-0001` — Globex Inc., 85 500 €, 36 months.

For reset between rehearsals: `POST /api/demo/reset`.

## If Replit modified files

In Shell:

```bash
git status
git restore .
git clean -fd
bash scripts/replit-run.sh
```

## For production demo link

For a hackathon preview link, the dev URL is fine.

For a stable shareable link, use **Reserved VM** deployment (not Static — you have a backend):
- Reserved VM keeps both backend + web always-on
- Static Deployment only works for frontends with no server

In `.replit`, `[deployment]` block is already set with `deploymentTarget = "vm"`.

## What is NOT in Replit

- Mobile (`mobile/`) — Expo, needs phone/simulator
- Real Pappers, Yousign, Stripe, Resend integrations — all mocked
- Real Postgres data — backend uses in-memory state for demo-extras routers; main routers need a real `DATABASE_URL` to function fully

#!/usr/bin/env bash
# LeaseAI demo runner for Replit.
# - backend (FastAPI) on 127.0.0.1:8000  (internal only)
# - web (Next.js)    on 0.0.0.0:3000     (externally mapped to port 80)
# - /api/* on web proxies to backend via next.config.ts rewrites.
#
# Mobile (Expo) is NOT started here — it cannot run inside Replit web preview.
# For mobile demo, run `npx expo start` locally and scan the QR code on phone.

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> LeaseAI demo runner"
echo "    repo root: $ROOT"

# ---------- backend ----------
echo "==> [backend] install python deps"
python -m pip install --upgrade --quiet pip
python -m pip install --quiet -r backend/requirements.txt

echo "==> [backend] start uvicorn on 127.0.0.1:8000"
(cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &
BACKEND_PID=$!
echo "    backend pid: $BACKEND_PID"

# wait for backend health
echo "==> [backend] wait for /health"
for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "    backend ready"
    break
  fi
  sleep 1
done

# ---------- web ----------
echo "==> [web] install node deps"
npm --prefix web install --no-audit --no-fund --loglevel=error

echo "==> [web] start next dev on 0.0.0.0:3000"
exec npm --prefix web run dev -- --hostname 0.0.0.0 --port 3000

"""
Create demo user accounts for all LeaseAI roles.

Usage:
    cd backend
    python scripts/create_demo_users.py

Reads SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from root .env.local.
Idempotent — skips users that already exist (matched by email).
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load from repo root .env.local
load_dotenv(Path(__file__).parent.parent.parent / ".env.local")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_ROLE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env.local")
    sys.exit(1)


DEMO_PASSWORD = "LeaseAI2026!"

# All demo accounts — one per role
DEMO_USERS = [
    # ── Lease.AI internal (web back-office) ──────────────────────────────────
    {
        "email": "admin@lease-ai.fr",
        "role": "admin",
        "full_name": "Sophie Martin",
        "title": "Administration des ventes",
        "company": "Lease.AI",
    },
    {
        "email": "commercial@lease-ai.fr",
        "role": "commercial",
        "full_name": "Thomas Bernard",
        "title": "Commercial",
        "company": "Lease.AI",
    },
    {
        "email": "ops@lease-ai.fr",
        "role": "ops",
        "full_name": "Julien Lefebvre",
        "title": "Responsable opérations",
        "company": "Lease.AI",
    },
    {
        "email": "risk@lease-ai.fr",
        "role": "risk",
        "full_name": "Camille Rousseau",
        "title": "Analyste risques",
        "company": "Lease.AI",
    },
    {
        "email": "financier@lease-ai.fr",
        "role": "financier",
        "full_name": "Marc Dupont",
        "title": "Chargé de refinancement",
        "company": "Lease.AI",
    },
    {
        "email": "cfo@lease-ai.fr",
        "role": "cfo",
        "full_name": "Isabelle Moreau",
        "title": "Directrice financière",
        "company": "Lease.AI",
    },
    {
        "email": "comptable@lease-ai.fr",
        "role": "comptable",
        "full_name": "Nicolas Petit",
        "title": "Responsable comptabilité",
        "company": "Lease.AI",
    },
    # ── External — Partenaires revendeurs (mobile app) ────────────────────────
    {
        "email": "partenaire@techpro-solutions.fr",
        "role": "partner",
        "full_name": "Antoine Leroy",
        "title": "Commercial",
        "company": "TechPro Solutions",
    },
    # ── External — Clients finaux (mobile app) ────────────────────────────────
    {
        "email": "client@globex-corp.fr",
        "role": "client",
        "full_name": "Pierre Durand",
        "title": "Directeur des systèmes d'information",
        "company": "Globex Corporation",
    },
]


async def create_users():
    import httpx

    admin_url = f"{SUPABASE_URL}/auth/v1/admin"
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        # Fetch existing users to avoid duplicates
        resp = await client.get(f"{admin_url}/users?per_page=1000", headers=headers)
        resp.raise_for_status()
        existing_emails = {u["email"] for u in resp.json().get("users", [])}

        created = 0
        skipped = 0

        for user in DEMO_USERS:
            email = user["email"]

            if email in existing_emails:
                print(f"  SKIP  {email} (already exists)")
                skipped += 1
                continue

            payload = {
                "email": email,
                "password": DEMO_PASSWORD,
                "email_confirm": True,
                "user_metadata": {
                    "active_role": user["role"],
                    "full_name": user["full_name"],
                    "title": user["title"],
                    "company": user["company"],
                },
            }

            resp = await client.post(f"{admin_url}/users", headers=headers, json=payload)

            if resp.status_code in (200, 201):
                print(f"  OK    {email} → role={user['role']} ({user['full_name']})")
                created += 1
            else:
                body = resp.json()
                print(f"  ERROR {email}: {resp.status_code} — {body.get('message', body)}")

        print(f"\nDone — {created} created, {skipped} skipped")
        print(f"\nAll accounts use password: {DEMO_PASSWORD}")
        print("\nDemo accounts summary:")
        for u in DEMO_USERS:
            print(f"  {u['role']:12}  {u['email']}")


if __name__ == "__main__":
    asyncio.run(create_users())

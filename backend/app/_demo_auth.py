"""Demo-only auth shim for the demo extras routers (refi, offers, contracts,
assets, billing, dashboards, ai, demo).

These routers operate on the in-memory `app.state` store and do not touch the
real Postgres-backed services on main. To keep the demo runnable without a
fully-provisioned Supabase project, this dependency:

- accepts an `X-Demo-Email: <role>@leaseai.demo` header in demo mode
- falls back to the real JWT verifier from `app.core.auth` if no header
- can be disabled by setting `DEMO_MODE=false` in env
"""
from __future__ import annotations

from fastapi import HTTPException, Request

from app.core.auth import AuthError, verify_token
from app.core.config import settings
from app.core.roles import UserRole

_DEMO_EMAIL_TO_ROLE: dict[str, tuple[UserRole, str]] = {
    "partner@leaseai.demo": (UserRole.partner, "user_partner_001"),
    "admin@leaseai.demo": (UserRole.admin, "user_admin_001"),
    "ops@leaseai.demo": (UserRole.ops, "user_ops_001"),
    "risk@leaseai.demo": (UserRole.risk, "user_risk_001"),
    "financier@leaseai.demo": (UserRole.financier, "user_financier_001"),
    "client@leaseai.demo": (UserRole.client, "user_client_001"),
    "cfo@leaseai.demo": (UserRole.cfo, "user_cfo_001"),
}


def _is_demo_mode() -> bool:
    return getattr(settings, "demo_mode", True)


async def get_current_user_demo(request: Request) -> dict:
    """Permissive auth used only by demo-extras routers."""
    if _is_demo_mode():
        email = request.headers.get("X-Demo-Email")
        if email and email in _DEMO_EMAIL_TO_ROLE:
            role, user_id = _DEMO_EMAIL_TO_ROLE[email]
            return {"user_id": user_id, "active_role": role, "email": email}
        if not request.headers.get("Authorization"):
            return {
                "user_id": "user_admin_001",
                "active_role": UserRole.admin,
                "email": "admin@leaseai.demo",
            }

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth_header[len("Bearer ") :]
    try:
        return await verify_token(token)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

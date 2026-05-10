import logging

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.core.roles import UserRole

logger = logging.getLogger(__name__)

_SUPABASE_AUTH_TIMEOUT = 10.0


def _extract_active_role(access_token: str) -> str:
    """Decode JWT payload (no verification needed — token just came from Supabase)."""
    import base64
    import json

    try:
        payload_part = access_token.split(".")[1]
        # Add padding
        padding = 4 - len(payload_part) % 4
        payload_part += "=" * (padding % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_part))
        return payload.get("user_metadata", {}).get("active_role", "")
    except (IndexError, ValueError, json.JSONDecodeError):
        logger.warning("Failed to extract active_role from JWT payload", exc_info=True)
        return ""


async def login(email: str, password: str) -> dict:
    url = f"{settings.supabase_url}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": settings.supabase_anon_key,
        "Content-Type": "application/json",
    }
    body = {"email": email, "password": password}

    async with httpx.AsyncClient(timeout=_SUPABASE_AUTH_TIMEOUT) as client:
        try:
            response = await client.post(url, headers=headers, json=body)
        except httpx.RequestError as exc:
            logger.error("Supabase auth request failed: %s", exc)
            raise HTTPException(status_code=502, detail="Auth service unavailable")

    if response.status_code in (400, 422):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if response.status_code != 200:
        logger.error("Supabase auth error: status=%d", response.status_code)
        raise HTTPException(status_code=502, detail="Auth service error")

    data = response.json()
    access_token: str = data.get("access_token", "")
    refresh_token: str = data.get("refresh_token", "")
    user_id: str = data.get("user", {}).get("id", "")

    if not access_token or not user_id:
        raise HTTPException(status_code=502, detail="Auth service returned incomplete response")

    active_role: str = _extract_active_role(access_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user_id,
        "active_role": active_role,
    }


async def set_active_role(user_id: str, role: str) -> dict:
    # Validate role before hitting the Admin API
    try:
        UserRole(role)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid role value")

    url = f"{settings.supabase_url}/auth/v1/admin/users/{user_id}"
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }
    body = {"user_metadata": {"active_role": role}}

    async with httpx.AsyncClient(timeout=_SUPABASE_AUTH_TIMEOUT) as client:
        try:
            response = await client.put(url, headers=headers, json=body)
        except httpx.RequestError as exc:
            logger.error("Supabase admin API request failed: %s", exc)
            raise HTTPException(status_code=502, detail="Auth service unavailable")

    if response.status_code != 200:
        logger.error(
            "Supabase admin user update failed: status=%d user_id=%s",
            response.status_code,
            user_id,
        )
        raise HTTPException(status_code=502, detail="Failed to update role")

    return {"user_id": user_id, "active_role": role, "message": "Role updated"}

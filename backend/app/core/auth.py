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

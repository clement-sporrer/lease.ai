"""Tests for POST /auth/login and POST /me/active-role endpoints."""
import base64
import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app


def _make_fake_jwt(user_id: str, active_role: str) -> str:
    """Build a minimal (unsigned) JWT for use in fake Supabase responses."""
    header = base64.urlsafe_b64encode(b'{"alg":"ES256"}').rstrip(b"=").decode()
    payload_data = {
        "sub": user_id,
        "aud": "authenticated",
        "user_metadata": {"active_role": active_role},
    }
    payload = (
        base64.urlsafe_b64encode(json.dumps(payload_data).encode())
        .rstrip(b"=")
        .decode()
    )
    return f"{header}.{payload}.fakesig"


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success():
    fake_result = {
        "access_token": _make_fake_jwt("user-abc", "partner"),
        "refresh_token": "fake-refresh-token",
        "user_id": "user-abc",
        "active_role": "partner",
    }
    with patch(
        "app.services.auth_service.login", new_callable=AsyncMock, return_value=fake_result
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "secret"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-abc"
    assert data["active_role"] == "partner"
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    from fastapi import HTTPException

    with patch(
        "app.services.auth_service.login",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=401, detail="Invalid credentials"),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/login",
                json={"email": "bad@example.com", "password": "wrong"},
            )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_supabase_server_error():
    from fastapi import HTTPException

    with patch(
        "app.services.auth_service.login",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=502, detail="Auth service error"),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "secret"},
            )

    assert response.status_code == 502


@pytest.mark.asyncio
async def test_login_missing_body():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/auth/login", json={})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /me/active-role
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_active_role_invalid_role(make_token, test_ec_key):
    """Invalid role value → 422 from service validation."""
    token = make_token("user-xyz", "partner")

    with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/me/active-role",
                json={"role": "not_a_real_role"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_active_role_success(make_token, test_ec_key):
    token = make_token("user-xyz", "partner")
    fake_result = {
        "user_id": "user-xyz",
        "active_role": "admin",
        "message": "Role updated",
    }
    with patch(
        "app.services.auth_service.set_active_role",
        new_callable=AsyncMock,
        return_value=fake_result,
    ):
        with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/me/active-role",
                    json={"role": "admin"},
                    headers={"Authorization": f"Bearer {token}"},
                )

    assert response.status_code == 200
    data = response.json()
    assert data["active_role"] == "admin"
    assert data["user_id"] == "user-xyz"
    assert data["message"] == "Role updated"


@pytest.mark.asyncio
async def test_active_role_no_token():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/me/active-role", json={"role": "admin"})

    # HTTPBearer returns 401 when no credentials provided
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_active_role_supabase_error(make_token, test_ec_key):
    from fastapi import HTTPException

    token = make_token("user-xyz", "partner")

    with patch(
        "app.services.auth_service.set_active_role",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=502, detail="Failed to update role"),
    ):
        with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/me/active-role",
                    json={"role": "admin"},
                    headers={"Authorization": f"Bearer {token}"},
                )

    assert response.status_code == 502

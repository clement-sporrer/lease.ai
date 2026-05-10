from unittest.mock import AsyncMock, patch
import pytest
from app.core.auth import verify_token, AuthError
from app.core.roles import UserRole


@pytest.mark.asyncio
async def test_verify_token_valid(test_ec_key, make_token):
    token = make_token("user-abc", "admin")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        result = await verify_token(token)
    assert result["user_id"] == "user-abc"
    assert result["active_role"] == UserRole.admin


@pytest.mark.asyncio
async def test_verify_token_expired(test_ec_key, make_token):
    token = make_token("user-abc", "admin", expired=True)
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        with pytest.raises(AuthError, match="expired"):
            await verify_token(token)


@pytest.mark.asyncio
async def test_verify_token_garbage(test_ec_key):
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        with pytest.raises(AuthError):
            await verify_token("not.a.token")


@pytest.mark.asyncio
async def test_verify_token_invalid_role(test_ec_key, make_token):
    token = make_token("user-abc", "superadmin")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        with pytest.raises(AuthError, match="role"):
            await verify_token(token)


@pytest.mark.asyncio
async def test_verify_token_empty_role(test_ec_key, make_token):
    """Empty active_role is valid — new users have no role yet."""
    token = make_token("user-abc", "")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        result = await verify_token(token)
    assert result["user_id"] == "user-abc"
    assert result["active_role"] is None

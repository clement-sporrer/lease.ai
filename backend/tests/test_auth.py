from unittest.mock import patch
import pytest
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


def test_verify_token_garbage(test_ec_key):
    with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
        with pytest.raises(AuthError):
            verify_token("not.a.token")


def test_verify_token_invalid_role(test_ec_key, make_token):
    token = make_token("user-abc", "superadmin")
    with patch("app.core.auth._get_jwks", return_value=test_ec_key["jwks"]):
        with pytest.raises(AuthError, match="role"):
            verify_token(token)

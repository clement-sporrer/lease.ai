from unittest.mock import AsyncMock, patch
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
    assert response.status_code == 401  # HTTPBearer returns 401 when no header


def test_me_invalid_token(client):
    response = client.get("/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert response.status_code == 401


def test_me_valid_token(client, test_ec_key, make_token):
    token = make_token("user-xyz", "partner")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-xyz"
    assert data["active_role"] == "partner"

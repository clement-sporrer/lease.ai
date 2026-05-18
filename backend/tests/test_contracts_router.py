# backend/tests/test_contracts_router.py
from __future__ import annotations

import uuid
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _make_contract() -> MagicMock:
    c = MagicMock()
    c.id = uuid.uuid4()
    c.deal_id = uuid.uuid4()
    c.public_id = "CTR-ABCD1234"
    c.status = "draft"
    c.sent_at = None
    c.signed_at = None
    c.activated_at = None
    c.total_commitment_cents = None
    c.created_at = datetime.datetime.now(datetime.timezone.utc)
    c.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return c


@pytest.mark.anyio
async def test_generate_contract_returns_201(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    contract = _make_contract()

    with (
        patch("app.routers.contracts.contract_service.generate_contract", new=AsyncMock(return_value=contract)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/deals/{contract.deal_id}/contracts",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 201
    assert res.json()["data"]["public_id"] == "CTR-ABCD1234"


@pytest.mark.anyio
async def test_generate_contract_forbidden_for_financier(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="financier")

    with patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/deals/{uuid.uuid4()}/contracts",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 403


@pytest.mark.anyio
async def test_get_latest_contract_returns_null_when_none(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    deal_id = uuid.uuid4()

    with (
        patch("app.routers.contracts.contract_service.get_latest_contract", new=AsyncMock(return_value=None)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(
                f"/deals/{deal_id}/contracts/latest",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"] is None


@pytest.mark.anyio
async def test_activate_contract_forbidden_for_financier(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="financier")

    with patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/contracts/{uuid.uuid4()}/activate",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 403


@pytest.mark.anyio
async def test_send_signature_returns_200(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    contract = _make_contract()
    contract.status = "sent_for_signature"

    with (
        patch("app.routers.contracts.contract_service.send_signature", new=AsyncMock(return_value=contract)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/contracts/{contract.id}/send-signature",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "sent_for_signature"


@pytest.mark.anyio
async def test_mock_sign_returns_200(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    contract = _make_contract()
    contract.status = "signed"
    contract.signed_at = datetime.datetime.now(datetime.timezone.utc)

    with (
        patch("app.routers.contracts.contract_service.mock_sign", new=AsyncMock(return_value=contract)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/contracts/{contract.id}/mock-sign",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "signed"


@pytest.mark.anyio
async def test_activate_contract_returns_200(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    contract = _make_contract()
    contract.status = "active"
    contract.activated_at = datetime.datetime.now(datetime.timezone.utc)
    contract.total_commitment_cents = 120000

    with (
        patch("app.routers.contracts.contract_service.activate", new=AsyncMock(return_value=contract)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/contracts/{contract.id}/activate",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "active"


@pytest.mark.anyio
async def test_activation_checklist_returns_200(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    contract_id = uuid.uuid4()
    checklist = {
        "items": [{"key": "contract_generated", "label": "Contrat généré", "satisfied": True}],
        "all_satisfied": True,
    }

    with (
        patch("app.routers.contracts.contract_service.activation_checklist", new=AsyncMock(return_value=checklist)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(
                f"/contracts/{contract_id}/activation-checklist",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"]["all_satisfied"] is True

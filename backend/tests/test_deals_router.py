import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _fake_deal(status: str = "company_enriched") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "public_id": "LD-2026-0001",
        "company_id": str(uuid.uuid4()),
        "partner_org_id": None,
        "submitted_by_user_id": None,
        "status": status,
        "amount_cents": 10_000_000,
        "currency": "EUR",
        "duration_months": 36,
        "risk_score": None,
        "risk_band": None,
        "monthly_payment_cents": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.mark.asyncio
async def test_create_deal_success(make_token, test_ec_key):
    token = make_token("user-abc", "partner")
    fake = _fake_deal()
    with patch(
        "app.routers.deals.deal_service.create_deal",
        new_callable=AsyncMock,
        return_value=fake,
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/deals",
                    json={
                        "company_id": str(uuid.uuid4()),
                        "amount_cents": 10_000_000,
                        "duration_months": 36,
                    },
                    headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "key-abc"},
                )
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "company_enriched"


@pytest.mark.asyncio
async def test_create_deal_idempotent_returns_existing(make_token, test_ec_key):
    from app.core import idempotency

    token = make_token("user-abc", "partner")
    fake = _fake_deal()
    idempotency.set_key("idem-key-xyz", fake)
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/deals",
                json={
                    "company_id": str(uuid.uuid4()),
                    "amount_cents": 10_000_000,
                    "duration_months": 36,
                },
                headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "idem-key-xyz"},
            )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "company_enriched"


@pytest.mark.asyncio
async def test_get_deal(make_token, test_ec_key):
    token = make_token("user-abc", "partner")
    deal_id = str(uuid.uuid4())
    fake = _fake_deal()
    with patch(
        "app.routers.deals.deal_service.get_deal",
        new_callable=AsyncMock,
        return_value=fake,
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    f"/deals/{deal_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_get_deal_not_found(make_token, test_ec_key):
    from app.core.errors import AppError

    token = make_token("user-abc", "partner")
    deal_id = str(uuid.uuid4())
    with patch(
        "app.routers.deals.deal_service.get_deal",
        new_callable=AsyncMock,
        side_effect=AppError(404, "DEAL_NOT_FOUND", "Deal not found"),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    f"/deals/{deal_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEAL_NOT_FOUND"


@pytest.mark.asyncio
async def test_submit_deal_invalid_transition(make_token, test_ec_key):
    from app.core.errors import AppError

    token = make_token("user-abc", "partner")
    deal_id = str(uuid.uuid4())
    with patch(
        "app.routers.deals.deal_service.submit_deal",
        new_callable=AsyncMock,
        side_effect=AppError(
            409,
            "INVALID_TRANSITION",
            "Cannot submit",
            {"current_status": "draft", "allowed_next": ["company_enriched", "cancelled"]},
        ),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/deals/{deal_id}/submit",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_TRANSITION"


@pytest.mark.asyncio
async def test_deal_timeline_returns_empty_list(make_token, test_ec_key):
    token = make_token("user-abc", "partner")
    deal_id = str(uuid.uuid4())
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/deals/{deal_id}/timeline",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.asyncio
async def test_deals_no_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/deals")
    assert response.status_code == 401

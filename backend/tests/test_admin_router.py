import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.deal import Deal


def _fake_deal(status: str = "submitted") -> MagicMock:
    d = MagicMock(spec=Deal)
    d.id = uuid.uuid4()
    d.public_id = "LD-2026-TEST"
    d.company_id = uuid.uuid4()
    d.partner_org_id = None
    d.submitted_by_user_id = None
    d.status = status
    d.amount_cents = 10_000_000
    d.currency = "EUR"
    d.duration_months = 36
    d.risk_score = 45.0
    d.risk_band = "medium"
    d.monthly_payment_cents = 280000
    d.created_at = datetime.now(timezone.utc)
    d.updated_at = datetime.now(timezone.utc)
    return d


_USER_OPS_ID = str(uuid.uuid4())
_USER_RISK_ID = str(uuid.uuid4())
_USER_ADMIN_ID = str(uuid.uuid4())
_USER_PARTNER_ID = str(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_queue_returns_deals(make_token, test_ec_key):
    deals = [_fake_deal("submitted"), _fake_deal("internal_review")]
    token = make_token(_USER_OPS_ID, "ops")
    with patch("app.routers.admin.admin_service.get_queue", new_callable=AsyncMock, return_value=deals):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/admin/queue", headers={"Authorization": f"Bearer {token}"}
                )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["meta"]["total"] == 2


@pytest.mark.asyncio
async def test_get_queue_forbidden_for_partner(make_token, test_ec_key):
    token = make_token(_USER_PARTNER_ID, "partner")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/admin/queue", headers={"Authorization": f"Bearer {token}"}
            )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_risk_can_read_queue(make_token, test_ec_key):
    token = make_token(_USER_RISK_ID, "risk")
    with patch("app.routers.admin.admin_service.get_queue", new_callable=AsyncMock, return_value=[]):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/admin/queue", headers={"Authorization": f"Bearer {token}"}
                )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_start_review_forbidden_for_risk(make_token, test_ec_key):
    token = make_token(_USER_RISK_ID, "risk")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/admin/deals/{uuid.uuid4()}/start-review",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_start_review_returns_deal(make_token, test_ec_key):
    deal = _fake_deal("internal_review")
    token = make_token(_USER_OPS_ID, "ops")
    with patch("app.routers.admin.admin_service.start_review", new_callable=AsyncMock, return_value=deal):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/admin/deals/{deal.id}/start-review",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "internal_review"


@pytest.mark.asyncio
async def test_pre_approve_returns_deal(make_token, test_ec_key):
    deal = _fake_deal("pre_approved")
    token = make_token(_USER_ADMIN_ID, "admin")
    with patch("app.routers.admin.admin_service.pre_approve", new_callable=AsyncMock, return_value=deal):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/admin/deals/{deal.id}/pre-approve",
                    json={"justification": None},
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "pre_approved"


@pytest.mark.asyncio
async def test_pre_approve_surfaces_reason_required_when_override_missing(make_token, test_ec_key):
    from app.core.errors import AppError

    token = make_token(_USER_ADMIN_ID, "admin")
    with patch(
        "app.routers.admin.admin_service.pre_approve",
        new_callable=AsyncMock,
        side_effect=AppError(422, "REASON_REQUIRED", "justification required for manual override"),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/admin/deals/{uuid.uuid4()}/pre-approve",
                    json={"justification": None},
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "REASON_REQUIRED"


@pytest.mark.asyncio
async def test_reject_surfaces_reason_required(make_token, test_ec_key):
    from app.core.errors import AppError

    token = make_token(_USER_OPS_ID, "ops")
    with patch(
        "app.routers.admin.admin_service.reject",
        new_callable=AsyncMock,
        side_effect=AppError(422, "REASON_REQUIRED", "reason required"),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/admin/deals/{uuid.uuid4()}/reject",
                    json={"reason": ""},
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "REASON_REQUIRED"

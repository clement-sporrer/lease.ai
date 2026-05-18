import datetime
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _make_offer() -> MagicMock:
    offer = MagicMock()
    offer.id = uuid.uuid4()
    offer.deal_id = uuid.uuid4()
    offer.version = 1
    offer.is_active = True
    offer.amount_cents = 8_000_000
    offer.duration_months = 36
    offer.monthly_payment_cents = 240_000
    offer.risk_band = "B"
    offer.currency = "EUR"
    offer.valid_until = None
    offer.created_at = datetime.datetime.now(datetime.timezone.utc)
    return offer


@pytest.mark.anyio
async def test_generate_offer_returns_201(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    offer = _make_offer()

    with (
        patch("app.routers.offers.offer_service.generate_offer", new=AsyncMock(return_value=offer)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/deals/{offer.deal_id}/offers",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 201
    assert res.json()["data"]["version"] == 1
    assert res.json()["data"]["is_active"] is True


@pytest.mark.anyio
async def test_get_active_offer_returns_200(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    offer = _make_offer()
    offer.version = 2

    with (
        patch("app.routers.offers.offer_service.get_active_offer", new=AsyncMock(return_value=offer)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(
                f"/deals/{offer.deal_id}/offers/active",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"]["version"] == 2


@pytest.mark.anyio
async def test_get_active_offer_returns_404_when_none(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    deal_id = uuid.uuid4()

    with (
        patch("app.routers.offers.offer_service.get_active_offer", new=AsyncMock(return_value=None)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(
                f"/deals/{deal_id}/offers/active",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "OFFER_NOT_FOUND"


@pytest.mark.anyio
async def test_list_offers_returns_200(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    offer1 = _make_offer()
    offer1.version = 2
    offer1.is_active = True
    offer2 = _make_offer()
    offer2.deal_id = offer1.deal_id
    offer2.version = 1
    offer2.is_active = False

    with (
        patch("app.routers.offers.offer_service.list_offers", new=AsyncMock(return_value=[offer1, offer2])),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(
                f"/deals/{offer1.deal_id}/offers",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert isinstance(res.json()["data"], list)
    assert len(res.json()["data"]) == 2

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.db import get_db
from app.main import app


@pytest.mark.asyncio
async def test_indicative_pricing_success(make_token, test_ec_key):
    token = make_token("00000000-0000-0000-0000-000000000001", "partner")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/pricing/indicative",
                json={"amount_cents": 10_000_000, "duration_months": 36},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["type"] == "indicative"
    assert body["data"]["monthly_payment_cents"] > 0
    assert body["data"]["amount_financed_cents"] == 10_000_000


@pytest.mark.asyncio
async def test_indicative_pricing_no_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/pricing/indicative",
            json={"amount_cents": 10_000_000, "duration_months": 36},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_latest_pricing_none_is_enveloped(make_token, test_ec_key):
    token = make_token("00000000-0000-0000-0000-000000000001", "partner")

    class FakeResult:
        def scalar_one_or_none(self):
            return None

    class FakeDb:
        async def execute(self, _query):
            return FakeResult()

    async def override_get_db():
        yield FakeDb()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/deals/{uuid.uuid4()}/pricing",
                    headers={"Authorization": f"Bearer {token}"},
                )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json() == {"data": None}

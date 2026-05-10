from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

FAKE_COMPANY = {
    "id": "00000000-0000-0000-0000-000000000001",
    "siren": "823456789",
    "siret": None,
    "legal_name": "ACME SAS",
    "trade_name": None,
    "address": {"street": "1 rue de la Paix", "city": "Paris", "zip": "75001"},
    "activity_code": "6201Z",
    "creation_date": "2019-03-15",
    "legal_status": "SAS",
    "is_active": True,
    "enrichment_source": "mock",
    "created_at": "2026-05-10T00:00:00Z",
}


@pytest.mark.asyncio
async def test_enrich_valid_siren(make_token, test_ec_key):
    token = make_token("user-abc", "partner")
    with patch(
        "app.routers.companies.enrichment_service.enrich_and_upsert",
        new_callable=AsyncMock,
        return_value=FAKE_COMPANY,
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/companies/enrich",
                    json={"siren_or_siret": "823456789"},
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 201
    body = response.json()
    assert body["data"]["siren"] == "823456789"
    assert body["data"]["legal_name"] == "ACME SAS"


@pytest.mark.asyncio
async def test_enrich_invalid_siren_format(make_token, test_ec_key):
    token = make_token("user-abc", "partner")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/companies/enrich",
                json={"siren_or_siret": "ABC123"},
                headers={"Authorization": f"Bearer {token}"},
            )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_enrich_no_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/companies/enrich", json={"siren_or_siret": "823456789"})
    assert response.status_code == 401

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _fake_document(deal_id: str, document_id: str | None = None) -> dict:
    return {
        "id": document_id or str(uuid.uuid4()),
        "deal_id": deal_id,
        "type": "quote",
        "status": "uploaded",
        "file_name": "quote.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 1234,
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.mark.asyncio
async def test_upload_url_success(make_token, test_ec_key):
    token = make_token("00000000-0000-0000-0000-000000000001", "partner")
    deal_id = str(uuid.uuid4())
    document_id = str(uuid.uuid4())
    with patch(
        "app.routers.documents.document_service.create_upload_url",
        new_callable=AsyncMock,
        return_value={
            "document_id": document_id,
            "upload_url": "https://storage.example/upload",
            "expires_in": 7200,
        },
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/deals/{deal_id}/documents/upload-url",
                    headers={"Authorization": f"Bearer {token}"},
                )

    assert response.status_code == 201
    body = response.json()
    assert body["data"]["document_id"] == document_id
    assert body["data"]["upload_url"] == "https://storage.example/upload"
    assert "storage_key" not in body["data"]


@pytest.mark.asyncio
async def test_confirm_upload_success(make_token, test_ec_key):
    token = make_token("00000000-0000-0000-0000-000000000001", "partner")
    deal_id = str(uuid.uuid4())
    document_id = str(uuid.uuid4())
    with patch(
        "app.routers.documents.document_service.confirm_upload",
        new_callable=AsyncMock,
        return_value=_fake_document(deal_id, document_id),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/deals/{deal_id}/documents/confirm",
                    json={
                        "document_id": document_id,
                        "storage_key": f"deals/{deal_id}/{document_id}",
                        "file_name": "quote.pdf",
                        "mime_type": "application/pdf",
                        "size_bytes": 1234,
                        "document_type": "quote",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "uploaded"


@pytest.mark.asyncio
async def test_documents_no_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(f"/deals/{uuid.uuid4()}/documents/upload-url")
    assert response.status_code == 401

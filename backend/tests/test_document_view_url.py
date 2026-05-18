import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.errors import AppError
from app.services import document_service


@pytest.mark.asyncio
async def test_get_view_url_returns_url():
    doc_id = uuid.uuid4()
    deal_id = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc.id = doc_id
    mock_doc.deal_id = deal_id
    mock_doc.storage_key = f"deals/{deal_id}/{doc_id}"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc

    db = AsyncMock()
    db.execute = AsyncMock(return_value=mock_result)

    fake_signed_path = f"/storage/v1/object/sign/documents/deals/{deal_id}/{doc_id}?token=abc"

    with patch("app.services.document_service.httpx") as mock_httpx:
        mock_response = MagicMock()
        mock_response.json.return_value = {"signedURL": fake_signed_path}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_httpx.AsyncClient.return_value = mock_client

        result = await document_service.get_view_url(db, doc_id, "admin")

    assert result["url"].endswith("?token=abc")
    assert result["expires_in"] == 3600


@pytest.mark.asyncio
async def test_get_view_url_raises_when_no_storage_key():
    doc_id = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc.storage_key = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc

    db = AsyncMock()
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(AppError) as exc_info:
        await document_service.get_view_url(db, doc_id, "admin")

    assert exc_info.value.code == "DOCUMENT_NOT_UPLOADED"


@pytest.mark.asyncio
async def test_get_view_url_raises_when_not_found():
    doc_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    db = AsyncMock()
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(AppError) as exc_info:
        await document_service.get_view_url(db, doc_id, "admin")

    assert exc_info.value.code == "DOCUMENT_NOT_FOUND"

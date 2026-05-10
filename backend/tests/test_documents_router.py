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
        "app.routers.documents.document_service.confirm_upload_and_maybe_resume_review",
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


@pytest.mark.asyncio
async def test_validate_document_ops_succeeds(make_token, test_ec_key):
    from unittest.mock import MagicMock

    from app.models.document import Document as DocModel

    doc_id = uuid.uuid4()
    fake_doc = MagicMock(spec=DocModel)
    fake_doc.id = doc_id
    fake_doc.deal_id = uuid.uuid4()
    fake_doc.type = "rib"
    fake_doc.status = "validated"
    fake_doc.file_name = "rib.pdf"
    fake_doc.mime_type = None
    fake_doc.size_bytes = None
    fake_doc.version = 1
    fake_doc.created_at = datetime.now(timezone.utc)

    token = make_token(str(uuid.uuid4()), "ops")
    with patch(
        "app.routers.documents.document_service.validate_document",
        new_callable=AsyncMock,
        return_value=fake_doc,
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/documents/{doc_id}/validate",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "validated"


@pytest.mark.asyncio
async def test_validate_document_risk_forbidden(make_token, test_ec_key):
    token = make_token(str(uuid.uuid4()), "risk")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/documents/{uuid.uuid4()}/validate",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reject_document_surfaces_reason_required(make_token, test_ec_key):
    from app.core.errors import AppError as _AppError

    token = make_token(str(uuid.uuid4()), "ops")
    with patch(
        "app.routers.documents.document_service.reject_document",
        new_callable=AsyncMock,
        side_effect=_AppError(422, "REASON_REQUIRED", "reason required"),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/documents/{uuid.uuid4()}/reject",
                    json={"reason": ""},
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "REASON_REQUIRED"


# ─── auto-transition service-level tests ────────────────────────────────────

@pytest.mark.asyncio
async def test_confirm_upload_and_maybe_resume_review_transitions_when_missing_documents():
    from unittest.mock import AsyncMock, MagicMock, patch
    from app.services import document_service, audit_service
    from app.models.deal import Deal
    from app.models.document import Document

    deal_id = uuid.uuid4()
    document_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    fake_doc = MagicMock(spec=Document)
    fake_doc.id = document_id
    fake_doc.deal_id = deal_id

    fake_deal = MagicMock(spec=Deal)
    fake_deal.id = deal_id
    fake_deal.status = "missing_documents"

    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = fake_deal

    db = AsyncMock()
    db.execute.return_value = deal_result

    with patch.object(document_service, "confirm_upload", new_callable=AsyncMock, return_value=fake_doc):
        with patch.object(audit_service, "log", new_callable=AsyncMock) as mock_log:
            result = await document_service.confirm_upload_and_maybe_resume_review(
                db=db,
                deal_id=deal_id,
                document_id=document_id,
                file_name="doc.pdf",
                mime_type="application/pdf",
                size_bytes=1024,
                document_type="rib",
                actor_id=actor_id,
                actor_role="partner",
            )

    assert result is fake_doc
    assert fake_deal.status == "internal_review"
    mock_log.assert_called_once()
    log_kwargs = mock_log.call_args.kwargs
    assert log_kwargs["action"] == "status_transition"
    assert log_kwargs["payload"]["from"] == "missing_documents"
    db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_confirm_upload_and_maybe_resume_review_no_transition_when_not_missing_documents():
    from unittest.mock import AsyncMock, MagicMock, patch
    from app.services import document_service, audit_service
    from app.models.deal import Deal
    from app.models.document import Document

    deal_id = uuid.uuid4()
    document_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    fake_doc = MagicMock(spec=Document)
    fake_doc.id = document_id
    fake_doc.deal_id = deal_id

    fake_deal = MagicMock(spec=Deal)
    fake_deal.id = deal_id
    fake_deal.status = "internal_review"  # NOT missing_documents

    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = fake_deal

    db = AsyncMock()
    db.execute.return_value = deal_result

    with patch.object(document_service, "confirm_upload", new_callable=AsyncMock, return_value=fake_doc):
        with patch.object(audit_service, "log", new_callable=AsyncMock) as mock_log:
            result = await document_service.confirm_upload_and_maybe_resume_review(
                db=db,
                deal_id=deal_id,
                document_id=document_id,
                file_name="doc.pdf",
                mime_type="application/pdf",
                size_bytes=1024,
                document_type="rib",
                actor_id=actor_id,
                actor_role="partner",
            )

    assert result is fake_doc
    assert fake_deal.status == "internal_review"  # unchanged
    mock_log.assert_not_called()
    db.commit.assert_not_called()

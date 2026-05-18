import uuid

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.models.document import Document

_SIGNED_URL_EXPIRES = 3600


def _as_uuid(value: str | uuid.UUID | None) -> uuid.UUID | None:
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(value)


async def create_upload_url(db: AsyncSession, deal_id: uuid.UUID, user_id: str | None) -> dict:
    document_id = uuid.uuid4()
    storage_key = f"deals/{deal_id}/{document_id}"

    url = f"{settings.supabase_url}/storage/v1/object/upload/sign/{settings.object_storage_bucket}/{storage_key}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, headers=headers)
        except httpx.RequestError as exc:
            raise AppError(502, "STORAGE_UNAVAILABLE", "Storage service unavailable") from exc

    if response.status_code != 200:
        raise AppError(502, "STORAGE_URL_FAILED", "Failed to generate upload URL")

    payload = response.json()
    signed_url = payload.get("url") or payload.get("signedURL", "")
    if signed_url.startswith("/"):
        upload_url = f"{settings.supabase_url}/storage/v1{signed_url}"
    else:
        upload_url = signed_url

    document = Document(
        id=document_id,
        deal_id=deal_id,
        type="quote",
        status="pending_upload",
        file_name="",
        storage_key=storage_key,
        uploaded_by_user_id=_as_uuid(user_id),
    )
    db.add(document)
    await db.commit()

    return {
        "document_id": document_id,
        "upload_url": upload_url,
        "expires_in": _SIGNED_URL_EXPIRES,
    }


async def confirm_upload(
    db: AsyncSession,
    deal_id: uuid.UUID,
    document_id: uuid.UUID,
    file_name: str,
    mime_type: str,
    size_bytes: int,
    document_type: str,
) -> Document:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.deal_id == deal_id)
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise AppError(404, "DOCUMENT_NOT_FOUND", f"Document {document_id} not found")

    document.file_name = file_name
    document.mime_type = mime_type
    document.size_bytes = size_bytes
    document.type = document_type
    document.status = "uploaded"
    await db.commit()
    await db.refresh(document)
    return document


async def validate_document(
    db: AsyncSession,
    document_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
) -> Document:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise AppError(404, "DOCUMENT_NOT_FOUND", f"Document {document_id} not found")

    document.status = "validated"
    document.validated_by_user_id = actor_id

    from app.services import audit_service

    await audit_service.log(
        db=db,
        deal_id=document.deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="document_validated",
        payload={"document_id": str(document_id), "document_type": document.type},
    )
    await db.commit()
    await db.refresh(document)
    return document


async def reject_document(
    db: AsyncSession,
    document_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    reason: str,
) -> Document:
    if not reason or not reason.strip():
        raise AppError(422, "REASON_REQUIRED", "A reason is required to reject a document")

    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise AppError(404, "DOCUMENT_NOT_FOUND", f"Document {document_id} not found")

    document.status = "rejected"

    from app.services import audit_service

    await audit_service.log(
        db=db,
        deal_id=document.deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="document_rejected",
        payload={
            "document_id": str(document_id),
            "document_type": document.type,
            "reason": reason,
        },
    )
    await db.commit()
    await db.refresh(document)
    return document


async def get_view_url(
    db: AsyncSession,
    document_id: uuid.UUID,
    actor_role: str,
    actor_id: uuid.UUID | None = None,
) -> dict:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise AppError(404, "DOCUMENT_NOT_FOUND", f"Document {document_id} not found")
    if document.storage_key is None:
        raise AppError(409, "DOCUMENT_NOT_UPLOADED", "Document has no file uploaded yet")

    sign_url = (
        f"{settings.supabase_url}/storage/v1/object/sign"
        f"/{settings.object_storage_bucket}/{document.storage_key}"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                sign_url,
                headers={
                    "Authorization": f"Bearer {settings.supabase_service_role_key}",
                    "apikey": settings.supabase_service_role_key,
                },
                json={"expiresIn": _SIGNED_URL_EXPIRES},
            )
    except httpx.RequestError as exc:
        raise AppError(502, "STORAGE_UNAVAILABLE", "Storage service unavailable") from exc

    if resp.status_code != 200:
        raise AppError(502, "STORAGE_SIGN_FAILED", f"Supabase storage sign request failed with status {resp.status_code}")

    payload = resp.json()

    signed_path: str = payload.get("signedURL") or payload.get("signedUrl") or ""
    if signed_path.startswith("/"):
        view_url = f"{settings.supabase_url}/storage/v1{signed_path}"
    else:
        view_url = signed_path

    if actor_id is not None:
        from app.services import audit_service

        await audit_service.log(
            db=db,
            deal_id=document.deal_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action="DOCUMENT_VIEWED",
            payload={"document_id": str(document_id), "document_type": document.type},
        )

    return {"url": view_url, "expires_in": _SIGNED_URL_EXPIRES}


async def confirm_upload_and_maybe_resume_review(
    db: AsyncSession,
    deal_id: uuid.UUID,
    document_id: uuid.UUID,
    file_name: str,
    mime_type: str,
    size_bytes: int,
    document_type: str,
    actor_id: uuid.UUID | None = None,
    actor_role: str = "partner",
) -> Document:
    from app.models.deal import Deal

    document = await confirm_upload(
        db, deal_id, document_id, file_name, mime_type, size_bytes, document_type
    )

    deal_result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = deal_result.scalar_one_or_none()

    if deal is not None and deal.status == "missing_documents" and actor_id is not None:
        deal.status = "internal_review"
        from app.services import audit_service

        await audit_service.log(
            db=db,
            deal_id=deal_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action="status_transition",
            payload={
                "from": "missing_documents",
                "to": "internal_review",
                "trigger": "document_uploaded",
            },
        )
        await db.commit()

    return document

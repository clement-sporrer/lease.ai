import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.roles import UserRole
from app.models.document import Document
from app.schemas.document import (
    DocumentConfirmRequest,
    DocumentRejectRequest,
    DocumentResponse,
    DocumentUploadUrlResponse,
)
from app.services import document_service

router = APIRouter(tags=["documents"])

_DOC_WRITE_ROLES = {UserRole.admin, UserRole.ops}


@router.post("/deals/{deal_id}/documents/upload-url", status_code=201)
async def get_upload_url(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await document_service.create_upload_url(db, deal_id, current_user["user_id"])
    return {"data": DocumentUploadUrlResponse(**result).model_dump(mode="json")}


@router.post("/deals/{deal_id}/documents/confirm")
async def confirm_upload(
    deal_id: uuid.UUID,
    body: DocumentConfirmRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    raw_user_id = current_user.get("user_id")
    try:
        actor_id: uuid.UUID | None = uuid.UUID(raw_user_id) if raw_user_id else None
    except ValueError:
        actor_id = None
    actor_role = current_user.get("active_role", "partner")
    if isinstance(actor_role, UserRole):
        actor_role = actor_role.value
    document = await document_service.confirm_upload_and_maybe_resume_review(
        db=db,
        deal_id=deal_id,
        document_id=body.document_id,
        file_name=body.file_name,
        mime_type=body.mime_type,
        size_bytes=body.size_bytes,
        document_type=body.document_type,
        actor_id=actor_id,
        actor_role=actor_role,
    )
    return {"data": DocumentResponse.model_validate(document).model_dump(mode="json")}


@router.post("/documents/{document_id}/validate")
async def validate_document(
    document_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if current_user.get("active_role") not in _DOC_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: ops or admin required")
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    if isinstance(actor_role, UserRole):
        actor_role = actor_role.value
    document = await document_service.validate_document(db, document_id, actor_id, actor_role)
    return {"data": DocumentResponse.model_validate(document).model_dump(mode="json")}


@router.post("/documents/{document_id}/reject")
async def reject_document(
    document_id: uuid.UUID,
    body: DocumentRejectRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if current_user.get("active_role") not in _DOC_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: ops or admin required")
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    if isinstance(actor_role, UserRole):
        actor_role = actor_role.value
    document = await document_service.reject_document(
        db, document_id, actor_id, actor_role, body.reason
    )
    return {"data": DocumentResponse.model_validate(document).model_dump(mode="json")}


_DOC_READ_ROLES = {UserRole.admin, UserRole.ops, UserRole.risk}


@router.get("/documents/{document_id}/view-url")
async def get_document_view_url(
    document_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    actor_role = current_user.get("active_role", "")
    if isinstance(actor_role, UserRole):
        actor_role = actor_role.value
    if actor_role not in {r.value for r in _DOC_READ_ROLES}:
        raise HTTPException(status_code=403, detail="Forbidden: admin, ops or risk required")
    raw_user_id = current_user.get("user_id")
    try:
        actor_id: uuid.UUID | None = uuid.UUID(raw_user_id) if raw_user_id else None
    except ValueError:
        actor_id = None
    result = await document_service.get_view_url(db, document_id, actor_role, actor_id)
    return {"data": result}


@router.get("/deals/{deal_id}/documents")
async def list_documents(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    result = await db.execute(select(Document).where(Document.deal_id == deal_id))
    documents = list(result.scalars().all())
    return {
        "data": [
            DocumentResponse.model_validate(document).model_dump(mode="json")
            for document in documents
        ],
        "meta": {"total": len(documents)},
    }

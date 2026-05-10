import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.document import Document
from app.schemas.document import (
    DocumentConfirmRequest,
    DocumentResponse,
    DocumentUploadUrlResponse,
)
from app.services import document_service

router = APIRouter(tags=["documents"])


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
    del current_user
    document = await document_service.confirm_upload(
        db=db,
        deal_id=deal_id,
        document_id=body.document_id,
        storage_key=body.storage_key,
        file_name=body.file_name,
        mime_type=body.mime_type,
        size_bytes=body.size_bytes,
        document_type=body.document_type,
    )
    return {"data": DocumentResponse.model_validate(document).model_dump(mode="json")}


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

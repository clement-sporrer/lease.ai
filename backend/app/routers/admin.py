import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.roles import UserRole
from app.schemas.admin import PreApproveRequest, RejectRequest, RequestDocumentRequest
from app.schemas.deal import DealResponse
from app.services import admin_service

_READ_ROLES = {UserRole.admin, UserRole.ops, UserRole.risk}
_WRITE_ROLES = {UserRole.admin, UserRole.ops}

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_read(current_user: dict) -> None:
    if current_user.get("active_role") not in _READ_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: internal roles only")


def _require_write(current_user: dict) -> None:
    if current_user.get("active_role") not in _WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: ops or admin required")


@router.get("/queue")
async def get_queue(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    deals, total = await admin_service.get_queue(
        db, status=status, search=search, page=page, page_size=page_size
    )
    return {
        "data": [DealResponse.model_validate(d).model_dump(mode="json") for d in deals],
        "meta": {"total": total, "page": page, "page_size": page_size},
    }


@router.get("/deals/{deal_id}/checklist")
async def get_checklist(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    checklist = await admin_service.get_checklist(db, deal_id)
    return {"data": checklist}


@router.post("/deals/{deal_id}/start-review")
async def start_review(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    deal = await admin_service.start_review(db, deal_id, actor_id, actor_role)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/deals/{deal_id}/request-document")
async def request_document(
    deal_id: uuid.UUID,
    body: RequestDocumentRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    deal = await admin_service.request_document(
        db, deal_id, actor_id, actor_role, body.document_type, body.reason
    )
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/deals/{deal_id}/pre-approve")
async def pre_approve(
    deal_id: uuid.UUID,
    body: PreApproveRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    deal = await admin_service.pre_approve(db, deal_id, actor_id, actor_role, body.justification)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/deals/{deal_id}/reject")
async def reject(
    deal_id: uuid.UUID,
    body: RejectRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    deal = await admin_service.reject(db, deal_id, actor_id, actor_role, body.reason)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import idempotency
from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.roles import UserRole
from app.schemas.deal import DealCreateRequest, DealPatchRequest, DealResponse, DealStatusRequest
from app.services import deal_service

_INTERNAL_ROLES = {UserRole.admin, UserRole.ops}

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", status_code=201)
async def create_deal(
    body: DealCreateRequest,
    response: Response,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if idempotency_key:
        cached = idempotency.get(idempotency_key)
        if cached is not None:
            response.status_code = 200
            return {"data": cached}

    deal = await deal_service.create_deal(
        db=db,
        company_id=body.company_id,
        user_id=current_user["user_id"],
        amount_cents=body.amount_cents,
        currency=body.currency,
        duration_months=body.duration_months,
    )
    serialized = DealResponse.model_validate(deal).model_dump(mode="json")
    if idempotency_key:
        idempotency.set_key(idempotency_key, serialized)
    return {"data": serialized}


@router.get("")
async def list_deals(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # TODO(phase4): filter by partner_org_id for partner_user once profile→org lookup is wired
    deals, total = await deal_service.list_deals(db, page=page, per_page=per_page)
    return {
        "data": [DealResponse.model_validate(deal).model_dump(mode="json") for deal in deals],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{deal_id}")
async def get_deal(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    deal = await deal_service.get_deal(db, deal_id)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.patch("/{deal_id}")
async def patch_deal(
    deal_id: uuid.UUID,
    body: DealPatchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    deal = await deal_service.patch_deal(
        db=db,
        deal_id=deal_id,
        amount_cents=body.amount_cents,
        duration_months=body.duration_months,
        currency=body.currency,
    )
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/{deal_id}/submit")
async def submit_deal(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    deal = await deal_service.submit_deal(db, deal_id, current_user["user_id"])
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/{deal_id}/status")
async def transition_deal_status(
    deal_id: uuid.UUID,
    body: DealStatusRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if current_user.get("active_role") not in _INTERNAL_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: internal endpoint")
    deal = await deal_service.transition_deal(db, deal_id, body.status)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.get("/{deal_id}/timeline")
async def get_deal_timeline(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    from app.schemas.admin import AuditEventResponse
    from app.services import audit_service as _audit_service
    events = await _audit_service.get_timeline(db, deal_id)
    return {
        "data": [AuditEventResponse.model_validate(e).model_dump(mode="json") for e in events],
        "meta": {"total": len(events)},
    }

import uuid
from typing import Any

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.deal import Deal
from app.models.document import Document
from app.services import audit_service
from app.services.deal_service import _assert_transition

_QUEUE_STATUSES = ("submitted", "internal_review", "missing_documents")

_STATUS_PRIORITY = case(
    (Deal.status == "submitted", 0),
    (Deal.status == "internal_review", 1),
    (Deal.status == "missing_documents", 2),
    else_=3,
)


async def _get_deal(db: AsyncSession, deal_id: uuid.UUID) -> Deal:
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if deal is None:
        raise AppError(404, "DEAL_NOT_FOUND", f"Deal {deal_id} not found")
    return deal


async def get_queue(db: AsyncSession) -> list[Deal]:
    result = await db.execute(
        select(Deal)
        .where(Deal.status.in_(_QUEUE_STATUSES))
        .order_by(_STATUS_PRIORITY.asc(), Deal.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_checklist(db: AsyncSession, deal_id: uuid.UUID) -> dict[str, Any]:
    deal = await _get_deal(db, deal_id)

    doc_result = await db.execute(select(Document).where(Document.deal_id == deal_id))
    documents = list(doc_result.scalars().all())

    doc_statuses = [
        {"id": str(d.id), "type": d.type, "status": d.status, "file_name": d.file_name}
        for d in documents
    ]
    all_docs_validated = bool(documents) and all(d.status == "validated" for d in documents)
    has_risk_score = deal.risk_score is not None

    return {
        "deal_id": str(deal_id),
        "status": deal.status,
        "documents": doc_statuses,
        "risk_score": deal.risk_score,
        "risk_band": deal.risk_band,
        "pricing_monthly": deal.monthly_payment_cents,
        "all_docs_validated": all_docs_validated,
        "checklist_complete": all_docs_validated and has_risk_score,
    }


async def start_review(
    db: AsyncSession, deal_id: uuid.UUID, actor_id: uuid.UUID, actor_role: str
) -> Deal:
    deal = await _get_deal(db, deal_id)
    _assert_transition(deal.status, "internal_review")
    prev_status = deal.status
    deal.status = "internal_review"
    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="status_transition",
        payload={"from": prev_status, "to": "internal_review"},
    )
    await db.commit()
    await db.refresh(deal)
    return deal


async def request_document(
    db: AsyncSession,
    deal_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    document_type: str,
    reason: str,
) -> Deal:
    deal = await _get_deal(db, deal_id)
    _assert_transition(deal.status, "missing_documents")
    deal.status = "missing_documents"
    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="document_requested",
        payload={"document_type": document_type, "reason": reason},
    )
    await db.commit()
    await db.refresh(deal)
    return deal


async def pre_approve(
    db: AsyncSession,
    deal_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    justification: str | None = None,
) -> Deal:
    deal = await _get_deal(db, deal_id)
    _assert_transition(deal.status, "pre_approved")

    checklist = await get_checklist(db, deal_id)
    checklist_incomplete = not checklist["checklist_complete"]

    if checklist_incomplete and not justification:
        raise AppError(
            422,
            "REASON_REQUIRED",
            "Justification is required to override an incomplete checklist",
        )

    payload: dict[str, Any] = {}
    if checklist_incomplete:
        payload["manual_override"] = True
        payload["justification"] = justification
    elif justification:
        payload["justification"] = justification

    deal.status = "pre_approved"
    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="pre_approved",
        payload=payload or None,
    )
    await db.commit()
    await db.refresh(deal)
    return deal


async def reject(
    db: AsyncSession,
    deal_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    reason: str,
) -> Deal:
    if not reason or not reason.strip():
        raise AppError(422, "REASON_REQUIRED", "A reason is required to reject a deal")
    deal = await _get_deal(db, deal_id)
    _assert_transition(deal.status, "financier_rejected")
    deal.status = "financier_rejected"
    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="deal_rejected",
        payload={"reason": reason},
    )
    await db.commit()
    await db.refresh(deal)
    return deal

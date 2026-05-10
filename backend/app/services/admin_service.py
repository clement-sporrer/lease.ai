import uuid
from typing import Any

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.deal import Deal
from app.models.document import Document

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

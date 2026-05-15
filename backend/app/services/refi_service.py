from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.refi_package import FinancierDecision, RefiPackage
from app.services import deal_service

_DECISION_PKG_STATUS = {"approved": "financier_approved", "rejected": "financier_rejected"}


async def create_refi_package(
    db: AsyncSession, deal_id: uuid.UUID, user_id: str
) -> RefiPackage:
    deal = await deal_service.get_deal(db, deal_id)
    if deal.status != "pre_approved":
        raise AppError(
            409,
            "INVALID_TRANSITION",
            f"Cannot create refi package from status {deal.status!r} — deal must be pre_approved",
            {"current_status": deal.status},
        )
    pkg = RefiPackage(
        id=uuid.uuid4(),
        deal_id=deal_id,
        status="draft",
        amount_cents=deal.amount_cents,
        duration_months=deal.duration_months,
        monthly_payment_cents=deal.monthly_payment_cents,
        risk_score=float(deal.risk_score) if deal.risk_score is not None else None,
        risk_band=deal.risk_band,
    )
    db.add(pkg)
    await deal_service.transition_deal(db, deal_id, "refi_package_ready")
    await db.refresh(pkg)
    return pkg


async def send_package(db: AsyncSession, pkg: RefiPackage, deal_id: uuid.UUID) -> RefiPackage:
    if pkg.status != "draft":
        raise AppError(409, "INVALID_STATE", f"Package status is {pkg.status!r}, must be draft")
    pkg.status = "sent"
    pkg.sent_at = datetime.now(timezone.utc)
    await deal_service.transition_deal(db, deal_id, "refi_review")
    await db.refresh(pkg)
    return pkg


async def get_package(db: AsyncSession, package_id: uuid.UUID) -> RefiPackage:
    result = await db.execute(select(RefiPackage).where(RefiPackage.id == package_id))
    pkg = result.scalar_one_or_none()
    if pkg is None:
        raise AppError(404, "REFI_PACKAGE_NOT_FOUND", f"RefiPackage {package_id} not found")
    return pkg


async def list_packages_for_deal(db: AsyncSession, deal_id: uuid.UUID) -> list[RefiPackage]:
    result = await db.execute(
        select(RefiPackage).where(RefiPackage.deal_id == deal_id).order_by(RefiPackage.created_at.desc())
    )
    return list(result.scalars().all())


def _to_uuid(value: str) -> uuid.UUID:
    """Convert a string to UUID, raising AppError(500) on invalid input."""
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        raise AppError(500, "INVALID_USER_ID", f"Cannot parse user_id as UUID: {value!r}")


async def record_decision(
    db: AsyncSession,
    pkg: RefiPackage,
    deal,
    decision: str,
    reason: str | None,
    user_id: str,
) -> FinancierDecision:
    if decision == "rejected" and not reason:
        raise AppError(422, "REASON_REQUIRED", "Rejection requires a reason", {})
    target_status = "financier_approved" if decision == "approved" else "financier_rejected"
    dec = FinancierDecision(
        id=uuid.uuid4(),
        refi_package_id=pkg.id,
        decision=decision,
        reason=reason,
        decided_by_user_id=_to_uuid(user_id),
    )
    db.add(dec)
    pkg.status = _DECISION_PKG_STATUS[decision]
    await deal_service.transition_deal(db, deal.id, target_status)
    await db.refresh(dec)
    return dec

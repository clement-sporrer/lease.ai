from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.offer import Offer
from app.services import deal_service

_ALLOWED_STATUSES = {"financier_approved", "firm_offer_generated"}


async def generate_offer(db: AsyncSession, deal_id: uuid.UUID, user_id: str) -> Offer:
    deal = await deal_service.get_deal(db, deal_id)
    if deal.status not in _ALLOWED_STATUSES:
        raise AppError(
            409,
            "INVALID_STATE",
            f"Cannot generate offer from status {deal.status!r}",
            {"current_status": deal.status, "allowed": sorted(_ALLOWED_STATUSES)},
        )
    result = await db.execute(select(Offer).where(Offer.deal_id == deal_id))
    existing = list(result.scalars().all())
    for prev in existing:
        prev.is_active = False
    next_version = max((o.version for o in existing), default=0) + 1
    offer = Offer(
        id=uuid.uuid4(),
        deal_id=deal_id,
        version=next_version,
        is_active=True,
        amount_cents=deal.amount_cents,
        duration_months=deal.duration_months,
        monthly_payment_cents=deal.monthly_payment_cents,
        risk_band=deal.risk_band,
        currency=deal.currency,
    )
    db.add(offer)
    if deal.status == "financier_approved":
        await deal_service.transition_deal(db, deal_id, "firm_offer_generated")
    await db.commit()
    await db.refresh(offer)
    return offer


async def get_active_offer(db: AsyncSession, deal_id: uuid.UUID) -> Offer | None:
    result = await db.execute(
        select(Offer).where(Offer.deal_id == deal_id, Offer.is_active.is_(True))
    )
    return result.scalar_one_or_none()


async def list_offers(db: AsyncSession, deal_id: uuid.UUID) -> list[Offer]:
    result = await db.execute(
        select(Offer).where(Offer.deal_id == deal_id).order_by(Offer.version.desc())
    )
    return list(result.scalars().all())

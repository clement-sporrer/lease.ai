import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.profile import Profile
from app.models.deal import Deal

_ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["company_enriched", "cancelled"],
    "company_enriched": ["quote_added", "cancelled"],
    "quote_added": ["indicative_offer_ready", "cancelled"],
    "indicative_offer_ready": ["submitted", "cancelled"],
    "submitted": ["internal_review"],
    "internal_review": ["missing_documents", "pre_approved", "financier_rejected"],
    "missing_documents": ["internal_review", "cancelled"],
    "pre_approved": ["refi_package_ready"],
    "refi_package_ready": ["refi_review"],
    "refi_review": ["financier_approved", "financier_rejected", "missing_documents"],
    "financier_approved": ["firm_offer_generated"],
    "firm_offer_generated": ["contract_generated"],
    "contract_generated": ["signing"],
    "signing": ["signed"],
    "signed": ["activation_pending"],
    "activation_pending": ["active"],
    "active": [],
    "cancelled": [],
}

def _generate_public_id() -> str:
    suffix = uuid.uuid4().hex[:8].upper()
    return f"LD-{datetime.now(timezone.utc).year}-{suffix}"


def _as_uuid(value: str | uuid.UUID | None) -> uuid.UUID | None:
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(value)


def _assert_transition(current: str, target: str) -> None:
    if current == target:
        return
    allowed = _ALLOWED_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise AppError(
            status_code=409,
            code="INVALID_TRANSITION",
            message=f"Cannot transition from {current!r} to {target!r}",
            details={"current_status": current, "allowed_next": allowed},
        )


async def _ensure_profile_exists(db: AsyncSession, user_id: str | None) -> uuid.UUID | None:
    user_uuid = _as_uuid(user_id)
    if user_uuid is None:
        return None

    result = await db.execute(select(Profile).where(Profile.id == user_uuid))
    profile = result.scalar_one_or_none()
    if profile is None:
        db.add(Profile(id=user_uuid))
    return user_uuid


async def create_deal(
    db: AsyncSession,
    company_id: uuid.UUID,
    user_id: str | None,
    amount_cents: int | None = None,
    currency: str = "EUR",
    duration_months: int | None = None,
) -> Deal:
    submitted_by_user_id = await _ensure_profile_exists(db, user_id)
    deal = Deal(
        id=uuid.uuid4(),
        public_id=_generate_public_id(),
        company_id=company_id,
        submitted_by_user_id=submitted_by_user_id,
        status="company_enriched",
        amount_cents=amount_cents,
        currency=currency,
        duration_months=duration_months,
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


async def get_deal(db: AsyncSession, deal_id: uuid.UUID) -> Deal:
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if deal is None:
        raise AppError(404, "DEAL_NOT_FOUND", f"Deal {deal_id} not found")
    return deal


async def patch_deal(
    db: AsyncSession,
    deal_id: uuid.UUID,
    amount_cents: int | None = None,
    duration_months: int | None = None,
    currency: str | None = None,
) -> Deal:
    deal = await get_deal(db, deal_id)
    if amount_cents is not None:
        deal.amount_cents = amount_cents
    if duration_months is not None:
        deal.duration_months = duration_months
    if currency is not None:
        deal.currency = currency
    await db.commit()
    await db.refresh(deal)
    return deal


async def transition_deal(db: AsyncSession, deal_id: uuid.UUID, target_status: str) -> Deal:
    deal = await get_deal(db, deal_id)
    if deal.status == target_status:
        return deal
    _assert_transition(deal.status, target_status)
    deal.status = target_status
    await db.commit()
    await db.refresh(deal)
    return deal


async def submit_deal(db: AsyncSession, deal_id: uuid.UUID, user_id: str | None) -> Deal:
    deal = await get_deal(db, deal_id)
    _assert_transition(deal.status, "submitted")
    deal.status = "submitted"
    deal.submitted_by_user_id = await _ensure_profile_exists(db, user_id)
    await db.commit()
    await db.refresh(deal)
    return deal


async def list_deals(
    db: AsyncSession,
    partner_org_id: uuid.UUID | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Deal], int]:
    base_query = select(Deal)
    count_query = select(func.count()).select_from(Deal)
    if partner_org_id is not None:
        base_query = base_query.where(Deal.partner_org_id == partner_org_id)
        count_query = count_query.where(Deal.partner_org_id == partner_org_id)

    result = await db.execute(
        base_query.order_by(Deal.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    )
    deals = list(result.scalars().all())
    total = int((await db.execute(count_query)).scalar_one())
    return deals, total

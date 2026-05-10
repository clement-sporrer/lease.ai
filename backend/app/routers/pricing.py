import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.pricing_proposal import PricingProposal
from app.schemas.pricing import IndicativePricingRequest, PricingProposalResponse
from app.services import deal_service
from app.services.pricing_service import PRICING_VERSION, build_pricing_proposal, compute_monthly_payment

router = APIRouter(tags=["pricing"])


@router.post("/pricing/indicative")
async def compute_indicative(
    body: IndicativePricingRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    del current_user
    proposal = build_pricing_proposal(body)
    return {"data": proposal.model_dump(mode="json")}


@router.post("/deals/{deal_id}/pricing/recalculate", status_code=201)
async def recalculate_pricing(
    deal_id: uuid.UUID,
    body: IndicativePricingRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    deal = await deal_service.get_deal(db, deal_id)
    monthly = compute_monthly_payment(
        amount_cents=body.amount_cents,
        duration_months=body.duration_months,
        refi_rate=body.refi_rate,
        margin_rate=body.margin_rate,
        fees_cents=body.fees_cents,
    )
    proposal = PricingProposal(
        id=uuid.uuid4(),
        deal_id=deal_id,
        type="indicative",
        amount_financed_cents=body.amount_cents,
        duration_months=body.duration_months,
        monthly_payment_cents=monthly,
        refi_rate=body.refi_rate,
        margin_rate=body.margin_rate,
        fees_cents=body.fees_cents,
        assumptions={
            "refi_rate": body.refi_rate,
            "margin_rate": body.margin_rate,
            "fees_cents": body.fees_cents,
        },
        version=PRICING_VERSION,
        created_at=datetime.now(timezone.utc),
    )
    db.add(proposal)
    deal.monthly_payment_cents = monthly
    await db.flush()
    await deal_service.transition_deal(db, deal_id, "indicative_offer_ready")
    await db.refresh(proposal)
    return {"data": PricingProposalResponse.model_validate(proposal).model_dump(mode="json")}


@router.get("/deals/{deal_id}/pricing")
async def get_latest_pricing(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    result = await db.execute(
        select(PricingProposal)
        .where(PricingProposal.deal_id == deal_id)
        .order_by(PricingProposal.created_at.desc())
        .limit(1)
    )
    proposal = result.scalar_one_or_none()
    if proposal is None:
        return {"data": None}
    return {"data": PricingProposalResponse.model_validate(proposal).model_dump(mode="json")}

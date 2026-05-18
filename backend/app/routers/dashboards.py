from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.deal import Deal

router = APIRouter(tags=["dashboards"])


@router.get("/dashboards/cfo/portfolio")
async def cfo_portfolio(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    active_statuses = [
        "firm_offer_generated", "contract_generated", "signing", "signed",
        "activation_pending", "active", "financier_approved",
    ]
    pipeline_statuses = [
        "submitted", "internal_review", "pre_approved",
        "refi_package_ready", "refi_review",
    ]

    commitment_result = await db.execute(
        select(func.sum(Deal.amount_cents)).where(Deal.status.in_(active_statuses))
    )
    total_commitment_cents = commitment_result.scalar_one() or 0

    active_count_result = await db.execute(
        select(func.count()).where(Deal.status == "active")
    )
    active_leases = active_count_result.scalar_one()

    pipeline_count_result = await db.execute(
        select(func.count()).where(Deal.status.in_(pipeline_statuses))
    )
    pipeline_count = pipeline_count_result.scalar_one()

    total_deals_result = await db.execute(select(func.count()).select_from(Deal))
    total_deals = total_deals_result.scalar_one() or 1  # avoid division by zero

    rejected_result = await db.execute(
        select(func.count()).where(Deal.status == "financier_rejected")
    )
    rejected_count = rejected_result.scalar_one()
    default_rate_pct = round(rejected_count / total_deals * 100, 1)

    risk_rows = await db.execute(
        select(Deal.risk_band, func.count(), func.sum(Deal.amount_cents))
        .where(Deal.risk_band.isnot(None))
        .group_by(Deal.risk_band)
        .order_by(Deal.risk_band)
    )
    risk_distribution = [
        {"band": band, "count": count, "exposure_eur": int((amount_cents or 0) / 100)}
        for band, count, amount_cents in risk_rows.all()
    ]

    return {
        "data": {
            "active_leases": active_leases,
            "pipeline_deals": pipeline_count,
            "total_commitment_eur": int(total_commitment_cents / 100),
            "cash_collected_month_eur": 0,
            "cash_collected_ytd_eur": 0,
            "late_payments": 0,
            "default_rate_pct": default_rate_pct,
            "refi_approval_rate_pct": 0,
            "activation_rate_pct": 0,
            "exposure_by_partner": [],
            "risk_distribution": risk_distribution,
            "monthly": [],
        }
    }

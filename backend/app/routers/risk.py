import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.errors import AppError
from app.models.company import Company
from app.models.risk_assessment import RiskAssessment
from app.schemas.risk import RiskAssessmentResponse
from app.services import deal_service, risk_service

router = APIRouter(tags=["risk"])


@router.post("/deals/{deal_id}/risk/assess", status_code=201)
async def assess_risk_for_deal(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    deal = await deal_service.get_deal(db, deal_id)
    company_result = await db.execute(select(Company).where(Company.id == deal.company_id))
    company = company_result.scalar_one_or_none()
    if company is None:
        raise AppError(404, "COMPANY_NOT_FOUND", "Company not found for this deal")

    result = risk_service.assess_risk(
        creation_date=company.creation_date,
        amount_cents=deal.amount_cents or 0,
        activity_code=company.activity_code,
        is_active=company.is_active,
    )

    assessment = RiskAssessment(
        id=uuid.uuid4(),
        deal_id=deal_id,
        score=int(result["score"]),
        band=str(result["band"]),
        flags=list(result["flags"]),
        rules_applied=list(result["rules_applied"]),
        recommendation=str(result["recommendation"]),
        created_by=uuid.UUID(current_user["user_id"]),
        version=1,
        created_at=datetime.now(timezone.utc),
    )
    db.add(assessment)
    deal.risk_score = int(result["score"])
    deal.risk_band = str(result["band"])
    await db.commit()
    await db.refresh(assessment)
    return {"data": RiskAssessmentResponse.model_validate(assessment).model_dump(mode="json")}


@router.get("/deals/{deal_id}/risk/latest")
async def get_latest_risk(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.deal_id == deal_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(1)
    )
    assessment = result.scalar_one_or_none()
    if assessment is None:
        raise AppError(404, "RISK_NOT_FOUND", "No risk assessment found for this deal")
    return {"data": RiskAssessmentResponse.model_validate(assessment).model_dump(mode="json")}

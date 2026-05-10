import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.errors import AppError
from app.models.company import Company
from app.schemas.company import CompanyResponse, EnrichRequest
from app.services import enrichment_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/enrich", status_code=201)
async def enrich_company(
    body: EnrichRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    company = await enrichment_service.enrich_and_upsert(db, body.siren_or_siret)
    return {"data": CompanyResponse.model_validate(company).model_dump(mode="json")}


@router.get("/{company_id}")
async def get_company(
    company_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if company is None:
        raise AppError(404, "COMPANY_NOT_FOUND", f"Company {company_id} not found")
    return {"data": CompanyResponse.model_validate(company).model_dump(mode="json")}

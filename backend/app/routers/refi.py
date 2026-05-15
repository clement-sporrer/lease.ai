import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.schemas.refi import FinancierDecisionRequest, FinancierDecisionResponse, RefiPackageResponse
from app.services import deal_service, refi_service

router = APIRouter(tags=["refi"])


@router.post("/deals/{deal_id}/refi-packages", status_code=201)
async def create_refi_package(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    pkg = await refi_service.create_refi_package(db, deal_id, current_user["user_id"])
    return {"data": RefiPackageResponse.model_validate(pkg).model_dump(mode="json")}


@router.post("/refi-packages/{package_id}/send")
async def send_refi_package(
    package_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    pkg = await refi_service.get_package(db, package_id)
    pkg = await refi_service.send_package(db, pkg, pkg.deal_id)
    return {"data": RefiPackageResponse.model_validate(pkg).model_dump(mode="json")}


@router.get("/refi-packages")
async def list_all_refi_packages(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    packages = await refi_service.list_all_packages(db)
    return {"data": [RefiPackageResponse.model_validate(p).model_dump(mode="json") for p in packages]}


@router.get("/deals/{deal_id}/refi-packages")
async def list_refi_packages(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    packages = await refi_service.list_packages_for_deal(db, deal_id)
    return {"data": [RefiPackageResponse.model_validate(p).model_dump(mode="json") for p in packages]}


@router.get("/refi-packages/{package_id}")
async def get_refi_package(
    package_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    pkg = await refi_service.get_package(db, package_id)
    return {"data": RefiPackageResponse.model_validate(pkg).model_dump(mode="json")}


@router.post("/refi-packages/{package_id}/decision")
async def record_financier_decision(
    package_id: uuid.UUID,
    body: FinancierDecisionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    pkg = await refi_service.get_package(db, package_id)
    deal = await deal_service.get_deal(db, pkg.deal_id)
    dec = await refi_service.record_decision(
        db, pkg, deal, body.decision, body.reason, current_user["user_id"]
    )
    return {"data": FinancierDecisionResponse.model_validate(dec).model_dump(mode="json")}

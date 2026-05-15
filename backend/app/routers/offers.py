import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.errors import AppError
from app.schemas.offer import OfferResponse
from app.services import offer_service

router = APIRouter(tags=["offers"])


@router.post("/deals/{deal_id}/offers", status_code=201)
async def generate_offer(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    offer = await offer_service.generate_offer(db, deal_id, current_user["user_id"])
    return {"data": OfferResponse.model_validate(offer).model_dump(mode="json")}


@router.get("/deals/{deal_id}/offers/active")
async def get_active_offer(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    offer = await offer_service.get_active_offer(db, deal_id)
    if offer is None:
        raise AppError(404, "OFFER_NOT_FOUND", f"No active offer for deal {deal_id}")
    return {"data": OfferResponse.model_validate(offer).model_dump(mode="json")}


@router.get("/deals/{deal_id}/offers")
async def list_offers(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    offers = await offer_service.list_offers(db, deal_id)
    return {"data": [OfferResponse.model_validate(o).model_dump(mode="json") for o in offers]}

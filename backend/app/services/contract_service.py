# backend/app/services/contract_service.py
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.contract import Contract
from app.services import deal_service

_GENERATE_ALLOWED = {"firm_offer_generated", "contract_generated", "signing", "signed"}


async def _get_latest_contract(db: AsyncSession, deal_id: uuid.UUID) -> Contract | None:
    result = await db.execute(
        select(Contract)
        .where(Contract.deal_id == deal_id)
        .order_by(Contract.created_at.desc())
    )
    return result.scalar_one_or_none()


async def get_contract(db: AsyncSession, contract_id: uuid.UUID) -> Contract:
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if contract is None:
        raise AppError(404, "CONTRACT_NOT_FOUND", f"Contract {contract_id} not found")
    return contract


async def generate_contract(db: AsyncSession, deal_id: uuid.UUID, user_id: str) -> Contract:
    deal = await deal_service.get_deal(db, deal_id)
    if deal.status not in _GENERATE_ALLOWED:
        raise AppError(
            409,
            "INVALID_STATE",
            f"Cannot generate contract from status {deal.status!r}",
            {"current_status": deal.status, "allowed": sorted(_GENERATE_ALLOWED)},
        )
    existing = await _get_latest_contract(db, deal_id)
    if existing is not None:
        return existing

    public_id = f"CTR-{deal.public_id}"
    contract = Contract(
        id=uuid.uuid4(),
        deal_id=deal_id,
        public_id=public_id,
        status="draft",
    )
    db.add(contract)
    if deal.status == "firm_offer_generated":
        await deal_service.transition_deal(db, deal_id, "contract_generated")
    await db.commit()
    await db.refresh(contract)
    return contract


async def send_signature(db: AsyncSession, contract_id: uuid.UUID, user_id: str) -> Contract:
    contract = await get_contract(db, contract_id)
    if contract.status != "draft":
        raise AppError(
            409,
            "INVALID_STATE",
            f"Contract status is {contract.status!r}, must be draft to send for signature",
        )
    contract.sent_at = datetime.now(timezone.utc)
    contract.status = "sent_for_signature"
    await deal_service.transition_deal(db, contract.deal_id, "signing")
    await db.commit()
    await db.refresh(contract)
    return contract


async def mock_sign(db: AsyncSession, contract_id: uuid.UUID, user_id: str) -> Contract:
    contract = await get_contract(db, contract_id)
    if contract.status != "sent_for_signature":
        raise AppError(
            409,
            "INVALID_STATE",
            f"Contract status is {contract.status!r}, must be sent_for_signature to sign",
        )
    contract.signed_at = datetime.now(timezone.utc)
    contract.status = "signed"
    await deal_service.transition_deal(db, contract.deal_id, "signed")
    await db.commit()
    await db.refresh(contract)
    return contract

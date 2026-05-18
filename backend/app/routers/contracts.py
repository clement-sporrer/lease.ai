# backend/app/routers/contracts.py
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.schemas.contract import ActivationChecklistResponse, ContractResponse
from app.services import contract_service

_READ_ROLES = {"admin", "ops", "risk"}
_WRITE_ROLES = {"admin", "ops"}

router = APIRouter(tags=["contracts"])


def _require_read(current_user: dict) -> None:
    if current_user.get("active_role") not in _READ_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: internal roles only")


def _require_write(current_user: dict) -> None:
    if current_user.get("active_role") not in _WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: ops or admin required")


@router.post("/deals/{deal_id}/contracts", status_code=201)
async def generate_contract(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    contract = await contract_service.generate_contract(db, deal_id, current_user["user_id"])
    return {"data": ContractResponse.model_validate(contract).model_dump(mode="json")}


@router.get("/deals/{deal_id}/contracts/latest")
async def get_latest_contract(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    contract = await contract_service.get_latest_contract(db, deal_id)
    data = ContractResponse.model_validate(contract).model_dump(mode="json") if contract else None
    return {"data": data}


@router.post("/contracts/{contract_id}/send-signature")
async def send_signature(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    contract = await contract_service.send_signature(db, contract_id, current_user["user_id"])
    return {"data": ContractResponse.model_validate(contract).model_dump(mode="json")}


@router.post("/contracts/{contract_id}/mock-sign")
async def mock_sign(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    contract = await contract_service.mock_sign(db, contract_id, current_user["user_id"])
    return {"data": ContractResponse.model_validate(contract).model_dump(mode="json")}


@router.get("/contracts/{contract_id}/activation-checklist")
async def get_activation_checklist(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    checklist = await contract_service.activation_checklist(db, contract_id)
    return {"data": ActivationChecklistResponse.model_validate(checklist).model_dump(mode="json")}


@router.post("/contracts/{contract_id}/activate")
async def activate_contract(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    contract = await contract_service.activate(db, contract_id, current_user["user_id"])
    return {"data": ContractResponse.model_validate(contract).model_dump(mode="json")}

# backend/app/schemas/contract.py
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    public_id: str
    status: str
    sent_at: datetime | None
    signed_at: datetime | None
    activated_at: datetime | None
    total_commitment_cents: int | None
    created_at: datetime


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    contract_id: uuid.UUID
    name: str
    category: str | None
    quantity: int
    unit_value_cents: int | None
    created_at: datetime


class PaymentScheduleEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    contract_id: uuid.UUID
    due_date: datetime
    amount_cents: int
    status: str
    created_at: datetime


class ActivationChecklistItem(BaseModel):
    key: str
    label: str
    satisfied: bool


class ActivationChecklistResponse(BaseModel):
    items: list[ActivationChecklistItem]
    all_satisfied: bool

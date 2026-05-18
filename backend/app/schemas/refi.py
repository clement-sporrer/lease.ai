import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class RefiPackageResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    deal_id: uuid.UUID
    status: str
    amount_cents: int | None
    duration_months: int | None
    monthly_payment_cents: int | None
    risk_score: float | None
    risk_band: str | None
    sent_at: datetime | None
    created_at: datetime
    updated_at: datetime
    company_name: str | None = None
    deal_public_id: str | None = None


class FinancierDecisionRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str | None = None


class FinancierDecisionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    refi_package_id: uuid.UUID
    decision: str
    reason: str | None
    decided_at: datetime

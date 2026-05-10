import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IndicativePricingRequest(BaseModel):
    amount_cents: int
    duration_months: int
    refi_rate: float = 0.045
    margin_rate: float = 0.025
    fees_cents: int = 50_000


class PricingProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    type: str
    amount_financed_cents: int
    duration_months: int
    monthly_payment_cents: int
    refi_rate: float
    margin_rate: float
    fees_cents: int
    assumptions: dict | None
    version: int = 1
    created_at: datetime | None = None

import uuid
from datetime import datetime

from pydantic import BaseModel


class OfferResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    deal_id: uuid.UUID
    version: int
    is_active: bool
    amount_cents: int | None
    duration_months: int | None
    monthly_payment_cents: int | None
    risk_band: str | None
    currency: str
    valid_until: datetime | None
    created_at: datetime

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DealCreateRequest(BaseModel):
    company_id: uuid.UUID
    amount_cents: int | None = None
    currency: str = "EUR"
    duration_months: int | None = None


class DealPatchRequest(BaseModel):
    amount_cents: int | None = None
    duration_months: int | None = None
    currency: str | None = None


class DealStatusRequest(BaseModel):
    status: str


class DealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    public_id: str
    company_id: uuid.UUID
    partner_org_id: uuid.UUID | None
    submitted_by_user_id: uuid.UUID | None
    status: str
    amount_cents: int | None
    currency: str
    duration_months: int | None
    risk_score: float | None
    risk_band: str | None
    monthly_payment_cents: int | None
    created_at: datetime
    updated_at: datetime

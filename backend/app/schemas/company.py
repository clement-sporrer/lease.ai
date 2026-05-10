import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class EnrichRequest(BaseModel):
    siren_or_siret: str = Field(..., pattern=r"^\d{9}$|^\d{14}$")


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    siren: str
    siret: str | None
    legal_name: str
    trade_name: str | None
    address: dict | None
    activity_code: str | None
    creation_date: date | None
    legal_status: str | None
    is_active: bool
    enrichment_source: str | None
    created_at: datetime

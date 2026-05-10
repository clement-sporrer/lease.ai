import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuoteCreateRequest(BaseModel):
    document_id: uuid.UUID | None = None
    supplier_name: str | None = None
    quote_number: str | None = None
    amount_excl_tax_cents: int | None = None
    amount_incl_tax_cents: int | None = None
    currency: str = "EUR"
    category: str | None = None


class QuotePatchRequest(BaseModel):
    supplier_name: str | None = None
    quote_number: str | None = None
    amount_excl_tax_cents: int | None = None
    amount_incl_tax_cents: int | None = None
    category: str | None = None


class QuoteItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    category: str | None
    quantity: int
    unit_price_cents: int | None
    total_price_cents: int | None


class QuoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    document_id: uuid.UUID | None
    supplier_name: str | None
    quote_number: str | None
    amount_excl_tax_cents: int | None
    amount_incl_tax_cents: int | None
    currency: str
    category: str | None
    extraction_status: str
    items: list[QuoteItemResponse] = []
    created_at: datetime
    updated_at: datetime

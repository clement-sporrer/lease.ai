import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.errors import AppError
from app.models.quote import Quote
from app.schemas.quote import QuoteCreateRequest, QuotePatchRequest, QuoteResponse
from app.services import deal_service

router = APIRouter(tags=["quotes"])

_MOCK_EXTRACTION = {
    "supplier_name": "Lenovo France",
    "quote_number": "DEV-2026-001",
    "amount_excl_tax_cents": 9_900_000,
    "amount_incl_tax_cents": 11_880_000,
    "category": "hardware",
    "items": [
        {"label": "ThinkPad X1 Carbon", "quantity": 5, "unit_price_cents": 1_980_000},
    ],
}


async def _get_quote(db: AsyncSession, deal_id: uuid.UUID, quote_id: uuid.UUID) -> Quote:
    result = await db.execute(select(Quote).where(Quote.id == quote_id, Quote.deal_id == deal_id))
    quote = result.scalar_one_or_none()
    if quote is None:
        raise AppError(404, "QUOTE_NOT_FOUND", f"Quote {quote_id} not found")
    return quote


@router.post("/deals/{deal_id}/quotes", status_code=201)
async def create_quote(
    deal_id: uuid.UUID,
    body: QuoteCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    deal = await deal_service.get_deal(db, deal_id)
    if deal.status not in {"company_enriched", "quote_added"}:
        raise AppError(
            409,
            "INVALID_TRANSITION",
            "Cannot add a quote from the current deal status",
            {
                "current_status": deal.status,
                "allowed_next": ["quote_added", "cancelled"],
            },
        )
    quote = Quote(
        deal_id=deal_id,
        document_id=body.document_id,
        supplier_name=body.supplier_name,
        quote_number=body.quote_number,
        amount_excl_tax_cents=body.amount_excl_tax_cents,
        amount_incl_tax_cents=body.amount_incl_tax_cents,
        currency=body.currency,
        category=body.category,
        extraction_status="pending",
    )
    db.add(quote)
    await db.flush()
    if deal.status == "company_enriched":
        await deal_service.transition_deal(db, deal_id, "quote_added")
    else:
        await db.commit()
    await db.refresh(quote)
    return {"data": QuoteResponse.model_validate(quote).model_dump(mode="json")}


@router.get("/deals/{deal_id}/quotes/{quote_id}")
async def get_quote(
    deal_id: uuid.UUID,
    quote_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    quote = await _get_quote(db, deal_id, quote_id)
    return {"data": QuoteResponse.model_validate(quote).model_dump(mode="json")}


@router.patch("/deals/{deal_id}/quotes/{quote_id}")
async def patch_quote(
    deal_id: uuid.UUID,
    quote_id: uuid.UUID,
    body: QuotePatchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    quote = await _get_quote(db, deal_id, quote_id)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(quote, field, value)
    await db.commit()
    await db.refresh(quote)
    return {"data": QuoteResponse.model_validate(quote).model_dump(mode="json")}


@router.post("/deals/{deal_id}/quotes/{quote_id}/extract")
async def extract_quote(
    deal_id: uuid.UUID,
    quote_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    quote = await _get_quote(db, deal_id, quote_id)
    quote.extraction_status = "done"
    quote.extraction_payload = _MOCK_EXTRACTION
    if not quote.supplier_name:
        quote.supplier_name = _MOCK_EXTRACTION["supplier_name"]
    if not quote.quote_number:
        quote.quote_number = _MOCK_EXTRACTION["quote_number"]
    if not quote.amount_excl_tax_cents:
        quote.amount_excl_tax_cents = _MOCK_EXTRACTION["amount_excl_tax_cents"]
    if not quote.amount_incl_tax_cents:
        quote.amount_incl_tax_cents = _MOCK_EXTRACTION["amount_incl_tax_cents"]
    if not quote.category:
        quote.category = _MOCK_EXTRACTION["category"]
    await db.commit()
    await db.refresh(quote)
    return {"data": QuoteResponse.model_validate(quote).model_dump(mode="json")}

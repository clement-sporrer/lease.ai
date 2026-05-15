import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.errors import AppError
from app.models.quote import Quote
from app.schemas.quote import QuoteCreateRequest, QuotePatchRequest, QuoteResponse
from app.services import deal_service

router = APIRouter(tags=["quotes"])


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

    from app.services.mistral_service import extract_quote_pdf
    result, source = await extract_quote_pdf(b"")  # no file — uses mock unless USE_REAL_MISTRAL

    quote.extraction_status = "done"
    quote.extraction_payload = result
    quote.extraction_source = source
    if not quote.supplier_name:
        quote.supplier_name = result.get("supplier_name")
    if not quote.quote_number:
        quote.quote_number = result.get("quote_number")
    if not quote.amount_excl_tax_cents:
        quote.amount_excl_tax_cents = result.get("amount_excl_tax_cents")
    if not quote.amount_incl_tax_cents:
        quote.amount_incl_tax_cents = result.get("amount_incl_tax_cents")
    if not quote.category:
        quote.category = result.get("category")
    await db.commit()
    await db.refresh(quote)
    return {"data": QuoteResponse.model_validate(quote).model_dump(mode="json")}


@router.post("/deals/{deal_id}/quotes/upload-and-extract", status_code=201)
async def upload_and_extract_quote(
    deal_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a quote and immediately extract it from an uploaded PDF."""
    del current_user
    pdf_bytes = await file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise AppError(413, "DOCUMENT_TOO_LARGE", "PDF must be under 20 MB")

    from app.services.mistral_service import extract_quote_pdf
    result, source = await extract_quote_pdf(pdf_bytes)

    quote = Quote(
        deal_id=deal_id,
        supplier_name=result.get("supplier_name"),
        quote_number=result.get("quote_number"),
        amount_excl_tax_cents=result.get("amount_excl_tax_cents"),
        amount_incl_tax_cents=result.get("amount_incl_tax_cents"),
        currency=result.get("currency", "EUR"),
        category=result.get("category"),
        extraction_status="done",
        extraction_payload=result,
        extraction_source=source,
    )
    db.add(quote)
    await db.commit()
    await db.refresh(quote)
    return {"data": QuoteResponse.model_validate(quote).model_dump(mode="json")}

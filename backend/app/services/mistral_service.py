"""Mistral OCR + structured extraction for quote PDFs.

Two-step: OCR with mistral-ocr-latest → structured extraction with mistral-small-latest.
Feature-flagged via USE_REAL_MISTRAL env var.
"""
from __future__ import annotations

import base64
import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_BASE = "https://api.mistral.ai/v1"

_EXTRACTION_PROMPT = """\
You are a document parser for IT leasing quotes. Extract the following from the provided text and return ONLY a JSON object with no markdown:
{
  "supplier_name": "company name",
  "quote_number": "reference number or null",
  "amount_excl_tax_cents": integer in euro cents (no VAT),
  "amount_incl_tax_cents": integer in euro cents (with VAT),
  "currency": "EUR",
  "category": "hardware" | "software" | "services" | "mixed",
  "items": [
    {
      "label": "product designation",
      "category": "hardware" | "software" | "services" | null,
      "quantity": integer,
      "unit_price_cents": integer in cents,
      "total_price_cents": integer in cents
    }
  ]
}
If a value cannot be determined, use null. All amounts must be integers in euro cents."""

_MOCK_RESULT = {
    "supplier_name": "Tech Distrib SAS",
    "quote_number": "TD-2026-1042",
    "amount_excl_tax_cents": 8_550_000,
    "amount_incl_tax_cents": 10_260_000,
    "currency": "EUR",
    "category": "hardware",
    "items": [
        {"label": 'MacBook Pro 16"', "category": "hardware", "quantity": 26, "unit_price_cents": 249_000, "total_price_cents": 6_474_000},
        {"label": "iPhone 15 Pro", "category": "hardware", "quantity": 18, "unit_price_cents": 119_000, "total_price_cents": 2_142_000},
    ],
}


async def extract_quote_pdf(pdf_bytes: bytes) -> tuple[dict, str]:
    """
    Returns (extracted_data, source) where source is "mistral" or "mock".
    Falls back to mock on any error.
    """
    if not settings.use_real_mistral or not settings.mistral_api_key:
        return _MOCK_RESULT, "mock"

    headers = {
        "Authorization": f"Bearer {settings.mistral_api_key}",
        "Content-Type": "application/json",
    }
    b64 = base64.b64encode(pdf_bytes).decode()

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Step 1: OCR
            ocr_resp = await client.post(
                f"{_BASE}/ocr",
                headers=headers,
                json={
                    "model": "mistral-ocr-latest",
                    "document": {
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{b64}",
                    },
                },
            )
            ocr_resp.raise_for_status()
            pages = ocr_resp.json().get("pages", [])
            ocr_text = "\n".join(p.get("markdown", "") for p in pages)

            if not ocr_text.strip():
                logger.warning("Mistral OCR returned empty text — falling back to mock")
                return _MOCK_RESULT, "mock"

            # Step 2: Structured extraction
            extract_resp = await client.post(
                f"{_BASE}/chat/completions",
                headers=headers,
                json={
                    "model": "mistral-small-latest",
                    "messages": [
                        {"role": "user", "content": f"{_EXTRACTION_PROMPT}\n\nDocument text:\n{ocr_text}"}
                    ],
                    "response_format": {"type": "json_object"},
                    "max_tokens": 1500,
                },
            )
            extract_resp.raise_for_status()
            content = extract_resp.json()["choices"][0]["message"]["content"]
            return json.loads(content), "mistral"

    except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, KeyError) as exc:
        logger.warning("Mistral extraction failed: %s — falling back to mock", exc)
        return _MOCK_RESULT, "mock"

"""Integration tests — require MISTRAL_API_KEY in env."""
import asyncio
import os

import pytest


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("MISTRAL_API_KEY"), reason="MISTRAL_API_KEY not set")
def test_extract_from_empty_bytes_falls_back_to_mock():
    from app.services.mistral_service import extract_quote_pdf
    result, source = asyncio.run(extract_quote_pdf(b""))
    assert "supplier_name" in result
    assert source in ("mistral", "mock")


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("MISTRAL_API_KEY"), reason="MISTRAL_API_KEY not set")
def test_extract_returns_required_keys():
    from app.services.mistral_service import extract_quote_pdf
    result, source = asyncio.run(extract_quote_pdf(b""))
    for key in ("supplier_name", "amount_excl_tax_cents", "currency", "items"):
        assert key in result

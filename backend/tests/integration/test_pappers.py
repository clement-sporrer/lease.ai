"""Integration tests — require PAPPERS_API_KEY in env. Run manually or in dedicated CI job."""
import asyncio
import os

import pytest


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("PAPPERS_API_KEY"), reason="PAPPERS_API_KEY not set")
def test_fetch_real_company():
    from app.services.pappers_service import fetch_company
    result = asyncio.run(fetch_company("443061841"))  # Société Générale
    assert result is not None
    assert result["siren"] == "443061841"
    assert result["enrichment_source"] == "pappers"
    assert result["legal_name"]


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("PAPPERS_API_KEY"), reason="PAPPERS_API_KEY not set")
def test_invalid_siren_returns_none():
    from app.services.pappers_service import fetch_company
    result = asyncio.run(fetch_company("000000000"))
    assert result is None

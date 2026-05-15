"""Pappers API client. Use via enrichment_service — do not call directly from routers."""
from __future__ import annotations

import logging
from datetime import date

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_BASE = "https://api.pappers.fr/v2"


async def fetch_company(siren: str) -> dict | None:
    """Fetch company data from Pappers. Returns None on any failure (caller falls back to mock)."""
    if not settings.pappers_api_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                f"{_BASE}/entreprise",
                params={"api_token": settings.pappers_api_key, "siren": siren},
            )
            if resp.status_code != 200:
                logger.warning("Pappers returned %s for siren=%s", resp.status_code, siren)
                return None
            data = resp.json()
    except httpx.RequestError as exc:
        logger.warning("Pappers request failed: %s", exc)
        return None

    return _normalize(data, siren)


def _normalize(raw: dict, siren: str) -> dict:
    """Map Pappers response to our Company field shape."""
    creation_raw = raw.get("date_creation")
    try:
        creation_date = date.fromisoformat(creation_raw) if creation_raw else None
    except ValueError:
        creation_date = None

    siege = raw.get("siege", {})
    address = {
        "street": siege.get("adresse_ligne_1", ""),
        "city": siege.get("ville", ""),
        "zip": siege.get("code_postal", ""),
    }

    return {
        "siren": siren,
        "siret": siege.get("siret"),
        "legal_name": raw.get("nom_entreprise", ""),
        "trade_name": raw.get("nom_commercial") or None,
        "address": address,
        "activity_code": raw.get("code_naf", ""),
        "creation_date": creation_date,
        "legal_status": raw.get("forme_juridique", ""),
        "is_active": raw.get("statut_rcs") != "Radié",
        "enrichment_source": "pappers",
        "enrichment_payload": {"raw_siren": siren, "pappers_response": raw},
    }

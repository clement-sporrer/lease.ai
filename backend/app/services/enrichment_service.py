import hashlib
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.company import Company


# --- mock fallback (deterministic from SIREN) ---

_LEGAL_NAMES = ["ACME SAS", "DELTA TECH", "NOVA SOLUTIONS", "ORION SYSTEMS", "APEX GROUP"]
_LEGAL_STATUSES = ["SAS", "SARL", "SA", "EURL"]
_ACTIVITIES = ["6201Z", "6202A", "4741Z", "7311Z", "6311Z"]
_CITIES = [
    {"street": "12 rue du Commerce", "city": "Paris", "zip": "75015"},
    {"street": "3 avenue des Fleurs", "city": "Lyon", "zip": "69003"},
    {"street": "8 place Bellecour", "city": "Marseille", "zip": "13001"},
]


def _pick(identifier: str, items: list, salt: str = "") -> object:
    digest = hashlib.md5(f"{identifier}{salt}".encode(), usedforsecurity=False).hexdigest()
    return items[int(digest[:8], 16) % len(items)]


def _normalize_siren_or_siret(value: str) -> tuple[str, str | None]:
    if len(value) == 14:
        return value[:9], value
    return value, None


def _mock_data(siren: str, siret: str | None) -> dict:
    offset_years = 2 + (int(siren[-1]) % 9)
    return {
        "siren": siren,
        "siret": siret,
        "legal_name": str(_pick(siren, _LEGAL_NAMES)),
        "trade_name": None,
        "address": _pick(siren, _CITIES, salt="addr"),
        "activity_code": str(_pick(siren, _ACTIVITIES, salt="act")),
        "creation_date": date(date.today().year - offset_years, 3, 15),
        "legal_status": str(_pick(siren, _LEGAL_STATUSES, salt="ls")),
        "is_active": True,
        "enrichment_source": "mock",
        "enrichment_payload": {"source": "mock_pappers", "lookup": siren},
    }


async def enrich_and_upsert(db: AsyncSession, siren_or_siret: str) -> Company:
    siren, siret = _normalize_siren_or_siret(siren_or_siret)

    result = await db.execute(select(Company).where(Company.siren == siren))
    existing = result.scalar_one_or_none()
    if existing is not None:
        if siret and not existing.siret:
            existing.siret = siret
            await db.commit()
            await db.refresh(existing)
        return existing

    # Attempt real Pappers lookup
    data: dict | None = None
    if settings.use_real_pappers:
        from app.services.pappers_service import fetch_company
        data = await fetch_company(siren)

    if data is None:
        data = _mock_data(siren, siret)

    company = Company(id=uuid.uuid4(), **data)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company

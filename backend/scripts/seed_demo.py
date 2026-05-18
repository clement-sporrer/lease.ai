#!/usr/bin/env python3
"""Seed 3 demo deals at different pipeline stages.

Run: cd backend && python scripts/seed_demo.py

Requires DATABASE_URL in environment (or .env.local).
"""
import asyncio
import pathlib
import sys
import uuid
from datetime import date, datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models import *  # noqa: F401,F403 — registers all models with Base

DATABASE_URL = (
    settings.database_url
    .replace("postgresql://", "postgresql+asyncpg://", 1)
    .replace("postgres://", "postgresql+asyncpg://", 1)
)


async def seed() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as db:
        # Clear existing demo data (deals first due to FK)
        await db.execute(
            text(
                "DELETE FROM deals WHERE public_id IN "
                "('D-2026-0001', 'D-2026-0002', 'D-2026-0003')"
            )
        )
        await db.execute(
            text(
                "DELETE FROM companies WHERE siren IN "
                "('123456789', '987654321', '456789012')"
            )
        )
        await db.commit()

        from app.models.company import Company

        globex = Company(
            id=uuid.uuid4(),
            siren="123456789",
            siret="12345678900012",
            legal_name="Globex Inc.",
            trade_name="Globex",
            address={"street": "12 Av. de l'Opéra", "city": "Paris", "zip": "75002"},
            activity_code="6202A",
            creation_date=date(2016, 5, 12),
            legal_status="SAS",
            is_active=True,
            enrichment_source="pappers",
            enrichment_payload={"capital_eur": 50_000, "employees": 42},
        )
        db.add(globex)

        acme = Company(
            id=uuid.uuid4(),
            siren="987654321",
            siret="98765432100018",
            legal_name="Acme Corporation",
            trade_name="Acme",
            address={"street": "21 rue de la Paix", "city": "Paris", "zip": "75002"},
            activity_code="4651Z",
            creation_date=date(2018, 9, 3),
            legal_status="SARL",
            is_active=True,
            enrichment_source="mock",
            enrichment_payload={},
        )
        db.add(acme)

        umbrella = Company(
            id=uuid.uuid4(),
            siren="456789012",
            legal_name="Umbrella Corp.",
            trade_name="Umbrella",
            address={"street": "8 Pl. de la République", "city": "Paris", "zip": "75003"},
            activity_code="7022Z",
            creation_date=date(2020, 1, 15),
            legal_status="SAS",
            is_active=True,
            enrichment_source="mock",
            enrichment_payload={},
        )
        db.add(umbrella)
        await db.flush()

        now = datetime.now(timezone.utc)

        from app.models.deal import Deal

        deal1 = Deal(
            id=uuid.uuid4(),
            public_id="D-2026-0001",
            company_id=globex.id,
            status="internal_review",
            amount_cents=8_550_000,
            currency="EUR",
            duration_months=36,
            risk_score=72.5,
            risk_band="A",
            monthly_payment_cents=250_000,
            created_at=now,
            updated_at=now,
        )
        db.add(deal1)

        deal2 = Deal(
            id=uuid.uuid4(),
            public_id="D-2026-0002",
            company_id=acme.id,
            status="refi_package_ready",
            amount_cents=12_000_000,
            currency="EUR",
            duration_months=48,
            risk_score=85.0,
            risk_band="A",
            monthly_payment_cents=275_000,
            created_at=now,
            updated_at=now,
        )
        db.add(deal2)

        deal3 = Deal(
            id=uuid.uuid4(),
            public_id="D-2026-0003",
            company_id=umbrella.id,
            status="pre_approved",
            amount_cents=6_030_000,
            currency="EUR",
            duration_months=36,
            risk_score=58.0,
            risk_band="C",
            monthly_payment_cents=185_000,
            created_at=now,
            updated_at=now,
        )
        db.add(deal3)

        await db.commit()

        from app.models.document import Document

        for doc_type, file_name in [
            ("quote", "devis_laptops_globex.pdf"),
            ("id_document", "kbis_globex.pdf"),
            ("rib", "rib_globex.pdf"),
        ]:
            db.add(
                Document(
                    id=uuid.uuid4(),
                    deal_id=deal1.id,
                    type=doc_type,
                    file_name=file_name,
                    status="validated",
                )
            )
        await db.commit()
        print("Demo seed complete: 3 companies, 3 deals at D-2026-0001..0003, 3 documents for Globex")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

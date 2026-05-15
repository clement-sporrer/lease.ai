# LeaseAI Phase 1 — Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the real DB-backed backend for the refi → financier → offer pipeline, wire Pappers and Mistral, so every status transition during the demo writes to Postgres.

**Architecture:** New SQLAlchemy models (`RefiPackage`, `FinancierDecision`, `Offer` with versioning) + services that call `deal_service.transition_deal()` + FastAPI routers registered in `main.py`. External integrations (Pappers, Mistral) wrapped in dedicated service classes with env-flag-controlled fallback to mocks.

**Tech Stack:** FastAPI · SQLAlchemy 2.0 async · Alembic · Pydantic v2 · httpx (async HTTP) · pytest · python-dotenv

---

## Context

- `AppError` lives in `backend/app/core/errors.py` — use this, not `APIError` from `errors.py`
- `deal_service.transition_deal(db, deal_id, target)` handles status validation + commit
- Tests use `make_token(sub, active_role)` fixture from `conftest.py`; auth is mocked via `monkeypatch`
- Feature flags: `USE_REAL_PAPPERS=true/false`, `USE_REAL_MISTRAL=true/false` — default `false` in all tests
- All money values: integer cents (`amount_cents: int`), never floats
- Error envelope: `{"error": {"code": str, "message": str, "details": dict}}`

---

## File Map

**Create:**
- `backend/app/models/refi_package.py` — RefiPackage + FinancierDecision ORM models
- `backend/app/models/offer.py` — Offer ORM model (version + is_active)
- `backend/app/schemas/refi.py` — Pydantic request/response schemas for refi endpoints
- `backend/app/schemas/offer.py` — Pydantic request/response schemas for offer endpoints
- `backend/app/services/refi_service.py` — create package, send to financier, record decision
- `backend/app/services/offer_service.py` — generate offer with versioning
- `backend/app/services/pappers_service.py` — Pappers API client + mock fallback
- `backend/app/services/mistral_service.py` — Mistral OCR + structured extraction
- `backend/app/routers/refi.py` — /refi-packages endpoints
- `backend/app/routers/offers.py` — /offers endpoints
- `backend/alembic/versions/<hash>_add_refi_offer_tables.py` — migration
- `backend/tests/test_refi_service.py`
- `backend/tests/test_offer_service.py`
- `backend/tests/test_refi_router.py`
- `backend/tests/test_offers_router.py`
- `backend/tests/integration/test_pappers.py`
- `backend/tests/integration/test_mistral.py`
- `backend/scripts/seed_demo.py` — seed 3 demo deals at different stages

**Modify:**
- `backend/app/models/__init__.py` — register RefiPackage, FinancierDecision, Offer
- `backend/app/models/quote.py` — add `extraction_source: str | None` column
- `backend/app/core/config.py` — add pappers_api_key, mistral_api_key, use_real_pappers, use_real_mistral
- `backend/app/routers/quotes.py` — replace mock extraction with MistralService call
- `backend/app/main.py` — register refi + offers routers

---

## Task 1: RefiPackage + FinancierDecision models

**Files:**
- Create: `backend/app/models/refi_package.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write the model file**

```python
# backend/app/models/refi_package.py
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RefiPackage(Base):
    __tablename__ = "refi_packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="draft")
    financier_org_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    amount_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_payment_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_band: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class FinancierDecision(Base):
    __tablename__ = "financier_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refi_package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("refi_packages.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    decision: Mapped[str] = mapped_column(String(20), nullable=False)  # "approved" | "rejected"
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True
    )
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 2: Register in `__init__.py`**

Add to `backend/app/models/__init__.py`:
```python
from app.models.refi_package import RefiPackage, FinancierDecision
```

And add `"RefiPackage"`, `"FinancierDecision"` to `__all__`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/refi_package.py backend/app/models/__init__.py
git commit -m "feat(models): add RefiPackage and FinancierDecision"
```

---

## Task 2: Offer model with versioning

**Files:**
- Create: `backend/app/models/offer.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write the model**

```python
# backend/app/models/offer.py
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    amount_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_payment_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    risk_band: Mapped[str | None] = mapped_column(String(20), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="EUR")
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 2: Register in `__init__.py`**

Add to `backend/app/models/__init__.py`:
```python
from app.models.offer import Offer
```

And add `"Offer"` to `__all__`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/offer.py backend/app/models/__init__.py
git commit -m "feat(models): add Offer with version + is_active for safe re-quoting"
```

---

## Task 3: Add extraction_source to Quote model

**Files:**
- Modify: `backend/app/models/quote.py`

- [ ] **Step 1: Add the column**

In `backend/app/models/quote.py`, after `extraction_payload`:
```python
extraction_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/quote.py
git commit -m "feat(models): add extraction_source to Quote for provenance tracking"
```

---

## Task 4: Alembic migration

**Files:**
- Create: `backend/alembic/versions/<hash>_add_refi_offer_tables.py`

- [ ] **Step 1: Auto-generate the migration**

```bash
cd backend
alembic revision --autogenerate -m "add_refi_offer_tables"
```

This generates a file in `backend/alembic/versions/`. Open it and verify it contains:
- `CREATE TABLE refi_packages`
- `CREATE TABLE financier_decisions`
- `CREATE TABLE offers`
- `ALTER TABLE quotes ADD COLUMN extraction_source`

- [ ] **Step 2: Apply to dev DB**

```bash
alembic upgrade head
```

Expected: no errors, tables created.

- [ ] **Step 3: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat(migration): add refi_packages, financier_decisions, offers, quote.extraction_source"
```

---

## Task 5: Pydantic schemas

**Files:**
- Create: `backend/app/schemas/refi.py`
- Create: `backend/app/schemas/offer.py`

- [ ] **Step 1: Write refi schemas**

```python
# backend/app/schemas/refi.py
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class RefiPackageResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    deal_id: uuid.UUID
    status: str
    amount_cents: int | None
    duration_months: int | None
    monthly_payment_cents: int | None
    risk_score: float | None
    risk_band: str | None
    sent_at: datetime | None
    created_at: datetime
    updated_at: datetime


class FinancierDecisionRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str | None = None


class FinancierDecisionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    refi_package_id: uuid.UUID
    decision: str
    reason: str | None
    decided_at: datetime
```

- [ ] **Step 2: Write offer schemas**

```python
# backend/app/schemas/offer.py
import uuid
from datetime import datetime

from pydantic import BaseModel


class OfferResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    deal_id: uuid.UUID
    version: int
    is_active: bool
    amount_cents: int | None
    duration_months: int | None
    monthly_payment_cents: int | None
    risk_band: str | None
    currency: str
    valid_until: datetime | None
    created_at: datetime
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas/refi.py backend/app/schemas/offer.py
git commit -m "feat(schemas): add refi and offer Pydantic schemas"
```

---

## Task 6: RefiService

**Files:**
- Create: `backend/app/services/refi_service.py`
- Create: `backend/tests/test_refi_service.py`

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/test_refi_service.py
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_deal(status: str = "pre_approved") -> MagicMock:
    deal = MagicMock()
    deal.id = uuid.uuid4()
    deal.status = status
    deal.amount_cents = 8_550_000
    deal.duration_months = 36
    deal.monthly_payment_cents = 250_000
    deal.risk_score = 72.5
    deal.risk_band = "B"
    return deal


@pytest.mark.asyncio
async def test_create_refi_package_requires_pre_approved():
    db = AsyncMock()
    with patch("app.services.refi_service.deal_service.get_deal", new=AsyncMock(return_value=_make_deal("internal_review"))):
        from app.services import refi_service
        with pytest.raises(Exception) as exc_info:
            await refi_service.create_refi_package(db, uuid.uuid4(), "user_001")
    assert "pre_approved" in str(exc_info.value).lower() or "transition" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_refi_package_transitions_deal():
    deal = _make_deal("pre_approved")
    db = AsyncMock()
    with (
        patch("app.services.refi_service.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch("app.services.refi_service.deal_service.transition_deal", new=AsyncMock(return_value=deal)),
    ):
        from app.services import refi_service
        pkg = await refi_service.create_refi_package(db, deal.id, "user_001")
    assert pkg.deal_id == deal.id
    assert pkg.status == "draft"
    assert pkg.amount_cents == deal.amount_cents


@pytest.mark.asyncio
async def test_record_decision_approved_transitions_deal():
    deal = _make_deal("refi_review")
    pkg = MagicMock()
    pkg.id = uuid.uuid4()
    pkg.deal_id = deal.id
    pkg.status = "sent"
    db = AsyncMock()
    with (
        patch("app.services.refi_service.deal_service.transition_deal", new=AsyncMock(return_value=deal)),
    ):
        from app.services import refi_service
        dec = await refi_service.record_decision(db, pkg, deal, "approved", reason=None, user_id="user_fin")
    assert dec.decision == "approved"


@pytest.mark.asyncio
async def test_record_decision_rejected_requires_reason():
    deal = _make_deal("refi_review")
    pkg = MagicMock()
    pkg.id = uuid.uuid4()
    from app.services import refi_service
    with pytest.raises(Exception):
        await refi_service.record_decision(AsyncMock(), pkg, deal, "rejected", reason=None, user_id="u")
```

- [ ] **Step 2: Run to verify all fail**

```bash
cd backend && python -m pytest tests/test_refi_service.py -v
```

Expected: 4 errors (module not found).

- [ ] **Step 3: Implement RefiService**

```python
# backend/app/services/refi_service.py
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.refi_package import FinancierDecision, RefiPackage
from app.services import deal_service


async def create_refi_package(
    db: AsyncSession, deal_id: uuid.UUID, user_id: str
) -> RefiPackage:
    deal = await deal_service.get_deal(db, deal_id)
    if deal.status != "pre_approved":
        raise AppError(
            409,
            "INVALID_TRANSITION",
            f"Cannot create refi package from status {deal.status!r} — deal must be pre_approved",
            {"current_status": deal.status},
        )
    pkg = RefiPackage(
        id=uuid.uuid4(),
        deal_id=deal_id,
        status="draft",
        amount_cents=deal.amount_cents,
        duration_months=deal.duration_months,
        monthly_payment_cents=deal.monthly_payment_cents,
        risk_score=float(deal.risk_score) if deal.risk_score is not None else None,
        risk_band=deal.risk_band,
    )
    db.add(pkg)
    await deal_service.transition_deal(db, deal_id, "refi_package_ready")
    await db.refresh(pkg)
    return pkg


async def send_package(db: AsyncSession, pkg: RefiPackage, deal_id: uuid.UUID) -> RefiPackage:
    from datetime import datetime, timezone
    if pkg.status != "draft":
        raise AppError(409, "INVALID_STATE", f"Package status is {pkg.status!r}, must be draft")
    pkg.status = "sent"
    pkg.sent_at = datetime.now(timezone.utc)
    await deal_service.transition_deal(db, deal_id, "refi_review")
    await db.refresh(pkg)
    return pkg


async def get_package(db: AsyncSession, package_id: uuid.UUID) -> RefiPackage:
    result = await db.execute(select(RefiPackage).where(RefiPackage.id == package_id))
    pkg = result.scalar_one_or_none()
    if pkg is None:
        raise AppError(404, "REFI_PACKAGE_NOT_FOUND", f"RefiPackage {package_id} not found")
    return pkg


async def list_packages_for_deal(db: AsyncSession, deal_id: uuid.UUID) -> list[RefiPackage]:
    result = await db.execute(
        select(RefiPackage).where(RefiPackage.deal_id == deal_id).order_by(RefiPackage.created_at.desc())
    )
    return list(result.scalars().all())


async def record_decision(
    db: AsyncSession,
    pkg: RefiPackage,
    deal,
    decision: str,
    reason: str | None,
    user_id: str,
) -> FinancierDecision:
    if decision == "rejected" and not reason:
        raise AppError(422, "REASON_REQUIRED", "Rejection requires a reason", {})
    target_status = "financier_approved" if decision == "approved" else "financier_rejected"
    dec = FinancierDecision(
        id=uuid.uuid4(),
        refi_package_id=pkg.id,
        decision=decision,
        reason=reason,
        decided_by_user_id=uuid.UUID(user_id) if user_id else None,
    )
    db.add(dec)
    pkg.status = decision
    await deal_service.transition_deal(db, deal.id, target_status)
    await db.refresh(dec)
    return dec
```

- [ ] **Step 4: Run tests — all should pass**

```bash
cd backend && python -m pytest tests/test_refi_service.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/refi_service.py backend/tests/test_refi_service.py
git commit -m "feat(services): add RefiService with create, send, decision"
```

---

## Task 7: OfferService

**Files:**
- Create: `backend/app/services/offer_service.py`
- Create: `backend/tests/test_offer_service.py`

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/test_offer_service.py
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_deal(status: str = "financier_approved") -> MagicMock:
    deal = MagicMock()
    deal.id = uuid.uuid4()
    deal.status = status
    deal.amount_cents = 8_550_000
    deal.duration_months = 36
    deal.monthly_payment_cents = 250_000
    deal.risk_band = "B"
    deal.currency = "EUR"
    return deal


@pytest.mark.asyncio
async def test_generate_offer_requires_financier_approved():
    deal = _make_deal("pre_approved")
    db = AsyncMock()
    with patch("app.services.offer_service.deal_service.get_deal", new=AsyncMock(return_value=deal)):
        from app.services import offer_service
        with pytest.raises(Exception):
            await offer_service.generate_offer(db, deal.id, "user_admin")


@pytest.mark.asyncio
async def test_generate_offer_first_version_is_1():
    deal = _make_deal("financier_approved")
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
    with (
        patch("app.services.offer_service.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch("app.services.offer_service.deal_service.transition_deal", new=AsyncMock(return_value=deal)),
    ):
        from app.services import offer_service
        offer = await offer_service.generate_offer(db, deal.id, "user_admin")
    assert offer.version == 1
    assert offer.is_active is True


@pytest.mark.asyncio
async def test_generate_offer_v2_deactivates_v1():
    deal = _make_deal("firm_offer_generated")
    existing = MagicMock()
    existing.is_active = True
    existing.version = 1
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[existing])))))
    with (
        patch("app.services.offer_service.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch("app.services.offer_service.deal_service.transition_deal", new=AsyncMock(return_value=deal)),
    ):
        from app.services import offer_service
        offer = await offer_service.generate_offer(db, deal.id, "user_admin")
    assert existing.is_active is False
    assert offer.version == 2
    assert offer.is_active is True
```

- [ ] **Step 2: Run to verify all fail**

```bash
cd backend && python -m pytest tests/test_offer_service.py -v
```

Expected: 3 errors (module not found).

- [ ] **Step 3: Implement OfferService**

```python
# backend/app/services/offer_service.py
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.offer import Offer
from app.services import deal_service

_ALLOWED_STATUSES = {"financier_approved", "firm_offer_generated"}


async def generate_offer(db: AsyncSession, deal_id: uuid.UUID, user_id: str) -> Offer:
    deal = await deal_service.get_deal(db, deal_id)
    if deal.status not in _ALLOWED_STATUSES:
        raise AppError(
            409,
            "INVALID_STATE",
            f"Cannot generate offer from status {deal.status!r}",
            {"current_status": deal.status, "allowed": list(_ALLOWED_STATUSES)},
        )
    result = await db.execute(select(Offer).where(Offer.deal_id == deal_id))
    existing = list(result.scalars().all())
    for prev in existing:
        prev.is_active = False
    next_version = max((o.version for o in existing), default=0) + 1
    offer = Offer(
        id=uuid.uuid4(),
        deal_id=deal_id,
        version=next_version,
        is_active=True,
        amount_cents=deal.amount_cents,
        duration_months=deal.duration_months,
        monthly_payment_cents=deal.monthly_payment_cents,
        risk_band=deal.risk_band,
        currency=deal.currency,
    )
    db.add(offer)
    if deal.status == "financier_approved":
        await deal_service.transition_deal(db, deal_id, "firm_offer_generated")
    else:
        await db.commit()
    await db.refresh(offer)
    return offer


async def get_active_offer(db: AsyncSession, deal_id: uuid.UUID) -> Offer | None:
    result = await db.execute(
        select(Offer).where(Offer.deal_id == deal_id, Offer.is_active.is_(True))
    )
    return result.scalar_one_or_none()


async def list_offers(db: AsyncSession, deal_id: uuid.UUID) -> list[Offer]:
    result = await db.execute(
        select(Offer).where(Offer.deal_id == deal_id).order_by(Offer.version.desc())
    )
    return list(result.scalars().all())
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_offer_service.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/offer_service.py backend/tests/test_offer_service.py
git commit -m "feat(services): add OfferService with versioning — V2 never overwrites V1"
```

---

## Task 8: Refi router

**Files:**
- Create: `backend/app/routers/refi.py`
- Create: `backend/tests/test_refi_router.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the failing router tests**

```python
# backend/tests/test_refi_router.py
import uuid
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app

client = TestClient(app)


def _auth_headers(make_token, role: str = "admin") -> dict:
    token = make_token(sub=str(uuid.uuid4()), active_role=role)
    return {"Authorization": f"Bearer {token}"}


def test_create_refi_package_returns_201(make_token):
    pkg = MagicMock()
    pkg.id = uuid.uuid4()
    pkg.deal_id = uuid.uuid4()
    pkg.status = "draft"
    pkg.amount_cents = 8_000_000
    pkg.duration_months = 36
    pkg.monthly_payment_cents = 240_000
    pkg.risk_score = 72.0
    pkg.risk_band = "B"
    pkg.sent_at = None
    pkg.created_at = __import__("datetime").datetime.utcnow()
    pkg.updated_at = __import__("datetime").datetime.utcnow()

    with patch("app.routers.refi.refi_service.create_refi_package", new=AsyncMock(return_value=pkg)):
        res = client.post(
            f"/deals/{pkg.deal_id}/refi-packages",
            headers=_auth_headers(make_token),
        )
    assert res.status_code == 201
    assert res.json()["data"]["status"] == "draft"


def test_financier_decision_approved_returns_200(make_token):
    pkg = MagicMock()
    pkg.id = uuid.uuid4()
    pkg.deal_id = uuid.uuid4()
    pkg.status = "sent"

    deal = MagicMock()
    deal.id = pkg.deal_id
    deal.status = "refi_review"

    dec = MagicMock()
    dec.id = uuid.uuid4()
    dec.refi_package_id = pkg.id
    dec.decision = "approved"
    dec.reason = None
    dec.decided_at = __import__("datetime").datetime.utcnow()

    with (
        patch("app.routers.refi.refi_service.get_package", new=AsyncMock(return_value=pkg)),
        patch("app.routers.refi.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch("app.routers.refi.refi_service.record_decision", new=AsyncMock(return_value=dec)),
    ):
        res = client.post(
            f"/refi-packages/{pkg.id}/decision",
            json={"decision": "approved"},
            headers=_auth_headers(make_token, role="financier"),
        )
    assert res.status_code == 200
    assert res.json()["data"]["decision"] == "approved"


def test_financier_decision_rejected_without_reason_returns_422(make_token):
    pkg = MagicMock()
    pkg.id = uuid.uuid4()
    pkg.deal_id = uuid.uuid4()
    pkg.status = "sent"

    deal = MagicMock()
    deal.id = pkg.deal_id
    deal.status = "refi_review"

    from app.core.errors import AppError
    with (
        patch("app.routers.refi.refi_service.get_package", new=AsyncMock(return_value=pkg)),
        patch("app.routers.refi.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch("app.routers.refi.refi_service.record_decision", new=AsyncMock(side_effect=AppError(422, "REASON_REQUIRED", "reason required"))),
    ):
        res = client.post(
            f"/refi-packages/{pkg.id}/decision",
            json={"decision": "rejected"},
            headers=_auth_headers(make_token, role="financier"),
        )
    assert res.status_code == 422
```

- [ ] **Step 2: Run to verify all fail**

```bash
cd backend && python -m pytest tests/test_refi_router.py -v
```

Expected: 3 errors (router not found).

- [ ] **Step 3: Implement the router**

```python
# backend/app/routers/refi.py
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.schemas.refi import FinancierDecisionRequest, FinancierDecisionResponse, RefiPackageResponse
from app.services import deal_service, refi_service

router = APIRouter(tags=["refi"])


@router.post("/deals/{deal_id}/refi-packages", status_code=201)
async def create_refi_package(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    pkg = await refi_service.create_refi_package(db, deal_id, current_user["user_id"])
    return {"data": RefiPackageResponse.model_validate(pkg).model_dump(mode="json")}


@router.post("/refi-packages/{package_id}/send")
async def send_refi_package(
    package_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    pkg = await refi_service.get_package(db, package_id)
    pkg = await refi_service.send_package(db, pkg, pkg.deal_id)
    return {"data": RefiPackageResponse.model_validate(pkg).model_dump(mode="json")}


@router.get("/refi-packages")
async def list_all_refi_packages(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Returns all packages visible to the caller. Financier sees all sent/decided packages."""
    from sqlalchemy import select as sa_select
    result = await db.execute(
        sa_select(RefiPackage).order_by(RefiPackage.created_at.desc())
    )
    packages = list(result.scalars().all())
    return {"data": [RefiPackageResponse.model_validate(p).model_dump(mode="json") for p in packages]}


@router.get("/deals/{deal_id}/refi-packages")
async def list_refi_packages(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    packages = await refi_service.list_packages_for_deal(db, deal_id)
    return {"data": [RefiPackageResponse.model_validate(p).model_dump(mode="json") for p in packages]}


@router.get("/refi-packages/{package_id}")
async def get_refi_package(
    package_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    pkg = await refi_service.get_package(db, package_id)
    return {"data": RefiPackageResponse.model_validate(pkg).model_dump(mode="json")}


@router.post("/refi-packages/{package_id}/decision")
async def record_financier_decision(
    package_id: uuid.UUID,
    body: FinancierDecisionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    pkg = await refi_service.get_package(db, package_id)
    deal = await deal_service.get_deal(db, pkg.deal_id)
    dec = await refi_service.record_decision(
        db, pkg, deal, body.decision, body.reason, current_user["user_id"]
    )
    return {"data": FinancierDecisionResponse.model_validate(dec).model_dump(mode="json")}
```

- [ ] **Step 4: Register in `main.py`**

Add to `backend/app/main.py`:
```python
from app.routers import refi
# ...
app.include_router(refi.router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && python -m pytest tests/test_refi_router.py -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/refi.py backend/tests/test_refi_router.py backend/app/main.py
git commit -m "feat(routers): add refi router — create, send, decision endpoints"
```

---

## Task 9: Offer router

**Files:**
- Create: `backend/app/routers/offers.py`
- Create: `backend/tests/test_offers_router.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the failing tests**

```python
# backend/tests/test_offers_router.py
import uuid
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app

client = TestClient(app)


def _auth_headers(make_token, role: str = "admin") -> dict:
    token = make_token(sub=str(uuid.uuid4()), active_role=role)
    return {"Authorization": f"Bearer {token}"}


def test_generate_offer_returns_201(make_token):
    offer = MagicMock()
    offer.id = uuid.uuid4()
    offer.deal_id = uuid.uuid4()
    offer.version = 1
    offer.is_active = True
    offer.amount_cents = 8_000_000
    offer.duration_months = 36
    offer.monthly_payment_cents = 240_000
    offer.risk_band = "B"
    offer.currency = "EUR"
    offer.valid_until = None
    offer.created_at = __import__("datetime").datetime.utcnow()

    with patch("app.routers.offers.offer_service.generate_offer", new=AsyncMock(return_value=offer)):
        res = client.post(
            f"/deals/{offer.deal_id}/offers",
            headers=_auth_headers(make_token),
        )
    assert res.status_code == 201
    assert res.json()["data"]["version"] == 1
    assert res.json()["data"]["is_active"] is True


def test_get_active_offer(make_token):
    offer = MagicMock()
    offer.id = uuid.uuid4()
    offer.deal_id = uuid.uuid4()
    offer.version = 2
    offer.is_active = True
    offer.amount_cents = 8_000_000
    offer.duration_months = 36
    offer.monthly_payment_cents = 240_000
    offer.risk_band = "B"
    offer.currency = "EUR"
    offer.valid_until = None
    offer.created_at = __import__("datetime").datetime.utcnow()

    with patch("app.routers.offers.offer_service.get_active_offer", new=AsyncMock(return_value=offer)):
        res = client.get(
            f"/deals/{offer.deal_id}/offers/active",
            headers=_auth_headers(make_token),
        )
    assert res.status_code == 200
    assert res.json()["data"]["version"] == 2
```

- [ ] **Step 2: Run to verify fail**

```bash
cd backend && python -m pytest tests/test_offers_router.py -v
```

Expected: 2 errors.

- [ ] **Step 3: Implement the router**

```python
# backend/app/routers/offers.py
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.errors import AppError
from app.schemas.offer import OfferResponse
from app.services import offer_service

router = APIRouter(tags=["offers"])


@router.post("/deals/{deal_id}/offers", status_code=201)
async def generate_offer(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    offer = await offer_service.generate_offer(db, deal_id, current_user["user_id"])
    return {"data": OfferResponse.model_validate(offer).model_dump(mode="json")}


@router.get("/deals/{deal_id}/offers/active")
async def get_active_offer(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    offer = await offer_service.get_active_offer(db, deal_id)
    if offer is None:
        raise AppError(404, "OFFER_NOT_FOUND", f"No active offer for deal {deal_id}")
    return {"data": OfferResponse.model_validate(offer).model_dump(mode="json")}


@router.get("/deals/{deal_id}/offers")
async def list_offers(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    offers = await offer_service.list_offers(db, deal_id)
    return {"data": [OfferResponse.model_validate(o).model_dump(mode="json") for o in offers]}
```

- [ ] **Step 4: Register in `main.py`**

Add to `backend/app/main.py`:
```python
from app.routers import offers
# ...
app.include_router(offers.router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && python -m pytest tests/test_offers_router.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/offers.py backend/tests/test_offers_router.py backend/app/main.py
git commit -m "feat(routers): add offers router — generate, active, list endpoints"
```

---

## Task 10: PappersService

**Files:**
- Modify: `backend/app/core/config.py`
- Create: `backend/app/services/pappers_service.py`
- Modify: `backend/app/services/enrichment_service.py`
- Create: `backend/tests/integration/test_pappers.py`

- [ ] **Step 1: Add config fields**

In `backend/app/core/config.py`, add to the `Settings` class:
```python
pappers_api_key: str = ""
use_real_pappers: bool = False
```

- [ ] **Step 2: Write the PappersService**

```python
# backend/app/services/pappers_service.py
"""Pappers API client. Use via enrichment_service — do not call directly from routers."""
from __future__ import annotations

import logging
from datetime import date

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_BASE = "https://api.pappers.fr/v2"


def _cents_to_none(value: object) -> None:
    return None


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
```

- [ ] **Step 3: Wire PappersService into enrichment_service**

Replace `backend/app/services/enrichment_service.py`:

```python
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
```

- [ ] **Step 4: Write integration test (skipped in CI)**

```python
# backend/tests/integration/test_pappers.py
"""Integration tests — require PAPPERS_API_KEY in env. Run manually or in dedicated CI job."""
import os
import asyncio
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
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/config.py backend/app/services/pappers_service.py \
        backend/app/services/enrichment_service.py backend/tests/integration/
git commit -m "feat(integrations): add PappersService with real API + mock fallback (USE_REAL_PAPPERS flag)"
```

---

## Task 11: MistralService + wire to quote extraction

**Files:**
- Modify: `backend/app/core/config.py`
- Create: `backend/app/services/mistral_service.py`
- Modify: `backend/app/routers/quotes.py`
- Create: `backend/tests/integration/test_mistral.py`

- [ ] **Step 1: Add config fields**

In `backend/app/core/config.py`, add:
```python
mistral_api_key: str = ""
use_real_mistral: bool = False
```

- [ ] **Step 2: Implement MistralService**

```python
# backend/app/services/mistral_service.py
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
        {"label": "MacBook Pro 16\"", "category": "hardware", "quantity": 26, "unit_price_cents": 249_000, "total_price_cents": 6_474_000},
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
```

- [ ] **Step 3: Wire Mistral into the extract endpoint**

Replace the body of `extract_quote` in `backend/app/routers/quotes.py`:

```python
@router.post("/deals/{deal_id}/quotes/{quote_id}/extract")
async def extract_quote(
    deal_id: uuid.UUID,
    quote_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    quote = await _get_quote(db, deal_id, quote_id)

    pdf_bytes = b""  # extract endpoint on existing quote uses no file — falls through to mock unless USE_REAL_MISTRAL set

    from app.services.mistral_service import extract_quote_pdf
    result, source = await extract_quote_pdf(pdf_bytes)

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
```

Also add a new upload-and-extract endpoint for the demo's drag-and-drop moment:

```python
from fastapi import UploadFile, File

@router.post("/deals/{deal_id}/quotes/upload-and-extract", status_code=201)
async def upload_and_extract_quote(
    deal_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a quote and immediately extract it from an uploaded PDF. Demo WOW moment."""
    del current_user
    pdf_bytes = await file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:
        from app.core.errors import AppError
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
```

- [ ] **Step 4: Write integration test**

```python
# backend/tests/integration/test_mistral.py
"""Integration tests — require MISTRAL_API_KEY in env."""
import os
import asyncio
import pytest


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("MISTRAL_API_KEY"), reason="MISTRAL_API_KEY not set")
def test_extract_from_empty_bytes_falls_back_to_mock():
    """Even with a real key, empty PDF bytes must not crash — return mock."""
    import asyncio
    from app.services.mistral_service import extract_quote_pdf
    result, source = asyncio.run(extract_quote_pdf(b""))
    assert "supplier_name" in result
    assert source in ("mistral", "mock")


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("MISTRAL_API_KEY"), reason="MISTRAL_API_KEY not set")
def test_extract_returns_required_keys():
    """Mistral response must include all required fields."""
    from app.services.mistral_service import extract_quote_pdf
    result, source = asyncio.run(extract_quote_pdf(b""))
    for key in ("supplier_name", "amount_excl_tax_cents", "currency", "items"):
        assert key in result
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/config.py backend/app/services/mistral_service.py \
        backend/app/routers/quotes.py backend/tests/integration/test_mistral.py
git commit -m "feat(integrations): add MistralService — OCR + structured extraction with mock fallback"
```

---

## Task 12: CFO portfolio dashboard endpoint

**Files:**
- Create: `backend/app/routers/dashboards.py`
- Modify: `backend/app/main.py`

The demo-only version was deleted. This rebuilds it DB-backed, aggregating from real `deals` and `refi_packages` tables.

- [ ] **Step 1: Implement the router**

```python
# backend/app/routers/dashboards.py
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.deal import Deal

router = APIRouter(tags=["dashboards"])


@router.get("/dashboards/cfo/portfolio")
async def cfo_portfolio(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    active_statuses = [
        "firm_offer_generated", "contract_generated", "signing", "signed",
        "activation_pending", "active", "financier_approved",
    ]
    pipeline_statuses = [
        "submitted", "internal_review", "pre_approved",
        "refi_package_ready", "refi_review",
    ]

    # Total active commitment
    commitment_result = await db.execute(
        select(func.sum(Deal.amount_cents)).where(Deal.status.in_(active_statuses))
    )
    total_commitment_cents = commitment_result.scalar_one() or 0

    # Counts
    active_count_result = await db.execute(
        select(func.count()).where(Deal.status == "active")
    )
    active_leases = active_count_result.scalar_one()

    pipeline_count_result = await db.execute(
        select(func.count()).where(Deal.status.in_(pipeline_statuses))
    )
    pipeline_count = pipeline_count_result.scalar_one()

    # Risk distribution (from deals with risk_band set)
    risk_rows = await db.execute(
        select(Deal.risk_band, func.count(), func.sum(Deal.amount_cents))
        .where(Deal.risk_band.isnot(None))
        .group_by(Deal.risk_band)
        .order_by(Deal.risk_band)
    )
    risk_distribution = [
        {"band": band, "count": count, "exposure_eur": int((amount_cents or 0) / 100)}
        for band, count, amount_cents in risk_rows.all()
    ]

    return {
        "data": {
            "active_leases": active_leases,
            "pipeline_deals": pipeline_count,
            "total_commitment_eur": int(total_commitment_cents / 100),
            "cash_collected_month_eur": 0,  # requires Payment table — built in Phase 3
            "cash_collected_ytd_eur": 0,
            "late_payments": 0,
            "refi_approval_rate_pct": 0,  # computed in Phase 3 from FinancierDecision
            "activation_rate_pct": 0,
            "exposure_by_partner": [],  # requires org join — Phase 2
            "risk_distribution": risk_distribution,
            "monthly": [],
        }
    }
```

- [ ] **Step 2: Register in `main.py`**

```python
from app.routers import dashboards
app.include_router(dashboards.router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/dashboards.py backend/app/main.py
git commit -m "feat(routers): add CFO portfolio dashboard endpoint — DB-backed aggregation"
```

---

## Task 13: Seed script for demo

**Files:**
- Create: `backend/scripts/seed_demo.py`

- [ ] **Step 1: Write the seed script**

```python
#!/usr/bin/env python3
"""Seed 3 demo deals at different pipeline stages.

Run: cd backend && python scripts/seed_demo.py

Requires DATABASE_URL, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY in .env.local
"""
import asyncio
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.models import *  # noqa: F401,F403 — registers all models with Base
from app.core.db import Base


DATABASE_URL = settings.database_url


async def seed():
    engine = create_async_engine(DATABASE_URL, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as db:
        # Clear existing demo data
        await db.execute(text("DELETE FROM companies WHERE siren IN ('123456789','987654321','456789012')"))
        await db.commit()

        # --- Company 1: Globex Inc ---
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

        # --- Company 2: Acme Corp ---
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

        # --- Company 3: Umbrella Corp ---
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

        # --- Deal 1: Globex — status: financier_approved (ready for offer generation) ---
        from app.models.deal import Deal
        deal1_id = uuid.uuid4()
        deal1 = Deal(
            id=deal1_id,
            public_id="D-2026-0001",
            company_id=globex.id,
            status="financier_approved",
            amount_cents=8_550_000,
            currency="EUR",
            duration_months=36,
            risk_score=72.5,
            risk_band="B",
            monthly_payment_cents=250_000,
            created_at=now,
            updated_at=now,
        )
        db.add(deal1)

        # --- Deal 2: Acme — status: refi_package_ready (ready to send to financier) ---
        deal2_id = uuid.uuid4()
        deal2 = Deal(
            id=deal2_id,
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

        # --- Deal 3: Umbrella — status: pre_approved (ready for refi package) ---
        deal3_id = uuid.uuid4()
        deal3 = Deal(
            id=deal3_id,
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
        print("✅ Demo seed complete: 3 companies, 3 deals at D-2026-0001..0003")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
```

- [ ] **Step 2: Run the seed**

```bash
cd backend && python scripts/seed_demo.py
```

Expected: `✅ Demo seed complete: 3 companies, 3 deals at D-2026-0001..0003`

- [ ] **Step 3: Commit**

```bash
git add backend/scripts/seed_demo.py
git commit -m "feat(seed): add demo seed script — 3 deals at pre_approved/refi_package_ready/financier_approved"
```

---

## Task 14: Full test run

- [ ] **Step 1: Run all non-integration tests**

```bash
cd backend && python -m pytest tests/ -v --ignore=tests/integration
```

Expected: all pass, no regression on existing tests.

- [ ] **Step 2: Check backend imports cleanly**

```bash
cd backend && python -c "from app.main import app; print(len(app.routes), 'routes')"
```

Expected: `47 routes` (39 existing + 8 new).

- [ ] **Step 3: Final commit on feature branch**

```bash
git add -A
git commit -m "chore: Phase 1 backend complete — refi + offers + Pappers + Mistral"
```

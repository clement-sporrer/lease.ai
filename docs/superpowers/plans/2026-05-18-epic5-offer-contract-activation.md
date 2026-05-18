# Epic 5 — Offer, Contract, Activation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the full contract lifecycle from `firm_offer_generated` to `active`, including contract generation, mock signature, auto-derived activation checklist, asset creation from quote lines, and payment schedule generation.

**Architecture:** New `ContractService` handles all business logic; `contracts.py` router exposes 6 endpoints following the existing thin-router pattern. Two new React components (`ContractPanel`, `ActivationChecklist`) render conditionally inside the existing deal detail page based on `deal.status`. No new DB migration needed — `contracts`, `assets`, `payment_schedules` tables must be created.

**Tech Stack:** FastAPI + SQLAlchemy 2.0 async + Pydantic v2 (backend); Next.js App Router + TypeScript + Sonner toasts (web)

---

## File Map

**Backend — new**
- `backend/app/models/contract.py` — `Contract`, `Asset`, `PaymentSchedule` ORM models
- `backend/alembic/versions/005_add_contracts_assets_schedules.py` — migration
- `backend/app/schemas/contract.py` — Pydantic request/response schemas
- `backend/app/services/contract_service.py` — all business logic
- `backend/app/routers/contracts.py` — thin router, 6 endpoints
- `backend/tests/test_contract_service.py` — service unit tests
- `backend/tests/test_contracts_router.py` — router integration tests

**Backend — modified**
- `backend/app/main.py` — add `from app.routers import contracts` + `app.include_router(contracts.router)`

**Web — new**
- `web/lib/types/contract.ts` — TypeScript types
- `web/lib/actions/contract-actions.ts` — server actions
- `web/components/admin/ContractPanel.tsx` — contract generation + signature flow
- `web/components/admin/ActivationChecklist.tsx` — checklist + activate button

**Web — modified**
- `web/app/(admin)/admin/deals/[id]/page.tsx` — add contract fetch + render new panels

---

## Task 1: ORM Models

**Files:**
- Create: `backend/app/models/contract.py`

- [ ] **Step 1: Write the models**

```python
# backend/app/models/contract.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    public_id: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="draft")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_commitment_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    unit_value_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/contract.py
git commit -m "feat(models): add Contract, Asset, PaymentSchedule ORM models"
```

---

## Task 2: Alembic Migration

**Files:**
- Create: `backend/alembic/versions/005_add_contracts_assets_schedules.py`

- [ ] **Step 1: Write the migration**

```python
# backend/alembic/versions/005_add_contracts_assets_schedules.py
"""add contracts assets payment_schedules

Revision ID: 005
Revises: 02f59637f6b5
Create Date: 2026-05-18
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "02f59637f6b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("deal_id", sa.UUID(), nullable=False),
        sa.Column("public_id", sa.String(30), nullable=False),
        sa.Column("status", sa.String(50), server_default="draft", nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_commitment_cents", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id"),
    )
    op.create_index("ix_contracts_deal_id", "contracts", ["deal_id"])

    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("contract_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("unit_value_cents", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assets_contract_id", "assets", ["contract_id"])

    op.create_table(
        "payment_schedules",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("contract_id", sa.UUID(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount_cents", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payment_schedules_contract_id", "payment_schedules", ["contract_id"])


def downgrade() -> None:
    op.drop_index("ix_payment_schedules_contract_id", table_name="payment_schedules")
    op.drop_table("payment_schedules")
    op.drop_index("ix_assets_contract_id", table_name="assets")
    op.drop_table("assets")
    op.drop_index("ix_contracts_deal_id", table_name="contracts")
    op.drop_table("contracts")
```

- [ ] **Step 2: Run migration**

```bash
cd backend
alembic upgrade head
```

Expected: migration applies cleanly, tables `contracts`, `assets`, `payment_schedules` created.

- [ ] **Step 3: Commit**

```bash
git add backend/alembic/versions/005_add_contracts_assets_schedules.py
git commit -m "feat(migration): add contracts, assets, payment_schedules tables"
```

---

## Task 3: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/contract.py`

- [ ] **Step 1: Write schemas**

```python
# backend/app/schemas/contract.py
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    public_id: str
    status: str
    sent_at: datetime | None
    signed_at: datetime | None
    activated_at: datetime | None
    total_commitment_cents: int | None
    created_at: datetime


class ActivationChecklistItem(BaseModel):
    key: str
    label: str
    satisfied: bool


class ActivationChecklistResponse(BaseModel):
    items: list[ActivationChecklistItem]
    all_satisfied: bool
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas/contract.py
git commit -m "feat(schemas): add ContractResponse and ActivationChecklist schemas"
```

---

## Task 4: ContractService — generate, send, mock-sign

**Files:**
- Create: `backend/app/services/contract_service.py`

- [ ] **Step 1: Write the failing test for generate_contract**

```python
# backend/tests/test_contract_service.py
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.errors import AppError
from app.services import contract_service


def _make_deal(status: str = "firm_offer_generated") -> MagicMock:
    deal = MagicMock()
    deal.id = uuid.uuid4()
    deal.status = status
    deal.amount_cents = 10_000_00
    deal.duration_months = 36
    deal.monthly_payment_cents = 30_000
    return deal


def _make_db() -> AsyncMock:
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.mark.anyio
async def test_generate_contract_creates_contract():
    deal = _make_deal("firm_offer_generated")
    db = _make_db()

    with (
        patch("app.services.contract_service.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch("app.services.contract_service._get_latest_contract", new=AsyncMock(return_value=None)),
        patch("app.services.contract_service.deal_service.transition_deal", new=AsyncMock(return_value=deal)),
    ):
        result = await contract_service.generate_contract(db, deal.id, str(uuid.uuid4()))

    assert db.add.called
    added = db.add.call_args[0][0]
    assert added.deal_id == deal.id
    assert added.status == "draft"
    assert added.public_id.startswith("CTR-")


@pytest.mark.anyio
async def test_generate_contract_idempotent():
    deal = _make_deal("contract_generated")
    existing = MagicMock()
    existing.deal_id = deal.id
    existing.status = "draft"
    db = _make_db()

    with (
        patch("app.services.contract_service.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch("app.services.contract_service._get_latest_contract", new=AsyncMock(return_value=existing)),
    ):
        result = await contract_service.generate_contract(db, deal.id, str(uuid.uuid4()))

    assert result is existing
    assert not db.add.called


@pytest.mark.anyio
async def test_generate_contract_rejects_wrong_status():
    deal = _make_deal("pre_approved")
    db = _make_db()

    with patch("app.services.contract_service.deal_service.get_deal", new=AsyncMock(return_value=deal)):
        with pytest.raises(AppError) as exc:
            await contract_service.generate_contract(db, deal.id, str(uuid.uuid4()))

    assert exc.value.status_code == 409
    assert exc.value.code == "INVALID_STATE"
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd backend
python -m pytest tests/test_contract_service.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — `contract_service` does not exist yet.

- [ ] **Step 3: Implement generate_contract, send_signature, mock_sign**

```python
# backend/app/services/contract_service.py
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.contract import Contract
from app.services import deal_service

_GENERATE_ALLOWED = {"firm_offer_generated", "contract_generated", "signing", "signed"}


async def _get_latest_contract(db: AsyncSession, deal_id: uuid.UUID) -> Contract | None:
    result = await db.execute(
        select(Contract)
        .where(Contract.deal_id == deal_id)
        .order_by(Contract.created_at.desc())
    )
    return result.scalar_one_or_none()


async def get_contract(db: AsyncSession, contract_id: uuid.UUID) -> Contract:
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if contract is None:
        raise AppError(404, "CONTRACT_NOT_FOUND", f"Contract {contract_id} not found")
    return contract


async def generate_contract(db: AsyncSession, deal_id: uuid.UUID, user_id: str) -> Contract:
    deal = await deal_service.get_deal(db, deal_id)
    if deal.status not in _GENERATE_ALLOWED:
        raise AppError(
            409,
            "INVALID_STATE",
            f"Cannot generate contract from status {deal.status!r}",
            {"current_status": deal.status, "allowed": sorted(_GENERATE_ALLOWED)},
        )
    existing = await _get_latest_contract(db, deal_id)
    if existing is not None:
        return existing

    short = str(deal_id)[:8].upper()
    public_id = f"CTR-{short}"
    contract = Contract(
        id=uuid.uuid4(),
        deal_id=deal_id,
        public_id=public_id,
        status="draft",
    )
    db.add(contract)
    if deal.status == "firm_offer_generated":
        await deal_service.transition_deal(db, deal_id, "contract_generated")
    await db.commit()
    await db.refresh(contract)
    return contract


async def send_signature(db: AsyncSession, contract_id: uuid.UUID, user_id: str) -> Contract:
    contract = await get_contract(db, contract_id)
    if contract.status != "draft":
        raise AppError(
            409,
            "INVALID_STATE",
            f"Contract status is {contract.status!r}, must be draft to send for signature",
        )
    contract.sent_at = datetime.now(timezone.utc)
    contract.status = "sent_for_signature"
    await deal_service.transition_deal(db, contract.deal_id, "signing")
    await db.commit()
    await db.refresh(contract)
    return contract


async def mock_sign(db: AsyncSession, contract_id: uuid.UUID, user_id: str) -> Contract:
    contract = await get_contract(db, contract_id)
    if contract.status != "sent_for_signature":
        raise AppError(
            409,
            "INVALID_STATE",
            f"Contract status is {contract.status!r}, must be sent_for_signature to sign",
        )
    contract.signed_at = datetime.now(timezone.utc)
    contract.status = "signed"
    await deal_service.transition_deal(db, contract.deal_id, "signed")
    await db.commit()
    await db.refresh(contract)
    return contract
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd backend
python -m pytest tests/test_contract_service.py::test_generate_contract_creates_contract tests/test_contract_service.py::test_generate_contract_idempotent tests/test_contract_service.py::test_generate_contract_rejects_wrong_status -v
```

Expected: all 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/contract_service.py backend/tests/test_contract_service.py
git commit -m "feat(service): add ContractService — generate, send_signature, mock_sign"
```

---

## Task 5: ContractService — activation_checklist + activate

**Files:**
- Modify: `backend/app/services/contract_service.py`
- Modify: `backend/tests/test_contract_service.py`

- [ ] **Step 1: Write failing tests for checklist and activate**

Add to `backend/tests/test_contract_service.py`:

```python
@pytest.mark.anyio
async def test_activation_checklist_all_satisfied():
    contract_id = uuid.uuid4()
    deal_id = uuid.uuid4()

    contract = MagicMock()
    contract.id = contract_id
    contract.deal_id = deal_id
    contract.status = "signed"
    contract.sent_at = datetime.now(timezone.utc)
    contract.signed_at = datetime.now(timezone.utc)

    db = _make_db()

    with (
        patch("app.services.contract_service.get_contract", new=AsyncMock(return_value=contract)),
        patch("app.services.contract_service._check_financier_decision", new=AsyncMock(return_value=True)),
        patch("app.services.contract_service._check_active_offer", new=AsyncMock(return_value=True)),
        patch("app.services.contract_service._check_quote_validated", new=AsyncMock(return_value=True)),
    ):
        result = await contract_service.activation_checklist(db, contract_id)

    assert result["all_satisfied"] is True
    assert all(item["satisfied"] for item in result["items"])


@pytest.mark.anyio
async def test_activation_checklist_partial():
    contract_id = uuid.uuid4()
    deal_id = uuid.uuid4()

    contract = MagicMock()
    contract.id = contract_id
    contract.deal_id = deal_id
    contract.status = "draft"
    contract.sent_at = None
    contract.signed_at = None

    db = _make_db()

    with (
        patch("app.services.contract_service.get_contract", new=AsyncMock(return_value=contract)),
        patch("app.services.contract_service._check_financier_decision", new=AsyncMock(return_value=False)),
        patch("app.services.contract_service._check_active_offer", new=AsyncMock(return_value=True)),
        patch("app.services.contract_service._check_quote_validated", new=AsyncMock(return_value=False)),
    ):
        result = await contract_service.activation_checklist(db, contract_id)

    assert result["all_satisfied"] is False
    failed = [item for item in result["items"] if not item["satisfied"]]
    assert len(failed) >= 3


@pytest.mark.anyio
async def test_activate_blocks_when_checklist_not_satisfied():
    contract_id = uuid.uuid4()
    deal_id = uuid.uuid4()

    contract = MagicMock()
    contract.id = contract_id
    contract.deal_id = deal_id
    contract.status = "signed"

    checklist_result = {
        "all_satisfied": False,
        "items": [
            {"key": "contract_signed", "label": "Contrat signé", "satisfied": False},
        ],
    }

    db = _make_db()

    with (
        patch("app.services.contract_service.get_contract", new=AsyncMock(return_value=contract)),
        patch("app.services.contract_service.activation_checklist", new=AsyncMock(return_value=checklist_result)),
    ):
        with pytest.raises(AppError) as exc:
            await contract_service.activate(db, contract_id, str(uuid.uuid4()))

    assert exc.value.status_code == 400
    assert exc.value.code == "ACTIVATION_BLOCKED"
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd backend
python -m pytest tests/test_contract_service.py::test_activation_checklist_all_satisfied tests/test_contract_service.py::test_activation_checklist_partial tests/test_contract_service.py::test_activate_blocks_when_checklist_not_satisfied -v
```

Expected: all FAIL — functions not defined yet.

- [ ] **Step 3: Implement checklist helpers and activate**

Append to `backend/app/services/contract_service.py`:

```python
from app.models.offer import Offer
from app.models.quote import Quote
from app.models.refi_package import FinancierDecision, RefiPackage
from app.models.contract import Asset, PaymentSchedule
from app.models.pricing_proposal import PricingProposal
from dateutil.relativedelta import relativedelta


async def _check_financier_decision(db: AsyncSession, deal_id: uuid.UUID) -> bool:
    pkg_result = await db.execute(
        select(RefiPackage).where(RefiPackage.deal_id == deal_id).order_by(RefiPackage.created_at.desc())
    )
    pkg = pkg_result.scalar_one_or_none()
    if pkg is None:
        return False
    dec_result = await db.execute(
        select(FinancierDecision).where(
            FinancierDecision.refi_package_id == pkg.id,
            FinancierDecision.decision == "approved",
        )
    )
    return dec_result.scalar_one_or_none() is not None


async def _check_active_offer(db: AsyncSession, deal_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Offer).where(Offer.deal_id == deal_id, Offer.is_active.is_(True))
    )
    return result.scalar_one_or_none() is not None


async def _check_quote_validated(db: AsyncSession, deal_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Quote).where(
            Quote.deal_id == deal_id,
            Quote.extraction_status == "validated",
        )
    )
    return result.scalar_one_or_none() is not None


async def activation_checklist(db: AsyncSession, contract_id: uuid.UUID) -> dict:
    contract = await get_contract(db, contract_id)

    financier_ok = await _check_financier_decision(db, contract.deal_id)
    offer_ok = await _check_active_offer(db, contract.deal_id)
    quote_ok = await _check_quote_validated(db, contract.deal_id)

    items = [
        {"key": "contract_generated", "label": "Contrat généré", "satisfied": True},
        {"key": "contract_sent", "label": "Contrat envoyé pour signature", "satisfied": contract.sent_at is not None},
        {"key": "contract_signed", "label": "Contrat signé", "satisfied": contract.signed_at is not None},
        {"key": "financier_decision_received", "label": "Accord financeur reçu", "satisfied": financier_ok},
        {"key": "active_offer_present", "label": "Offre ferme active", "satisfied": offer_ok},
        {"key": "quote_validated", "label": "Devis validé", "satisfied": quote_ok},
    ]
    all_satisfied = all(item["satisfied"] for item in items)
    return {"items": items, "all_satisfied": all_satisfied}


async def activate(db: AsyncSession, contract_id: uuid.UUID, user_id: str) -> Contract:
    contract = await get_contract(db, contract_id)

    checklist = await activation_checklist(db, contract_id)
    if not checklist["all_satisfied"]:
        failed = [item["key"] for item in checklist["items"] if not item["satisfied"]]
        raise AppError(
            400,
            "ACTIVATION_BLOCKED",
            "Activation blocked: not all conditions are satisfied",
            {"failed_conditions": failed},
        )

    # Fetch active offer for schedule amount
    offer_result = await db.execute(
        select(Offer).where(Offer.deal_id == contract.deal_id, Offer.is_active.is_(True))
    )
    offer = offer_result.scalar_one_or_none()

    # Fetch pricing proposal for duration and monthly amount
    pricing_result = await db.execute(
        select(PricingProposal)
        .where(PricingProposal.deal_id == contract.deal_id)
        .order_by(PricingProposal.version.desc())
    )
    pricing = pricing_result.scalar_one_or_none()
    if pricing is None:
        raise AppError(
            409,
            "PRICING_PROPOSAL_MISSING",
            "No pricing proposal found for this deal — cannot generate payment schedule",
        )

    # Fetch quote items for asset creation
    from app.models.quote import QuoteItem
    quote_result = await db.execute(
        select(Quote)
        .where(Quote.deal_id == contract.deal_id)
        .order_by(Quote.created_at.desc())
    )
    quote = quote_result.scalar_one_or_none()

    if quote:
        items_result = await db.execute(
            select(QuoteItem).where(QuoteItem.quote_id == quote.id)
        )
        quote_items = list(items_result.scalars().all())
        for item in quote_items:
            asset = Asset(
                id=uuid.uuid4(),
                contract_id=contract.id,
                name=item.label,
                category=item.category,
                quantity=item.quantity,
                unit_value_cents=item.unit_price_cents,
            )
            db.add(asset)

    # Generate payment schedule
    now = datetime.now(timezone.utc)
    for n in range(1, pricing.duration_months + 1):
        schedule_entry = PaymentSchedule(
            id=uuid.uuid4(),
            contract_id=contract.id,
            due_date=now + relativedelta(months=n),
            amount_cents=pricing.monthly_payment_cents,
            status="pending",
        )
        db.add(schedule_entry)

    # Update total commitment
    contract.total_commitment_cents = pricing.monthly_payment_cents * pricing.duration_months
    contract.activated_at = now
    contract.status = "active"

    await deal_service.transition_deal(db, contract.deal_id, "activation_pending")
    await deal_service.transition_deal(db, contract.deal_id, "active")

    await db.commit()
    await db.refresh(contract)
    return contract
```

> **Note:** `python-dateutil` must be available. Check `backend/requirements.txt` — if not present, add `python-dateutil>=2.9`.

- [ ] **Step 4: Run all contract service tests**

```bash
cd backend
python -m pytest tests/test_contract_service.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/contract_service.py backend/tests/test_contract_service.py
git commit -m "feat(service): add activation_checklist and activate to ContractService"
```

---

## Task 6: Contracts Router

**Files:**
- Create: `backend/app/routers/contracts.py`
- Create: `backend/tests/test_contracts_router.py`

- [ ] **Step 1: Write failing router tests**

```python
# backend/tests/test_contracts_router.py
from __future__ import annotations

import uuid
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _make_contract() -> MagicMock:
    c = MagicMock()
    c.id = uuid.uuid4()
    c.deal_id = uuid.uuid4()
    c.public_id = "CTR-ABCD1234"
    c.status = "draft"
    c.sent_at = None
    c.signed_at = None
    c.activated_at = None
    c.total_commitment_cents = None
    c.created_at = datetime.datetime.now(datetime.timezone.utc)
    c.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return c


@pytest.mark.anyio
async def test_generate_contract_returns_201(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    contract = _make_contract()

    with (
        patch("app.routers.contracts.contract_service.generate_contract", new=AsyncMock(return_value=contract)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/deals/{contract.deal_id}/contracts",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 201
    assert res.json()["data"]["public_id"] == "CTR-ABCD1234"


@pytest.mark.anyio
async def test_generate_contract_forbidden_for_financier(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="financier")

    with patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/deals/{uuid.uuid4()}/contracts",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 403


@pytest.mark.anyio
async def test_get_latest_contract_returns_null_when_none(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    deal_id = uuid.uuid4()

    with (
        patch("app.routers.contracts.contract_service._get_latest_contract", new=AsyncMock(return_value=None)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(
                f"/deals/{deal_id}/contracts/latest",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"] is None


@pytest.mark.anyio
async def test_activation_checklist_returns_200(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    contract_id = uuid.uuid4()
    checklist = {
        "items": [{"key": "contract_generated", "label": "Contrat généré", "satisfied": True}],
        "all_satisfied": True,
    }

    with (
        patch("app.routers.contracts.contract_service.activation_checklist", new=AsyncMock(return_value=checklist)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get(
                f"/contracts/{contract_id}/activation-checklist",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"]["all_satisfied"] is True
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd backend
python -m pytest tests/test_contracts_router.py -v
```

Expected: `ImportError` — `app.routers.contracts` does not exist.

- [ ] **Step 3: Implement router**

```python
# backend/app/routers/contracts.py
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.schemas.contract import ActivationChecklistResponse, ContractResponse
from app.services import contract_service

_READ_ROLES = {"admin", "ops", "risk"}
_WRITE_ROLES = {"admin", "ops"}

router = APIRouter(tags=["contracts"])


def _require_read(current_user: dict) -> None:
    if current_user.get("active_role") not in _READ_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: internal roles only")


def _require_write(current_user: dict) -> None:
    if current_user.get("active_role") not in _WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: ops or admin required")


@router.post("/deals/{deal_id}/contracts", status_code=201)
async def generate_contract(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    contract = await contract_service.generate_contract(db, deal_id, current_user["user_id"])
    return {"data": ContractResponse.model_validate(contract).model_dump(mode="json")}


@router.get("/deals/{deal_id}/contracts/latest")
async def get_latest_contract(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    contract = await contract_service._get_latest_contract(db, deal_id)
    data = ContractResponse.model_validate(contract).model_dump(mode="json") if contract else None
    return {"data": data}


@router.post("/contracts/{contract_id}/send-signature")
async def send_signature(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    contract = await contract_service.send_signature(db, contract_id, current_user["user_id"])
    return {"data": ContractResponse.model_validate(contract).model_dump(mode="json")}


@router.post("/contracts/{contract_id}/mock-sign")
async def mock_sign(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    contract = await contract_service.mock_sign(db, contract_id, current_user["user_id"])
    return {"data": ContractResponse.model_validate(contract).model_dump(mode="json")}


@router.get("/contracts/{contract_id}/activation-checklist")
async def get_activation_checklist(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    checklist = await contract_service.activation_checklist(db, contract_id)
    return {"data": ActivationChecklistResponse(**checklist).model_dump()}


@router.post("/contracts/{contract_id}/activate")
async def activate_contract(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    contract = await contract_service.activate(db, contract_id, current_user["user_id"])
    return {"data": ContractResponse.model_validate(contract).model_dump(mode="json")}
```

- [ ] **Step 4: Register router in main.py**

In `backend/app/main.py`, add `contracts` to the import and `app.include_router` lines:

```python
# Change this line:
from app.routers import admin, auth, companies, dashboards, deals, documents, me, offers, pricing, quotes, refi, risk

# To:
from app.routers import admin, auth, companies, contracts, dashboards, deals, documents, me, offers, pricing, quotes, refi, risk
```

And add after the existing `app.include_router(refi.router)` line:
```python
app.include_router(contracts.router)
```

- [ ] **Step 5: Run router tests**

```bash
cd backend
python -m pytest tests/test_contracts_router.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 6: Run full test suite**

```bash
cd backend
python -m pytest -v
```

Expected: all tests pass (no regressions).

- [ ] **Step 7: Commit**

```bash
git add backend/app/routers/contracts.py backend/tests/test_contracts_router.py backend/app/main.py
git commit -m "feat(router): add contracts router — generate, send-signature, mock-sign, checklist, activate"
```

---

## Task 7: Web Types and Server Actions

**Files:**
- Create: `web/lib/types/contract.ts`
- Create: `web/lib/actions/contract-actions.ts`

- [ ] **Step 1: Write TypeScript types**

```typescript
// web/lib/types/contract.ts
export interface Contract {
  id: string
  deal_id: string
  public_id: string
  status: string
  sent_at: string | null
  signed_at: string | null
  activated_at: string | null
  total_commitment_cents: number | null
  created_at: string
}

export interface ActivationChecklistItem {
  key: string
  label: string
  satisfied: boolean
}

export interface ActivationChecklist {
  items: ActivationChecklistItem[]
  all_satisfied: boolean
}
```

- [ ] **Step 2: Write server actions**

```typescript
// web/lib/actions/contract-actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import type { Contract } from '@/lib/types/contract'

async function getToken(): Promise<string> {
  const supabase = await createSupabaseServerClient()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error('Not authenticated')
  return session.access_token
}

export async function generateContract(dealId: string): Promise<{ data: Contract } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Contract }>(`/deals/${dealId}/contracts`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Échec de la génération du contrat' }
  }
}

export async function sendSignature(contractId: string, dealId: string): Promise<{ data: Contract } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Contract }>(`/contracts/${contractId}/send-signature`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Échec de l\'envoi pour signature' }
  }
}

export async function mockSign(contractId: string, dealId: string): Promise<{ data: Contract } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Contract }>(`/contracts/${contractId}/mock-sign`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Échec de la signature simulée' }
  }
}

export async function activateContract(contractId: string, dealId: string): Promise<{ data: Contract } | { error: string }> {
  try {
    const token = await getToken()
    const result = await apiFetch<{ data: Contract }>(`/contracts/${contractId}/activate`, token, { method: 'POST' })
    revalidatePath(`/admin/deals/${dealId}`)
    return result
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Échec de l\'activation' }
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add web/lib/types/contract.ts web/lib/actions/contract-actions.ts
git commit -m "feat(web): contract types and server actions"
```

---

## Task 8: ContractPanel Component

**Files:**
- Create: `web/components/admin/ContractPanel.tsx`

- [ ] **Step 1: Write the component**

```tsx
// web/components/admin/ContractPanel.tsx
'use client'

import { useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { generateContract, sendSignature, mockSign } from '@/lib/actions/contract-actions'
import { Button } from '@/components/ui/button'
import type { Contract } from '@/lib/types/contract'

const CONTRACT_VISIBLE_STATUSES = new Set([
  'firm_offer_generated',
  'contract_generated',
  'signing',
  'signed',
  'activation_pending',
  'active',
])

interface Props {
  dealId: string
  dealStatus: string
  contract: Contract | null
}

export function ContractPanel({ dealId, dealStatus, contract }: Props) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()

  if (!CONTRACT_VISIBLE_STATUSES.has(dealStatus)) return null

  function handleGenerate() {
    startTransition(async () => {
      const result = await generateContract(dealId)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        toast.success('Contrat généré')
        router.refresh()
      }
    })
  }

  function handleSendSignature() {
    if (!contract) return
    startTransition(async () => {
      const result = await sendSignature(contract.id, dealId)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        toast.success('Contrat envoyé pour signature')
        router.refresh()
      }
    })
  }

  function handleMockSign() {
    if (!contract) return
    startTransition(async () => {
      const result = await mockSign(contract.id, dealId)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        toast.success('Contrat signé')
        router.refresh()
      }
    })
  }

  return (
    <div className="rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
        <h2 className="text-sm font-semibold text-navy-900">Contrat</h2>
        {dealStatus === 'firm_offer_generated' && (
          <Button variant="primary" size="sm" onClick={handleGenerate} disabled={isPending}>
            {isPending ? 'Génération…' : 'Générer le contrat'}
          </Button>
        )}
        {contract?.status === 'draft' && dealStatus === 'contract_generated' && (
          <Button variant="primary" size="sm" onClick={handleSendSignature} disabled={isPending}>
            {isPending ? 'Envoi…' : 'Envoyer pour signature'}
          </Button>
        )}
        {contract?.status === 'sent_for_signature' && dealStatus === 'signing' && (
          <Button variant="success" size="sm" onClick={handleMockSign} disabled={isPending}>
            {isPending ? 'Signature…' : 'Simuler la signature'}
          </Button>
        )}
      </div>
      <div className="px-6 py-5">
        {contract ? (
          <div className="space-y-2.5">
            <Row label="Référence">
              <span className="font-mono text-sm">{contract.public_id}</span>
            </Row>
            <Row label="Statut">
              <ContractStatusBadge status={contract.status} />
            </Row>
            <Row label="Généré le">
              <span className="text-sm text-gray-600">
                {new Date(contract.created_at).toLocaleDateString('fr-FR')}
              </span>
            </Row>
            {contract.sent_at && (
              <Row label="Envoyé le">
                <span className="text-sm text-gray-600">
                  {new Date(contract.sent_at).toLocaleDateString('fr-FR')}
                </span>
              </Row>
            )}
            {contract.signed_at && (
              <Row label="Signé le">
                <span className="text-sm text-teal-700 font-medium">
                  {new Date(contract.signed_at).toLocaleDateString('fr-FR')}
                </span>
              </Row>
            )}
            {contract.total_commitment_cents != null && (
              <Row label="Engagement total">
                <span className="font-mono text-sm tabular-nums">
                  {(contract.total_commitment_cents / 100).toLocaleString('fr-FR', {
                    style: 'currency',
                    currency: 'EUR',
                  })}
                </span>
              </Row>
            )}
          </div>
        ) : (
          <p className="italic text-gray-400 text-sm">Aucun contrat généré</p>
        )}
      </div>
    </div>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-500">{label}</span>
      {children}
    </div>
  )
}

const CONTRACT_STATUS_LABELS: Record<string, { label: string; className: string }> = {
  draft: { label: 'Brouillon', className: 'bg-gray-100 text-gray-600' },
  sent_for_signature: { label: 'En signature', className: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200' },
  signed: { label: 'Signé', className: 'bg-teal-50 text-teal-700 ring-1 ring-teal-200' },
  active: { label: 'Actif', className: 'bg-teal-50 text-teal-700 ring-1 ring-teal-200' },
}

function ContractStatusBadge({ status }: { status: string }) {
  const config = CONTRACT_STATUS_LABELS[status] ?? { label: status, className: 'bg-gray-100 text-gray-500' }
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${config.className}`}>
      {config.label}
    </span>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add web/components/admin/ContractPanel.tsx
git commit -m "feat(web): add ContractPanel component"
```

---

## Task 9: ActivationChecklist Component

**Files:**
- Create: `web/components/admin/ActivationChecklist.tsx`

- [ ] **Step 1: Write the component**

```tsx
// web/components/admin/ActivationChecklist.tsx
'use client'

import { useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { activateContract } from '@/lib/actions/contract-actions'
import { Button } from '@/components/ui/button'
import type { ActivationChecklist as ActivationChecklistType, Contract } from '@/lib/types/contract'

const CHECKLIST_VISIBLE_STATUSES = new Set(['signed', 'activation_pending', 'active'])

interface Props {
  dealId: string
  dealStatus: string
  contract: Contract | null
  checklist: ActivationChecklistType | null
}

export function ActivationChecklist({ dealId, dealStatus, contract, checklist }: Props) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()

  if (!CHECKLIST_VISIBLE_STATUSES.has(dealStatus) || !contract) return null

  const isAlreadyActive = dealStatus === 'active'

  function handleActivate() {
    if (!contract) return
    startTransition(async () => {
      const result = await activateContract(contract.id, dealId)
      if ('error' in result) {
        toast.error(result.error)
      } else {
        toast.success('Contrat activé — dossier actif')
        router.refresh()
      }
    })
  }

  const failedConditions = checklist?.items.filter(item => !item.satisfied) ?? []

  return (
    <div className="rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
        <h2 className="text-sm font-semibold text-navy-900">Checklist d'activation</h2>
        {!isAlreadyActive && (
          <Button
            variant="primary"
            size="sm"
            onClick={handleActivate}
            disabled={isPending || !checklist?.all_satisfied}
            title={
              !checklist?.all_satisfied
                ? `${failedConditions.length} condition(s) manquante(s)`
                : undefined
            }
          >
            {isPending ? 'Activation…' : 'Activer le contrat'}
          </Button>
        )}
        {isAlreadyActive && (
          <span className="inline-flex items-center gap-1 rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700 ring-1 ring-teal-200">
            ✓ Actif
          </span>
        )}
      </div>
      <div className="px-6 py-5">
        {checklist ? (
          <ul className="space-y-2.5">
            {checklist.items.map(item => (
              <li key={item.key} className="flex items-center gap-3">
                <span
                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-bold ${
                    item.satisfied
                      ? 'bg-teal-100 text-teal-700'
                      : 'bg-red-50 text-red-500 ring-1 ring-red-200'
                  }`}
                >
                  {item.satisfied ? '✓' : '✗'}
                </span>
                <span className={`text-sm ${item.satisfied ? 'text-gray-700' : 'text-gray-500'}`}>
                  {item.label}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="italic text-gray-400 text-sm">Chargement de la checklist…</p>
        )}
        {!isAlreadyActive && failedConditions.length > 0 && (
          <p className="mt-4 text-xs text-red-500">
            {failedConditions.length} condition(s) à remplir avant activation.
          </p>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add web/components/admin/ActivationChecklist.tsx
git commit -m "feat(web): add ActivationChecklist component"
```

---

## Task 10: Wire into Deal Detail Page

**Files:**
- Modify: `web/app/(admin)/admin/deals/[id]/page.tsx`

- [ ] **Step 1: Read the current page**

Read `web/app/(admin)/admin/deals/[id]/page.tsx` fully before editing.

- [ ] **Step 2: Add contract fetch and new panel imports**

Add at the top of the file with the other imports:

```tsx
import { ContractPanel } from '@/components/admin/ContractPanel'
import { ActivationChecklist } from '@/components/admin/ActivationChecklist'
import type { Contract, ActivationChecklist as ActivationChecklistType } from '@/lib/types/contract'
```

- [ ] **Step 3: Add contract and checklist state variables**

In the variable declarations section (after `let activeOffer: Offer | null = null`), add:

```tsx
let contract: Contract | null = null
let activationChecklist: ActivationChecklistType | null = null
```

- [ ] **Step 4: Add contract to the initial Promise.allSettled**

The page currently fetches deal, checklist, timeline, refi in parallel. Add contract fetch to that block:

```tsx
const [dealResult, checklistResult, timelineResult, refiResult, contractResult] = await Promise.allSettled([
  apiFetch<{ data: Deal }>(`/deals/${id}`, token),
  apiFetch<{ data: DealChecklist }>(`/admin/deals/${id}/checklist`, token),
  apiFetch<TimelineResponse>(`/deals/${id}/timeline`, token),
  apiFetch<{ data: RefiPackage[] }>(`/deals/${id}/refi-packages`, token),
  apiFetch<{ data: Contract | null }>(`/deals/${id}/contracts/latest`, token),
])
```

And after the existing `if (refiResult...)` line:

```tsx
if (contractResult.status === 'fulfilled') contract = contractResult.value.data
```

- [ ] **Step 5: Fetch activation checklist when contract exists**

In the second `Promise.allSettled` block (which runs after deal loads), add the activation checklist fetch when a signed contract exists. After the `[companyResult, offerResult]` settlement block, add:

```tsx
if (contract && ['signed', 'activation_pending', 'active'].includes(deal.status ?? '')) {
  const checklistResult = await apiFetch<{ data: ActivationChecklistType }>(
    `/contracts/${contract.id}/activation-checklist`,
    token
  ).catch(() => null)
  if (checklistResult) activationChecklist = checklistResult.data
}
```

- [ ] **Step 6: Render the new panels in the JSX**

After the existing `<OfferPanel ... />` in the JSX, add:

```tsx
<ContractPanel
  dealId={id}
  dealStatus={deal.status}
  contract={contract}
/>
<ActivationChecklist
  dealId={id}
  dealStatus={deal.status}
  contract={contract}
  checklist={activationChecklist}
/>
```

- [ ] **Step 7: TypeScript check**

```bash
cd web
npx tsc --noEmit
```

Expected: 0 errors.

- [ ] **Step 8: Commit**

```bash
git add web/app/\(admin\)/admin/deals/\[id\]/page.tsx
git commit -m "feat(web): wire ContractPanel + ActivationChecklist into deal detail page"
```

---

## Task 11: python-dateutil Dependency Check

**Files:**
- Possibly modify: `backend/requirements.txt`

- [ ] **Step 1: Check if python-dateutil is already listed**

```bash
grep "dateutil\|python-dateutil" backend/requirements.txt
```

- [ ] **Step 2: Add if missing**

If not found, add to `backend/requirements.txt`:

```
python-dateutil>=2.9.0
```

Then:

```bash
cd backend
pip install python-dateutil
```

- [ ] **Step 3: Commit if changed**

```bash
git add backend/requirements.txt
git commit -m "chore(deps): add python-dateutil for relativedelta in contract activation"
```

---

## Task 12: Final Validation

- [ ] **Step 1: Run full backend test suite**

```bash
cd backend
python -m pytest -v
```

Expected: all tests pass.

- [ ] **Step 2: Start backend and verify routes appear in OpenAPI**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` and confirm these routes are visible under "contracts":
- `POST /deals/{deal_id}/contracts`
- `GET /deals/{deal_id}/contracts/latest`
- `POST /contracts/{contract_id}/send-signature`
- `POST /contracts/{contract_id}/mock-sign`
- `GET /contracts/{contract_id}/activation-checklist`
- `POST /contracts/{contract_id}/activate`

- [ ] **Step 3: TypeScript check on web**

```bash
cd web
npx tsc --noEmit
```

Expected: 0 errors.

- [ ] **Step 4: Final commit summary**

```bash
git log --oneline feat/phase1-web | head -15
```

Verify the 10 feature commits are present.

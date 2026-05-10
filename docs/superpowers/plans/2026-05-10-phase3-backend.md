# Phase 3 Backend — Deal Creation Flow

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the full backend for Phase 3: migrations, ORM models, schemas, services (pricing, risk, enrichment, deals, documents), and routers covering the `draft → company_enriched → quote_added → indicative_offer_ready → submitted` lifecycle.

**Architecture:** Service-layer pattern — thin routers validate input and call one service function, services own all business logic and DB access. Tests mock at the service layer using `unittest.mock.patch` + `ASGITransport`. Normalized responses: `{"data": ...}` for all success, `{"error": {"code", "message", "details"}}` for all failures via a custom `AppError` exception.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 async, Alembic, Pydantic v2, pytest-asyncio, httpx ASGITransport, `unittest.mock`. Run tests from `backend/` with `pytest tests/ -v`.

---

## File Map

**New files:**
- `backend/alembic/versions/002_phase3_deal_creation.py`
- `backend/app/models/quote.py`
- `backend/app/models/document.py`
- `backend/app/models/risk_assessment.py`
- `backend/app/models/pricing_proposal.py`
- `backend/app/core/errors.py` — AppError + exception handler
- `backend/app/core/idempotency.py` — in-memory idempotency store
- `backend/app/schemas/common.py` — shared response types
- `backend/app/schemas/deal.py`
- `backend/app/schemas/company.py`
- `backend/app/schemas/quote.py`
- `backend/app/schemas/document.py`
- `backend/app/schemas/pricing.py`
- `backend/app/schemas/risk.py`
- `backend/app/services/pricing_service.py`
- `backend/app/services/risk_service.py`
- `backend/app/services/enrichment_service.py`
- `backend/app/services/deal_service.py`
- `backend/app/services/document_service.py`
- `backend/app/routers/deals.py`
- `backend/app/routers/companies.py`
- `backend/app/routers/pricing.py`
- `backend/tests/test_pricing_service.py`
- `backend/tests/test_risk_service.py`
- `backend/tests/test_companies_router.py`
- `backend/tests/test_deals_router.py`

**Modified files:**
- `backend/app/models/__init__.py` — add new model imports
- `backend/app/main.py` — register new routers + AppError handler

---

## Task 1: Alembic Migration 002

**Files:**
- Create: `backend/alembic/versions/002_phase3_deal_creation.py`

- [ ] **Step 1: Write the migration**

```python
# backend/alembic/versions/002_phase3_deal_creation.py
"""phase3_deal_creation

Revision ID: 002
Revises: 001
Create Date: 2026-05-10
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="uploaded", nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("validated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("supplier_name", sa.String(255), nullable=True),
        sa.Column("quote_number", sa.String(100), nullable=True),
        sa.Column("amount_excl_tax_cents", sa.BigInteger(), nullable=True),
        sa.Column("amount_incl_tax_cents", sa.BigInteger(), nullable=True),
        sa.Column("currency", sa.String(3), server_default="EUR", nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("extraction_status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("extraction_payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "quote_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("unit_price_cents", sa.BigInteger(), nullable=True),
        sa.Column("total_price_cents", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "risk_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("band", sa.String(20), nullable=False),
        sa.Column("flags", postgresql.JSONB(), nullable=True),
        sa.Column("rules_applied", postgresql.JSONB(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "pricing_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(20), server_default="indicative", nullable=False),
        sa.Column("amount_financed_cents", sa.BigInteger(), nullable=False),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("monthly_payment_cents", sa.BigInteger(), nullable=False),
        sa.Column("residual_value_cents", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("refi_rate", sa.Numeric(6, 4), nullable=False),
        sa.Column("margin_rate", sa.Numeric(6, 4), nullable=False),
        sa.Column("fees_cents", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("assumptions", postgresql.JSONB(), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("pricing_proposals")
    op.drop_table("risk_assessments")
    op.drop_table("quote_items")
    op.drop_table("quotes")
    op.drop_table("documents")
```

- [ ] **Step 2: Apply migration via Supabase MCP**

Use `mcp__supabase__apply_migration` with the SQL content above (converted from Alembic to raw SQL), project `conxwmnjhntbzftwgxig`. Then update `alembic_version` to `002`:
```sql
UPDATE alembic_version SET version_num = '002';
```

- [ ] **Step 3: Commit**

```bash
git add backend/alembic/versions/002_phase3_deal_creation.py
git commit -m "feat(backend): Alembic migration 002 — quotes, documents, risk_assessments, pricing_proposals"
```

---

## Task 2: ORM Models

**Files:**
- Create: `backend/app/models/document.py`
- Create: `backend/app/models/quote.py`
- Create: `backend/app/models/risk_assessment.py`
- Create: `backend/app/models/pricing_proposal.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Write document.py**

```python
# backend/app/models/document.py
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    contract_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="uploaded")
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str | None] = mapped_column(Text(), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    validated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

- [ ] **Step 2: Write quote.py**

```python
# backend/app/models/quote.py
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    supplier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quote_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount_excl_tax_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    amount_incl_tax_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="EUR")
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pending")
    extraction_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    unit_price_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    total_price_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
```

- [ ] **Step 3: Write risk_assessment.py**

```python
# backend/app/models/risk_assessment.py
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    band: Mapped[str] = mapped_column(Text(), nullable=False)
    flags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    rules_applied: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

- [ ] **Step 4: Write pricing_proposal.py**

```python
# backend/app/models/pricing_proposal.py
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PricingProposal(Base):
    __tablename__ = "pricing_proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="indicative")
    amount_financed_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_payment_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    residual_value_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    refi_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    margin_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False)
    fees_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    assumptions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

- [ ] **Step 5: Update models/__init__.py**

```python
# backend/app/models/__init__.py
from app.models.base import *  # noqa: F401, F403 — re-export Base
from app.models.company import Company
from app.models.deal import Deal
from app.models.document import Document
from app.models.organization import Organization
from app.models.pricing_proposal import PricingProposal
from app.models.profile import Profile
from app.models.quote import Quote, QuoteItem
from app.models.risk_assessment import RiskAssessment
from app.models.user_role import UserRole

__all__ = [
    "Company",
    "Deal",
    "Document",
    "Organization",
    "PricingProposal",
    "Profile",
    "Quote",
    "QuoteItem",
    "RiskAssessment",
    "UserRole",
]
```

- [ ] **Step 6: Verify models import cleanly**

```bash
cd backend && python -c "from app.models import Deal, Quote, Document, RiskAssessment, PricingProposal; print('OK')"
```
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/
git commit -m "feat(backend): ORM models for quotes, documents, risk_assessments, pricing_proposals"
```

---

## Task 3: Errors, Idempotency, and Schemas

**Files:**
- Create: `backend/app/core/errors.py`
- Create: `backend/app/core/idempotency.py`
- Create: `backend/app/schemas/common.py`
- Create: `backend/app/schemas/deal.py`
- Create: `backend/app/schemas/company.py`
- Create: `backend/app/schemas/quote.py`
- Create: `backend/app/schemas/document.py`
- Create: `backend/app/schemas/pricing.py`
- Create: `backend/app/schemas/risk.py`

- [ ] **Step 1: Write errors.py**

```python
# backend/app/core/errors.py
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )
```

- [ ] **Step 2: Write idempotency.py**

```python
# backend/app/core/idempotency.py
import time
from typing import Any

_STORE: dict[str, tuple[Any, float]] = {}
_TTL_SECONDS = 86_400  # 24 hours


def get(key: str) -> Any | None:
    entry = _STORE.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if time.monotonic() > expires_at:
        del _STORE[key]
        return None
    return value


def set_key(key: str, value: Any) -> None:
    _STORE[key] = (value, time.monotonic() + _TTL_SECONDS)
```

- [ ] **Step 3: Write schemas/common.py**

```python
# backend/app/schemas/common.py
from pydantic import BaseModel


class Meta(BaseModel):
    total: int
    page: int
    per_page: int
```

- [ ] **Step 4: Write schemas/deal.py**

```python
# backend/app/schemas/deal.py
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DealCreateRequest(BaseModel):
    company_id: uuid.UUID
    amount_cents: int | None = None
    currency: str = "EUR"
    duration_months: int | None = None


class DealPatchRequest(BaseModel):
    amount_cents: int | None = None
    duration_months: int | None = None
    currency: str | None = None


class DealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    public_id: str
    company_id: uuid.UUID
    partner_org_id: uuid.UUID | None
    submitted_by_user_id: uuid.UUID | None
    status: str
    amount_cents: int | None
    currency: str
    duration_months: int | None
    risk_score: float | None
    risk_band: str | None
    monthly_payment_cents: int | None
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 5: Write schemas/company.py**

```python
# backend/app/schemas/company.py
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class EnrichRequest(BaseModel):
    siren: str = Field(..., pattern=r"^\d{9}$|^\d{14}$")


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    siren: str
    siret: str | None
    legal_name: str
    trade_name: str | None
    address: dict | None
    activity_code: str | None
    creation_date: date | None
    legal_status: str | None
    is_active: bool
    enrichment_source: str | None
    created_at: datetime
```

- [ ] **Step 6: Write schemas/quote.py**

```python
# backend/app/schemas/quote.py
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QuoteCreateRequest(BaseModel):
    document_id: uuid.UUID | None = None
    supplier_name: str | None = None
    quote_number: str | None = None
    amount_excl_tax_cents: int | None = None
    amount_incl_tax_cents: int | None = None
    currency: str = "EUR"
    category: str | None = None


class QuotePatchRequest(BaseModel):
    supplier_name: str | None = None
    quote_number: str | None = None
    amount_excl_tax_cents: int | None = None
    amount_incl_tax_cents: int | None = None
    category: str | None = None


class QuoteItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    category: str | None
    quantity: int
    unit_price_cents: int | None
    total_price_cents: int | None


class QuoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    document_id: uuid.UUID | None
    supplier_name: str | None
    quote_number: str | None
    amount_excl_tax_cents: int | None
    amount_incl_tax_cents: int | None
    currency: str
    category: str | None
    extraction_status: str
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 7: Write schemas/document.py**

```python
# backend/app/schemas/document.py
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentUploadUrlResponse(BaseModel):
    document_id: uuid.UUID
    upload_url: str
    storage_path: str
    expires_in: int = 3600


class DocumentConfirmRequest(BaseModel):
    document_id: uuid.UUID
    storage_key: str
    file_name: str
    mime_type: str
    size_bytes: int
    document_type: str = "quote"


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    type: str
    status: str
    file_name: str
    mime_type: str | None
    size_bytes: int | None
    version: int
    created_at: datetime
```

- [ ] **Step 8: Write schemas/pricing.py**

```python
# backend/app/schemas/pricing.py
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IndicativePricingRequest(BaseModel):
    amount_cents: int
    duration_months: int
    refi_rate: float = 0.045
    margin_rate: float = 0.025
    fees_cents: int = 50_000


class PricingProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    type: str
    amount_financed_cents: int
    duration_months: int
    monthly_payment_cents: int
    refi_rate: float
    margin_rate: float
    fees_cents: int
    assumptions: dict | None
    version: int = 1
    created_at: datetime | None = None
```

- [ ] **Step 9: Write schemas/risk.py**

```python
# backend/app/schemas/risk.py
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    score: int
    band: str
    flags: list | None
    rules_applied: list | None
    recommendation: str | None
    version: int
    created_at: datetime
```

- [ ] **Step 10: Verify schemas import cleanly**

```bash
cd backend && python -c "
from app.schemas.deal import DealCreateRequest, DealResponse
from app.schemas.company import EnrichRequest, CompanyResponse
from app.schemas.quote import QuoteCreateRequest, QuoteResponse
from app.schemas.document import DocumentUploadUrlResponse, DocumentConfirmRequest
from app.schemas.pricing import IndicativePricingRequest, PricingProposalResponse
from app.schemas.risk import RiskAssessmentResponse
print('OK')
"
```
Expected: `OK`

- [ ] **Step 11: Commit**

```bash
git add backend/app/core/errors.py backend/app/core/idempotency.py backend/app/schemas/
git commit -m "feat(backend): AppError, idempotency store, and all Phase 3 Pydantic schemas"
```

---

## Task 4: PricingService + Tests

**Files:**
- Create: `backend/app/services/pricing_service.py`
- Create: `backend/tests/test_pricing_service.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_pricing_service.py
import pytest
from app.services.pricing_service import compute_monthly_payment


def test_standard_annuity():
    # 100 000€ over 36 months, refi=4.5%, margin=2.5%, fees=500€
    # r = 0.07/12 = 0.005833...
    # monthly ≈ 100000 * 0.005833 / (1 - 1.005833^-36) ≈ 3087.69 + 13.88 fees = 3101.57
    result = compute_monthly_payment(
        amount_cents=10_000_000,
        duration_months=36,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=50_000,
    )
    assert 309_000 <= result <= 312_000  # ~3100€/month in cents


def test_zero_rate_uses_straight_line():
    result = compute_monthly_payment(
        amount_cents=12_000_000,
        duration_months=12,
        refi_rate=0.0,
        margin_rate=0.0,
        fees_cents=0,
    )
    assert result == 1_000_000  # 12000€ / 12 = 1000€


def test_fees_added_per_month():
    result_no_fees = compute_monthly_payment(
        amount_cents=10_000_000,
        duration_months=36,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=0,
    )
    result_with_fees = compute_monthly_payment(
        amount_cents=10_000_000,
        duration_months=36,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=36_000,  # 1€/month × 36
    )
    assert result_with_fees == result_no_fees + 1_000  # 36 000 / 36 = 1 000 cents


def test_short_duration():
    result = compute_monthly_payment(
        amount_cents=6_000_000,
        duration_months=6,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=0,
    )
    assert result > 0


def test_result_is_integer():
    result = compute_monthly_payment(
        amount_cents=10_000_001,
        duration_months=37,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=50_001,
    )
    assert isinstance(result, int)
```

- [ ] **Step 2: Run tests and confirm they fail**

```bash
cd backend && pytest tests/test_pricing_service.py -v
```
Expected: `ImportError` or `ModuleNotFoundError` (service not yet created)

- [ ] **Step 3: Implement pricing_service.py**

```python
# backend/app/services/pricing_service.py
import datetime
from app.schemas.pricing import IndicativePricingRequest, PricingProposalResponse


def compute_monthly_payment(
    amount_cents: int,
    duration_months: int,
    refi_rate: float = 0.045,
    margin_rate: float = 0.025,
    fees_cents: int = 50_000,
) -> int:
    r = (refi_rate + margin_rate) / 12
    if r == 0:
        base = amount_cents / duration_months
    else:
        base = amount_cents * r / (1 - (1 + r) ** -duration_months)
    monthly = base + fees_cents / duration_months
    return round(monthly)


def build_pricing_proposal(req: IndicativePricingRequest) -> PricingProposalResponse:
    monthly = compute_monthly_payment(
        amount_cents=req.amount_cents,
        duration_months=req.duration_months,
        refi_rate=req.refi_rate,
        margin_rate=req.margin_rate,
        fees_cents=req.fees_cents,
    )
    return PricingProposalResponse(
        type="indicative",
        amount_financed_cents=req.amount_cents,
        duration_months=req.duration_months,
        monthly_payment_cents=monthly,
        refi_rate=req.refi_rate,
        margin_rate=req.margin_rate,
        fees_cents=req.fees_cents,
        assumptions={
            "refi_rate": req.refi_rate,
            "margin_rate": req.margin_rate,
            "total_rate": req.refi_rate + req.margin_rate,
            "fees_cents": req.fees_cents,
            "computed_at": datetime.datetime.utcnow().isoformat(),
        },
        version=1,
    )
```

- [ ] **Step 4: Run tests and confirm they pass**

```bash
cd backend && pytest tests/test_pricing_service.py -v
```
Expected: 5 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/pricing_service.py backend/tests/test_pricing_service.py
git commit -m "feat(backend): PricingService — financial annuity formula + tests"
```

---

## Task 5: RiskService + Tests

**Files:**
- Create: `backend/app/services/risk_service.py`
- Create: `backend/tests/test_risk_service.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_risk_service.py
import pytest
from datetime import date, timedelta
from app.services.risk_service import assess_risk, RISKY_NAF_CODES


def _age(years: float) -> date:
    return date.today() - timedelta(days=int(years * 365))


def test_default_score_is_75_green():
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=5_000_000,
        activity_code="6201Z",
        is_active=True,
    )
    assert result["score"] == 75
    assert result["band"] == "green"


def test_recent_company_penalty():
    result = assess_risk(
        creation_date=_age(1),
        amount_cents=5_000_000,
        activity_code="6201Z",
        is_active=True,
    )
    assert result["score"] == 45  # 75 - 30
    assert result["band"] == "orange"
    assert "recent_company" in result["flags"]


def test_high_amount_penalty():
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=15_000_000,  # > 100k€
        activity_code="6201Z",
        is_active=True,
    )
    assert result["score"] == 65  # 75 - 10
    assert result["band"] == "green"
    assert "high_amount" in result["flags"]


def test_risky_sector_penalty():
    risky_code = next(iter(RISKY_NAF_CODES))
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=5_000_000,
        activity_code=risky_code,
        is_active=True,
    )
    assert result["score"] == 60  # 75 - 15
    assert "risky_sector" in result["flags"]


def test_inactive_company_penalty():
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=5_000_000,
        activity_code="6201Z",
        is_active=False,
    )
    assert result["score"] == 25  # 75 - 50
    assert result["band"] == "red"
    assert "company_inactive" in result["flags"]


def test_combined_penalties_floor_at_zero():
    risky_code = next(iter(RISKY_NAF_CODES))
    result = assess_risk(
        creation_date=_age(0.5),
        amount_cents=15_000_000,
        activity_code=risky_code,
        is_active=False,
    )
    assert result["score"] == 0  # 75 - 50 - 30 - 10 - 15 = -30 → clamped to 0
    assert result["band"] == "red"


def test_none_activity_code_no_penalty():
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=5_000_000,
        activity_code=None,
        is_active=True,
    )
    assert result["score"] == 75
```

- [ ] **Step 2: Run tests and confirm they fail**

```bash
cd backend && pytest tests/test_risk_service.py -v
```
Expected: `ImportError`

- [ ] **Step 3: Implement risk_service.py**

```python
# backend/app/services/risk_service.py
from datetime import date

RISKY_NAF_CODES: frozenset[str] = frozenset({
    "5610A", "5610B", "5630Z",  # restauration
    "9200Z",  # jeux de hasard
    "4711A", "4711B",  # commerce alimentaire discount
    "8010Z",  # sécurité privée
})

_BAND_THRESHOLDS = [
    (60, "green"),
    (30, "orange"),
    (0, "red"),
]


def _band_for_score(score: int) -> str:
    for threshold, band in _BAND_THRESHOLDS:
        if score >= threshold:
            return band
    return "red"


def assess_risk(
    creation_date: date | None,
    amount_cents: int,
    activity_code: str | None,
    is_active: bool,
) -> dict:
    score = 75
    flags: list[str] = []
    rules_applied: list[str] = []

    if not is_active:
        score -= 50
        flags.append("company_inactive")
        rules_applied.append("inactive_company: -50")

    if creation_date is not None:
        age_years = (date.today() - creation_date).days / 365
        if age_years < 2:
            score -= 30
            flags.append("recent_company")
            rules_applied.append("company_age_lt_2y: -30")

    if amount_cents > 10_000_000:  # > 100 000€
        score -= 10
        flags.append("high_amount")
        rules_applied.append("amount_gt_100k: -10")

    if activity_code and activity_code in RISKY_NAF_CODES:
        score -= 15
        flags.append("risky_sector")
        rules_applied.append("risky_naf_code: -15")

    score = max(0, score)
    band = _band_for_score(score)

    recommendations = {
        "green": "Profil favorable.",
        "orange": "Profil à surveiller.",
        "red": "Profil à risque élevé.",
    }

    return {
        "score": score,
        "band": band,
        "flags": flags,
        "rules_applied": rules_applied,
        "recommendation": recommendations[band],
    }
```

- [ ] **Step 4: Run tests and confirm they pass**

```bash
cd backend && pytest tests/test_risk_service.py -v
```
Expected: 7 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/risk_service.py backend/tests/test_risk_service.py
git commit -m "feat(backend): RiskService — rule-based scoring (7 rules) + tests"
```

---

## Task 6: EnrichmentService + Companies Router + Tests

**Files:**
- Create: `backend/app/services/enrichment_service.py`
- Create: `backend/app/routers/companies.py`
- Create: `backend/tests/test_companies_router.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_companies_router.py
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app


FAKE_COMPANY = {
    "id": "00000000-0000-0000-0000-000000000001",
    "siren": "823456789",
    "siret": None,
    "legal_name": "ACME SAS",
    "trade_name": None,
    "address": {"street": "1 rue de la Paix", "city": "Paris", "zip": "75001"},
    "activity_code": "6201Z",
    "creation_date": "2019-03-15",
    "legal_status": "SAS",
    "is_active": True,
    "enrichment_source": "mock",
    "created_at": "2026-05-10T00:00:00Z",
}


@pytest.mark.asyncio
async def test_enrich_valid_siren(make_token, test_ec_key):
    token = make_token("user-abc", "partner_user")
    with patch("app.routers.companies.enrichment_service.enrich_and_upsert", new_callable=AsyncMock, return_value=FAKE_COMPANY):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/companies/enrich",
                    json={"siren": "823456789"},
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 201
    body = response.json()
    assert body["data"]["siren"] == "823456789"
    assert body["data"]["legal_name"] == "ACME SAS"


@pytest.mark.asyncio
async def test_enrich_invalid_siren_format(make_token, test_ec_key):
    token = make_token("user-abc", "partner_user")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/companies/enrich",
                json={"siren": "ABC123"},
                headers={"Authorization": f"Bearer {token}"},
            )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_enrich_no_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/companies/enrich", json={"siren": "823456789"})
    assert response.status_code == 401
```

- [ ] **Step 2: Implement enrichment_service.py**

```python
# backend/app/services/enrichment_service.py
import hashlib
import uuid
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.company import Company

_LEGAL_NAMES = ["ACME SAS", "DELTA TECH", "NOVA SOLUTIONS", "ORION SYSTEMS", "APEX GROUP"]
_LEGAL_STATUSES = ["SAS", "SARL", "SA", "EURL"]
_ACTIVITIES = ["6201Z", "6202A", "4741Z", "7311Z", "6311Z"]
_CITIES = [
    {"street": "12 rue du Commerce", "city": "Paris", "zip": "75015"},
    {"street": "3 avenue des Fleurs", "city": "Lyon", "zip": "69003"},
    {"street": "8 place Bellecour", "city": "Marseille", "zip": "13001"},
]


def _pick(siren: str, items: list, salt: str = "") -> object:
    digest = hashlib.md5(f"{siren}{salt}".encode()).hexdigest()
    return items[int(digest[:8], 16) % len(items)]


def _mock_creation_date(siren: str) -> date:
    # Deterministic: hash last digit to a year offset 2–10 years ago
    offset_years = 2 + (int(siren[-1]) % 9)
    return date(date.today().year - offset_years, 3, 15)


async def enrich_and_upsert(db: AsyncSession, siren: str) -> Company:
    # Check existing
    result = await db.execute(select(Company).where(Company.siren == siren))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    company = Company(
        id=uuid.uuid4(),
        siren=siren,
        legal_name=str(_pick(siren, _LEGAL_NAMES)),
        trade_name=None,
        address=_pick(siren, _CITIES, salt="addr"),
        activity_code=str(_pick(siren, _ACTIVITIES, salt="act")),
        creation_date=_mock_creation_date(siren),
        legal_status=str(_pick(siren, _LEGAL_STATUSES, salt="ls")),
        is_active=True,
        enrichment_source="mock",
        enrichment_payload={"source": "mock_pappers", "siren": siren},
        created_at=datetime.utcnow(),
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company
```

- [ ] **Step 3: Implement companies router**

```python
# backend/app/routers/companies.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.schemas.company import CompanyResponse, EnrichRequest
from app.services import enrichment_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/enrich", status_code=201)
async def enrich_company(
    body: EnrichRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    company = await enrichment_service.enrich_and_upsert(db, body.siren)
    return {"data": CompanyResponse.model_validate(company).model_dump()}
```

- [ ] **Step 4: Register router in main.py temporarily to run tests**

```python
# In backend/app/main.py — add:
from app.routers import companies
app.include_router(companies.router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && pytest tests/test_companies_router.py -v
```
Expected: 3 tests PASSED

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/enrichment_service.py backend/app/routers/companies.py backend/tests/test_companies_router.py
git commit -m "feat(backend): EnrichmentService (mock Pappers) + GET /companies/enrich + tests"
```

---

## Task 7: DealService + Deals Router + Tests

**Files:**
- Create: `backend/app/services/deal_service.py`
- Create: `backend/app/routers/deals.py`
- Create: `backend/tests/test_deals_router.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_deals_router.py
import pytest
import uuid
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app


def _fake_deal(status: str = "draft") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "public_id": "LD-2026-0001",
        "company_id": str(uuid.uuid4()),
        "partner_org_id": None,
        "submitted_by_user_id": None,
        "status": status,
        "amount_cents": 10_000_000,
        "currency": "EUR",
        "duration_months": 36,
        "risk_score": None,
        "risk_band": None,
        "monthly_payment_cents": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.mark.asyncio
async def test_create_deal_success(make_token, test_ec_key):
    token = make_token("user-abc", "partner_user")
    fake = _fake_deal()
    with patch("app.routers.deals.deal_service.create_deal", new_callable=AsyncMock, return_value=fake):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/deals",
                    json={"company_id": str(uuid.uuid4()), "amount_cents": 10_000_000, "duration_months": 36},
                    headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "key-abc"},
                )
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "draft"


@pytest.mark.asyncio
async def test_create_deal_idempotent_returns_existing(make_token, test_ec_key):
    from app.core import idempotency
    token = make_token("user-abc", "partner_user")
    fake = _fake_deal()
    idempotency.set_key("idem-key-xyz", fake)
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/deals",
                json={"company_id": str(uuid.uuid4()), "amount_cents": 10_000_000, "duration_months": 36},
                headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "idem-key-xyz"},
            )
    assert response.status_code == 200  # existing deal returned, not 201
    assert response.json()["data"]["status"] == "draft"


@pytest.mark.asyncio
async def test_get_deal(make_token, test_ec_key):
    token = make_token("user-abc", "partner_user")
    deal_id = str(uuid.uuid4())
    fake = _fake_deal()
    with patch("app.routers.deals.deal_service.get_deal", new_callable=AsyncMock, return_value=fake):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/deals/{deal_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_get_deal_not_found(make_token, test_ec_key):
    from app.core.errors import AppError
    token = make_token("user-abc", "partner_user")
    deal_id = str(uuid.uuid4())
    with patch(
        "app.routers.deals.deal_service.get_deal",
        new_callable=AsyncMock,
        side_effect=AppError(404, "DEAL_NOT_FOUND", "Deal not found"),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/deals/{deal_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEAL_NOT_FOUND"


@pytest.mark.asyncio
async def test_submit_deal_invalid_transition(make_token, test_ec_key):
    from app.core.errors import AppError
    token = make_token("user-abc", "partner_user")
    deal_id = str(uuid.uuid4())
    with patch(
        "app.routers.deals.deal_service.submit_deal",
        new_callable=AsyncMock,
        side_effect=AppError(
            409, "INVALID_TRANSITION", "Cannot submit",
            {"current_status": "draft", "allowed_next": ["company_enriched", "cancelled"]}
        ),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/deals/{deal_id}/submit",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_TRANSITION"


@pytest.mark.asyncio
async def test_deal_timeline_returns_empty_list(make_token, test_ec_key):
    token = make_token("user-abc", "partner_user")
    deal_id = str(uuid.uuid4())
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/deals/{deal_id}/timeline",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.asyncio
async def test_deals_no_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/deals")
    assert response.status_code == 401
```

- [ ] **Step 2: Implement deal_service.py**

```python
# backend/app/services/deal_service.py
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.deal import Deal

_ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["company_enriched", "cancelled"],
    "company_enriched": ["quote_added", "cancelled"],
    "quote_added": ["indicative_offer_ready", "cancelled"],
    "indicative_offer_ready": ["submitted", "cancelled"],
    "submitted": ["internal_review"],
    "internal_review": ["missing_documents", "pre_approved", "financier_rejected"],
    "missing_documents": ["internal_review", "cancelled"],
    "pre_approved": ["refi_package_ready"],
    "refi_package_ready": ["refi_review"],
    "refi_review": ["financier_approved", "financier_rejected", "missing_documents"],
    "financier_approved": ["firm_offer_generated"],
    "firm_offer_generated": ["contract_generated"],
    "contract_generated": ["signing"],
    "signing": ["signed"],
    "signed": ["activation_pending"],
    "activation_pending": ["active"],
    "active": [],
    "cancelled": [],
}

_COUNTER = 0


def _generate_public_id() -> str:
    global _COUNTER
    _COUNTER += 1
    return f"LD-{datetime.utcnow().year}-{_COUNTER:04d}"


def _assert_transition(current: str, target: str) -> None:
    allowed = _ALLOWED_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise AppError(
            status_code=409,
            code="INVALID_TRANSITION",
            message=f"Cannot transition from {current!r} to {target!r}",
            details={"current_status": current, "allowed_next": allowed},
        )


async def create_deal(db: AsyncSession, company_id: uuid.UUID, user_id: str, **kwargs) -> Deal:
    deal = Deal(
        id=uuid.uuid4(),
        public_id=_generate_public_id(),
        company_id=company_id,
        status="company_enriched",  # company_id provided → skip draft, go straight to company_enriched
        submitted_by_user_id=uuid.UUID(user_id) if user_id else None,
        **kwargs,
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


async def get_deal(db: AsyncSession, deal_id: uuid.UUID) -> Deal:
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if deal is None:
        raise AppError(404, "DEAL_NOT_FOUND", f"Deal {deal_id} not found")
    return deal


async def patch_deal(db: AsyncSession, deal_id: uuid.UUID, **fields) -> Deal:
    deal = await get_deal(db, deal_id)
    for key, value in fields.items():
        if value is not None:
            setattr(deal, key, value)
    await db.commit()
    await db.refresh(deal)
    return deal


async def transition_deal(db: AsyncSession, deal_id: uuid.UUID, target_status: str) -> Deal:
    deal = await get_deal(db, deal_id)
    _assert_transition(deal.status, target_status)
    deal.status = target_status
    await db.commit()
    await db.refresh(deal)
    return deal


async def submit_deal(db: AsyncSession, deal_id: uuid.UUID, user_id: str) -> Deal:
    deal = await get_deal(db, deal_id)
    _assert_transition(deal.status, "submitted")
    deal.status = "submitted"
    deal.submitted_by_user_id = uuid.UUID(user_id) if user_id else None
    await db.commit()
    await db.refresh(deal)
    return deal


async def list_deals(db: AsyncSession, partner_org_id: uuid.UUID | None = None, page: int = 1, per_page: int = 20) -> tuple[list[Deal], int]:
    query = select(Deal)
    if partner_org_id:
        query = query.where(Deal.partner_org_id == partner_org_id)
    result = await db.execute(query.offset((page - 1) * per_page).limit(per_page))
    deals = list(result.scalars().all())
    count_result = await db.execute(select(Deal).where(Deal.partner_org_id == partner_org_id) if partner_org_id else select(Deal))
    total = len(list(count_result.scalars().all()))
    return deals, total
```

- [ ] **Step 3: Implement deals router**

```python
# backend/app/routers/deals.py
import uuid
from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core import idempotency
from app.schemas.deal import DealCreateRequest, DealPatchRequest, DealResponse
from app.services import deal_service

router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("", status_code=201)
async def create_deal(
    body: DealCreateRequest,
    response: Response,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if idempotency_key:
        cached = idempotency.get(idempotency_key)
        if cached is not None:
            response.status_code = 200  # existing deal — not a creation
            return {"data": cached}

    deal = await deal_service.create_deal(
        db,
        company_id=body.company_id,
        user_id=current_user["user_id"],
        amount_cents=body.amount_cents,
        currency=body.currency,
        duration_months=body.duration_months,
    )
    serialized = DealResponse.model_validate(deal).model_dump(mode="json")
    if idempotency_key:
        idempotency.set_key(idempotency_key, serialized)
    return {"data": serialized}


@router.get("")
async def list_deals(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    deals, total = await deal_service.list_deals(db, page=page, per_page=per_page)
    return {
        "data": [DealResponse.model_validate(d).model_dump(mode="json") for d in deals],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{deal_id}")
async def get_deal(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    deal = await deal_service.get_deal(db, deal_id)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.patch("/{deal_id}")
async def patch_deal(
    deal_id: uuid.UUID,
    body: DealPatchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    deal = await deal_service.patch_deal(
        db, deal_id,
        amount_cents=body.amount_cents,
        duration_months=body.duration_months,
        currency=body.currency,
    )
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/{deal_id}/submit", status_code=200)
async def submit_deal(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    deal = await deal_service.submit_deal(db, deal_id, current_user["user_id"])
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.get("/{deal_id}/timeline")
async def get_deal_timeline(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
) -> dict:
    # Phase 4-ready stub: audit_events wired in Phase 4
    return {"data": [], "meta": {"total": 0}}
```

- [ ] **Step 4: Run tests**

```bash
cd backend && pytest tests/test_deals_router.py -v
```
Expected: 7 tests PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/deal_service.py backend/app/routers/deals.py backend/tests/test_deals_router.py
git commit -m "feat(backend): DealService + deals router (CRUD, submit, idempotency, timeline stub)"
```

---

## Task 8: DocumentService + Pricing Router + Risk Router + Quote Router

**Files:**
- Create: `backend/app/services/document_service.py`
- Create: `backend/app/routers/pricing.py`
- Create: `backend/app/routers/quotes.py`
- Create: `backend/app/routers/documents.py`
- Create: `backend/app/routers/risk.py`

- [ ] **Step 1: Implement document_service.py**

```python
# backend/app/services/document_service.py
import uuid
from datetime import datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.models.document import Document

_BUCKET = "documents"
_SIGNED_URL_EXPIRES = 3600


async def create_upload_url(db: AsyncSession, deal_id: uuid.UUID, user_id: str) -> dict:
    doc_id = uuid.uuid4()
    storage_path = f"deals/{deal_id}/{doc_id}"

    # Generate signed upload URL via Supabase Storage API
    url = f"{settings.supabase_url}/storage/v1/object/upload/sign/{_BUCKET}/{storage_path}"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(url, headers=headers)
        except httpx.RequestError as exc:
            raise AppError(502, "STORAGE_UNAVAILABLE", "Storage service unavailable") from exc

    if resp.status_code != 200:
        raise AppError(502, "STORAGE_URL_FAILED", "Failed to generate upload URL")

    signed_url = resp.json().get("signedURL", "")
    full_upload_url = f"{settings.supabase_url}{signed_url}" if signed_url.startswith("/") else signed_url

    # Pre-create document record (status: pending_upload)
    doc = Document(
        id=doc_id,
        deal_id=deal_id,
        type="quote",
        status="pending_upload",
        file_name="",
        uploaded_by_user_id=uuid.UUID(user_id) if user_id else None,
        created_at=datetime.utcnow(),
    )
    db.add(doc)
    await db.commit()

    return {
        "document_id": doc_id,
        "upload_url": full_upload_url,
        "storage_path": storage_path,
        "expires_in": _SIGNED_URL_EXPIRES,
    }


async def confirm_upload(db: AsyncSession, document_id: uuid.UUID, storage_key: str, file_name: str, mime_type: str, size_bytes: int, document_type: str) -> Document:
    from sqlalchemy import select
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if doc is None:
        raise AppError(404, "DOCUMENT_NOT_FOUND", f"Document {document_id} not found")

    doc.storage_key = storage_key
    doc.file_name = file_name
    doc.mime_type = mime_type
    doc.size_bytes = size_bytes
    doc.type = document_type
    doc.status = "uploaded"
    await db.commit()
    await db.refresh(doc)
    return doc
```

- [ ] **Step 2: Implement pricing router**

```python
# backend/app/routers/pricing.py
import uuid
import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.pricing_proposal import PricingProposal
from app.schemas.pricing import IndicativePricingRequest, PricingProposalResponse
from app.services import deal_service
from app.services.pricing_service import build_pricing_proposal, compute_monthly_payment

router = APIRouter(tags=["pricing"])


@router.post("/pricing/indicative", status_code=200)
async def compute_indicative(
    body: IndicativePricingRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    proposal = build_pricing_proposal(body)
    return {"data": proposal.model_dump(mode="json")}


@router.post("/deals/{deal_id}/pricing/recalculate", status_code=201)
async def recalculate_pricing(
    deal_id: uuid.UUID,
    body: IndicativePricingRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Save pricing proposal and transition deal to indicative_offer_ready."""
    deal = await deal_service.get_deal(db, deal_id)
    monthly = compute_monthly_payment(
        amount_cents=body.amount_cents,
        duration_months=body.duration_months,
        refi_rate=body.refi_rate,
        margin_rate=body.margin_rate,
        fees_cents=body.fees_cents,
    )
    proposal = PricingProposal(
        id=uuid.uuid4(),
        deal_id=deal_id,
        type="indicative",
        amount_financed_cents=body.amount_cents,
        duration_months=body.duration_months,
        monthly_payment_cents=monthly,
        refi_rate=body.refi_rate,
        margin_rate=body.margin_rate,
        fees_cents=body.fees_cents,
        assumptions={
            "refi_rate": body.refi_rate,
            "margin_rate": body.margin_rate,
            "fees_cents": body.fees_cents,
        },
        version=1,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(proposal)
    # Transition to indicative_offer_ready
    await deal_service.transition_deal(db, deal_id, "indicative_offer_ready")
    deal.monthly_payment_cents = monthly
    await db.commit()
    await db.refresh(proposal)
    return {"data": PricingProposalResponse.model_validate(proposal).model_dump(mode="json")}
```

- [ ] **Step 3: Implement quotes router (nested under /deals)**

```python
# backend/app/routers/quotes.py
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


@router.post("/deals/{deal_id}/quotes", status_code=201)
async def create_quote(
    deal_id: uuid.UUID,
    body: QuoteCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    await deal_service.get_deal(db, deal_id)  # 404 if not found
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
    # Transition deal to quote_added
    await deal_service.transition_deal(db, deal_id, "quote_added")
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
    result = await db.execute(select(Quote).where(Quote.id == quote_id, Quote.deal_id == deal_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise AppError(404, "QUOTE_NOT_FOUND", f"Quote {quote_id} not found")
    return {"data": QuoteResponse.model_validate(quote).model_dump(mode="json")}


@router.patch("/deals/{deal_id}/quotes/{quote_id}")
async def patch_quote(
    deal_id: uuid.UUID,
    quote_id: uuid.UUID,
    body: QuotePatchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Quote).where(Quote.id == quote_id, Quote.deal_id == deal_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise AppError(404, "QUOTE_NOT_FOUND", f"Quote {quote_id} not found")
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
    result = await db.execute(select(Quote).where(Quote.id == quote_id, Quote.deal_id == deal_id))
    quote = result.scalar_one_or_none()
    if not quote:
        raise AppError(404, "QUOTE_NOT_FOUND", f"Quote {quote_id} not found")
    # Mock extraction: populate fields from deterministic mock
    quote.extraction_status = "done"
    quote.extraction_payload = _MOCK_EXTRACTION
    if not quote.supplier_name:
        quote.supplier_name = _MOCK_EXTRACTION["supplier_name"]
    if not quote.amount_excl_tax_cents:
        quote.amount_excl_tax_cents = _MOCK_EXTRACTION["amount_excl_tax_cents"]
    if not quote.amount_incl_tax_cents:
        quote.amount_incl_tax_cents = _MOCK_EXTRACTION["amount_incl_tax_cents"]
    await db.commit()
    await db.refresh(quote)
    return {"data": QuoteResponse.model_validate(quote).model_dump(mode="json")}
```

- [ ] **Step 4: Implement documents and risk routers**

```python
# backend/app/routers/documents.py
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.schemas.document import DocumentConfirmRequest, DocumentResponse, DocumentUploadUrlResponse
from app.services import document_service

router = APIRouter(tags=["documents"])


@router.post("/deals/{deal_id}/documents/upload-url", status_code=201)
async def get_upload_url(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await document_service.create_upload_url(db, deal_id, current_user["user_id"])
    return {"data": DocumentUploadUrlResponse(**result).model_dump(mode="json")}


@router.post("/deals/{deal_id}/documents/confirm")
async def confirm_upload(
    deal_id: uuid.UUID,
    body: DocumentConfirmRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    doc = await document_service.confirm_upload(
        db,
        document_id=body.document_id,
        storage_key=body.storage_key,
        file_name=body.file_name,
        mime_type=body.mime_type,
        size_bytes=body.size_bytes,
        document_type=body.document_type,
    )
    return {"data": DocumentResponse.model_validate(doc).model_dump(mode="json")}


@router.get("/deals/{deal_id}/documents")
async def list_documents(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from app.models.document import Document
    result = await db.execute(select(Document).where(Document.deal_id == deal_id))
    docs = list(result.scalars().all())
    return {
        "data": [DocumentResponse.model_validate(d).model_dump(mode="json") for d in docs],
        "meta": {"total": len(docs)},
    }
```

```python
# backend/app/routers/risk.py
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.errors import AppError
from app.models.risk_assessment import RiskAssessment
from app.schemas.risk import RiskAssessmentResponse
from app.services import deal_service, risk_service
from app.models.company import Company
from app.models.deal import Deal

router = APIRouter(tags=["risk"])


@router.post("/deals/{deal_id}/risk/assess", status_code=201)
async def assess_risk(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    deal = await deal_service.get_deal(db, deal_id)
    company_result = await db.execute(select(Company).where(Company.id == deal.company_id))
    company = company_result.scalar_one_or_none()
    if not company:
        raise AppError(404, "COMPANY_NOT_FOUND", "Company not found for this deal")

    result = risk_service.assess_risk(
        creation_date=company.creation_date,
        amount_cents=deal.amount_cents or 0,
        activity_code=company.activity_code,
        is_active=company.is_active,
    )

    assessment = RiskAssessment(
        id=uuid.uuid4(),
        deal_id=deal_id,
        score=result["score"],
        band=result["band"],
        flags=result["flags"],
        rules_applied=result["rules_applied"],
        recommendation=result["recommendation"],
        created_by=uuid.UUID(current_user["user_id"]) if current_user.get("user_id") else None,
        version=1,
        created_at=datetime.utcnow(),
    )
    db.add(assessment)
    # Update deal with latest risk info
    deal.risk_score = result["score"]
    deal.risk_band = result["band"]
    await db.commit()
    await db.refresh(assessment)
    return {"data": RiskAssessmentResponse.model_validate(assessment).model_dump(mode="json")}


@router.get("/deals/{deal_id}/risk/latest")
async def get_latest_risk(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.deal_id == deal_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(1)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise AppError(404, "RISK_NOT_FOUND", "No risk assessment found for this deal")
    return {"data": RiskAssessmentResponse.model_validate(assessment).model_dump(mode="json")}
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/document_service.py backend/app/routers/pricing.py backend/app/routers/quotes.py backend/app/routers/documents.py backend/app/routers/risk.py
git commit -m "feat(backend): DocumentService, pricing/quotes/documents/risk routers"
```

---

## Task 9: Wire Everything into main.py + Run Full Suite

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Update main.py with all routers and AppError handler**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import AppError, app_error_handler
from app.routers import auth, me, companies, deals, pricing, quotes, documents, risk

app = FastAPI(title="LeaseAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)

app.include_router(auth.router)
app.include_router(me.router)
app.include_router(companies.router)
app.include_router(deals.router)
app.include_router(pricing.router)
app.include_router(quotes.router)
app.include_router(documents.router)
app.include_router(risk.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

- [ ] **Step 2: Run the full test suite**

```bash
cd backend && pytest tests/ -v
```
Expected: all tests PASSED (existing 35 + new ~17 = ~52 total)

- [ ] **Step 3: Final commit**

```bash
git add backend/app/main.py
git commit -m "feat(backend): register all Phase 3 routers — Phase 3 backend complete"
```

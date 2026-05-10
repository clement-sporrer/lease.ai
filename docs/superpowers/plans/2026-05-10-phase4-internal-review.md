# Phase 4 — Internal Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the internal review workflow — ADV/risk team can receive submitted deals, validate documents, and make a pre-approval or rejection decision — including full audit trail and web back-office UI.

**Architecture:** Backend-first. New `audit_events` table (migration 003). Two new services (`AuditService`, `AdminService`), one new router (`/admin`), extensions to document service/router and deals timeline. Web: Next.js App Router pages for queue + SCR-ADMIN-003 deal review, wired to real API via TanStack Query.

**Tech Stack:** FastAPI + SQLAlchemy async + Pydantic v2 (backend) · Next.js 16 App Router + TanStack Query v5 + shadcn/ui + Tailwind (web) · pytest + AsyncMock (tests)

---

## File Map

**Backend — Create:**
- `backend/alembic/versions/003_phase4_audit_events.py`
- `backend/app/models/audit_event.py`
- `backend/app/services/audit_service.py`
- `backend/app/services/admin_service.py`
- `backend/app/routers/admin.py`
- `backend/app/schemas/admin.py`
- `backend/tests/test_audit_service.py`
- `backend/tests/test_admin_service.py`
- `backend/tests/test_admin_router.py`

**Backend — Modify:**
- `backend/app/core/roles.py` — add `risk` role
- `backend/app/models/__init__.py` — import AuditEvent (if exists, else note in task)
- `backend/app/services/document_service.py` — add validate/reject + auto-transition
- `backend/app/routers/documents.py` — add validate/reject endpoints
- `backend/app/routers/deals.py` — implement timeline endpoint
- `backend/app/main.py` — register admin router
- `backend/tests/test_documents_router.py` — add validate/reject tests

**Web — Create:**
- `web/lib/supabase-server.ts`
- `web/lib/api-client.ts`
- `web/lib/types/admin.ts`
- `web/components/providers.tsx`
- `web/components/admin/DealQueue.tsx`
- `web/components/admin/DealReviewHeader.tsx`
- `web/components/admin/CompanySummary.tsx`
- `web/components/admin/QuoteSummary.tsx`
- `web/components/admin/RiskSummary.tsx`
- `web/components/admin/DocumentList.tsx`
- `web/components/admin/AuditTimeline.tsx`
- `web/components/admin/ActionPanel.tsx`
- `web/app/(admin)/admin/queue/page.tsx`
- `web/app/(admin)/admin/deals/[id]/page.tsx`
- `web/app/(admin)/admin/deals/[id]/loading.tsx`

**Web — Modify:**
- `web/app/layout.tsx` — wrap with QueryClientProvider

---

## Task 1: Migration 003 + AuditEvent Model + UserRole.risk

**Files:**
- Create: `backend/alembic/versions/003_phase4_audit_events.py`
- Create: `backend/app/models/audit_event.py`
- Modify: `backend/app/core/roles.py`

- [ ] **Step 1: Add `risk` to UserRole enum**

```python
# backend/app/core/roles.py
from enum import Enum


class UserRole(str, Enum):
    partner = "partner"
    client = "client"
    admin = "admin"
    ops = "ops"
    risk = "risk"
    financier = "financier"
    cfo = "cfo"
```

- [ ] **Step 2: Create migration file**

```python
# backend/alembic/versions/003_phase4_audit_events.py
"""phase4_audit_events

Revision ID: 003
Revises: 002
Create Date: 2026-05-10
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_VALID_ACTIONS = (
    "status_transition",
    "document_validated",
    "document_rejected",
    "pre_approved",
    "deal_rejected",
    "document_requested",
)


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_role", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            f"action IN ({', '.join(repr(a) for a in _VALID_ACTIONS)})",
            name="chk_audit_action",
        ),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_events_deal_id", "audit_events", ["deal_id"])
    op.create_index("idx_audit_events_created_at", "audit_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_audit_events_created_at", table_name="audit_events")
    op.drop_index("idx_audit_events_deal_id", table_name="audit_events")
    op.drop_table("audit_events")
```

- [ ] **Step 3: Create AuditEvent SQLAlchemy model**

```python
# backend/app/models/audit_event.py
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), nullable=False
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 4: Verify existing tests still pass**

```bash
cd backend && python -m pytest tests/ -q
```
Expected: all existing tests green, no import errors.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/versions/003_phase4_audit_events.py \
        backend/app/models/audit_event.py \
        backend/app/core/roles.py
git commit -m "feat(backend): migration 003 — audit_events table + risk role"
```

---

## Task 2: AuditService

**Files:**
- Create: `backend/app/services/audit_service.py`
- Create: `backend/tests/test_audit_service.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_audit_service.py
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import audit_service


@pytest.mark.asyncio
async def test_log_creates_audit_event():
    db = AsyncMock()
    deal_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role="ops",
        action="status_transition",
        payload={"from": "submitted", "to": "internal_review"},
    )

    db.add.assert_called_once()
    event = db.add.call_args[0][0]
    assert event.deal_id == deal_id
    assert event.actor_id == actor_id
    assert event.actor_role == "ops"
    assert event.action == "status_transition"
    assert event.payload == {"from": "submitted", "to": "internal_review"}
    db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_log_without_payload():
    db = AsyncMock()
    await audit_service.log(
        db=db,
        deal_id=uuid.uuid4(),
        actor_id=uuid.uuid4(),
        actor_role="admin",
        action="pre_approved",
    )
    event = db.add.call_args[0][0]
    assert event.payload is None


@pytest.mark.asyncio
async def test_get_timeline_returns_events_desc():
    from datetime import datetime, timezone
    from unittest.mock import MagicMock

    from app.models.audit_event import AuditEvent

    deal_id = uuid.uuid4()
    events = [
        AuditEvent(
            id=uuid.uuid4(),
            deal_id=deal_id,
            actor_id=uuid.uuid4(),
            actor_role="ops",
            action="status_transition",
            payload={"from": "submitted", "to": "internal_review"},
            created_at=datetime(2026, 5, 10, 10, 0, tzinfo=timezone.utc),
        ),
        AuditEvent(
            id=uuid.uuid4(),
            deal_id=deal_id,
            actor_id=uuid.uuid4(),
            actor_role="admin",
            action="pre_approved",
            payload=None,
            created_at=datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = events
    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await audit_service.get_timeline(db, deal_id)
    assert result == events
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && python -m pytest tests/test_audit_service.py -v
```
Expected: `ImportError` or `ModuleNotFoundError` for `audit_service`.

- [ ] **Step 3: Implement AuditService**

```python
# backend/app/services/audit_service.py
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent


async def log(
    db: AsyncSession,
    deal_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    action: str,
    payload: dict[str, Any] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        id=uuid.uuid4(),
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        payload=payload,
    )
    db.add(event)
    await db.commit()
    return event


async def get_timeline(db: AsyncSession, deal_id: uuid.UUID) -> list[AuditEvent]:
    result = await db.execute(
        select(AuditEvent)
        .where(AuditEvent.deal_id == deal_id)
        .order_by(AuditEvent.created_at.desc())
    )
    return list(result.scalars().all())
```

- [ ] **Step 4: Run tests — expect green**

```bash
cd backend && python -m pytest tests/test_audit_service.py -v
```
Expected: 3 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/audit_service.py backend/tests/test_audit_service.py
git commit -m "feat(backend): AuditService — log + get_timeline"
```

---

## Task 3: AdminService — queue + checklist

**Files:**
- Create: `backend/app/services/admin_service.py` (partial)
- Create: `backend/tests/test_admin_service.py` (partial)

- [ ] **Step 1: Write failing tests for queue and checklist**

```python
# backend/tests/test_admin_service.py
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.deal import Deal
from app.models.document import Document


def _make_deal(status: str = "submitted") -> Deal:
    return Deal(
        id=uuid.uuid4(),
        public_id="LD-2026-AAAA",
        company_id=uuid.uuid4(),
        status=status,
        currency="EUR",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_get_queue_returns_submitted_and_internal_review():
    from app.services import admin_service

    deal1 = _make_deal("submitted")
    deal2 = _make_deal("internal_review")
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [deal1, deal2]
    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await admin_service.get_queue(db)
    assert len(result) == 2
    assert db.execute.called


@pytest.mark.asyncio
async def test_get_checklist_all_docs_validated():
    from app.services import admin_service

    deal = _make_deal("internal_review")
    deal.risk_score = 42.0
    deal.risk_band = "medium"
    deal.monthly_payment_cents = 100000

    doc1 = Document(
        id=uuid.uuid4(), deal_id=deal.id, type="quote", status="validated",
        file_name="q.pdf", created_at=datetime.now(timezone.utc),
    )
    doc2 = Document(
        id=uuid.uuid4(), deal_id=deal.id, type="id_card", status="validated",
        file_name="id.pdf", created_at=datetime.now(timezone.utc),
    )

    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = [doc1, doc2]
    db.execute.side_effect = [deal_result, doc_result]

    checklist = await admin_service.get_checklist(db, deal.id)
    assert checklist["all_docs_validated"] is True
    assert checklist["risk_score"] == 42.0
    assert checklist["checklist_complete"] is True


@pytest.mark.asyncio
async def test_get_checklist_incomplete_when_doc_pending():
    from app.services import admin_service

    deal = _make_deal("internal_review")
    deal.risk_score = 55.0
    deal.risk_band = "medium"
    deal.monthly_payment_cents = 90000

    doc = Document(
        id=uuid.uuid4(), deal_id=deal.id, type="quote", status="pending",
        file_name="q.pdf", created_at=datetime.now(timezone.utc),
    )

    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = [doc]
    db.execute.side_effect = [deal_result, doc_result]

    checklist = await admin_service.get_checklist(db, deal.id)
    assert checklist["all_docs_validated"] is False
    assert checklist["checklist_complete"] is False
```

- [ ] **Step 2: Run to verify they fail**

```bash
cd backend && python -m pytest tests/test_admin_service.py -v
```
Expected: `ImportError` — `admin_service` not found.

- [ ] **Step 3: Implement queue + checklist in AdminService**

```python
# backend/app/services/admin_service.py
import uuid
from typing import Any

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.deal import Deal
from app.models.document import Document

_QUEUE_STATUSES = ("submitted", "internal_review", "missing_documents")

_STATUS_PRIORITY = case(
    (Deal.status == "submitted", 0),
    (Deal.status == "internal_review", 1),
    (Deal.status == "missing_documents", 2),
    else_=3,
)


async def get_queue(db: AsyncSession) -> list[Deal]:
    result = await db.execute(
        select(Deal)
        .where(Deal.status.in_(_QUEUE_STATUSES))
        .order_by(_STATUS_PRIORITY.asc(), Deal.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_checklist(db: AsyncSession, deal_id: uuid.UUID) -> dict[str, Any]:
    deal_result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = deal_result.scalar_one_or_none()
    if deal is None:
        raise AppError(404, "DEAL_NOT_FOUND", f"Deal {deal_id} not found")

    doc_result = await db.execute(select(Document).where(Document.deal_id == deal_id))
    documents = list(doc_result.scalars().all())

    doc_statuses = [
        {"id": str(d.id), "type": d.type, "status": d.status, "file_name": d.file_name}
        for d in documents
    ]
    all_docs_validated = bool(documents) and all(d.status == "validated" for d in documents)
    has_risk_score = deal.risk_score is not None

    return {
        "deal_id": str(deal_id),
        "status": deal.status,
        "documents": doc_statuses,
        "risk_score": deal.risk_score,
        "risk_band": deal.risk_band,
        "pricing_monthly": deal.monthly_payment_cents,
        "all_docs_validated": all_docs_validated,
        "checklist_complete": all_docs_validated and has_risk_score,
    }
```

- [ ] **Step 4: Run tests — expect green**

```bash
cd backend && python -m pytest tests/test_admin_service.py -v
```
Expected: 3 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/admin_service.py backend/tests/test_admin_service.py
git commit -m "feat(backend): AdminService — queue (priority sort) + checklist"
```

---

## Task 4: AdminService — transitions

**Files:**
- Modify: `backend/app/services/admin_service.py`
- Modify: `backend/tests/test_admin_service.py`

- [ ] **Step 1: Add failing tests for transitions**

Append to `backend/tests/test_admin_service.py`:

```python
@pytest.mark.asyncio
async def test_start_review_transitions_submitted_to_internal_review():
    from unittest.mock import patch
    from app.services import admin_service, audit_service

    deal = _make_deal("submitted")
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    db.execute.return_value = deal_result

    actor_id = uuid.uuid4()
    with patch.object(audit_service, "log", new_callable=AsyncMock) as mock_log:
        result = await admin_service.start_review(db, deal.id, actor_id, "ops")

    assert result.status == "internal_review"
    mock_log.assert_called_once_with(
        db=db,
        deal_id=deal.id,
        actor_id=actor_id,
        actor_role="ops",
        action="status_transition",
        payload={"from": "submitted", "to": "internal_review"},
    )


@pytest.mark.asyncio
async def test_start_review_invalid_transition_raises():
    from app.services import admin_service

    deal = _make_deal("draft")
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    db.execute.return_value = deal_result

    with pytest.raises(AppError) as exc_info:
        await admin_service.start_review(db, deal.id, uuid.uuid4(), "ops")
    assert exc_info.value.code == "INVALID_TRANSITION"


@pytest.mark.asyncio
async def test_request_document_transitions_to_missing_documents():
    from unittest.mock import patch
    from app.services import admin_service, audit_service

    deal = _make_deal("internal_review")
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    db.execute.return_value = deal_result
    actor_id = uuid.uuid4()

    with patch.object(audit_service, "log", new_callable=AsyncMock):
        result = await admin_service.request_document(
            db, deal.id, actor_id, "ops", "rib", "RIB manquant"
        )
    assert result.status == "missing_documents"


@pytest.mark.asyncio
async def test_pre_approve_sets_pre_approved_status():
    from unittest.mock import patch
    from app.services import admin_service, audit_service

    deal = _make_deal("internal_review")
    deal.risk_score = 50.0
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = []
    db.execute.side_effect = [deal_result, doc_result, deal_result]
    actor_id = uuid.uuid4()

    with patch.object(audit_service, "log", new_callable=AsyncMock) as mock_log:
        result = await admin_service.pre_approve(db, deal.id, actor_id, "admin")

    assert result.status == "pre_approved"
    call_kwargs = mock_log.call_args.kwargs
    assert call_kwargs["action"] == "pre_approved"


@pytest.mark.asyncio
async def test_pre_approve_sets_manual_override_when_checklist_incomplete():
    from unittest.mock import patch
    from app.services import admin_service, audit_service

    deal = _make_deal("internal_review")
    deal.risk_score = None  # no risk score → checklist incomplete
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = []
    db.execute.side_effect = [deal_result, doc_result, deal_result]
    actor_id = uuid.uuid4()

    with patch.object(audit_service, "log", new_callable=AsyncMock) as mock_log:
        await admin_service.pre_approve(db, deal.id, actor_id, "ops", justification="Override needed")

    payload = mock_log.call_args.kwargs["payload"]
    assert payload["manual_override"] is True
    assert payload["justification"] == "Override needed"


@pytest.mark.asyncio
async def test_reject_requires_reason():
    from app.services import admin_service

    deal = _make_deal("internal_review")
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    db.execute.return_value = deal_result

    with pytest.raises(AppError) as exc_info:
        await admin_service.reject(db, deal.id, uuid.uuid4(), "ops", reason="")
    assert exc_info.value.code == "JUSTIFICATION_REQUIRED"


@pytest.mark.asyncio
async def test_reject_transitions_to_financier_rejected():
    from unittest.mock import patch
    from app.services import admin_service, audit_service

    deal = _make_deal("internal_review")
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    db.execute.return_value = deal_result
    actor_id = uuid.uuid4()

    with patch.object(audit_service, "log", new_callable=AsyncMock):
        result = await admin_service.reject(db, deal.id, actor_id, "admin", reason="Dossier incomplet")

    assert result.status == "financier_rejected"
```

- [ ] **Step 2: Run to verify they fail**

```bash
cd backend && python -m pytest tests/test_admin_service.py -v -k "start_review or request_document or pre_approve or reject"
```
Expected: `AttributeError` — functions not defined yet.

- [ ] **Step 3: Add transition methods to AdminService**

Append to `backend/app/services/admin_service.py`:

```python
from app.core.errors import AppError
from app.models.deal import Deal
from app.services import audit_service
from app.services.deal_service import _assert_transition


async def _get_deal(db: AsyncSession, deal_id: uuid.UUID) -> Deal:
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if deal is None:
        raise AppError(404, "DEAL_NOT_FOUND", f"Deal {deal_id} not found")
    return deal


async def start_review(
    db: AsyncSession, deal_id: uuid.UUID, actor_id: uuid.UUID, actor_role: str
) -> Deal:
    deal = await _get_deal(db, deal_id)
    _assert_transition(deal.status, "internal_review")
    deal.status = "internal_review"
    await db.commit()
    await db.refresh(deal)
    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="status_transition",
        payload={"from": "submitted", "to": "internal_review"},
    )
    return deal


async def request_document(
    db: AsyncSession,
    deal_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    document_type: str,
    reason: str,
) -> Deal:
    deal = await _get_deal(db, deal_id)
    _assert_transition(deal.status, "missing_documents")
    deal.status = "missing_documents"
    await db.commit()
    await db.refresh(deal)
    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="document_requested",
        payload={"document_type": document_type, "reason": reason},
    )
    return deal


async def pre_approve(
    db: AsyncSession,
    deal_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    justification: str | None = None,
) -> Deal:
    deal = await _get_deal(db, deal_id)
    _assert_transition(deal.status, "pre_approved")

    checklist = await get_checklist(db, deal_id)
    checklist_incomplete = not checklist["checklist_complete"]

    deal.status = "pre_approved"
    await db.commit()
    await db.refresh(deal)

    payload: dict[str, Any] = {}
    if checklist_incomplete:
        payload["manual_override"] = True
        payload["justification"] = justification
    elif justification:
        payload["justification"] = justification

    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="pre_approved",
        payload=payload or None,
    )
    return deal


async def reject(
    db: AsyncSession,
    deal_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    reason: str,
) -> Deal:
    if not reason or not reason.strip():
        raise AppError(422, "JUSTIFICATION_REQUIRED", "A reason is required to reject a deal")
    deal = await _get_deal(db, deal_id)
    _assert_transition(deal.status, "financier_rejected")
    deal.status = "financier_rejected"
    await db.commit()
    await db.refresh(deal)
    await audit_service.log(
        db=db,
        deal_id=deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="deal_rejected",
        payload={"reason": reason},
    )
    return deal
```

**Important:** Also add `from typing import Any` at the top of `admin_service.py` if not already present, and update the imports section to include all needed symbols. The final imports block at the top of the file should be:

```python
import uuid
from typing import Any

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.deal import Deal
from app.models.document import Document
from app.services import audit_service
from app.services.deal_service import _assert_transition
```

- [ ] **Step 4: Run all admin_service tests**

```bash
cd backend && python -m pytest tests/test_admin_service.py -v
```
Expected: 10 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/admin_service.py backend/tests/test_admin_service.py
git commit -m "feat(backend): AdminService — start_review, request_document, pre_approve (manual_override), reject"
```

---

## Task 5: Admin schemas + Router + Register

**Files:**
- Create: `backend/app/schemas/admin.py`
- Create: `backend/app/routers/admin.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_admin_router.py`

- [ ] **Step 1: Create Pydantic schemas**

```python
# backend/app/schemas/admin.py
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class StartReviewRequest(BaseModel):
    pass


class RequestDocumentRequest(BaseModel):
    document_type: str
    reason: str


class PreApproveRequest(BaseModel):
    justification: str | None = None


class RejectRequest(BaseModel):
    reason: str


class DocumentStatusItem(BaseModel):
    id: uuid.UUID
    type: str
    status: str
    file_name: str


class DealChecklistResponse(BaseModel):
    deal_id: str
    status: str
    documents: list[DocumentStatusItem]
    risk_score: float | None
    risk_band: str | None
    pricing_monthly: int | None
    all_docs_validated: bool
    checklist_complete: bool


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    actor_id: uuid.UUID
    actor_role: str
    action: str
    payload: dict[str, Any] | None
    created_at: datetime
```

- [ ] **Step 2: Write failing router tests**

```python
# backend/tests/test_admin_router.py
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.deal import Deal


def _fake_deal(status: str = "submitted") -> Deal:
    d = Deal.__new__(Deal)
    d.id = uuid.uuid4()
    d.public_id = "LD-2026-TEST"
    d.company_id = uuid.uuid4()
    d.partner_org_id = None
    d.submitted_by_user_id = None
    d.status = status
    d.amount_cents = 10_000_000
    d.currency = "EUR"
    d.duration_months = 36
    d.risk_score = 45.0
    d.risk_band = "medium"
    d.monthly_payment_cents = 280000
    d.created_at = datetime.now(timezone.utc)
    d.updated_at = datetime.now(timezone.utc)
    return d


def _auth_headers(make_token, test_ec_key, role: str = "ops") -> dict:
    token = make_token("user-ops-1", role)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_queue_returns_deals(make_token, test_ec_key):
    deals = [_fake_deal("submitted"), _fake_deal("internal_review")]
    with patch("app.routers.admin.admin_service.get_queue", new_callable=AsyncMock, return_value=deals):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    "/admin/queue", headers=_auth_headers(make_token, test_ec_key)
                )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_queue_forbidden_for_partner(make_token, test_ec_key):
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/admin/queue", headers=_auth_headers(make_token, test_ec_key, role="partner")
            )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_start_review_returns_deal(make_token, test_ec_key):
    deal = _fake_deal("internal_review")
    with patch("app.routers.admin.admin_service.start_review", new_callable=AsyncMock, return_value=deal):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/admin/deals/{deal.id}/start-review",
                    headers=_auth_headers(make_token, test_ec_key),
                )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "internal_review"


@pytest.mark.asyncio
async def test_start_review_forbidden_for_risk(make_token, test_ec_key):
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/admin/deals/{uuid.uuid4()}/start-review",
                headers=_auth_headers(make_token, test_ec_key, role="risk"),
            )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_pre_approve_returns_deal(make_token, test_ec_key):
    deal = _fake_deal("pre_approved")
    with patch("app.routers.admin.admin_service.pre_approve", new_callable=AsyncMock, return_value=deal):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/admin/deals/{deal.id}/pre-approve",
                    json={"justification": None},
                    headers=_auth_headers(make_token, test_ec_key, role="admin"),
                )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "pre_approved"


@pytest.mark.asyncio
async def test_reject_requires_reason(make_token, test_ec_key):
    from app.core.errors import AppError
    with patch(
        "app.routers.admin.admin_service.reject",
        new_callable=AsyncMock,
        side_effect=AppError(422, "JUSTIFICATION_REQUIRED", "reason required"),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/admin/deals/{uuid.uuid4()}/reject",
                    json={"reason": ""},
                    headers=_auth_headers(make_token, test_ec_key),
                )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "JUSTIFICATION_REQUIRED"


@pytest.mark.asyncio
async def test_request_document_returns_deal(make_token, test_ec_key):
    deal = _fake_deal("missing_documents")
    with patch("app.routers.admin.admin_service.request_document", new_callable=AsyncMock, return_value=deal):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/admin/deals/{deal.id}/request-document",
                    json={"document_type": "rib", "reason": "RIB manquant"},
                    headers=_auth_headers(make_token, test_ec_key),
                )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "missing_documents"
```

- [ ] **Step 3: Run to verify tests fail**

```bash
cd backend && python -m pytest tests/test_admin_router.py -v
```
Expected: `ImportError` — admin router not registered.

- [ ] **Step 4: Create admin router**

```python
# backend/app/routers/admin.py
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.roles import UserRole
from app.schemas.admin import (
    DealChecklistResponse,
    PreApproveRequest,
    RejectRequest,
    RequestDocumentRequest,
)
from app.schemas.deal import DealResponse
from app.services import admin_service, audit_service
from app.schemas.admin import AuditEventResponse

_READ_ROLES = {UserRole.admin, UserRole.ops, UserRole.risk}
_WRITE_ROLES = {UserRole.admin, UserRole.ops}

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_read(current_user: dict) -> None:
    if current_user.get("active_role") not in _READ_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: internal endpoint")


def _require_write(current_user: dict) -> None:
    if current_user.get("active_role") not in _WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: write action requires ops or admin")


@router.get("/queue")
async def get_queue(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    deals = await admin_service.get_queue(db)
    return {
        "data": [DealResponse.model_validate(d).model_dump(mode="json") for d in deals],
        "meta": {"total": len(deals)},
    }


@router.get("/deals/{deal_id}/checklist")
async def get_checklist(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    checklist = await admin_service.get_checklist(db, deal_id)
    return {"data": checklist}


@router.post("/deals/{deal_id}/start-review")
async def start_review(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    deal = await admin_service.start_review(db, deal_id, actor_id, actor_role)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/deals/{deal_id}/request-document")
async def request_document(
    deal_id: uuid.UUID,
    body: RequestDocumentRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    deal = await admin_service.request_document(
        db, deal_id, actor_id, actor_role, body.document_type, body.reason
    )
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/deals/{deal_id}/pre-approve")
async def pre_approve(
    deal_id: uuid.UUID,
    body: PreApproveRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    deal = await admin_service.pre_approve(db, deal_id, actor_id, actor_role, body.justification)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}


@router.post("/deals/{deal_id}/reject")
async def reject(
    deal_id: uuid.UUID,
    body: RejectRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_write(current_user)
    actor_id = uuid.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    deal = await admin_service.reject(db, deal_id, actor_id, actor_role, body.reason)
    return {"data": DealResponse.model_validate(deal).model_dump(mode="json")}
```

- [ ] **Step 5: Register admin router in main.py**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import AppError, app_error_handler
from app.routers import admin, auth, companies, deals, documents, me, pricing, quotes, risk

app = FastAPI(title="LeaseAI API", version="0.1.0")
app.add_exception_handler(AppError, app_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(deals.router)
app.include_router(documents.router)
app.include_router(me.router)
app.include_router(pricing.router)
app.include_router(quotes.router)
app.include_router(risk.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

- [ ] **Step 6: Run all admin router tests**

```bash
cd backend && python -m pytest tests/test_admin_router.py -v
```
Expected: 7 tests PASSED.

- [ ] **Step 7: Run full test suite**

```bash
cd backend && python -m pytest tests/ -q
```
Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/admin.py backend/app/routers/admin.py \
        backend/app/main.py backend/tests/test_admin_router.py
git commit -m "feat(backend): admin router — queue, checklist, start-review, request-document, pre-approve, reject"
```

---

## Task 6: Document service extensions + auto-transition

**Files:**
- Modify: `backend/app/services/document_service.py`
- Modify: `backend/tests/test_documents_router.py`

- [ ] **Step 1: Add failing tests for validate/reject document**

Append to `backend/tests/test_documents_router.py`:

```python
@pytest.mark.asyncio
async def test_validate_document_ops_succeeds(make_token, test_ec_key):
    from app.models.document import Document as DocModel
    import uuid as _uuid
    from datetime import datetime, timezone

    doc_id = _uuid.uuid4()
    fake_doc = DocModel.__new__(DocModel)
    fake_doc.id = doc_id
    fake_doc.deal_id = _uuid.uuid4()
    fake_doc.type = "rib"
    fake_doc.status = "validated"
    fake_doc.file_name = "rib.pdf"
    fake_doc.storage_key = None
    fake_doc.mime_type = None
    fake_doc.size_bytes = None
    fake_doc.version = 1
    fake_doc.uploaded_by_user_id = None
    fake_doc.validated_by_user_id = _uuid.uuid4()
    fake_doc.created_at = datetime.now(timezone.utc)

    token = make_token("user-ops", "ops")
    with patch(
        "app.routers.documents.document_service.validate_document",
        new_callable=AsyncMock,
        return_value=fake_doc,
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/documents/{doc_id}/validate",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "validated"


@pytest.mark.asyncio
async def test_validate_document_risk_forbidden(make_token, test_ec_key):
    token = make_token("user-risk", "risk")
    with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/documents/{uuid.uuid4()}/validate",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reject_document_requires_reason(make_token, test_ec_key):
    from app.core.errors import AppError as _AppError
    token = make_token("user-ops", "ops")
    with patch(
        "app.routers.documents.document_service.reject_document",
        new_callable=AsyncMock,
        side_effect=_AppError(422, "JUSTIFICATION_REQUIRED", "reason required"),
    ):
        with patch("app.core.auth._get_jwks", new_callable=AsyncMock, return_value=test_ec_key["jwks"]):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    f"/documents/{uuid.uuid4()}/reject",
                    json={"reason": ""},
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert response.status_code == 422
```

- [ ] **Step 2: Run to verify they fail**

```bash
cd backend && python -m pytest tests/test_documents_router.py -v -k "validate or reject"
```
Expected: `AttributeError` — `validate_document` not found.

- [ ] **Step 3: Extend document_service.py**

Add to `backend/app/services/document_service.py`:

```python
async def validate_document(
    db: AsyncSession,
    document_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
) -> Document:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise AppError(404, "DOCUMENT_NOT_FOUND", f"Document {document_id} not found")

    document.status = "validated"
    document.validated_by_user_id = actor_id
    await db.commit()
    await db.refresh(document)

    from app.services import audit_service
    await audit_service.log(
        db=db,
        deal_id=document.deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="document_validated",
        payload={"document_id": str(document_id), "document_type": document.type},
    )
    return document


async def reject_document(
    db: AsyncSession,
    document_id: uuid.UUID,
    actor_id: uuid.UUID,
    actor_role: str,
    reason: str,
) -> Document:
    if not reason or not reason.strip():
        raise AppError(422, "JUSTIFICATION_REQUIRED", "A reason is required to reject a document")

    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise AppError(404, "DOCUMENT_NOT_FOUND", f"Document {document_id} not found")

    document.status = "rejected"
    await db.commit()
    await db.refresh(document)

    from app.services import audit_service
    await audit_service.log(
        db=db,
        deal_id=document.deal_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action="document_rejected",
        payload={"document_id": str(document_id), "document_type": document.type, "reason": reason},
    )
    return document


async def confirm_upload_and_maybe_resume_review(
    db: AsyncSession,
    deal_id: uuid.UUID,
    document_id: uuid.UUID,
    file_name: str,
    mime_type: str,
    size_bytes: int,
    document_type: str,
    actor_id: uuid.UUID | None = None,
    actor_role: str = "partner",
) -> Document:
    """confirm_upload extended: auto-transitions missing_documents → internal_review."""
    document = await confirm_upload(db, deal_id, document_id, file_name, mime_type, size_bytes, document_type)

    from app.models.deal import Deal
    from sqlalchemy import select as _select
    deal_result = await db.execute(_select(Deal).where(Deal.id == deal_id))
    deal = deal_result.scalar_one_or_none()
    if deal is not None and deal.status == "missing_documents":
        deal.status = "internal_review"
        await db.commit()
        if actor_id is not None:
            from app.services import audit_service
            await audit_service.log(
                db=db,
                deal_id=deal_id,
                actor_id=actor_id,
                actor_role=actor_role,
                action="status_transition",
                payload={"from": "missing_documents", "to": "internal_review", "trigger": "document_uploaded"},
            )

    return document
```

Also add `from sqlalchemy import select` if not already at the top of `document_service.py`.

- [ ] **Step 4: Add validate/reject endpoints to documents router**

Append to `backend/app/routers/documents.py`:

```python
import uuid as _uuid_mod

from app.core.roles import UserRole
from app.schemas.document import DocumentRejectRequest

_DOC_WRITE_ROLES = {UserRole.admin, UserRole.ops}


@router.post("/documents/{document_id}/validate")
async def validate_document(
    document_id: _uuid_mod.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if current_user.get("active_role") not in _DOC_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: ops or admin required")
    actor_id = _uuid_mod.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    document = await document_service.validate_document(db, document_id, actor_id, actor_role)
    return {"data": DocumentResponse.model_validate(document).model_dump(mode="json")}


@router.post("/documents/{document_id}/reject")
async def reject_document(
    document_id: _uuid_mod.UUID,
    body: DocumentRejectRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if current_user.get("active_role") not in _DOC_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden: ops or admin required")
    actor_id = _uuid_mod.UUID(current_user["user_id"])
    actor_role = current_user.get("active_role", "")
    document = await document_service.reject_document(db, document_id, actor_id, actor_role, body.reason)
    return {"data": DocumentResponse.model_validate(document).model_dump(mode="json")}
```

Also add `from fastapi import HTTPException` to the imports in `documents.py` if not present.

Add `DocumentRejectRequest` to `backend/app/schemas/document.py`:

```python
class DocumentRejectRequest(BaseModel):
    reason: str
```

- [ ] **Step 5: Update documents router confirm endpoint to call the new function**

In `backend/app/routers/documents.py`, replace the `confirm_upload` handler body:

```python
@router.post("/deals/{deal_id}/documents/confirm")
async def confirm_upload(
    deal_id: uuid.UUID,
    body: DocumentConfirmRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    actor_id_str = current_user.get("user_id")
    actor_id = uuid.UUID(actor_id_str) if actor_id_str else None
    actor_role = current_user.get("active_role", "partner")
    document = await document_service.confirm_upload_and_maybe_resume_review(
        db=db,
        deal_id=deal_id,
        document_id=body.document_id,
        file_name=body.file_name,
        mime_type=body.mime_type,
        size_bytes=body.size_bytes,
        document_type=body.document_type,
        actor_id=actor_id,
        actor_role=actor_role,
    )
    return {"data": DocumentResponse.model_validate(document).model_dump(mode="json")}
```

- [ ] **Step 6: Run document router tests**

```bash
cd backend && python -m pytest tests/test_documents_router.py -v
```
Expected: all existing + 3 new tests PASSED.

- [ ] **Step 7: Run full suite**

```bash
cd backend && python -m pytest tests/ -q
```
Expected: all green.

- [ ] **Step 8: Commit**

```bash
git add backend/app/services/document_service.py \
        backend/app/routers/documents.py \
        backend/app/schemas/document.py \
        backend/tests/test_documents_router.py
git commit -m "feat(backend): document validate/reject + auto-transition missing_documents→internal_review on upload"
```

---

## Task 7: Deals timeline endpoint

**Files:**
- Modify: `backend/app/routers/deals.py`
- Modify: `backend/app/schemas/admin.py` (reuse AuditEventResponse)

- [ ] **Step 1: Implement timeline endpoint**

Replace the stub in `backend/app/routers/deals.py`:

```python
# Replace the existing stub:
# @router.get("/{deal_id}/timeline")
# async def get_deal_timeline(...):
#     del deal_id, current_user
#     return {"data": [], "meta": {"total": 0}}

# With:
from app.schemas.admin import AuditEventResponse
from app.services import audit_service as _audit_service

@router.get("/{deal_id}/timeline")
async def get_deal_timeline(
    deal_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    del current_user
    events = await _audit_service.get_timeline(db, deal_id)
    return {
        "data": [AuditEventResponse.model_validate(e).model_dump(mode="json") for e in events],
        "meta": {"total": len(events)},
    }
```

Also add `db: AsyncSession = Depends(get_db)` import — it's already imported at the top of deals.py.

- [ ] **Step 2: Run full test suite**

```bash
cd backend && python -m pytest tests/ -q
```
Expected: all green, no regressions.

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/deals.py
git commit -m "feat(backend): implement GET /deals/{id}/timeline via audit_events"
```

---

## Task 8: Web infrastructure

**Files:**
- Create: `web/lib/supabase-server.ts`
- Create: `web/lib/api-client.ts`
- Create: `web/lib/types/admin.ts`
- Create: `web/components/providers.tsx`
- Modify: `web/app/layout.tsx`

- [ ] **Step 1: Create Supabase server client**

```typescript
// web/lib/supabase-server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createSupabaseServerClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
      },
    }
  )
}
```

- [ ] **Step 2: Create API client**

```typescript
// web/lib/api-client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export async function apiFetch<T>(
  path: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const code = body?.error?.code ?? 'UNKNOWN'
    const message = body?.error?.message ?? `HTTP ${response.status}`
    throw new Error(`[${code}] ${message}`)
  }

  return response.json() as Promise<T>
}
```

- [ ] **Step 3: Create admin types**

```typescript
// web/lib/types/admin.ts
export type DealStatus =
  | 'draft' | 'company_enriched' | 'quote_added' | 'indicative_offer_ready'
  | 'submitted' | 'internal_review' | 'missing_documents'
  | 'pre_approved' | 'financier_rejected' | 'refi_package_ready'
  | 'refi_review' | 'financier_approved' | 'firm_offer_generated'
  | 'contract_generated' | 'signing' | 'signed' | 'activation_pending' | 'active' | 'cancelled'

export interface Deal {
  id: string
  public_id: string
  company_id: string
  partner_org_id: string | null
  submitted_by_user_id: string | null
  status: DealStatus
  amount_cents: number | null
  currency: string
  duration_months: number | null
  risk_score: number | null
  risk_band: string | null
  monthly_payment_cents: number | null
  created_at: string
  updated_at: string
}

export interface DocumentItem {
  id: string
  type: string
  status: 'pending_upload' | 'uploaded' | 'validated' | 'rejected' | 'pending'
  file_name: string
}

export interface DealChecklist {
  deal_id: string
  status: DealStatus
  documents: DocumentItem[]
  risk_score: number | null
  risk_band: string | null
  pricing_monthly: number | null
  all_docs_validated: boolean
  checklist_complete: boolean
}

export interface AuditEvent {
  id: string
  deal_id: string
  actor_id: string
  actor_role: string
  action: string
  payload: Record<string, unknown> | null
  created_at: string
}

export interface QueueResponse {
  data: Deal[]
  meta: { total: number }
}

export interface ChecklistResponse {
  data: DealChecklist
}

export interface TimelineResponse {
  data: AuditEvent[]
  meta: { total: number }
}
```

- [ ] **Step 4: Create TanStack Query provider**

```tsx
// web/components/providers.tsx
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: 30_000 } },
      })
  )
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
```

- [ ] **Step 5: Wrap root layout with Providers**

Read the existing `web/app/layout.tsx` first, then wrap `{children}` with `<Providers>`:

```tsx
// web/app/layout.tsx (full replacement — read first to preserve existing content)
import type { Metadata } from 'next'
import { Providers } from '@/components/providers'
import './globals.css'

export const metadata: Metadata = {
  title: 'LeaseAI Back-office',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

- [ ] **Step 6: TypeScript check**

```bash
cd web && npx tsc --noEmit
```
Expected: 0 errors.

- [ ] **Step 7: Commit**

```bash
git add web/lib/supabase-server.ts web/lib/api-client.ts web/lib/types/admin.ts \
        web/components/providers.tsx web/app/layout.tsx
git commit -m "feat(web): infra — Supabase server client, API client, admin types, TanStack Query provider"
```

---

## Task 9: Web queue page

**Files:**
- Create: `web/components/admin/DealQueue.tsx`
- Create: `web/app/(admin)/admin/queue/page.tsx`

- [ ] **Step 1: Create DealQueue component**

```tsx
// web/components/admin/DealQueue.tsx
'use client'

import Link from 'next/link'
import type { Deal } from '@/lib/types/admin'

const STATUS_LABEL: Record<string, string> = {
  submitted: 'Soumis',
  internal_review: 'En révision',
  missing_documents: 'Pièces manquantes',
}

const STATUS_COLOR: Record<string, string> = {
  submitted: 'bg-blue-100 text-blue-800',
  internal_review: 'bg-yellow-100 text-yellow-800',
  missing_documents: 'bg-red-100 text-red-800',
}

function formatAmount(cents: number | null): string {
  if (cents === null) return '—'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100)
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

interface Props {
  deals: Deal[]
}

export function DealQueue({ deals }: Props) {
  if (deals.length === 0) {
    return <p className="text-sm text-gray-400 py-8 text-center">Aucun dossier en attente.</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-xs text-gray-500 uppercase tracking-wide">
            <th className="pb-3 pr-4 font-medium">ID</th>
            <th className="pb-3 pr-4 font-medium">Statut</th>
            <th className="pb-3 pr-4 font-medium">Montant</th>
            <th className="pb-3 pr-4 font-medium">Durée</th>
            <th className="pb-3 pr-4 font-medium">Score</th>
            <th className="pb-3 font-medium">Mis à jour</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {deals.map((deal) => (
            <tr key={deal.id} className="hover:bg-gray-50 transition-colors">
              <td className="py-3 pr-4">
                <Link
                  href={`/admin/deals/${deal.id}`}
                  className="font-mono text-xs text-blue-600 hover:underline"
                >
                  {deal.public_id}
                </Link>
              </td>
              <td className="py-3 pr-4">
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLOR[deal.status] ?? 'bg-gray-100 text-gray-700'}`}
                >
                  {STATUS_LABEL[deal.status] ?? deal.status}
                </span>
              </td>
              <td className="py-3 pr-4 tabular-nums">{formatAmount(deal.amount_cents)}</td>
              <td className="py-3 pr-4">{deal.duration_months ? `${deal.duration_months} mois` : '—'}</td>
              <td className="py-3 pr-4">
                {deal.risk_score !== null ? (
                  <span className="tabular-nums">{Math.round(deal.risk_score)}/100</span>
                ) : (
                  <span className="text-gray-400">—</span>
                )}
              </td>
              <td className="py-3 text-gray-500">{formatDate(deal.updated_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

- [ ] **Step 2: Create queue page (server component)**

```tsx
// web/app/(admin)/admin/queue/page.tsx
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { DealQueue } from '@/components/admin/DealQueue'
import type { QueueResponse } from '@/lib/types/admin'

export default async function AdminQueuePage() {
  const supabase = await createSupabaseServerClient()
  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    return (
      <DashboardShell role="admin" title="File d'attente">
        <p className="text-sm text-gray-500">Non authentifié.</p>
      </DashboardShell>
    )
  }

  let queueData: QueueResponse = { data: [], meta: { total: 0 } }
  try {
    queueData = await apiFetch<QueueResponse>('/admin/queue', session.access_token)
  } catch (err) {
    console.error('Failed to fetch admin queue:', err)
  }

  return (
    <DashboardShell
      role="admin"
      title="File d'attente"
      subtitle={`${queueData.meta.total} dossier(s) à traiter`}
    >
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <DealQueue deals={queueData.data} />
      </div>
    </DashboardShell>
  )
}
```

- [ ] **Step 3: TypeScript check**

```bash
cd web && npx tsc --noEmit
```
Expected: 0 errors.

- [ ] **Step 4: Commit**

```bash
git add web/components/admin/DealQueue.tsx web/app/\(admin\)/admin/queue/page.tsx
git commit -m "feat(web): admin queue page — deal list with status + priority sort"
```

---

## Task 10: Web deal review page (SCR-ADMIN-003)

**Files:**
- Create: `web/components/admin/DealReviewHeader.tsx`
- Create: `web/components/admin/CompanySummary.tsx`
- Create: `web/components/admin/QuoteSummary.tsx`
- Create: `web/components/admin/RiskSummary.tsx`
- Create: `web/components/admin/DocumentList.tsx`
- Create: `web/components/admin/AuditTimeline.tsx`
- Create: `web/components/admin/ActionPanel.tsx`
- Create: `web/app/(admin)/admin/deals/[id]/page.tsx`
- Create: `web/app/(admin)/admin/deals/[id]/loading.tsx`

- [ ] **Step 1: Create DealReviewHeader**

```tsx
// web/components/admin/DealReviewHeader.tsx
import type { Deal, DealStatus } from '@/lib/types/admin'

const STATUS_LABEL: Record<DealStatus, string> = {
  draft: 'Brouillon',
  company_enriched: 'Entreprise enrichie',
  quote_added: 'Devis ajouté',
  indicative_offer_ready: 'Offre indicative',
  submitted: 'Soumis',
  internal_review: 'En révision',
  missing_documents: 'Pièces manquantes',
  pre_approved: 'Pré-accordé',
  financier_rejected: 'Refusé',
  refi_package_ready: 'Package refi prêt',
  refi_review: 'Révision financeur',
  financier_approved: 'Approuvé financeur',
  firm_offer_generated: 'Offre ferme',
  contract_generated: 'Contrat généré',
  signing: 'Signature',
  signed: 'Signé',
  activation_pending: 'Activation en cours',
  active: 'Actif',
  cancelled: 'Annulé',
}

const STATUS_COLOR: Record<string, string> = {
  submitted: 'bg-blue-100 text-blue-800',
  internal_review: 'bg-yellow-100 text-yellow-800',
  missing_documents: 'bg-red-100 text-red-800',
  pre_approved: 'bg-green-100 text-green-800',
  financier_rejected: 'bg-red-200 text-red-900',
}

interface Props {
  deal: Deal
}

export function DealReviewHeader({ deal }: Props) {
  const color = STATUS_COLOR[deal.status] ?? 'bg-gray-100 text-gray-700'
  const submittedAt = new Date(deal.created_at).toLocaleDateString('fr-FR', {
    day: '2-digit', month: 'long', year: 'numeric',
  })

  return (
    <div className="flex items-start justify-between mb-8">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h2 className="text-lg font-bold text-gray-900 font-mono">{deal.public_id}</h2>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-semibold ${color}`}>
            {STATUS_LABEL[deal.status] ?? deal.status}
          </span>
        </div>
        <p className="text-sm text-gray-500">Soumis le {submittedAt}</p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create CompanySummary**

```tsx
// web/components/admin/CompanySummary.tsx
interface CompanyData {
  name?: string
  siren?: string
  sector?: string
  creation_date?: string
  is_recent?: boolean
  is_inactive?: boolean
}

interface Props {
  companyId: string
  enrichment?: CompanyData
}

export function CompanySummary({ companyId, enrichment }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Entreprise</h3>
      {enrichment ? (
        <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
          <div>
            <dt className="text-gray-500">Nom</dt>
            <dd className="font-medium text-gray-900">{enrichment.name ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">SIREN</dt>
            <dd className="font-mono">{enrichment.siren ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Secteur</dt>
            <dd>{enrichment.sector ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Création</dt>
            <dd>{enrichment.creation_date ?? '—'}</dd>
          </div>
          {enrichment.is_recent && (
            <div className="col-span-2">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                ⚠ Société récente
              </span>
            </div>
          )}
          {enrichment.is_inactive && (
            <div className="col-span-2">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                ⚠ Société inactive
              </span>
            </div>
          )}
        </dl>
      ) : (
        <p className="text-sm text-gray-400">Données enrichissement non disponibles (ID: {companyId})</p>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Create QuoteSummary**

```tsx
// web/components/admin/QuoteSummary.tsx
import type { Deal } from '@/lib/types/admin'

function formatAmount(cents: number | null): string {
  if (cents === null) return '—'
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100)
}

export function QuoteSummary({ deal }: { deal: Deal }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Devis</h3>
      <dl className="grid grid-cols-3 gap-x-6 gap-y-3 text-sm">
        <div>
          <dt className="text-gray-500">Montant total</dt>
          <dd className="font-semibold text-gray-900 tabular-nums">{formatAmount(deal.amount_cents)}</dd>
        </div>
        <div>
          <dt className="text-gray-500">Durée</dt>
          <dd>{deal.duration_months ? `${deal.duration_months} mois` : '—'}</dd>
        </div>
        <div>
          <dt className="text-gray-500">Mensualité indicative</dt>
          <dd className="font-semibold tabular-nums">{formatAmount(deal.monthly_payment_cents)}</dd>
        </div>
      </dl>
    </div>
  )
}
```

- [ ] **Step 4: Create RiskSummary**

```tsx
// web/components/admin/RiskSummary.tsx
import type { Deal } from '@/lib/types/admin'

const BAND_COLOR: Record<string, string> = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  very_high: 'bg-red-100 text-red-800',
}

const BAND_LABEL: Record<string, string> = {
  low: 'Faible',
  medium: 'Moyen',
  high: 'Élevé',
  very_high: 'Très élevé',
}

export function RiskSummary({ deal }: { deal: Deal }) {
  const band = deal.risk_band ?? null
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Score de risque</h3>
      {deal.risk_score !== null && band ? (
        <div className="flex items-center gap-4">
          <span className="text-3xl font-bold font-mono text-gray-900">{Math.round(deal.risk_score)}</span>
          <span className="text-sm text-gray-500">/100</span>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-semibold ${BAND_COLOR[band] ?? 'bg-gray-100 text-gray-700'}`}>
            {BAND_LABEL[band] ?? band}
          </span>
        </div>
      ) : (
        <p className="text-sm text-gray-400">Score non calculé.</p>
      )}
    </div>
  )
}
```

- [ ] **Step 5: Create DocumentList**

```tsx
// web/components/admin/DocumentList.tsx
'use client'

import { useState } from 'react'
import type { DocumentItem } from '@/lib/types/admin'

const STATUS_COLOR: Record<string, string> = {
  validated: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  uploaded: 'bg-blue-100 text-blue-800',
  pending: 'bg-gray-100 text-gray-600',
  pending_upload: 'bg-gray-100 text-gray-600',
}

const STATUS_LABEL: Record<string, string> = {
  validated: 'Validé',
  rejected: 'Refusé',
  uploaded: 'Uploadé',
  pending: 'En attente',
  pending_upload: 'En attente d\'upload',
}

interface Props {
  documents: DocumentItem[]
  canWrite: boolean
  token: string
}

export function DocumentList({ documents, canWrite, token }: Props) {
  const [loadingId, setLoadingId] = useState<string | null>(null)
  const [results, setResults] = useState<Record<string, string>>({})

  const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

  async function validate(docId: string) {
    setLoadingId(docId)
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}/validate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      setResults((r) => ({ ...r, [docId]: res.ok ? 'validated' : 'error' }))
    } finally {
      setLoadingId(null)
    }
  }

  async function reject(docId: string) {
    const reason = window.prompt('Raison du refus :')
    if (!reason) return
    setLoadingId(docId)
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}/reject`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      })
      setResults((r) => ({ ...r, [docId]: res.ok ? 'rejected' : 'error' }))
    } finally {
      setLoadingId(null)
    }
  }

  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Documents</h3>
        <p className="text-sm text-gray-400">Aucun document.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Documents</h3>
      <ul className="divide-y divide-gray-100">
        {documents.map((doc) => {
          const effectiveStatus = results[doc.id] ?? doc.status
          return (
            <li key={doc.id} className="py-3 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3 min-w-0">
                <span className={`shrink-0 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLOR[effectiveStatus] ?? 'bg-gray-100 text-gray-600'}`}>
                  {STATUS_LABEL[effectiveStatus] ?? effectiveStatus}
                </span>
                <span className="text-sm text-gray-700 truncate">{doc.file_name || doc.type}</span>
              </div>
              {canWrite && effectiveStatus !== 'validated' && effectiveStatus !== 'rejected' && (
                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => validate(doc.id)}
                    disabled={loadingId === doc.id}
                    className="text-xs px-3 py-1 rounded border border-green-300 text-green-700 hover:bg-green-50 disabled:opacity-50"
                  >
                    Valider
                  </button>
                  <button
                    onClick={() => reject(doc.id)}
                    disabled={loadingId === doc.id}
                    className="text-xs px-3 py-1 rounded border border-red-300 text-red-700 hover:bg-red-50 disabled:opacity-50"
                  >
                    Refuser
                  </button>
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
```

- [ ] **Step 6: Create AuditTimeline**

```tsx
// web/components/admin/AuditTimeline.tsx
import type { AuditEvent } from '@/lib/types/admin'

const ACTION_LABEL: Record<string, string> = {
  status_transition: 'Changement de statut',
  document_validated: 'Document validé',
  document_rejected: 'Document refusé',
  pre_approved: 'Pré-accordé',
  deal_rejected: 'Dossier refusé',
  document_requested: 'Pièce demandée',
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export function AuditTimeline({ events }: { events: AuditEvent[] }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Historique</h3>
      {events.length === 0 ? (
        <p className="text-sm text-gray-400">Aucun événement.</p>
      ) : (
        <ol className="relative border-l border-gray-200 ml-2 space-y-4">
          {events.map((event) => (
            <li key={event.id} className="ml-4">
              <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full border border-white bg-gray-400" />
              <p className="text-xs text-gray-400 mb-0.5">{formatDateTime(event.created_at)}</p>
              <p className="text-sm font-medium text-gray-900">
                {ACTION_LABEL[event.action] ?? event.action}
              </p>
              <p className="text-xs text-gray-500 capitalize">{event.actor_role}</p>
              {event.payload && (
                <pre className="mt-1 text-xs text-gray-400 font-mono bg-gray-50 rounded px-2 py-1 overflow-x-auto">
                  {JSON.stringify(event.payload, null, 2)}
                </pre>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
```

- [ ] **Step 7: Create ActionPanel**

```tsx
// web/components/admin/ActionPanel.tsx
'use client'

import { useState } from 'react'

interface Props {
  dealId: string
  token: string
  canWrite: boolean
}

type Modal = 'request_doc' | 'pre_approve' | 'reject' | null

export function ActionPanel({ dealId, token, canWrite }: Props) {
  const [modal, setModal] = useState<Modal>(null)
  const [loading, setLoading] = useState(false)
  const [docType, setDocType] = useState('')
  const [reason, setReason] = useState('')
  const [justification, setJustification] = useState('')
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

  async function post(path: string, body: object) {
    setLoading(true)
    setMessage(null)
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) {
        setMessage({ type: 'error', text: data?.error?.message ?? `Erreur ${res.status}` })
      } else {
        setMessage({ type: 'success', text: 'Action effectuée.' })
        setModal(null)
      }
    } catch {
      setMessage({ type: 'error', text: 'Erreur réseau.' })
    } finally {
      setLoading(false)
    }
  }

  if (!canWrite) return null

  return (
    <div className="sticky bottom-0 bg-white border-t border-gray-200 px-8 py-4 flex items-center gap-3">
      <button
        onClick={() => setModal('request_doc')}
        className="px-4 py-2 rounded-lg border border-yellow-400 text-yellow-700 text-sm font-medium hover:bg-yellow-50"
      >
        Demander une pièce
      </button>
      <button
        onClick={() => setModal('pre_approve')}
        className="px-4 py-2 rounded-lg bg-green-600 text-white text-sm font-medium hover:bg-green-700"
      >
        Pré-accorder
      </button>
      <button
        onClick={() => setModal('reject')}
        className="px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700"
      >
        Refuser
      </button>

      {message && (
        <span className={`text-sm ml-2 ${message.type === 'success' ? 'text-green-600' : 'text-red-600'}`}>
          {message.text}
        </span>
      )}

      {modal === 'request_doc' && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h4 className="font-semibold mb-4">Demander une pièce</h4>
            <label className="block text-sm text-gray-600 mb-1">Type de document</label>
            <input
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-3"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              placeholder="rib, kbis, id_card..."
            />
            <label className="block text-sm text-gray-600 mb-1">Raison</label>
            <textarea
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-4"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setModal(null)} className="text-sm text-gray-500">Annuler</button>
              <button
                disabled={loading || !docType || !reason}
                onClick={() => post(`/admin/deals/${dealId}/request-document`, { document_type: docType, reason })}
                className="px-4 py-2 bg-yellow-500 text-white rounded text-sm font-medium disabled:opacity-50"
              >
                Envoyer
              </button>
            </div>
          </div>
        </div>
      )}

      {modal === 'pre_approve' && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h4 className="font-semibold mb-4">Pré-accorder le dossier</h4>
            <label className="block text-sm text-gray-600 mb-1">Justification (optionnelle)</label>
            <textarea
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-4"
              rows={3}
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setModal(null)} className="text-sm text-gray-500">Annuler</button>
              <button
                disabled={loading}
                onClick={() => post(`/admin/deals/${dealId}/pre-approve`, { justification: justification || null })}
                className="px-4 py-2 bg-green-600 text-white rounded text-sm font-medium disabled:opacity-50"
              >
                Confirmer
              </button>
            </div>
          </div>
        </div>
      )}

      {modal === 'reject' && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <h4 className="font-semibold mb-4">Refuser le dossier</h4>
            <label className="block text-sm text-gray-600 mb-1">Raison du refus <span className="text-red-500">*</span></label>
            <textarea
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-4"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setModal(null)} className="text-sm text-gray-500">Annuler</button>
              <button
                disabled={loading || !reason}
                onClick={() => post(`/admin/deals/${dealId}/reject`, { reason })}
                className="px-4 py-2 bg-red-600 text-white rounded text-sm font-medium disabled:opacity-50"
              >
                Confirmer le refus
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 8: Create loading skeleton**

```tsx
// web/app/(admin)/admin/deals/[id]/loading.tsx
export default function DealReviewLoading() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <div className="w-64 bg-white border-r border-gray-200" />
      <div className="flex-1 p-8 animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-48" />
        <div className="h-32 bg-gray-200 rounded" />
        <div className="h-24 bg-gray-200 rounded" />
        <div className="h-48 bg-gray-200 rounded" />
      </div>
    </div>
  )
}
```

- [ ] **Step 9: Create deal review page**

```tsx
// web/app/(admin)/admin/deals/[id]/page.tsx
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { DealReviewHeader } from '@/components/admin/DealReviewHeader'
import { CompanySummary } from '@/components/admin/CompanySummary'
import { QuoteSummary } from '@/components/admin/QuoteSummary'
import { RiskSummary } from '@/components/admin/RiskSummary'
import { DocumentList } from '@/components/admin/DocumentList'
import { AuditTimeline } from '@/components/admin/AuditTimeline'
import { ActionPanel } from '@/components/admin/ActionPanel'
import type { Deal, DealChecklist, TimelineResponse } from '@/lib/types/admin'

const WRITE_ROLES = ['admin_user', 'ops_user']

interface Props {
  params: Promise<{ id: string }>
}

export default async function DealReviewPage({ params }: Props) {
  const { id } = await params
  const supabase = await createSupabaseServerClient()
  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    return (
      <DashboardShell role="admin" title="Dossier">
        <p className="text-sm text-gray-500">Non authentifié.</p>
      </DashboardShell>
    )
  }

  const token = session.access_token
  const activeRole = (session.user.user_metadata?.active_role as string | undefined) ?? ''
  const canWrite = WRITE_ROLES.includes(activeRole)

  let deal: Deal | null = null
  let checklist: DealChecklist | null = null
  let timeline: TimelineResponse = { data: [], meta: { total: 0 } }

  try {
    const [dealRes, checklistRes, timelineRes] = await Promise.all([
      apiFetch<{ data: Deal }>(`/deals/${id}`, token),
      apiFetch<{ data: DealChecklist }>(`/admin/deals/${id}/checklist`, token),
      apiFetch<TimelineResponse>(`/deals/${id}/timeline`, token),
    ])
    deal = dealRes.data
    checklist = checklistRes.data
    timeline = timelineRes
  } catch (err) {
    console.error('Failed to fetch deal review data:', err)
  }

  if (!deal) {
    return (
      <DashboardShell role="admin" title="Dossier introuvable">
        <p className="text-sm text-gray-500">Impossible de charger ce dossier.</p>
      </DashboardShell>
    )
  }

  return (
    <DashboardShell role="admin" title="Révision dossier" subtitle={deal.public_id}>
      <div className="max-w-4xl">
        <DealReviewHeader deal={deal} />
        <CompanySummary companyId={deal.company_id} />
        <QuoteSummary deal={deal} />
        <RiskSummary deal={deal} />
        <DocumentList
          documents={checklist?.documents ?? []}
          canWrite={canWrite}
          token={token}
        />
        <AuditTimeline events={timeline.data} />
      </div>
      <ActionPanel dealId={id} token={token} canWrite={canWrite} />
    </DashboardShell>
  )
}
```

- [ ] **Step 10: TypeScript check**

```bash
cd web && npx tsc --noEmit
```
Expected: 0 errors.

- [ ] **Step 11: Run full backend test suite one final time**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/ -q
```
Expected: all tests green (~93 total).

- [ ] **Step 12: Commit**

```bash
git add web/components/admin/ web/app/\(admin\)/admin/deals/
git commit -m "feat(web): SCR-ADMIN-003 deal review — 7 components + queue page + action panel"
```

- [ ] **Step 13: Final commit — Phase 4 complete**

```bash
git add -A
git status  # verify nothing unexpected
git commit -m "feat: Phase 4 complete — internal review, audit trail, admin router, web back-office" --allow-empty
```

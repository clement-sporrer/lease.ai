import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.deal import Deal
from app.models.document import Document


def _make_deal(status: str = "submitted") -> MagicMock:
    d = MagicMock(spec=Deal)
    d.id = uuid.uuid4()
    d.public_id = "LD-2026-AAAA"
    d.company_id = uuid.uuid4()
    d.partner_org_id = None
    d.submitted_by_user_id = None
    d.status = status
    d.amount_cents = 10_000_000
    d.currency = "EUR"
    d.duration_months = 36
    d.risk_score = None
    d.risk_band = None
    d.monthly_payment_cents = None
    d.created_at = datetime.now(timezone.utc)
    d.updated_at = datetime.now(timezone.utc)
    return d


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


@pytest.mark.asyncio
async def test_get_checklist_all_docs_validated():
    from app.services import admin_service

    deal = _make_deal("internal_review")
    deal.risk_score = 42.0
    deal.risk_band = "medium"
    deal.monthly_payment_cents = 100000

    doc1 = MagicMock(spec=Document)
    doc1.id = uuid.uuid4()
    doc1.deal_id = deal.id
    doc1.type = "quote"
    doc1.status = "validated"
    doc1.file_name = "q.pdf"
    doc1.created_at = datetime.now(timezone.utc)

    doc2 = MagicMock(spec=Document)
    doc2.id = uuid.uuid4()
    doc2.deal_id = deal.id
    doc2.type = "id_card"
    doc2.status = "validated"
    doc2.file_name = "id.pdf"
    doc2.created_at = datetime.now(timezone.utc)

    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = [doc1, doc2]
    db.execute.side_effect = [deal_result, doc_result]

    checklist = await admin_service.get_checklist(db, deal.id)
    assert checklist["all_docs_validated"] is True
    assert checklist["checklist_complete"] is True


@pytest.mark.asyncio
async def test_get_checklist_incomplete_when_doc_pending():
    from app.services import admin_service

    deal = _make_deal("internal_review")
    deal.risk_score = 55.0
    deal.risk_band = "medium"
    deal.monthly_payment_cents = 90000

    doc = MagicMock(spec=Document)
    doc.id = uuid.uuid4()
    doc.deal_id = deal.id
    doc.type = "quote"
    doc.status = "uploaded"
    doc.file_name = "q.pdf"
    doc.created_at = datetime.now(timezone.utc)

    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = [doc]
    db.execute.side_effect = [deal_result, doc_result]

    checklist = await admin_service.get_checklist(db, deal.id)
    assert checklist["all_docs_validated"] is False
    assert checklist["checklist_complete"] is False

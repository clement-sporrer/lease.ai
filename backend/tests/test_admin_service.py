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
    assert all(d.status in ("submitted", "internal_review", "missing_documents") for d in result)
    db.execute.assert_called_once()


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


@pytest.mark.asyncio
async def test_get_checklist_incomplete_when_no_risk_score():
    from app.services import admin_service

    deal = _make_deal("internal_review")
    deal.risk_score = None  # no risk score — checklist_complete must be False
    deal.risk_band = None
    deal.monthly_payment_cents = None

    doc = MagicMock(spec=Document)
    doc.id = uuid.uuid4()
    doc.deal_id = deal.id
    doc.type = "quote"
    doc.status = "validated"
    doc.file_name = "q.pdf"
    doc.created_at = datetime.now(timezone.utc)

    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = [doc]
    db.execute.side_effect = [deal_result, doc_result]

    checklist = await admin_service.get_checklist(db, deal.id)
    assert checklist["all_docs_validated"] is True
    assert checklist["checklist_complete"] is False  # doc validated but risk_score missing


@pytest.mark.asyncio
async def test_get_checklist_empty_docs_all_docs_validated_false():
    from app.services import admin_service

    deal = _make_deal("internal_review")
    deal.risk_score = 70.0
    deal.risk_band = "low"
    deal.monthly_payment_cents = 80000

    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = []
    db.execute.side_effect = [deal_result, doc_result]

    checklist = await admin_service.get_checklist(db, deal.id)
    assert checklist["all_docs_validated"] is False
    assert checklist["checklist_complete"] is False


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
    db.commit.assert_called_once()
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
    from app.core.errors import AppError

    deal = _make_deal("draft")
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    db.execute.return_value = deal_result

    with pytest.raises(AppError) as exc_info:
        await admin_service.start_review(db, deal.id, uuid.uuid4(), "ops")
    assert exc_info.value.code == "INVALID_TRANSITION"


@pytest.mark.asyncio
async def test_pre_approve_manual_override_requires_justification():
    from app.services import admin_service
    from app.core.errors import AppError

    deal = _make_deal("internal_review")
    deal.risk_score = None  # incomplete checklist

    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = []
    # pre_approve calls _get_deal (1), then get_checklist calls _get_deal (2) + doc query (3)
    db.execute.side_effect = [deal_result, deal_result, doc_result]

    with pytest.raises(AppError) as exc_info:
        await admin_service.pre_approve(db, deal.id, uuid.uuid4(), "ops", justification=None)
    assert exc_info.value.code == "REASON_REQUIRED"


@pytest.mark.asyncio
async def test_pre_approve_manual_override_with_justification_succeeds():
    from unittest.mock import patch
    from app.services import admin_service, audit_service

    deal = _make_deal("internal_review")
    deal.risk_score = None  # incomplete checklist

    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    doc_result = MagicMock()
    doc_result.scalars.return_value.all.return_value = []
    # _get_deal called twice: once in pre_approve, once in get_checklist; doc query last
    db.execute.side_effect = [deal_result, deal_result, doc_result]

    with patch.object(audit_service, "log", new_callable=AsyncMock) as mock_log:
        result = await admin_service.pre_approve(
            db, deal.id, uuid.uuid4(), "admin", justification="Override — client VIP"
        )

    assert result.status == "pre_approved"
    db.commit.assert_called_once()
    payload = mock_log.call_args.kwargs["payload"]
    assert payload["manual_override"] is True
    assert payload["justification"] == "Override — client VIP"


@pytest.mark.asyncio
async def test_reject_requires_reason():
    from app.services import admin_service
    from app.core.errors import AppError

    deal = _make_deal("internal_review")
    db = AsyncMock()
    deal_result = MagicMock()
    deal_result.scalar_one_or_none.return_value = deal
    db.execute.return_value = deal_result

    with pytest.raises(AppError) as exc_info:
        await admin_service.reject(db, deal.id, uuid.uuid4(), "ops", reason="")
    assert exc_info.value.code == "REASON_REQUIRED"


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
    with patch.object(audit_service, "log", new_callable=AsyncMock) as mock_log:
        result = await admin_service.reject(
            db, deal.id, actor_id, "admin", reason="Dossier incomplet"
        )

    assert result.status == "financier_rejected"
    db.commit.assert_called_once()
    mock_log.assert_called_once_with(
        db=db,
        deal_id=deal.id,
        actor_id=actor_id,
        actor_role="admin",
        action="deal_rejected",
        payload={"reason": "Dossier incomplet"},
    )

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


@pytest.mark.anyio
async def test_create_refi_package_requires_pre_approved():
    db = AsyncMock()
    with patch("app.services.refi_service.deal_service.get_deal", new=AsyncMock(return_value=_make_deal("internal_review"))):
        from app.services import refi_service
        with pytest.raises(Exception) as exc_info:
            await refi_service.create_refi_package(db, uuid.uuid4(), "user_001")
    assert "pre_approved" in str(exc_info.value).lower() or "transition" in str(exc_info.value).lower()


@pytest.mark.anyio
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


@pytest.mark.anyio
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
        dec = await refi_service.record_decision(db, pkg, deal, "approved", reason=None, user_id=str(uuid.uuid4()))
    assert dec.decision == "approved"


@pytest.mark.anyio
async def test_record_decision_rejected_requires_reason():
    deal = _make_deal("refi_review")
    pkg = MagicMock()
    pkg.id = uuid.uuid4()
    from app.services import refi_service
    with pytest.raises(Exception):
        await refi_service.record_decision(AsyncMock(), pkg, deal, "rejected", reason=None, user_id="u")

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


@pytest.mark.anyio
async def test_send_signature_sets_sent_at_and_transitions():
    contract = MagicMock()
    contract.id = uuid.uuid4()
    contract.deal_id = uuid.uuid4()
    contract.status = "draft"
    contract.sent_at = None
    db = _make_db()

    with (
        patch("app.services.contract_service.get_contract", new=AsyncMock(return_value=contract)),
        patch("app.services.contract_service.deal_service.transition_deal", new=AsyncMock()),
    ):
        result = await contract_service.send_signature(db, contract.id, str(uuid.uuid4()))

    assert contract.status == "sent_for_signature"
    assert contract.sent_at is not None
    assert db.commit.called


@pytest.mark.anyio
async def test_send_signature_rejects_non_draft():
    contract = MagicMock()
    contract.id = uuid.uuid4()
    contract.status = "sent_for_signature"
    db = _make_db()

    with patch("app.services.contract_service.get_contract", new=AsyncMock(return_value=contract)):
        with pytest.raises(AppError) as exc:
            await contract_service.send_signature(db, contract.id, str(uuid.uuid4()))

    assert exc.value.status_code == 409


@pytest.mark.anyio
async def test_mock_sign_sets_signed_at_and_transitions():
    contract = MagicMock()
    contract.id = uuid.uuid4()
    contract.deal_id = uuid.uuid4()
    contract.status = "sent_for_signature"
    contract.signed_at = None
    db = _make_db()

    with (
        patch("app.services.contract_service.get_contract", new=AsyncMock(return_value=contract)),
        patch("app.services.contract_service.deal_service.transition_deal", new=AsyncMock()),
    ):
        result = await contract_service.mock_sign(db, contract.id, str(uuid.uuid4()))

    assert contract.status == "signed"
    assert contract.signed_at is not None
    assert db.commit.called


@pytest.mark.anyio
async def test_mock_sign_rejects_non_sent():
    contract = MagicMock()
    contract.id = uuid.uuid4()
    contract.status = "draft"
    db = _make_db()

    with patch("app.services.contract_service.get_contract", new=AsyncMock(return_value=contract)):
        with pytest.raises(AppError) as exc:
            await contract_service.mock_sign(db, contract.id, str(uuid.uuid4()))

    assert exc.value.status_code == 409


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

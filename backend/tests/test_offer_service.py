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


@pytest.mark.anyio
async def test_generate_offer_requires_financier_approved():
    deal = _make_deal("pre_approved")
    db = AsyncMock()
    with patch("app.services.offer_service.deal_service.get_deal", new=AsyncMock(return_value=deal)):
        from app.services import offer_service
        with pytest.raises(Exception):
            await offer_service.generate_offer(db, deal.id, "user_admin")


@pytest.mark.anyio
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


@pytest.mark.anyio
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

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import admin_service


def _make_deal(status: str, public_id: str = "LD-2024-ABC"):
    d = MagicMock()
    d.id = uuid.uuid4()
    d.status = status
    d.public_id = public_id
    d.amount_cents = 10000
    d.duration_months = 36
    d.risk_score = 70.0
    d.risk_band = "B"
    d.monthly_payment_cents = 300
    d.updated_at = MagicMock()
    return d


@pytest.mark.asyncio
async def test_get_queue_no_filters_returns_all():
    deals = [_make_deal("submitted"), _make_deal("internal_review")]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = deals
    mock_data_result = MagicMock()
    mock_data_result.scalars.return_value = mock_scalars

    mock_count_scalars = MagicMock()
    mock_count_scalars.one.return_value = 2
    mock_count_result = MagicMock()
    mock_count_result.scalars.return_value = mock_count_scalars

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[mock_data_result, mock_count_result])

    result_deals, total = await admin_service.get_queue(db)
    assert len(result_deals) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_get_queue_filters_by_status():
    deals = [_make_deal("submitted")]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = deals
    mock_data_result = MagicMock()
    mock_data_result.scalars.return_value = mock_scalars

    mock_count_scalars = MagicMock()
    mock_count_scalars.one.return_value = 1
    mock_count_result = MagicMock()
    mock_count_result.scalars.return_value = mock_count_scalars

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[mock_data_result, mock_count_result])

    result_deals, total = await admin_service.get_queue(db, status="submitted")
    assert total == 1


@pytest.mark.asyncio
async def test_get_queue_paginates():
    deals = [_make_deal("submitted")]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = deals
    mock_data_result = MagicMock()
    mock_data_result.scalars.return_value = mock_scalars

    mock_count_scalars = MagicMock()
    mock_count_scalars.one.return_value = 25
    mock_count_result = MagicMock()
    mock_count_result.scalars.return_value = mock_count_scalars

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[mock_data_result, mock_count_result])

    result_deals, total = await admin_service.get_queue(db, page=2, page_size=20)
    assert total == 25

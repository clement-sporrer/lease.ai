import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.deal import Deal
from app.models.profile import Profile
from app.services import deal_service


def test_generate_public_id_is_bounded_and_year_prefixed():
    public_id = deal_service._generate_public_id()
    assert public_id.startswith("LD-")
    assert len(public_id) <= 20


def test_same_status_transition_is_allowed():
    deal_service._assert_transition("quote_added", "quote_added")


@pytest.mark.asyncio
async def test_create_deal_creates_missing_profile():
    db = MagicMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: None))
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    await deal_service.create_deal(
        db=db,
        company_id=uuid.uuid4(),
        user_id=str(uuid.uuid4()),
        currency="EUR",
    )

    assert any(isinstance(call.args[0], Profile) for call in db.add.call_args_list)

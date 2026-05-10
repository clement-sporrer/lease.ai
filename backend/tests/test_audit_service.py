import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import audit_service


@pytest.mark.asyncio
async def test_log_adds_event_and_flushes_without_commit():
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
    db.flush.assert_called_once()
    db.commit.assert_not_called()  # commit is the caller's responsibility

    event = db.add.call_args[0][0]
    assert event.deal_id == deal_id
    assert event.actor_id == actor_id
    assert event.actor_role == "ops"
    assert event.action == "status_transition"
    assert event.payload == {"from": "submitted", "to": "internal_review"}


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
async def test_get_timeline_returns_events():
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
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = events
    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await audit_service.get_timeline(db, deal_id)
    assert result == events

    stmt = db.execute.call_args[0][0]
    whereclause = str(stmt.whereclause.compile(compile_kwargs={"literal_binds": True}))
    # SQLAlchemy renders UUIDs without dashes in literal binds
    assert str(deal_id).replace("-", "") in whereclause


@pytest.mark.asyncio
async def test_log_with_none_actor_id():
    db = AsyncMock()
    await audit_service.log(
        db=db,
        deal_id=uuid.uuid4(),
        actor_id=None,
        actor_role="system",
        action="status_transition",
        payload={"from": "submitted", "to": "internal_review"},
    )
    db.flush.assert_called_once()
    db.commit.assert_not_called()
    event = db.add.call_args[0][0]
    assert event.actor_id is None

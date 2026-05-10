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
    await db.flush()  # visible in session; caller commits
    return event


async def get_timeline(db: AsyncSession, deal_id: uuid.UUID) -> list[AuditEvent]:
    result = await db.execute(
        select(AuditEvent)
        .where(AuditEvent.deal_id == deal_id)
        .order_by(AuditEvent.created_at.desc())
    )
    return list(result.scalars().all())

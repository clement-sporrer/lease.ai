import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RequestDocumentRequest(BaseModel):
    document_type: str
    reason: str


class PreApproveRequest(BaseModel):
    justification: str | None = None


class RejectRequest(BaseModel):
    reason: str


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    actor_id: uuid.UUID | None
    actor_role: str
    action: str
    payload: dict[str, Any] | None
    created_at: datetime

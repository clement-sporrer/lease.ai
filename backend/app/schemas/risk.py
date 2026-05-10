import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    score: int
    band: str
    flags: list | None
    rules_applied: list | None
    recommendation: str | None
    version: int
    created_at: datetime

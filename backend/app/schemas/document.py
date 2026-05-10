import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentUploadUrlResponse(BaseModel):
    document_id: uuid.UUID
    upload_url: str
    expires_in: int = 3600


class DocumentConfirmRequest(BaseModel):
    document_id: uuid.UUID
    file_name: str
    mime_type: str
    size_bytes: int
    document_type: str = "quote"


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    deal_id: uuid.UUID
    type: str
    status: str
    file_name: str
    mime_type: str | None
    size_bytes: int | None
    version: int
    created_at: datetime

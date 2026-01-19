from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class AttachmentOut(BaseModel):
    id: UUID
    file_name: str
    file_path: str  # Ye browser mein image dikhane ke kaam aayega
    issue_id: UUID
    uploader_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AttachmentUpdate(BaseModel):
    file_name: str

from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    message: str = Field(..., max_length=1000)
    type: str = Field(..., max_length=50)
    issue_id: Optional[UUID4] = None

class NotificationCreate(NotificationBase):
    user_id: UUID4

class NotificationResponse(NotificationBase):
    id: UUID4
    user_id: UUID4
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True

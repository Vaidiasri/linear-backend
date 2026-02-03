from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from .user import UserOut


class ActivityOut(BaseModel):
    """
    Activity log output - Issue ki history dikhane ke liye
    """

    id: UUID
    issue_id: UUID
    user_id: UUID
    attribute: str  # Kaunsa field change hua (status, priority, etc.)
    old_value: str | None
    new_value: str
    created_at: datetime

    # Nested user data - Kisne change kiya
    user: UserOut

    class Config:
        from_attributes = True

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from .user import UserOut


class CommentCreate(BaseModel):
    """
    User sirf content bhejega.
    - issue_id: URL se aayega (e.g., POST /issues/{issue_id}/comments)
    - author_id: Current logged-in user se automatically set hoga
    - created_at: Database automatically set karega
    """

    content: str


class CommentOut(BaseModel):
    """
    Frontend ko ye sab data chahiye:
    - Comment ki details
    - Author ka naam aur email (nested UserOut)
    """

    id: UUID
    content: str
    issue_id: UUID
    author_id: UUID
    created_at: datetime

    # Nested author data
    author: UserOut

    class Config:
        from_attributes = True

from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum


# Issue Status Enum
class IssueStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


# Issue Priority Enum
class IssuePriority(int, Enum):
    NO_PRIORITY = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[IssueStatus] = IssueStatus.BACKLOG
    priority: Optional[IssuePriority] = IssuePriority.NO_PRIORITY
    team_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None


class IssueCreate(IssueBase):
    pass


class IssueOut(IssueBase):
    id: UUID
    creator_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Enhanced Issue Detail Schema with nested data
class IssueDetailOut(IssueBase):
    """
    Complete issue details with comments and activities
    Used for single issue view (GET /issues/{id})
    """

    id: UUID
    creator_id: UUID
    created_at: datetime

    # Nested related data - imported to avoid circular imports
    comments: list = []  # list[CommentOut]
    activities: list = []  # list[ActivityOut]

    class Config:
        from_attributes = True

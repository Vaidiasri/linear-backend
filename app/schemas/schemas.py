from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from enum import Enum


# Issue Status Enum - Sirf ye values allowed hain
class IssueStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


# Issue Priority Enum - 0 to 3 tak
class IssuePriority(int, Enum):
    NO_PRIORITY = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class UserBase(BaseModel):
    full_name: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID

    class Config:
        from_attributes = True


class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[IssueStatus] = IssueStatus.BACKLOG  # Enum validation
    priority: Optional[IssuePriority] = IssuePriority.NO_PRIORITY  # Enum validation
    team_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None


class IssueCreate(IssueBase):
    pass


class IssueOut(IssueBase):
    id: UUID
    creator_id: UUID
    created_at: datetime
    # Optional: UserOut schema ko nested bhej sakte ho (Relationship ke zariye)
    # assignee: Optional[UserOut] = None

    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    name: str
    key: str


class TeamOut(BaseModel):
    id: UUID
    name: str
    key: str

    class Config:
        from_attributes = True


# project schema
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    team_id: UUID


class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    team_id: UUID

    class Config:
        from_attributes = True

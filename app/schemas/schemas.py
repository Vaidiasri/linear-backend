from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


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
    status: Optional[str] = "backlog"
    priority: Optional[int] = 0
    team_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None


class IssueCreate(IssueBase):
    pass


class IssueOut(IssueBase):
    id: UUID
    creator_id: UUID
    created_at: datetime
    
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
    name:str
    description:Optional[str]=None
    team_id:UUID
class ProjectOut(BaseModel):
    id:UUID
    name:str
    description:Optional[str]
    team_id:UUID
    class Config:
        from_attributes=True


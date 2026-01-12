from typing import Optional
from pydantic import BaseModel
from uuid import UUID


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

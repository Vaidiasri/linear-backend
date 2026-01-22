from pydantic import BaseModel
from uuid import UUID
from typing import List


class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None


class TeamCreate(BaseModel):
    name: str
    key: str


class TeamOut(BaseModel):
    id: UUID
    name: str
    key: str
    projects: list[ProjectOut] = []

    class Config:
        from_attributes = True

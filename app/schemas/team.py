from pydantic import BaseModel
from uuid import UUID


class TeamCreate(BaseModel):
    name: str
    key: str


class TeamOut(BaseModel):
    id: UUID
    name: str
    key: str

    class Config:
        from_attributes = True

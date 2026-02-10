from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CycleBase(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    team_id: UUID


class CycleCreate(CycleBase):
    pass


class CycleUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CycleOut(CycleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    full_name: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID

    class Config:
        from_attributes = True

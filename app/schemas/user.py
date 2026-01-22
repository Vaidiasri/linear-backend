from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.model.user import UserRole


class UserBase(BaseModel):
    full_name: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID

    class Config:
        from_attributes = True


class UserUpdateRole(BaseModel):
    role: UserRole
    team_id: UUID | None = None

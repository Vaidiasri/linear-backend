from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.model.user import UserRole


class UserBase(BaseModel):
    full_name: str | None = None
    email: EmailStr
    avatar_url: str | None = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class UserUpdateRole(BaseModel):
    role: UserRole
    team_id: UUID | None = None

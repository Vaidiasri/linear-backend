from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, model, utils
from app.schemas.user import UserCreate


class UserService:
    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> model.User:
        # Check if user with this email already exists
        existing_user = await crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Hash the password
        hash_password = utils.hash_password(user_in.password)

        # Prepare data for DB
        user_data = user_in.model_dump()
        user_data.pop("password")

        # Create user object
        new_user = model.User(**user_data, hashed_password=hash_password)

        # Save to DB
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[model.User]:
        return await crud.user.get_by_email(db, email=email)

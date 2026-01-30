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

    @staticmethod
    async def update_role(
        db: AsyncSession, user_id: str, role: str, team_id: Optional[str] = None
    ) -> model.User:
        # Check if user exists
        user = await crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # If team_id is provided, validate it
        if team_id:
            team = await crud.team.get(db, id=team_id)
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
                )

        # Update
        user.role = role
        user.team_id = team_id

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    # api for update user avatar
    @staticmethod
    async def update_avatar(db: AsyncSession, user_id: str, avatar: str) -> model.User:
        # Check if user exists
        user = await crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.avatar_url = avatar
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[model.User]:
        return await crud.user.get_multi(db, skip=skip, limit=limit)

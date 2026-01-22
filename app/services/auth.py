from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, utils, oauth2


class AuthService:
    @staticmethod
    async def login(db: AsyncSession, credentials: OAuth2PasswordRequestForm) -> dict:
        # 1. User dhundo by email
        user = await crud.user.get_by_email(db, email=credentials.username)

        # 2. Validation
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # 3. Password Check
        if not utils.verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # 4. Create Token
        access_token = oauth2.create_access_token(data={"sub": user.email})

        return {"access_token": access_token, "token_type": "bearer"}

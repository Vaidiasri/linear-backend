from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..lib.database import get_db
from .. import model, utils, oauth2

# Auth router banao - saare authentication endpoints yahan honge
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),  # Form se username/password lega
    db: AsyncSession = Depends(get_db),  # Database session inject karo
):
    """
    User login endpoint
    - Email aur password verify karta hai
    - Valid credentials pe JWT token return karta hai
    """

    # 1. Database se user dhundo email (username field) se
    # OAuth2PasswordRequestForm mein email "username" field mein aata hai
    query = select(model.User).where(model.User.email == user_credentials.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()  # Ek user ya None return karega

    # 2. Agar user nahi mila toh invalid credentials error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # 3. Password verify karo - hashed password se compare karo
    if not utils.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # 4. Sab sahi hai toh JWT token banao
    # Token mein user ka email store karo (subject field mein)
    access_token = oauth2.create_access_token(data={"sub": user.email})

    # 5. Token return karo OAuth2 standard format mein
    return {"access_token": access_token, "token_type": "bearer"}

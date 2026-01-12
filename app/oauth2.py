from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .lib.database import get_db
from .model import User  # Refactored: direct import instead of model.User

# .env file se environment variables load karo
load_dotenv()

# JWT Configuration .env se load karo
SECRET_KEY = os.getenv("SECRET_KEY")  # Ye secret key token sign karne ke liye
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default HS256 algorithm use karenge
EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)  # Token 30 min baad expire hoga
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)  # y ek security  tool hai jo


# Agar SECRET_KEY nahi mila toh error throw karo
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable nahi mila .env file mein")


def create_access_token(data: dict):
    """
    JWT access token banata hai
    data: dict - Token mein store karne ka data (usually user email/id)
    Returns: encoded JWT token string
    """

    # Original data ko copy karo taaki modify na ho
    to_encode = data.copy()

    # Expiry time calculate karo (current time + EXPIRE_MINUTES)
    time_delta = timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": datetime.utcnow() + time_delta})

    # Token encode karo SECRET_KEY aur ALGORITHM se
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Protect  route  the code
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    # 1. Pehle ek standard error message bana lo
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Bhai, tera token sahi nahi hai ya expire ho gaya!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 2 Token ko decode (Unlock) karo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 3. Payload se ID nikaalo (Humne login mein 'sub' mein ID/Email dali thi)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        # Agar token kisi ne tampered kiya ya algorithm galat hai
        raise credentials_exception
    # 4. Database mein check karo ki ye user asali hai ya nahi
    query = select(User).where(User.email == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if user is None:
        raise credentials_exception

    # 5. Sab sahi raha toh 'user' ka pura object return kar do
    return user

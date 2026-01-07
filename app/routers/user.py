from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .. import schemas, model, utils  # ".." matlab bahar jao aur ye files lao
from ..lib.database import get_db

# Router instance bana dia
router = APIRouter(prefix="/users", tags=["Users"])


# chal bhai signup ka logic likhte hai
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Pehle check karo ki email already exist toh nahi karta
    existing_user_query = select(model.User).where(model.User.email == user.email)
    result = await db.execute(existing_user_query)
    existing_user = result.scalar_one_or_none()

    # Agar user mil gaya matlab email already registered hai
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bhai ek  hi email se do baar do bar register kar  raha  le error 😂",
        )

    # 2. Password hash kiya (naam dhyan se dekho)
    hashed_pwd = utils.hash_password(user.password)

    # 3. Data nikalo aur password pop karo
    user_data = user.model_dump()
    user_data.pop("password")

    # 4. Model banao (Yahan dono naam match hone chahiye)
    # router/user.py mein
    new_user = model.User(
        **user_data, hashed_password=hashed_pwd
    )  # hashed_password match hona chahiye model se

    # 5. DB mein save
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

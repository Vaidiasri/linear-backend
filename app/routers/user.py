from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, model, utils
from ..lib.database import get_db
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(
    user: schemas.UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Check if user with this email already exists
    query = select(model.User).where(model.User.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash the password
    hash_password = utils.hash_password(user.password)
    
    # Create user data dictionary
    user_data = user.model_dump()
    user_data.pop("password")
    
    # Create new user with hashed password
    new_user = model.User(**user_data, hashed_password=hash_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

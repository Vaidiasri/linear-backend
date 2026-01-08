from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, model, utils  # ".." matlab bahar jao aur ye files lao
from ..lib.database import get_db
from sqlalchemy import select # Ye import zaroori hai top par

# Router instance bana dia
router = APIRouter(prefix="/users", tags=["Users"])


# chal bhai signup ka logic likhte hai
@router.post("/")
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # password=schemas.UserCreate y galat kar  raha tha tu
    # creat_user ke andar  query bana  raha hu  because email same  nahi honi chaiye  y db m error  de sakti hai 
    query=select(model.User).where(model.User.email == user.email)
     # database m query  execute karo
    result=await db.execute(query)
    # result se  user nikal raha hu
    existing_user=result.scalars().first()
    # check agar  banda  mil gaya tho ruka ja error dege  hum isse 
    if existing_user:
        raise HTTPException(status_code=400,detail="Bhai ek  hi email se do baar do bar register kar  raha  le error 😂")
   
    # 1. Sabse phele password #### kar de
    hash_password = utils.hash_password(user.password)
    # 2. user data m purane  plain password  ki jaga  hash password daal do
    user.password = hash_password
    # 3. Ab is data  ko Database Model (User) m bablo
    user_data = user.model_dump() # Saara data nikal liya
    user_data.pop("password")     # 'password' ko dictionary se nikaal diya
    
    # Ab data pack karke bhejo aur manual hash_password add kar do
    new_user = model.User(**user_data, hashed_password=hash_password)
    # ab bas db m add kar dete hai
    db.add(new_user)  # y khali nahi hoga issme jo naya object banay hai  vo hoga
    await db.commit()
    await db.refresh(new_user)  # same for  this  to
    return new_user

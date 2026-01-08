# ab aur kiya kiya import  karna hai 
# 1 get_db function database se baat chize k liye
#2 schema chahiye api m data  kaise dekhega  y aaega  uske  liye 
#3 utils bhai le hi aate hai 
#4 model bhi chahiye  bhai 
#5 select taki query  run kar pau
# 6 AsyncSession async way mein database se baat karta hai bina app ko block kiye.
from fastapi import APIRouter,HTTPException,status,Depends
from .. import schemas, model, utils, oauth2  # ".." matlab bahar jao aur ye files lao
from ..lib.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/issues", tags=["Issues"]) # make  the  instance of APIRouter
@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_issues(issue:schemas.IssueCreate,db:AsyncSession=Depends(get_db),current_user:model.User=Depends(oauth2.get_current_user)):
    # naya  issue bana lete  hai
    new_issue=model.Issue(
        **issue.model_dump(),
        creator_id=current_user.id # token se  id  khud  le  le  ga 
    ) 
    db.add(new_issue)
    await db.commit()
    await db.refresh(new_issue)
    return new_issue



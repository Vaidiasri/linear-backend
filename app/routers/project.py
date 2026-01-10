from fastapi import APIRouter,HTTPException,Depends,status
from ..lib.database import get_db
from  .. import model,schemas,utils,oauth2
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
router=APIRouter(prefix="/projects",tags=["Projects"])
# get  all project
@router.get("/",status_code=status.HTTP_200_OK,response_model=list[schemas.ProjectOut])
async def get_all_projects(db:AsyncSession=Depends(get_db),current_user:model.User=Depends(oauth2.get_current_user)):
    query=select(model.Project)
    result= await db.execute(query)
    all_project=result.scalars().all() # yaad rakhna hai bhai 
    return all_project
# get the  user  with id 
@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=schemas.ProjectOut)
async def get_project_by_id(id:UUID,db:AsyncSession=Depends(get_db),current_user:model.User=Depends(oauth2.get_current_user)):
    project_by_id=select(model.Project).where(model.Project.id==id)
    result= await db.execute(project_by_id)
    project=result.scalar().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Bhai asi koi id nahi hai")
    return project
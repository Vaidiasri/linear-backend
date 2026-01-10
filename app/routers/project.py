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
    query = select(model.Project).where(model.Project.id == id)
    result = await db.execute(query)
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProjectOut)
async def create_project(
    project: schemas.ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    # Check if team exists (since project needs a valid team_id)
    team_query = select(model.Team).where(model.Team.id == project.team_id)
    team_result = await db.execute(team_query)
    team = team_result.scalars().first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Create new project
    new_project = model.Project(**project.model_dump())
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return new_project


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ProjectOut)
async def update_project(
    id: UUID,
    updated_project: schemas.ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    # Check if project exists
    query = select(model.Project).where(model.Project.id == id)
    result = await db.execute(query)
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if team exists (if team_id is being updated)
    if updated_project.team_id != project.team_id:
        team_query = select(model.Team).where(model.Team.id == updated_project.team_id)
        team_result = await db.execute(team_query)
        team = team_result.scalars().first()
        
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
    
    # Update project data
    for key, value in updated_project.model_dump().items():
        setattr(project, key, value)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    # Check if project exists
    query = select(model.Project).where(model.Project.id == id)
    result = await db.execute(query)
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Delete project
    await db.delete(project)
    await db.commit()
    
    return None
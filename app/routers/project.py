from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, model, oauth2
from ..lib.database import get_db
from ..services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[schemas.ProjectOut]
)
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await ProjectService.get_all(db)


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ProjectOut)
async def get_project_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await ProjectService.get(db, id=id)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProjectOut
)
async def create_project(
    project: schemas.ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await ProjectService.create(db, project_in=project)


@router.put(
    "/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.ProjectOut
)
async def update_project(
    id: UUID,
    update_project: schemas.ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await ProjectService.update(db, id=id, project_in=update_project)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    await ProjectService.delete(db, id=id)
    return None

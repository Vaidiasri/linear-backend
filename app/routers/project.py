from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.user import UserRole

from .. import model, oauth2, schemas
from ..lib.database import get_db
from ..services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[schemas.ProjectOut]
)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        return await ProjectService.get_all(db, skip=skip, limit=limit)

    if current_user.team_id:
        return await ProjectService.get_by_team(
            db, team_id=current_user.team_id, skip=skip, limit=limit
        )

    return []


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
    # Strict Check
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can create projects",
        )
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
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can update projects",
        )

    return await ProjectService.update(db, id=id, project_in=update_project)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can delete projects",
        )
    await ProjectService.delete(db, id=id)
    return None

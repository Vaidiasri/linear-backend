from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, model
from app.schemas.project import ProjectCreate, ProjectCreate as ProjectUpdate


class ProjectService:
    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[model.Project]:
        return await crud.project.get_multi(db, skip=skip, limit=limit)

    @staticmethod
    async def get_by_team(
        db: AsyncSession, team_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[model.Project]:
        return await crud.project.get_multi_by_owner(
            db, owner_id=team_id, skip=skip, limit=limit, owner_field="team_id"
        )

    @staticmethod
    async def get(db: AsyncSession, id: UUID) -> model.Project:
        project = await crud.project.get(db, id=id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )
        return project

    @staticmethod
    async def create(db: AsyncSession, project_in: ProjectCreate) -> model.Project:
        # Validate that the team exists
        team = await crud.team.get(db, id=project_in.team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
            )

        return await crud.project.create(db, obj_in=project_in)

    @staticmethod
    async def update(
        db: AsyncSession, id: UUID, project_in: ProjectUpdate
    ) -> model.Project:
        project = await ProjectService.get(db, id)

        # If team_id is being updated, validate it exists
        if project_in.team_id != project.team_id:
            team = await crud.team.get(db, id=project_in.team_id)
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
                )

        return await crud.project.update(db, db_obj=project, obj_in=project_in)

    @staticmethod
    async def delete(db: AsyncSession, id: UUID) -> None:
        project = await ProjectService.get(db, id)
        await crud.project.remove(db, id=id)

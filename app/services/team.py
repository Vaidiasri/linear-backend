from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, model
from app.schemas.team import TeamCreate, TeamCreate as TeamUpdate


class TeamService:
    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[model.Team]:
        return await crud.team.get_multi(db, skip=skip, limit=limit)

    @staticmethod
    async def get(db: AsyncSession, id: UUID) -> model.Team:
        team = await crud.team.get(db, id=id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
            )
        return team

    @staticmethod
    async def create(db: AsyncSession, team_in: TeamCreate) -> model.Team:
        # Check if team with same key already exists
        existing_team = await crud.team.get_by_key(db, key=team_in.key)
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team with this key already exists",
            )
        new_team = await crud.team.create(db, obj_in=team_in)
        # Re-fetch to ensure relationships (like projects) are eager-loaded for schema validation
        return await TeamService.get(db, new_team.id)

    @staticmethod
    async def update(db: AsyncSession, id: UUID, team_in: TeamUpdate) -> model.Team:
        team = await TeamService.get(db, id)

        # Check if updated key already exists (if key is being changed)
        if team_in.key != team.key:
            existing_team = await crud.team.get_by_key(db, key=team_in.key)
            if existing_team:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Team with this key already exists",
                )

        return await crud.team.update(db, db_obj=team, obj_in=team_in)

    @staticmethod
    async def delete(db: AsyncSession, id: UUID) -> None:
        team = await TeamService.get(db, id)
        await crud.team.remove(db, id=id)

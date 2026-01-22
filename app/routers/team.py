from uuid import UUID
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, model, oauth2
from ..lib.database import get_db
from ..services.team import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.TeamOut])
async def get_teams(
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await TeamService.get_all(db)


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.TeamOut)
async def get_team_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await TeamService.get(db, id=id)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TeamOut)
async def create_team(
    team: schemas.TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await TeamService.create(db, team_in=team)


@router.put(
    "/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.TeamOut
)
async def update_team(
    id: UUID,
    update_team: schemas.TeamCreate,
    db: AsyncSession = Depends(get_db),
    # Added auth dependency for consistency, though original didn't have it explicitly used but likely needed
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await TeamService.update(db, id=id, team_in=update_team)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    await TeamService.delete(db, id=id)
    return None

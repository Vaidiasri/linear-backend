from uuid import UUID
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, model, utils, oauth2  # ".." matlab bahar jao aur ye files lao
from ..lib.database import get_db
from sqlalchemy import select

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.TeamOut])
async def get_teams(
    db: AsyncSession = Depends(get_db), 
    current_user: model.User = Depends(oauth2.get_current_user)
):
    # 1. Database se saari teams uthao
    query = select(model.Team)
    result = await db.execute(query)
    all_teams = result.scalars().all()

    # 2. Teams ki list wapas bhej do
    return all_teams


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.TeamOut)
async def get_team_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    # Query to get team by ID
    query = select(model.Team).where(model.Team.id == id)
    result = await db.execute(query)
    team = result.scalars().first()
    
    # Check if team exists
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return team

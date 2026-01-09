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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TeamOut)
async def create_team(
    team: schemas.TeamCreate,  # Request body se data aayega: {name: "Engineering", key: "ENG"}
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    # team.key = Request body mein jo "key" value aayi hai (e.g., "ENG", "DESIGN")
    # Example: Agar request body me {"name": "Engineering Team", "key": "ENG"} hai
    # To team.key = "ENG" hoga
    
    # Check if team with same key already exists
    # Database mein pehle se hi same key ki team hai ya nahi check kar rahe hain
    query = select(model.Team).where(model.Team.key == team.key)  # team.key = request se aaya key
    result = await db.execute(query)
    existing_team = result.scalars().first()  # Agar mil gayi to existing_team mein data hoga, nahi to None
    
    if existing_team:
        # Agar same key ki team already exist karti hai, to error throw karo
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this key already exists"
        )
    
    # Create new team
    # team.model_dump() = {"name": "Engineering Team", "key": "ENG"} (dictionary ban jayega)
    new_team = model.Team(**team.model_dump())  # Dictionary ko unpack karke Team model object banao
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    
    return new_team
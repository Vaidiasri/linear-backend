# ab aur kiya kiya import  karna hai
# 1 get_db function database se baat chize k liye
# 2 schema chahiye api m data  kaise dekhega  y aaega  uske  liye
# 3 utils bhai le hi aate hai
# 4 model bhi chahiye  bhai
# 5 select taki query  run kar pau
# 6 AsyncSession async way mein database se baat karta hai bina app ko block kiye.
from fastapi import APIRouter, HTTPException, status, Depends
from .. import schemas, model, utils, oauth2  # ".." matlab bahar jao aur ye files lao
from ..lib.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID  # UUID type ke liye import

router = APIRouter(
    prefix="/issues", tags=["Issues"]
)  # make  the  instance of APIRouter


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_issues(
    issue: schemas.IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # naya  issue bana lete  hai
    new_issue = model.Issue(
        **issue.model_dump(),
        creator_id=current_user.id  # token se  id  khud  le  le  ga
    )
    db.add(new_issue)
    await db.commit()
    await db.refresh(new_issue)
    return new_issue


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_issues(
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # Query: Saare issues uthao jo is user ne banaye hain
    query = select(model.Issue).where(model.Issue.creator_id == current_user.id)

    result = await db.execute(query)
    issues = result.scalars().all()

    return issues


@router.put("/{id}")
async def update_issue(
    id: UUID,
    updated_issue: schemas.IssueCreate,  # Wahi schema use kar sakte hain
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # Pehle check karo ki issue exist karta hai aur user uska owner hai ya nahi
    query = select(model.Issue).where(
        model.Issue.id == id, model.Issue.creator_id == current_user.id
    )
    result = await db.execute(query)
    issue = result.scalars().first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue nahi mila ya aap owner nahi ho!",
        )

    # Data update karo
    for key, value in updated_issue.model_dump().items():
        setattr(issue, key, value)

    await db.commit()
    await db.refresh(issue)
    return issue


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # Check karo ki issue user ka hi hai
    query = select(model.Issue).where(
        model.Issue.id == id, model.Issue.creator_id == current_user.id
    )
    result = await db.execute(query)
    issue = result.scalars().first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue nahi mila!"
        )

    await db.delete(issue)
    await db.commit()
    return None

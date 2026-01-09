from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from .. import schemas, model, utils, oauth2
from ..lib.database import get_db

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.IssueOut)
async def create_issues(
    issue: schemas.IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # Create new issue
    new_issue = model.Issue(
        **issue.model_dump(),
        creator_id=current_user.id
    )
    db.add(new_issue)
    await db.commit()
    await db.refresh(new_issue)
    return new_issue


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.IssueOut])
async def get_all_issues(
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # Get all issues created by the current user
    query = select(model.Issue).where(model.Issue.creator_id == current_user.id)
    result = await db.execute(query)
    issues = result.scalars().all()
    
    return issues


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.IssueOut)
async def update_issue(
    id: UUID,
    updated_issue: schemas.IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # Check if issue exists and user is the owner
    query = select(model.Issue).where(
        model.Issue.id == id, model.Issue.creator_id == current_user.id
    )
    result = await db.execute(query)
    issue = result.scalars().first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found or you are not the owner"
        )

    # Update issue data
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
    # Check if issue exists and user is the owner
    query = select(model.Issue).where(
        model.Issue.id == id, model.Issue.creator_id == current_user.id
    )
    result = await db.execute(query)
    issue = result.scalars().first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found or you are not the owner"
        )

    await db.delete(issue)
    await db.commit()
    return None

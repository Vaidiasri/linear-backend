from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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
    try:
        # 1. Project Validation
        if issue.project_id:
            project_query = select(model.Project).where(
                model.Project.id == issue.project_id
            )
            project_result = await db.execute(project_query)
            project = project_result.scalars().first()

            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )

        # 2. Assignee Validation
        if issue.assignee_id:
            user_query = select(model.User).where(model.User.id == issue.assignee_id)
            user_result = await db.execute(user_query)
            assignee = user_result.scalars().first()

            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee user not found",
                )

        # 3. Team Validation
        if issue.team_id:
            team_query = select(model.Team).where(model.Team.id == issue.team_id)
            team_result = await db.execute(team_query)
            team = team_result.scalars().first()

            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
                )

        # 4. Create new issue
        new_issue = model.Issue(**issue.model_dump(), creator_id=current_user.id)

        db.add(new_issue)
        # Activity Log for Creation
        creation_log = model.Activity(
            issue_id=new_issue.id,
            user_id=current_user.id,
            attribute="created",
            old_value="",  # Empty string instead of None (NOT NULL constraint)
            new_value=f"Issue created by {current_user.email}",
        )
        db.add(creation_log)
        # Note: Assignee log NOT created on creation - it's part of initial state
        # Activity logs are only for CHANGES, not initial values
        # ---------------------------
        await db.commit()
        await db.refresh(new_issue)
        return new_issue

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        await db.rollback()
        raise
    except Exception as e:
        # Rollback on any other error
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create issue: {str(e)}",
        )


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.IssueOut])
async def get_all_issues(
    # 1. Saare optional filters yahan add kar diye
    status_filter: str | None = None,
    priority: int | None = None,
    team_id: UUID | None = None,
    project_id: UUID | None = None,
    assignee_id: UUID | None = None,
    search: str | None = None,  # Title search ke liye
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # 2. Base query
    query = select(model.Issue).where(model.Issue.creator_id == current_user.id)

    # 3. Dynamic Filters (Jo user ne bheja sirf wahi add hoga)
    if status_filter:
        query = query.where(model.Issue.status == status_filter)

    if priority is not None:
        query = query.where(model.Issue.priority == priority)

    if team_id:
        query = query.where(model.Issue.team_id == team_id)

    if project_id:
        query = query.where(model.Issue.project_id == project_id)

    if assignee_id:
        query = query.where(model.Issue.assignee_id == assignee_id)

    # 4. Search Logic (Title mein kahin bhi word match ho jaye)
    if search:
        # ilike case-insensitive hota hai (Bug = bug)
        query = query.where(model.Issue.title.ilike(f"%{search}%"))

    # 5. Result
    result = await db.execute(query)
    issues = result.scalars().all()

    return issues


# get  issue  by id with complete details (comments + activities)
@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.IssueDetailOut
)
async def get_issue_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # Eager loading - ek hi query mein sab kuch fetch karo
    # selectinload se N+1 query problem avoid hoga
    query = (
        select(model.Issue)
        .where(model.Issue.id == id, model.Issue.creator_id == current_user.id)
        .options(
            # Comments load karo with author details
            selectinload(model.Issue.comments).selectinload(model.Comment.author),
            # Activities load karo with user details
            selectinload(model.Issue.activities).selectinload(model.Activity.user),
        )
    )

    result = await db.execute(query)
    issue = result.scalars().first()

    # Validation
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found or you don't have access",
        )

    return issue


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.IssueOut)
async def update_issue(
    id: UUID,
    updated_issue: schemas.IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    try:
        # Check if issue exists and user is the owner
        query = select(model.Issue).where(
            model.Issue.id == id, model.Issue.creator_id == current_user.id
        )
        result = await db.execute(query)
        issue = result.scalars().first()

        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found or you are not the owner",
            )

        # Validate project_id if provided and changed
        if updated_issue.project_id and updated_issue.project_id != issue.project_id:
            project_query = select(model.Project).where(
                model.Project.id == updated_issue.project_id
            )
            project_result = await db.execute(project_query)
            project = project_result.scalars().first()

            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
                )

        # Validate assignee_id if provided and changed
        if updated_issue.assignee_id and updated_issue.assignee_id != issue.assignee_id:
            user_query = select(model.User).where(
                model.User.id == updated_issue.assignee_id
            )
            user_result = await db.execute(user_query)
            assignee = user_result.scalars().first()

            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee user not found",
                )

        # Validate team_id if provided and changed
        if updated_issue.team_id and updated_issue.team_id != issue.team_id:
            team_query = select(model.Team).where(
                model.Team.id == updated_issue.team_id
            )
            team_result = await db.execute(team_query)
            team = team_result.scalars().first()

            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
                )

        # Fields to track for activity logging
        tracked_fields = ["status", "priority", "title", "assignee_id"]

        # Update issue data - ONLY process changed fields
        update_data = updated_issue.model_dump(exclude_unset=True)

        for key, new_value in update_data.items():
            old_value = getattr(issue, key)

            # Only update if value actually changed
            if old_value != new_value:
                # Create activity log for tracked fields
                if key in tracked_fields:
                    new_log = model.Activity(
                        issue_id=issue.id,
                        user_id=current_user.id,
                        attribute=key,
                        old_value=str(old_value) if old_value is not None else "None",
                        new_value=str(new_value) if new_value is not None else "None",
                    )
                    db.add(new_log)

                # Update the field
                setattr(issue, key, new_value)

        await db.commit()
        await db.refresh(issue)
        return issue

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        await db.rollback()
        raise
    except Exception as e:
        # Rollback on any other error
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update issue: {str(e)}",
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    try:
        # Check if issue exists and user is the owner
        query = select(model.Issue).where(
            model.Issue.id == id, model.Issue.creator_id == current_user.id
        )
        result = await db.execute(query)
        issue = result.scalars().first()

        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found or you are not the owner",
            )

        await db.delete(issue)
        await db.commit()
        return None

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        await db.rollback()
        raise
    except Exception as e:
        # Rollback on any other error
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete issue: {str(e)}",
        )

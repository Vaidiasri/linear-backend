from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from .. import schemas, model, oauth2
from app.permission import check_permission
from ..lib.database import get_db
from ..services.issue import IssueService
from ..filters import IssueFilters
from app.connectionManager import connection_manager
from app.middleware.rate_limiter import limiter
import json

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.IssueOut)
@limiter.limit("30/minute")  # Limit issue creation
async def create_issue(
    request: Request,
    issue: schemas.IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Create a new issue.
    Delegates to IssueService.create
    """
    check_permission(current_user, "issue", "create")
    new_issue = await IssueService.create(db, issue_in=issue, current_user=current_user)

    # Broadcast notification
    if new_issue.team_id:
        await connection_manager.broadcast(
            new_issue.team_id,
            json.dumps(
                {
                    "event": "ISSUE_CREATED",
                    "issue_id": str(new_issue.id),
                    "title": new_issue.title,
                    "project_id": (
                        str(new_issue.project_id) if new_issue.project_id else None
                    ),
                }
            ),
        )

    return new_issue


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.IssueOut])
@limiter.limit("100/minute")  # Generous for reads
async def get_all_issues(
    request: Request,
    filters: IssueFilters = Depends(),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Retrieve a list of issues with optional filtering and pagination.
    Delegates to IssueService.get_all
    """
    return await IssueService.get_all(
        db, filters=filters, skip=skip, limit=limit, current_user=current_user
    )


@router.get("/export", status_code=status.HTTP_200_OK)
async def export_issues(
    filters: IssueFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Export filtered issues to a CSV file.
    Delegates to IssueService.export_csv
    """
    return await IssueService.export_csv(db, filters=filters, current_user=current_user)


@router.get(
    "/search", status_code=status.HTTP_200_OK, response_model=list[schemas.IssueOut]
)
@limiter.limit("50/minute")  # Moderate limit for search
async def search_issues(
    request: Request,
    q: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Global search for issues.
    Delegates to IssueService.search
    """
    return await IssueService.search(db, q=q, skip=skip, limit=limit)


@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.IssueDetailOut
)
async def get_issue_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Get detailed information about a specific issue.
    Delegates to IssueService.get
    """
    issue = await IssueService.get(db, id=id, current_user=current_user)
    check_permission(current_user, "issue", "read", resource=issue)
    return issue


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.IssueOut)
async def update_issue(
    id: UUID,
    updated_issue: schemas.IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Update an existing issue.
    Delegates to IssueService.update
    """
    # Fetch first to check permission
    issue = await IssueService.get(db, id=id, current_user=current_user)
    check_permission(current_user, "issue", "update", resource=issue)

    updated = await IssueService.update(
        db, id=id, issue_in=updated_issue, current_user=current_user
    )

    # Broadcast notification
    if updated.team_id:
        await connection_manager.broadcast(
            updated.team_id,
            json.dumps(
                {
                    "event": "ISSUE_UPDATED",
                    "issue_id": str(updated.id),
                    "title": updated.title,
                }
            ),
        )

    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Delete an issue.
    Delegates to IssueService.delete
    """
    # Fetch first to check permission
    issue = await IssueService.get(db, id=id, current_user=current_user)
    check_permission(current_user, "issue", "delete", resource=issue)

    await IssueService.delete(db, id=id, current_user=current_user)

    # Broadcast notification
    if issue.team_id:
        await connection_manager.broadcast(
            issue.team_id,
            json.dumps(
                {
                    "event": "ISSUE_DELETED",
                    "issue_id": str(issue.id),
                    "title": issue.title,
                }
            ),
        )

    return None


@router.get("/stats", response_model=schemas.IssueStats)
async def get_issue_stats(
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Get aggregated statistics.
    Delegates to IssueService.get_stats
    """
    return await IssueService.get_stats(db, current_user=current_user)

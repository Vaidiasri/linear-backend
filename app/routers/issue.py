from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from .. import schemas, model, oauth2
from ..lib.database import get_db
from ..services.issue import IssueService
from ..filters import IssueFilters

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.IssueOut)
async def create_issue(
    issue: schemas.IssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Create a new issue.
    Delegates to IssueService.create
    """
    return await IssueService.create(db, issue_in=issue, current_user=current_user)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.IssueOut])
async def get_all_issues(
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
async def search_issues(
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
    return await IssueService.get(db, id=id, current_user=current_user)


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
    return await IssueService.update(
        db, id=id, issue_in=updated_issue, current_user=current_user
    )


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
    await IssueService.delete(db, id=id, current_user=current_user)
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

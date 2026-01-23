from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .. import model, oauth2
from ..lib.database import get_db
from ..model.issue import Issue
from ..schemas.dashboard import DashboardOut
from ..schemas.issue import IssueStatus
from ..crud.issue import issue

# api router for dashboard
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardOut)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    # get stats from crud
    stats = await issue.get_stats(db)

    # Extract data safely
    total_count = stats.get("total_count", 0)
    status_counts = stats.get("status_counts", {})
    priority_counts = stats.get("priority_counts", {})

    # Calculate completed issues safely using Enum
    completed_issues = status_counts.get(IssueStatus.DONE.value, 0)

    # Linear calculation (Complexity 1)
    progress_percentage = (
        (completed_issues / total_count * 100) if total_count > 0 else 0.0
    )

    return DashboardOut(
        status_counts=status_counts,
        priority_counts=priority_counts,
        total_issues=total_count,
        completed_issues=completed_issues,
        progress_percentage=round(progress_percentage, 2),
    )

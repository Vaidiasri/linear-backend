from pydantic import BaseModel

class DashboardOut(BaseModel):
    status_counts: dict[str, int] # e.g. {"backlog": 10, "todo": 20, "in_progress": 30, "done": 40, "canceled": 50}
    priority_counts: dict[str, int] # e.g. {"low": 10, "medium": 20, "high": 30, "critical": 40}
    # total issues and completed issues
    total_issues: int
    completed_issues: int
    progress_percentage: float
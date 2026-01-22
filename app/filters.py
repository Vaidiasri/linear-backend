from typing import Optional
from uuid import UUID
from fastapi import Query


class IssueFilters:
    def __init__(
        self,
        status_filter: Optional[str] = Query(None, alias="status"),
        priority: Optional[int] = Query(None),
        team_id: Optional[UUID] = Query(None),
        project_id: Optional[UUID] = Query(None),
        assignee_id: Optional[UUID] = Query(None),
        search: Optional[str] = Query(None),
    ):
        self.status = status_filter
        self.priority = priority
        self.team_id = team_id
        self.project_id = project_id
        self.assignee_id = assignee_id
        self.search = search

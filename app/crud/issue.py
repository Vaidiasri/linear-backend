from typing import List, Optional
from uuid import UUID
import asyncio

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.model.issue import Issue
from app.model.comment import Comment
from app.model.activity import Activity
from app.schemas.issue import (
    IssueCreate,
    IssueCreate as IssueUpdate,
)  # Reuse schema for now


from app.model.team import Team


class CRUDIssue(CRUDBase[Issue, IssueCreate, IssueUpdate]):
    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        creator_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        team_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> List[Issue]:
        query = select(self.model)
        if creator_id:
            query = query.where(self.model.creator_id == creator_id)

        if status:
            query = query.where(self.model.status == status)
        if priority is not None:
            query = query.where(self.model.priority == priority)
        if team_id:
            query = query.where(self.model.team_id == team_id)
        if project_id:
            query = query.where(self.model.project_id == project_id)
        if assignee_id:
            query = query.where(self.model.assignee_id == assignee_id)
        if search:
            query = query.where(self.model.title.ilike(f"%{search}%"))

        query = query.options(
            selectinload(self.model.assignee),
            selectinload(self.model.team).selectinload(Team.projects),
        )

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_relations(
        self, db: AsyncSession, *, id: UUID, creator_id: Optional[UUID] = None
    ) -> Optional[Issue]:
        query = select(self.model).where(self.model.id == id)
        if creator_id:
            query = query.where(self.model.creator_id == creator_id)

        query = query.options(
            selectinload(self.model.comments).selectinload(Comment.author),
            selectinload(self.model.activities).selectinload(Activity.user),
            selectinload(self.model.assignee),
            selectinload(self.model.team).selectinload(Team.projects),
        )

        result = await db.execute(query)
        return result.scalars().first()

    async def get_all_for_export(
        self,
        db: AsyncSession,
        *,
        creator_id: Optional[UUID] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        team_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> List[Issue]:
        query = select(self.model)
        if creator_id:
            query = query.where(self.model.creator_id == creator_id)

        query = query.options(
            selectinload(self.model.assignee),
            selectinload(self.model.project),
            selectinload(self.model.team),
        )

        if status:
            query = query.where(self.model.status == status)
        if priority is not None:
            query = query.where(self.model.priority == priority)
        if team_id:
            query = query.where(self.model.team_id == team_id)
        if project_id:
            query = query.where(self.model.project_id == project_id)
        if assignee_id:
            query = query.where(self.model.assignee_id == assignee_id)
        if search:
            query = query.where(self.model.title.ilike(f"%{search}%"))

        result = await db.execute(query)
        return result.scalars().all()

    async def search_global(
        self, db: AsyncSession, *, q: str, skip: int = 0, limit: int = 100
    ) -> List[Issue]:
        if not q:
            return []
        query = (
            select(self.model)
            .where(
                or_(
                    self.model.title.ilike(f"%{q}%"),
                    self.model.description.ilike(f"%{q}%"),
                )
            )
            .options(
                selectinload(self.model.assignee),
                selectinload(self.model.team).selectinload(Team.projects),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_stats(
        self, db: AsyncSession, *, creator_id: Optional[UUID] = None
    ) -> dict:
        total_query = select(func.count(self.model.id))

        status_query = select(self.model.status, func.count(self.model.id)).group_by(
            self.model.status
        )

        priority_query = select(
            self.model.priority, func.count(self.model.id)
        ).group_by(self.model.priority)

        if creator_id:
            total_query = total_query.where(self.model.creator_id == creator_id)
            status_query = status_query.where(self.model.creator_id == creator_id)
            priority_query = priority_query.where(self.model.creator_id == creator_id)

        # Execute queries sequentially to avoid SQLAlchemy async session concurrency issues
        total_result = await db.execute(total_query)
        status_result = await db.execute(status_query)
        priority_result = await db.execute(priority_query)

        total_count = total_result.scalar() or 0
        status_counts = {row[0]: row[1] for row in status_result.all()}
        priority_counts = {str(row[0]): row[1] for row in priority_result.all()}

        return {
            "total_count": total_count,
            "status_counts": status_counts,
            "priority_counts": priority_counts,
        }


issue = CRUDIssue(Issue)

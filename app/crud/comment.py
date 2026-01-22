from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.model.comment import Comment
from app.schemas.comment import CommentCreate, CommentCreate as CommentUpdate


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    async def get_multi_by_issue(
        self, db: AsyncSession, *, issue_id: UUID
    ) -> List[Comment]:
        query = (
            select(self.model)
            .options(selectinload(self.model.author))
            .where(self.model.issue_id == issue_id)
            .order_by(self.model.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_author(self, db: AsyncSession, *, id: UUID) -> Comment | None:
        query = (
            select(self.model)
            .options(selectinload(self.model.author))
            .where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()


comment = CRUDComment(Comment)

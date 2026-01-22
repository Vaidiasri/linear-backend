from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.model.attached import Attachment
from app.schemas.attached import AttachmentUpdate


class CRUDAttachment(CRUDBase[Attachment, None, AttachmentUpdate]):
    async def get_multi_by_issue(
        self, db: AsyncSession, *, issue_id: UUID
    ) -> List[Attachment]:
        query = select(self.model).where(self.model.issue_id == issue_id)
        result = await db.execute(query)
        return result.scalars().all()


attachment = CRUDAttachment(Attachment)

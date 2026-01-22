from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.model.team import Team
from app.schemas.team import TeamCreate, TeamCreate as TeamUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    async def get_by_key(self, db: AsyncSession, *, key: str) -> Optional[Team]:
        query = select(self.model).where(self.model.key == key)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Team]:
        query = (
            select(self.model)
            .options(selectinload(self.model.projects))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get(self, db: AsyncSession, id: Any) -> Optional[Team]:
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.projects))
        )
        result = await db.execute(query)
        return result.scalars().first()


team = CRUDTeam(Team)

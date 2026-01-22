from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.model.team import Team
from app.schemas.team import TeamCreate, TeamCreate as TeamUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    async def get_by_key(self, db: AsyncSession, *, key: str) -> Optional[Team]:
        query = select(self.model).where(self.model.key == key)
        result = await db.execute(query)
        return result.scalars().first()


team = CRUDTeam(Team)

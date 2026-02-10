from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from ..model.cycle import Cycle
from ..schemas.cycle import CycleCreate, CycleUpdate


class CRUDCycle(CRUDBase[Cycle, CycleCreate, CycleUpdate]):
    async def get_multi_by_team(
        self, db: AsyncSession, *, team_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Cycle]:
        result = await db.execute(
            select(self.model)
            .where(self.model.team_id == team_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CycleCreate) -> Cycle:
        # Override to use model_dump() instead of jsonable_encoder
        # This preserves datetime objects which asyncpg requires
        db_obj = Cycle(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


cycle = CRUDCycle(Cycle)

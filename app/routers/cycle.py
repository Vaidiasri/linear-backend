from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.lib.database import get_db

router = APIRouter(prefix="/cycles", tags=["Cycles"])


@router.get("/", response_model=List[schemas.CycleOut])
async def read_cycles(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    team_id: Optional[UUID] = None,
):
    if team_id:
        cycles = await crud.cycle.get_multi_by_team(
            db, team_id=team_id, skip=skip, limit=limit
        )
    else:
        cycles = await crud.cycle.get_multi(db, skip=skip, limit=limit)
    return cycles


@router.post("/", response_model=schemas.CycleOut)
async def create_cycle(
    cycle_in: schemas.CycleCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.cycle.create(db, obj_in=cycle_in)


@router.get("/{cycle_id}", response_model=schemas.CycleOut)
async def read_cycle(
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    cycle = await crud.cycle.get(db, id=cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return cycle


@router.patch("/{cycle_id}", response_model=schemas.CycleOut)
async def update_cycle(
    cycle_id: UUID,
    cycle_in: schemas.CycleUpdate,
    db: AsyncSession = Depends(get_db),
):
    cycle = await crud.cycle.get(db, id=cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return await crud.cycle.update(db, db_obj=cycle, obj_in=cycle_in)


@router.delete("/{cycle_id}", response_model=schemas.CycleOut)
async def delete_cycle(
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    cycle = await crud.cycle.get(db, id=cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return await crud.cycle.remove(db, id=cycle_id)

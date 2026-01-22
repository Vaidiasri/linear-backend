from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.model.user import UserRole
from .. import schemas, model, oauth2
from ..lib.database import get_db
from ..services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService.create(db, user_in=user)


@router.put("/{user_id}/role", response_model=schemas.UserOut)
async def update_user_role(
    user_id: UUID,
    data: schemas.UserUpdateRole,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can assign roles"
        )

    return await UserService.update_role(
        db, user_id=user_id, role=data.role, team_id=data.team_id
    )

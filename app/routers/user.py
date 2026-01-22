from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import shutil
import os
from app.model.user import UserRole
from .. import schemas, model, oauth2
from ..lib.database import get_db
from ..services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])

UPLOAD_DIR = "static/avatars"


@router.get("/me", response_model=schemas.UserOut)
async def get_my_profile(current_user: model.User = Depends(oauth2.get_current_user)):
    return current_user


@router.post("/me/avatar", response_model=schemas.UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # Ensure directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Create file path: static/avatars/user_id_filename
    # Sanitize filename to avoid directory traversal
    filename = f"{current_user.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update User Profile
    # Storing relative path, assuming frontend prepends API base URL or backend serves it
    # Using forward slashes for URL compatibility
    avatar_url = f"/static/avatars/{filename}"

    current_user.avatar_url = avatar_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return current_user


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

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import shutil
import os
from app.model.user import UserRole
from .. import schemas, model, oauth2
from ..lib.database import get_db
from ..services.user import UserService
from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/public_debug")
async def public_debug():
    return {"message": "debug ok"}


UPLOAD_DIR = "static/avatars"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB


@router.get("/", response_model=list[schemas.UserOut])
# @limiter.limit("100/minute")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await UserService.get_all(db, skip=skip, limit=limit)


@router.get("/verify_this")
async def verify_this():
    return {"status": "live"}


@router.get("/ping")
async def ping():
    return {"message": "pong"}


@router.get("/me", response_model=schemas.UserOut)
# @limiter.limit("100/minute")  # Generous for profile reads
async def get_my_profile(
    request: Request, current_user: model.User = Depends(oauth2.get_current_user)
):
    return current_user


@router.post("/me/avatar", response_model=schemas.UserOut)
# @limiter.limit("30/minute")  # Limit avatar uploads
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # 1. Validate File Extension & Content Type
    filename_lower = file.filename.lower() if file.filename else ""
    extension = filename_lower.split(".")[-1] if "." in filename_lower else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
        )

    # Ensure directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Create file path: static/avatars/user_id_filename
    # Sanitize filename to avoid directory traversal (using just the basename logic mostly covered by split above, but let's be safe)
    safe_filename = os.path.basename(file.filename)
    # prepend user id to ensure uniqueness and simple sanitization
    final_filename = f"{current_user.id}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, final_filename)

    # 2. Stream & Validate Size
    file_size = 0

    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # Read 1MB chunks
                file_size += len(chunk)
                if file_size > MAX_AVATAR_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File too large. Maximum size allowed is {MAX_AVATAR_SIZE // (1024 * 1024)}MB",
                    )
                buffer.write(chunk)

    except HTTPException:
        # Cleanup partial file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        # Cleanup on any other error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # Update User Profile
    # Storing relative path, assuming frontend prepends API base URL or backend serves it
    # Using forward slashes for URL compatibility
    avatar_url = f"/static/avatars/{final_filename}"

    current_user.avatar_url = avatar_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
# @limiter.limit("10/minute")  # Limit user creation to prevent spam
async def create_user(
    request: Request, user: schemas.UserCreate, db: AsyncSession = Depends(get_db)
):
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Delete a user.
    """
    # Optional: Check if admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can delete users",
        )

    # Prevent self-deletion?
    # if current_user.id == id:
    #     raise HTTPException(status_code=400, detail="Cannot delete your own account")

    await UserService.delete(db, user_id=id)
    return None

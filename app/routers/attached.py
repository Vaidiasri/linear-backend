from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from ..lib.database import get_db
from ..model.attached import Attachment
from ..model.issue import Issue
from ..schemas.attached import AttachmentOut
from .. import oauth2
import shutil
import os
import uuid
import asyncio

# Router Configuration
router = APIRouter(
    prefix="/attachments",  # Is file ke saare URLs '/attachments' se shuru honge
    tags=["Attachments"],  # Swagger UI or Docs mein 'Attachments' section mein dikhega
)


# post  api
@router.post("/{issue_id}", response_model=AttachmentOut)
async def create_attachment(
    issue_id: uuid.UUID,
    file: UploadFile = File(...),  # Asli file yahan aayegi
    db: AsyncSession = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    # 0. Validate Issue Exists
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
        )

    # 1. Folder Check (Tera logic sahi tha)
    upload_dir = "static/uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # 2. Unique Filename
    # Validate extension (Basic security)
    allowed_extensions = {".png", ".jpg", ".jpeg", ".pdf", ".txt", ".docx"}
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {allowed_extensions}",
        )

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)

    # 3. Save File (Async friendly way using threads)
    # Blocking I/O ko thread mein run karenge taaki event loop block na ho
    def save_file_to_disk():
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    await asyncio.to_thread(save_file_to_disk)

    # 4. Database Entry
    new_attachment = Attachment(
        file_name=file.filename,
        file_path=file_path,
        issue_id=issue_id,  # Kis ticket ka hai
        uploader_id=current_user.id,  # Kisne upload kiya
    )

    db.add(new_attachment)
    await db.commit()
    await db.refresh(new_attachment)

    return new_attachment

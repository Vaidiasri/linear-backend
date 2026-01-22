import asyncio
import logging
import os
import shutil
import uuid
from typing import List
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, model
from app.schemas.attached import AttachmentUpdate

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttachmentService:
    UPLOAD_DIR = "static/uploads"
    ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf", ".txt", ".docx"}

    @staticmethod
    async def create(
        db: AsyncSession,
        issue_id: uuid.UUID,
        file: UploadFile,
        current_user: model.User,
    ) -> model.Attachment:
        # 0. Validate Issue Exists
        issue = await crud.issue.get(db, id=issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
            )

        # 1. Folder Check
        if not os.path.exists(AttachmentService.UPLOAD_DIR):
            os.makedirs(AttachmentService.UPLOAD_DIR)

        # 2. Unique Filename & Extension Validation
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in AttachmentService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {AttachmentService.ALLOWED_EXTENSIONS}",
            )

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(AttachmentService.UPLOAD_DIR, unique_filename)

        # 3. Save File (Async friendly way using threads)
        def save_file_to_disk():
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        await asyncio.to_thread(save_file_to_disk)

        # 4. Database Entry
        # Since we don't have a standard Pydantic Create schema matching exactly (due to file handling),
        # we create the object manually.
        new_attachment = model.Attachment(
            file_name=file.filename,
            file_path=file_path,
            issue_id=issue_id,
            uploader_id=current_user.id,
        )

        db.add(new_attachment)
        await db.commit()
        await db.refresh(new_attachment)

        return new_attachment

    @staticmethod
    async def get_by_issue(
        db: AsyncSession, issue_id: uuid.UUID
    ) -> List[model.Attachment]:
        return await crud.attachment.get_multi_by_issue(db, issue_id=issue_id)

    @staticmethod
    async def get(db: AsyncSession, attachment_id: uuid.UUID) -> model.Attachment:
        attachment = await crud.attachment.get(db, id=attachment_id)
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
            )
        return attachment

    @staticmethod
    async def update(
        db: AsyncSession,
        attachment_id: uuid.UUID,
        updated_attachment: AttachmentUpdate,
        current_user: model.User,
    ) -> model.Attachment:
        attachment = await AttachmentService.get(db, attachment_id)

        if attachment.uploader_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this attachment",
            )

        return await crud.attachment.update(
            db, db_obj=attachment, obj_in=updated_attachment
        )

    @staticmethod
    async def delete(
        db: AsyncSession, attachment_id: uuid.UUID, current_user: model.User
    ) -> None:
        attachment = await AttachmentService.get(db, attachment_id)

        # Authorization
        if attachment.uploader_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this attachment",
            )

        # 1. Delete file from disk
        if os.path.exists(attachment.file_path):
            try:
                await asyncio.to_thread(os.remove, attachment.file_path)
            except OSError as e:
                logger.error(f"Error deleting file: {e}")

        # 2. Delete entry from DB
        await crud.attachment.remove(db, id=attachment_id)

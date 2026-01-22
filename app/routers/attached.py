import uuid
from typing import List
from fastapi import APIRouter, status, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from ..lib.database import get_db
from ..schemas.attached import AttachmentOut, AttachmentUpdate
from .. import model, oauth2
from ..services.attached import AttachmentService

router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)


@router.post("/{issue_id}", response_model=AttachmentOut)
async def create_attachment(
    issue_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await AttachmentService.create(
        db, issue_id=issue_id, file=file, current_user=current_user
    )


@router.get("/issue/{issue_id}", response_model=List[AttachmentOut])
async def get_attachments_by_issue(
    issue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await AttachmentService.get_by_issue(db, issue_id=issue_id)


@router.get("/{attachment_id}", response_model=AttachmentOut)
async def get_attachment(
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await AttachmentService.get(db, attachment_id=attachment_id)


@router.put("/{attachment_id}", response_model=AttachmentOut)
async def update_attachment(
    attachment_id: uuid.UUID,
    updated_attachment: AttachmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await AttachmentService.update(
        db,
        attachment_id=attachment_id,
        updated_attachment=updated_attachment,
        current_user=current_user,
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    await AttachmentService.delete(
        db, attachment_id=attachment_id, current_user=current_user
    )
    return None

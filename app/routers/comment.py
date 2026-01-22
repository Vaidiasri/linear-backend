from uuid import UUID
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, model, oauth2
from ..lib.database import get_db
from ..services.comment import CommentService

router = APIRouter(prefix="/issues/{issue_id}/comments", tags=["Comments"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.CommentOut
)
async def create_comment(
    issue_id: UUID,
    comment: schemas.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await CommentService.create(
        db, issue_id=issue_id, comment_in=comment, current_user=current_user
    )


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[schemas.CommentOut]
)
async def get_all_comments(
    issue_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await CommentService.get_all_by_issue(db, issue_id=issue_id)


@router.get(
    "/{comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.CommentOut,
)
async def get_comment_by_id(
    issue_id: UUID,
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await CommentService.get(db, id=comment_id, issue_id=issue_id)


@router.put(
    "/{comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.CommentOut,
)
async def update_comment(
    issue_id: UUID,
    comment_id: UUID,
    updated_comment: schemas.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    return await CommentService.update(
        db,
        issue_id=issue_id,
        comment_id=comment_id,
        comment_in=updated_comment,
        current_user=current_user,
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    issue_id: UUID,
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    await CommentService.delete(
        db, issue_id=issue_id, comment_id=comment_id, current_user=current_user
    )
    return None

from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, model
from app.schemas.comment import CommentCreate, CommentCreate as CommentUpdate


class CommentService:
    @staticmethod
    async def get_all_by_issue(db: AsyncSession, issue_id: UUID) -> List[model.Comment]:
        # Validate issue exists
        issue = await crud.issue.get(db, id=issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
            )
        return await crud.comment.get_multi_by_issue(db, issue_id=issue_id)

    @staticmethod
    async def get(db: AsyncSession, id: UUID, issue_id: UUID) -> model.Comment:
        comment = await crud.comment.get_with_author(db, id=id)
        if not comment or comment.issue_id != issue_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found for this issue",
            )
        return comment

    @staticmethod
    async def create(
        db: AsyncSession,
        issue_id: UUID,
        comment_in: CommentCreate,
        current_user: model.User,
    ) -> model.Comment:
        # 1. Check if issue exists
        issue = await crud.issue.get(db, id=issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
            )

        # 2. Create new comment
        # Note: We can't use CRUDBase.create directly easily because we need to set issue_id and author_id
        # So we manually create object or extend CRUD create
        # Let's do it manually here or prepare clean dict for CRUD

        # Better approach: Create object manually to ensure IDs are set correctly
        new_comment = model.Comment(
            content=comment_in.content, issue_id=issue_id, author_id=current_user.id
        )
        db.add(new_comment)

        # 3. Add Activity Log
        comment_log = model.Activity(
            issue_id=issue_id,
            user_id=current_user.id,
            attribute="comment",
            old_value=None,
            new_value="New comment added",
        )
        db.add(comment_log)

        await db.commit()
        await db.refresh(new_comment)

        # Fetch with author for response
        return await crud.comment.get_with_author(db, id=new_comment.id)

    @staticmethod
    async def update(
        db: AsyncSession,
        issue_id: UUID,
        comment_id: UUID,
        comment_in: CommentUpdate,
        current_user: model.User,
    ) -> model.Comment:
        comment = await CommentService.get(db, id=comment_id, issue_id=issue_id)

        # Authorization
        if comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this comment",
            )

        return await crud.comment.update(db, db_obj=comment, obj_in=comment_in)

    @staticmethod
    async def delete(
        db: AsyncSession,
        issue_id: UUID,
        comment_id: UUID,
        current_user: model.User,
    ) -> None:
        comment = await CommentService.get(db, id=comment_id, issue_id=issue_id)

        # Authorization
        if comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment",
            )

        await crud.comment.remove(db, id=comment_id)

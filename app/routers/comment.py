from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from .. import schemas, model, oauth2
from ..lib.database import get_db

router = APIRouter(prefix="/issues/{issue_id}/comments", tags=["Comments"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.CommentOut)
async def create_comment(
    issue_id: UUID,
    comment: schemas.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    # 1. Check if issue exists (Tera logic perfect hai)
    issue_query = select(model.Issue).where(model.Issue.id == issue_id)
    issue_result = await db.execute(issue_query)
    issue = issue_result.scalars().first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # 2. Create new comment
    new_comment = model.Comment(
        content=comment.content, issue_id=issue_id, author_id=current_user.id
    )
    db.add(new_comment)

    # --- NAYA PART: Activity Log add karo ---
    comment_log = model.Activity(
        issue_id=issue_id,
        user_id=current_user.id,
        attribute="comment",
        old_value=None,
        new_value=f"New comment added" # Ya fir: comment.content[:50]...
    )
    db.add(comment_log)
    # ---------------------------------------

    await db.commit()
    await db.refresh(new_comment)

    # 3. Load author for response (Tera logic perfect hai)
    comment_query = (
        select(model.Comment)
        .options(selectinload(model.Comment.author))
        .where(model.Comment.id == new_comment.id)
    )
    result = await db.execute(comment_query)
    return result.scalars().first()

@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[schemas.CommentOut]
)
async def get_all_comments(
    issue_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Ek specific issue ke saare comments fetch karo
    - Author details ke saath (nested UserOut)
    """
    # 1. Check if issue exists
    issue_query = select(model.Issue).where(model.Issue.id == issue_id)
    issue_result = await db.execute(issue_query)
    issue = issue_result.scalars().first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
        )

    # 2. Get all comments for this issue with author details
    comments_query = (
        select(model.Comment)
        .options(selectinload(model.Comment.author))
        .where(model.Comment.issue_id == issue_id)
        .order_by(model.Comment.created_at.desc())  # Latest comments pehle
    )
    result = await db.execute(comments_query)
    comments = result.scalars().all()

    return comments


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
    """
    Ek specific comment fetch karo by ID
    """
    # Check if comment exists and belongs to the specified issue
    comment_query = (
        select(model.Comment)
        .options(selectinload(model.Comment.author))
        .where(model.Comment.id == comment_id, model.Comment.issue_id == issue_id)
    )
    result = await db.execute(comment_query)
    comment = result.scalars().first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found for this issue",
        )

    return comment


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
    """
    Comment update karo
    - Sirf comment ka author hi update kar sakta hai
    """
    # Check if comment exists, belongs to issue, and user is the author
    comment_query = select(model.Comment).where(
        model.Comment.id == comment_id,
        model.Comment.issue_id == issue_id,
        model.Comment.author_id == current_user.id,
    )
    result = await db.execute(comment_query)
    comment = result.scalars().first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you are not the author",
        )

    # Update comment content
    comment.content = updated_comment.content

    await db.commit()
    await db.refresh(comment)

    # Load author relationship for response
    comment_query = (
        select(model.Comment)
        .options(selectinload(model.Comment.author))
        .where(model.Comment.id == comment.id)
    )
    result = await db.execute(comment_query)
    comment_with_author = result.scalars().first()

    return comment_with_author


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    issue_id: UUID,
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    """
    Comment delete karo
    - Sirf comment ka author hi delete kar sakta hai
    """
    # Check if comment exists, belongs to issue, and user is the author
    comment_query = select(model.Comment).where(
        model.Comment.id == comment_id,
        model.Comment.issue_id == issue_id,
        model.Comment.author_id == current_user.id,
    )
    result = await db.execute(comment_query)
    comment = result.scalars().first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not delete kar sakta hai",
        )

    await db.delete(comment)
    await db.commit()
    return None

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.lib.database import get_db
from app.model.notification import Notification
from app.schemas.notification import NotificationResponse
from app.oauth2 import get_current_user
from app.model.user import User

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get all notifications for the current user.
    Ordered by most recent first.
    """
    query = (
        select(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    result = await db.execute(query)
    notifications = result.scalars().all()
    return notifications

@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a specific notification as read.
    """
    query = (
        select(Notification)
        .filter(
            Notification.id == notification_id, Notification.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    notification = result.scalars().first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    notification.read = True
    await db.commit()
    await db.refresh(notification)
    return notification

@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Mark all unread notifications as read for the current user.
    """
    query = (
        select(Notification)
        .filter(Notification.user_id == current_user.id, Notification.read == False)
    )
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    for notification in notifications:
        notification.read = True
        
    await db.commit()
    return None

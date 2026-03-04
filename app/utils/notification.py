from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.model.notification import Notification

async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    message: str,
    type: str,
    issue_id: UUID = None
) -> Notification:
    """
    Utility function to create an in-app notification.
    
    Args:
        db: Database session
        user_id: The ID of the user receiving the notification
        title: Notification title
        message: Notification descriptive message
        type: Type of notification (issue_assigned, issue_status_changed, comment_created)
        issue_id: (Optional) The related issue ID
        
    Returns:
        The created Notification object
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        issue_id=issue_id
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification

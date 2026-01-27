"""
Example usage of Celery email tasks in FastAPI routes
All functions refactored to Complexity 1
"""

from fastapi import APIRouter, HTTPException
from app.workers.email_tasks import (
    send_email_task,
    send_welcome_email,
    send_password_reset_email,
    send_bulk_emails,
    send_issue_notification,
)
from celery.result import AsyncResult

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS - Complexity 1 each
# ============================================================================

# Task state messages - data-driven approach
TASK_STATE_MESSAGES = {
    "PENDING": "Task is waiting to be executed",
    "STARTED": "Task is currently running",
    "SUCCESS": "Task completed successfully",
    "FAILURE": "Task failed",
}


def _build_task_response(task_id: str, task: AsyncResult) -> dict:
    """
    Build task status response
    Complexity: 1 (early returns, no nesting)
    """
    base_response = {
        "task_id": task_id,
        "status": task.state.lower(),
        "message": TASK_STATE_MESSAGES.get(task.state, "Unknown state"),
    }

    # Early return for SUCCESS
    if task.state == "SUCCESS":
        base_response["result"] = task.result
        return base_response

    # Early return for FAILURE
    if task.state == "FAILURE":
        base_response["error"] = str(task.info)
        return base_response

    # Default return
    return base_response


# ============================================================================
# API ENDPOINTS - Complexity 1 each
# ============================================================================


@router.post("/auth/signup")
async def signup(email: str, username: str):
    """
    User signup endpoint - sends welcome email in background
    Complexity: 1 (linear flow)
    """
    # ... your user creation logic here ...

    # Queue welcome email (non-blocking)
    task = send_welcome_email.delay(email, username)

    return {
        "message": "User created successfully",
        "email_task_id": task.id,
        "status": "Welcome email queued",
    }


@router.post("/auth/forgot-password")
async def forgot_password(email: str):
    """
    Forgot password endpoint - sends reset email
    Complexity: 1 (linear flow)
    """
    # ... generate reset token ...
    reset_token = "your_generated_token_here"

    # Queue password reset email
    task = send_password_reset_email.delay(email, reset_token)

    return {"message": "Password reset email sent", "task_id": task.id}


@router.post("/admin/send-announcement")
async def send_announcement(subject: str, body: str):
    """
    Admin endpoint - send announcement to all users
    Complexity: 1 (linear flow)
    """
    # ... fetch all user emails from database ...
    # Example:
    # from app.database import get_db
    # users = db.query(User).all()
    # user_emails = [user.email for user in users]

    user_emails = ["user1@example.com", "user2@example.com"]

    # Queue bulk emails
    result = send_bulk_emails.delay(user_emails, subject, body)

    return {
        "message": f"Queued emails for {len(user_emails)} users",
        "task_id": result.id,
    }


@router.post("/issues/{issue_id}/notify")
async def notify_issue_assignee(issue_id: int, assignee_email: str):
    """
    Send notification when issue is assigned
    Complexity: 1 (linear flow)
    """
    # ... fetch issue details from database ...
    issue_title = "Fix login bug"
    actor = "John Doe"

    # Queue notification email
    task = send_issue_notification.delay(assignee_email, issue_title, "assigned", actor)

    return {"message": "Notification sent", "task_id": task.id}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Check status of a background task
    Complexity: 1 (delegated to helper)
    """
    task = AsyncResult(task_id)
    return _build_task_response(task_id, task)


@router.post("/test/send-email")
async def test_send_email(email: str, subject: str, body: str):
    """
    Test endpoint to send a simple email
    Complexity: 1 (linear flow)
    """
    task = send_email_task.delay(email, subject, body)
    return {"message": "Email queued", "task_id": task.id}

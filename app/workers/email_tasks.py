from celery import Task
from app.workers.celery_app import celery_app
from app.workers.email_templates import EmailTemplate
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.utils.email import conf
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS - Complexity 1 each
# ============================================================================


def _run_async_in_sync(coro):
    """
    Run async coroutine in sync context (Celery worker)
    Complexity: 1 (linear flow with finally)
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _is_valid_email(email: str) -> bool:
    """
    Validate email format
    Complexity: 1 (early return pattern)
    """
    from email_validator import validate_email, EmailNotValidError

    try:
        # Allow test/example domains for development
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def _create_email_message(email: str, subject: str, body: str) -> MessageSchema:
    """
    Create email message schema
    Complexity: 1 (single return)
    """
    return MessageSchema(
        subject=subject, recipients=[email], body=body, subtype=MessageType.html
    )


# ============================================================================
# BASE TASK CLASS
# ============================================================================


class EmailTask(Task):
    """Base task class with automatic retry logic"""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 5}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes max backoff
    retry_jitter = True


# ============================================================================
# CORE EMAIL TASKS - Complexity 1 each
# ============================================================================


@celery_app.task(base=EmailTask, name="send_email_task")
def send_email_task(email: str, subject: str, body: str):
    """
    Send email asynchronously via Celery worker
    Complexity: 1 (linear flow with early return)

    Args:
        email: Recipient email address
        subject: Email subject
        body: HTML email body

    Returns:
        dict: Status and email address
    """
    # Guard clause - early return for invalid email
    if not _is_valid_email(email):
        logger.error(f"❌ Invalid email: {email}")
        raise ValueError(f"Invalid email address: {email}")

    # Linear flow - no branching
    message = _create_email_message(email, subject, body)
    _run_async_in_sync(FastMail(conf).send_message(message))
    logger.info(f"✅ Email sent successfully to {email}")

    return {"status": "success", "email": email}


@celery_app.task(name="send_bulk_emails")
def send_bulk_emails(emails: list, subject: str, body: str):
    """
    Send bulk emails to multiple recipients
    Complexity: 1 (simple loop, no nesting)

    Args:
        emails: List of email addresses
        subject: Email subject
        body: HTML email body

    Returns:
        dict: Total count and task IDs
    """
    task_ids = []
    for email in emails:
        task = send_email_task.delay(email, subject, body)
        task_ids.append(task.id)
        logger.info(f"📧 Queued email for {email} - Task ID: {task.id}")

    return {"total": len(emails), "task_ids": task_ids}


# ============================================================================
# SPECIFIC EMAIL TASKS - Complexity 1 each
# ============================================================================


@celery_app.task(name="send_welcome_email")
def send_welcome_email(email: str, username: str):
    """
    Send welcome email to new users
    Complexity: 1 (linear delegation)
    """
    subject, body = EmailTemplate.welcome(username)
    return send_email_task(email, subject, body)


@celery_app.task(name="send_password_reset_email")
def send_password_reset_email(email: str, reset_token: str):
    """
    Send password reset email
    Complexity: 1 (linear delegation)
    """
    subject, body = EmailTemplate.password_reset(reset_token)
    return send_email_task(email, subject, body)


@celery_app.task(name="send_issue_notification")
def send_issue_notification(email: str, issue_title: str, action: str, actor: str):
    """
    Send notification when issue is created/updated
    Complexity: 1 (linear delegation)
    """
    subject, body = EmailTemplate.issue_notification(issue_title, action, actor)
    return send_email_task(email, subject, body)


# ============================================================================
# SCHEDULED TASKS - Complexity 1 each
# ============================================================================


@celery_app.task(name="daily_report_email")
def daily_report_email():
    """
    Scheduled task: Send daily reports
    Runs via Celery Beat at 9 AM daily
    Complexity: 1 (linear flow)
    """
    logger.info("📊 Generating daily reports...")

    # Generate report content
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject, body = EmailTemplate.daily_report(report_date)

    # Send to admin emails
    admin_emails = ["admin@example.com"]
    return send_bulk_emails(admin_emails, subject, body)


@celery_app.task(name="cleanup_logs")
def cleanup_logs():
    """
    Scheduled task: Cleanup old logs
    Runs via Celery Beat at 2 AM daily
    Complexity: 1 (linear flow)
    """
    logger.info("🧹 Cleaning up old logs...")

    # Your cleanup logic here
    # Example: Delete logs older than 30 days

    return {"status": "completed", "timestamp": str(datetime.now())}

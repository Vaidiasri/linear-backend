# Email Worker & Background Jobs Setup Guide 📧

Complete guide to implement email workers and background job processing in your FastAPI project.

---

## Table of Contents

1. [Overview](#overview)
2. [Option 1: Celery + Redis (Recommended)](#option-1-celery--redis-recommended)
3. [Option 2: ARQ (Async Alternative)](#option-2-arq-async-alternative)
4. [Option 3: FastAPI BackgroundTasks](#option-3-fastapi-backgroundtasks)
5. [Docker Setup](#docker-setup)
6. [Testing](#testing)
7. [Monitoring](#monitoring)

---

## Overview

### Why Use Background Workers?

- ✅ **Non-blocking**: API responds immediately, tasks run in background
- ✅ **Retry Logic**: Failed tasks automatically retry
- ✅ **Scalability**: Run multiple workers for high load
- ✅ **Scheduled Tasks**: Cron-like jobs (daily reports, cleanup, etc.)
- ✅ **Monitoring**: Track task status and failures

### Comparison

| Feature          | Celery      | ARQ | BackgroundTasks        |
| ---------------- | ----------- | --- | ---------------------- |
| Async Support    | ✅          | ✅  | ✅                     |
| Retry Mechanism  | ✅          | ✅  | ❌                     |
| Persistence      | ✅          | ✅  | ❌                     |
| Scheduled Tasks  | ✅          | ✅  | ❌                     |
| Monitoring UI    | ✅ (Flower) | ❌  | ❌                     |
| Complexity       | Medium      | Low | Very Low               |
| Production Ready | ✅          | ✅  | ⚠️ (Simple tasks only) |

---

## Option 1: Celery + Redis (Recommended)

### Step 1: Install Dependencies

```bash
pip install celery redis flower
```

Update `requirements.txt`:

```txt
# Background Jobs
celery==5.3.4
redis==5.0.1
flower==2.0.1
```

### Step 2: Create Project Structure

```
backend/
├── app/
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery configuration
│   │   └── email_tasks.py     # Email tasks
│   ├── utils/
│   │   └── email.py            # Existing email utilities
│   └── routers/
│       └── ...
```

### Step 3: Create Celery Configuration

Create `app/workers/__init__.py`:

```python
# Empty file to make it a package
```

Create `app/workers/celery_app.py`:

```python
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
celery_app = Celery(
    "linear_backend",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    task_acks_late=True,  # Acknowledge task after completion
    worker_prefetch_multiplier=1,  # One task at a time per worker
)

# Scheduled Tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "send-daily-report": {
        "task": "daily_report_email",
        "schedule": crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    "cleanup-old-logs": {
        "task": "cleanup_logs",
        "schedule": crontab(hour=2, minute=0),  # Every day at 2 AM
    },
}

# Auto-discover tasks from workers module
celery_app.autodiscover_tasks(["app.workers"])
```

### Step 4: Create Email Tasks

Create `app/workers/email_tasks.py`:

```python
from celery import Task
from app.workers.celery_app import celery_app
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.utils.email import conf
import logging
import asyncio

logger = logging.getLogger(__name__)


class EmailTask(Task):
    """Base task class with automatic retry logic"""
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 5}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes max backoff
    retry_jitter = True


@celery_app.task(base=EmailTask, name="send_email_task")
def send_email_task(email: str, subject: str, body: str):
    """
    Send email asynchronously via Celery worker

    Args:
        email: Recipient email address
        subject: Email subject
        body: HTML email body

    Returns:
        dict: Status and email address
    """
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype=MessageType.html
        )

        fm = FastMail(conf)

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(fm.send_message(message))
        loop.close()

        logger.info(f"✅ Email sent successfully to {email}")
        return {"status": "success", "email": email}

    except Exception as e:
        logger.error(f"❌ Failed to send email to {email}: {str(e)}")
        raise


@celery_app.task(name="send_bulk_emails")
def send_bulk_emails(emails: list, subject: str, body: str):
    """
    Send bulk emails to multiple recipients

    Args:
        emails: List of email addresses
        subject: Email subject
        body: HTML email body

    Returns:
        list: Task IDs for all queued emails
    """
    task_ids = []
    for email in emails:
        task = send_email_task.delay(email, subject, body)
        task_ids.append(task.id)
        logger.info(f"📧 Queued email for {email} - Task ID: {task.id}")

    return {"total": len(emails), "task_ids": task_ids}


@celery_app.task(name="send_welcome_email")
def send_welcome_email(email: str, username: str):
    """Send welcome email to new users"""
    subject = f"Welcome to Linear Backend, {username}! 🎉"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>Welcome {username}! 👋</h1>
            <p>Thanks for joining our platform.</p>
            <p>We're excited to have you on board!</p>
            <br>
            <p>Best regards,<br>The Team</p>
        </body>
    </html>
    """
    return send_email_task(email, subject, body)


@celery_app.task(name="send_password_reset_email")
def send_password_reset_email(email: str, reset_token: str):
    """Send password reset email"""
    reset_link = f"https://yourapp.com/reset-password?token={reset_token}"
    subject = "Password Reset Request 🔐"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Reset Password
            </a>
            <p style="margin-top: 20px; color: #666;">
                This link will expire in 1 hour.
            </p>
            <p style="color: #666;">
                If you didn't request this, please ignore this email.
            </p>
        </body>
    </html>
    """
    return send_email_task(email, subject, body)


@celery_app.task(name="daily_report_email")
def daily_report_email():
    """
    Scheduled task: Send daily reports
    Runs via Celery Beat at 9 AM daily
    """
    logger.info("📊 Generating daily reports...")

    # Your logic here:
    # 1. Fetch data from database
    # 2. Generate report
    # 3. Send to admin emails

    admin_emails = ["admin@example.com"]
    subject = "Daily Report - " + str(datetime.now().date())
    body = "<h1>Daily Report</h1><p>Report content here...</p>"

    return send_bulk_emails(admin_emails, subject, body)


@celery_app.task(name="cleanup_logs")
def cleanup_logs():
    """
    Scheduled task: Cleanup old logs
    Runs via Celery Beat at 2 AM daily
    """
    logger.info("🧹 Cleaning up old logs...")
    # Your cleanup logic here
    return {"status": "completed"}
```

### Step 5: Update Environment Variables

Add to `.env`:

```env
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Step 6: Use in FastAPI Routes

Update your routes to use Celery tasks:

```python
from fastapi import APIRouter, HTTPException
from app.workers.email_tasks import (
    send_email_task,
    send_welcome_email,
    send_password_reset_email,
    send_bulk_emails
)

router = APIRouter()


@router.post("/auth/signup")
async def signup(email: str, username: str):
    # ... user creation logic ...

    # Queue welcome email (non-blocking)
    task = send_welcome_email.delay(email, username)

    return {
        "message": "User created successfully",
        "email_task_id": task.id
    }


@router.post("/auth/forgot-password")
async def forgot_password(email: str):
    # ... generate reset token ...
    reset_token = "your_generated_token"

    # Queue password reset email
    task = send_password_reset_email.delay(email, reset_token)

    return {
        "message": "Password reset email sent",
        "task_id": task.id
    }


@router.post("/admin/send-announcement")
async def send_announcement(subject: str, body: str):
    # ... fetch all user emails from database ...
    user_emails = ["user1@example.com", "user2@example.com"]

    # Queue bulk emails
    result = send_bulk_emails.delay(user_emails, subject, body)

    return {
        "message": f"Queued emails for {len(user_emails)} users",
        "task_id": result.id
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Check status of a background task"""
    from celery.result import AsyncResult

    task = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

### Step 7: Run the Workers

Open **3 separate terminals**:

**Terminal 1 - FastAPI Server:**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

> **Note**: Use `--pool=solo` on Windows. On Linux/Mac, you can use default pool.

**Terminal 3 - Celery Beat (for scheduled tasks):**

```bash
cd backend
celery -A app.workers.celery_app beat --loglevel=info
```

**Terminal 4 (Optional) - Flower Monitoring UI:**

```bash
cd backend
celery -A app.workers.celery_app flower --port=5555
```

Then open: http://localhost:5555

---

## Option 2: ARQ (Async Alternative)

### Step 1: Install ARQ

```bash
pip install arq
```

### Step 2: Create ARQ Worker

Create `app/workers/arq_worker.py`:

```python
import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.utils.email import conf
import os
import logging

logger = logging.getLogger(__name__)


async def send_email_arq(ctx, email: str, subject: str, body: str):
    """ARQ email task (async)"""
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)

        logger.info(f"✅ Email sent to {email}")
        return f"Email sent to {email}"

    except Exception as e:
        logger.error(f"❌ Failed to send email: {str(e)}")
        raise


async def startup(ctx):
    """Worker startup"""
    logger.info("🚀 ARQ Worker started")


async def shutdown(ctx):
    """Worker shutdown"""
    logger.info("🛑 ARQ Worker stopped")


class WorkerSettings:
    """ARQ Worker Configuration"""
    redis_settings = RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379))
    )

    functions = [send_email_arq]
    queue_name = "linear_backend_queue"

    on_startup = startup
    on_shutdown = shutdown

    max_jobs = 10
    job_timeout = 300  # 5 minutes
```

### Step 3: Use in FastAPI

```python
from arq import create_pool
from arq.connections import RedisSettings

@router.post("/send-email")
async def send_email_endpoint(email: str, subject: str, body: str):
    redis = await create_pool(RedisSettings())
    job = await redis.enqueue_job("send_email_arq", email, subject, body)

    return {"job_id": job.job_id, "status": "queued"}
```

### Step 4: Run ARQ Worker

```bash
arq app.workers.arq_worker.WorkerSettings
```

---

## Option 3: FastAPI BackgroundTasks

### Already Implemented! ✅

Your current `app/utils/email.py` already uses this:

```python
from fastapi import BackgroundTasks

async def send_email(
    background_tasks: BackgroundTasks, email: str, subject: str, body: str
):
    message = MessageSchema(
        subject=subject, recipients=[email], body=body, subtype=MessageType.html
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
```

**Usage:**

```python
@router.post("/signup")
async def signup(background_tasks: BackgroundTasks, email: str):
    # ... user creation ...

    await send_email(
        background_tasks,
        email,
        "Welcome!",
        "<h1>Welcome!</h1>"
    )

    return {"message": "User created"}
```

**Limitations:**

- ❌ No retry on failure
- ❌ No persistence (lost on server restart)
- ❌ No monitoring
- ✅ Simple and fast for basic tasks

---

## Docker Setup

### Update `docker-compose.yml`

```yaml
version: "3.8"

services:
  # Your existing services...

  redis:
    image: redis:7-alpine
    container_name: linear_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - linear_network

  celery_worker:
    build: .
    container_name: linear_celery_worker
    command: celery -A app.workers.celery_app worker --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - redis
      - db
    networks:
      - linear_network

  celery_beat:
    build: .
    container_name: linear_celery_beat
    command: celery -A app.workers.celery_app beat --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - redis
    networks:
      - linear_network

  flower:
    build: .
    container_name: linear_flower
    command: celery -A app.workers.celery_app flower --port=5555
    ports:
      - "5555:5555"
    env_file:
      - .env
    depends_on:
      - redis
      - celery_worker
    networks:
      - linear_network

volumes:
  redis_data:

networks:
  linear_network:
    driver: bridge
```

### Run with Docker

```bash
docker-compose up -d
```

---

## Testing

### Test Email Task

```python
# test_email_worker.py
from app.workers.email_tasks import send_email_task

# Queue a test email
task = send_email_task.delay(
    "test@example.com",
    "Test Email",
    "<h1>This is a test</h1>"
)

print(f"Task ID: {task.id}")
print(f"Status: {task.status}")

# Wait for result
result = task.get(timeout=10)
print(f"Result: {result}")
```

### Check Task Status

```bash
# In Python shell
from celery.result import AsyncResult

task = AsyncResult("your-task-id")
print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE
print(task.result)
```

---

## Monitoring

### Flower Dashboard

Access at: http://localhost:5555

Features:

- ✅ Real-time task monitoring
- ✅ Worker status
- ✅ Task history
- ✅ Task details and results
- ✅ Retry failed tasks

### Logs

```bash
# View Celery worker logs
docker logs -f linear_celery_worker

# View Celery beat logs
docker logs -f linear_celery_beat
```

---

## Best Practices

### 1. Task Design

- ✅ Keep tasks small and focused
- ✅ Make tasks idempotent (safe to retry)
- ✅ Add proper logging
- ✅ Set reasonable timeouts

### 2. Error Handling

```python
@celery_app.task(bind=True, max_retries=3)
def my_task(self, arg):
    try:
        # Task logic
        pass
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### 3. Monitoring

- ✅ Use Flower for production
- ✅ Set up alerts for failed tasks
- ✅ Monitor queue length
- ✅ Track task execution time

### 4. Security

- ✅ Don't pass sensitive data in task args (use IDs)
- ✅ Validate input in tasks
- ✅ Use secure Redis connection in production

---

## Troubleshooting

### Issue: Tasks not executing

**Solution:**

```bash
# Check if Redis is running
redis-cli ping  # Should return PONG

# Check if worker is running
celery -A app.workers.celery_app inspect active
```

### Issue: Import errors

**Solution:**

```bash
# Make sure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

### Issue: Windows compatibility

**Solution:**

```bash
# Use solo pool on Windows
celery -A app.workers.celery_app worker --pool=solo --loglevel=info
```

---

## Summary

### Recommended Setup for Production:

1. ✅ **Celery + Redis** for background jobs
2. ✅ **Flower** for monitoring
3. ✅ **Docker Compose** for easy deployment
4. ✅ **Proper logging** and error handling

### Quick Start Commands:

```bash
# Install
pip install celery redis flower

# Run locally
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
celery -A app.workers.celery_app beat --loglevel=info
celery -A app.workers.celery_app flower --port=5555

# Run with Docker
docker-compose up -d
```

---

**Happy Coding! 🚀**

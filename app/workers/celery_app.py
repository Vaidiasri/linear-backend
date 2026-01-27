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
    # Fix: Explicitly import tasks to register them
    imports=("app.workers.email_tasks",),
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

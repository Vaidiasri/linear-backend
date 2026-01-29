"""
Quick test script for Celery email worker
Run this after starting Redis and Celery worker
"""

from app.workers.email_tasks import (
    send_email_task,
    send_welcome_email,
    send_password_reset_email,
    send_issue_notification,
)
import time


def test_celery_worker():
    """Test all email tasks"""

    print("=" * 60)
    print("🚀 Testing Celery Email Worker")
    print("=" * 60)

    # Test 1: Simple email
    print("\n📧 Test 1: Sending simple email...")
    task1 = send_email_task.delay(
        "test@example.com",
        "Test Email from Celery",
        "<h1>Hello from Celery!</h1><p>This is a test email.</p>",
    )
    print(f"   ✓ Task ID: {task1.id}")
    print(f"   ✓ Status: {task1.status}")

    # Test 2: Welcome email
    print("\n👋 Test 2: Sending welcome email...")
    task2 = send_welcome_email.delay("newuser@example.com", "John Doe")
    print(f"   ✓ Task ID: {task2.id}")
    print(f"   ✓ Status: {task2.status}")

    # Test 3: Password reset email
    print("\n🔐 Test 3: Sending password reset email...")
    task3 = send_password_reset_email.delay("user@example.com", "abc123xyz456")
    print(f"   ✓ Task ID: {task3.id}")
    print(f"   ✓ Status: {task3.status}")

    # Test 4: Issue notification
    print("\n📋 Test 4: Sending issue notification...")
    task4 = send_issue_notification.delay(
        "developer@example.com", "Fix login bug", "assigned", "Project Manager"
    )
    print(f"   ✓ Task ID: {task4.id}")
    print(f"   ✓ Status: {task4.status}")

    # Wait for tasks to complete
    print("\n⏳ Waiting for tasks to complete (5 seconds)...")
    time.sleep(5)

    # Check results
    print("\n" + "=" * 60)
    print("📊 Results:")
    print("=" * 60)

    tasks = [
        ("Simple Email", task1),
        ("Welcome Email", task2),
        ("Password Reset", task3),
        ("Issue Notification", task4),
    ]

    for name, task in tasks:
        status = task.status
        status_emoji = (
            "✅" if status == "SUCCESS" else "❌" if status == "FAILURE" else "⏳"
        )

        print(f"\n{status_emoji} {name}:")
        print(f"   Status: {status}")

        if task.ready():
            if status == "SUCCESS":
                print(f"   Result: {task.result}")
            elif status == "FAILURE":
                print(f"   Error: {task.info}")
        else:
            print(f"   Still processing...")

    print("\n" + "=" * 60)
    print("🎉 Test completed!")
    print("=" * 60)

    # Instructions
    print("\n💡 Next Steps:")
    print("   1. Check Celery worker logs for detailed output")
    print("   2. Open Flower UI: http://localhost:5555")
    print("   3. Check your email inbox (if SMTP is configured)")
    print("   4. Integrate tasks in your FastAPI routes")


if __name__ == "__main__":
    try:
        test_celery_worker()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Make sure Redis is running")
        print("   2. Make sure Celery worker is running")
        print("   3. Check .env file for correct REDIS_URL")
        print("   4. Verify PYTHONPATH is set correctly")

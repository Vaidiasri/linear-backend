# Quick Start Guide - Celery Email Worker 🚀

## ✅ Setup Complete!

Your Celery email worker is ready to use. Here's how to run it:

---

## 🏃 Running the System

### Step 1: Redis (Already Running ✅)

Redis container is running on Docker:

```powershell
docker ps
# Should show redis container on port 6379
```

To stop/start Redis:

```powershell
docker stop redis
docker start redis
```

---

### Step 2: Start Celery Worker

**Option A - Using Batch Script (Easiest):**

```powershell
# Double-click or run:
start_celery_worker.bat
```

**Option B - Manual Command:**

```powershell
# Activate virtual environment
myenv\Scripts\Activate

# Start worker
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

You should see:

```
-------------- celery@YOUR-PC v5.6.2
--- ***** -----
...
[tasks]
  . send_email_task
  . send_welcome_email
  . send_password_reset_email
  . send_issue_notification
  . send_bulk_emails
  . daily_report_email
  . cleanup_logs

[INFO] Connected to redis://localhost:6379/0
[INFO] celery@YOUR-PC ready.
```

**Keep this terminal open!** Worker needs to run continuously.

---

### Step 3: Start Your FastAPI Server (Another Terminal)

```powershell
# Activate virtual environment
myenv\Scripts\Activate

# Start server
uvicorn app.main:app --reload
```

---

### Step 4: (Optional) Start Flower Monitoring

**Option A - Using Batch Script:**

```powershell
start_flower.bat
```

**Option B - Manual:**

```powershell
myenv\Scripts\Activate
celery -A app.workers.celery_app flower --port=5555
```

Then open: **http://localhost:5555**

---

## 🧪 Testing

### Quick Test

```powershell
# In a new terminal
myenv\Scripts\Activate
python test_celery.py
```

### Manual Test in Python

```powershell
myenv\Scripts\Activate
python
```

```python
from app.workers.email_tasks import send_welcome_email

# Queue a task
task = send_welcome_email.delay("test@example.com", "TestUser")

# Check status
print(f"Task ID: {task.id}")
print(f"Status: {task.status}")  # PENDING -> STARTED -> SUCCESS

# Get result (wait for completion)
result = task.get(timeout=10)
print(result)
```

---

## 📝 Using in Your FastAPI Routes

### Example 1: Welcome Email on Signup

```python
from fastapi import APIRouter
from app.workers.email_tasks import send_welcome_email

router = APIRouter()

@router.post("/auth/signup")
async def signup(email: str, username: str):
    # ... create user in database ...

    # Queue welcome email (non-blocking)
    task = send_welcome_email.delay(email, username)

    return {
        "message": "User created successfully",
        "email_task_id": task.id
    }
```

### Example 2: Check Task Status

```python
from celery.result import AsyncResult

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

More examples in: [`app/workers/example_usage.py`](file:///c:/Users/ghild/OneDrive/Desktop/one-month/backend/app/workers/example_usage.py)

---

## 🎯 Typical Workflow

### Development (3 Terminals)

**Terminal 1 - Redis:**

```powershell
docker start redis
```

**Terminal 2 - Celery Worker:**

```powershell
start_celery_worker.bat
```

**Terminal 3 - FastAPI:**

```powershell
myenv\Scripts\Activate
uvicorn app.main:app --reload
```

**Terminal 4 (Optional) - Flower:**

```powershell
start_flower.bat
```

---

## 📊 Monitoring

### Flower Dashboard

- URL: http://localhost:5555
- View active tasks
- Check worker status
- See task history
- Retry failed tasks

### Worker Logs

Check the terminal where worker is running for detailed logs.

---

## 🔧 Available Email Tasks

1. **`send_email_task(email, subject, body)`**
   - Generic email sender
   - Auto-retry on failure

2. **`send_welcome_email(email, username)`**
   - Welcome email for new users
   - Professional HTML template

3. **`send_password_reset_email(email, reset_token)`**
   - Password reset with link
   - Token-based authentication

4. **`send_issue_notification(email, issue_title, action, actor)`**
   - Issue assignment/update notifications
   - Customizable action types

5. **`send_bulk_emails(emails, subject, body)`**
   - Send to multiple recipients
   - Returns list of task IDs

6. **`daily_report_email()`** (Scheduled)
   - Runs daily at 9 AM
   - Automatic via Celery Beat

7. **`cleanup_logs()`** (Scheduled)
   - Runs daily at 2 AM
   - Automatic cleanup tasks

---

## ⚙️ Configuration

### Email Settings (`.env`)

Update your email credentials in `.env`:

```env
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=noreply@yourapp.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

### Redis Settings (Already Configured)

```env
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 🐛 Troubleshooting

### Issue: Worker not processing tasks

**Solution:**

1. Make sure Redis is running: `docker ps`
2. Make sure worker is running: Check terminal
3. Check worker logs for errors

### Issue: "Connection refused" error

**Solution:**

```powershell
# Restart Redis
docker restart redis

# Restart worker
# Stop worker (Ctrl+C) and run again
start_celery_worker.bat
```

### Issue: Tasks stuck in PENDING

**Solution:**

- Worker is not running
- Start worker: `start_celery_worker.bat`

### Issue: Email not sending

**Solution:**

1. Check email credentials in `.env`
2. For Gmail, use App Password (not regular password)
3. Check worker logs for SMTP errors

---

## 📚 Documentation

- **Complete Guide:** [`EMAIL_WORKER_GUIDE.md`](file:///c:/Users/ghild/OneDrive/Desktop/one-month/backend/EMAIL_WORKER_GUIDE.md)
- **Redis Setup:** [`REDIS_SETUP_WINDOWS.md`](file:///c:/Users/ghild/OneDrive/Desktop/one-month/backend/REDIS_SETUP_WINDOWS.md)
- **Example Usage:** [`app/workers/example_usage.py`](file:///c:/Users/ghild/OneDrive/Desktop/one-month/backend/app/workers/example_usage.py)
- **Walkthrough:** Check artifacts folder

---

## ✅ Checklist

- [x] Redis installed and running (Docker)
- [x] Dependencies installed (Celery, Redis, Flower)
- [x] Worker files created
- [x] Configuration updated (.env)
- [x] Batch scripts created
- [ ] **Start Celery worker** ← Do this now!
- [ ] Test email tasks
- [ ] Integrate in your routes
- [ ] Configure email credentials

---

## 🚀 Next Steps

1. **Start the worker:**

   ```powershell
   start_celery_worker.bat
   ```

2. **Test it:**

   ```powershell
   python test_celery.py
   ```

3. **Use in your app:**
   - Copy examples from `example_usage.py`
   - Add to your routes
   - Queue emails on user actions

4. **Monitor:**
   - Open Flower: http://localhost:5555
   - Watch worker logs

---

**You're all set! Happy coding! 🎉**

# Redis Installation & Setup Guide for Windows 🪟

## Quick Start - Install Redis on Windows

### Option 1: Using Memurai (Recommended for Windows) ⭐

Memurai is a Redis-compatible server optimized for Windows.

1. **Download Memurai:**
   - Visit: https://www.memurai.com/get-memurai
   - Download the free version (Memurai Developer)

2. **Install:**
   - Run the installer
   - Follow the installation wizard
   - Memurai will automatically start as a Windows service

3. **Verify Installation:**

   ```powershell
   # Check if Memurai service is running
   Get-Service Memurai

   # Test connection
   memurai-cli ping
   # Should return: PONG
   ```

### Option 2: Using WSL (Windows Subsystem for Linux)

1. **Install WSL:**

   ```powershell
   wsl --install
   ```

2. **Install Redis in WSL:**

   ```bash
   sudo apt update
   sudo apt install redis-server
   ```

3. **Start Redis:**

   ```bash
   sudo service redis-server start
   ```

4. **Test:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

### Option 3: Using Docker (Easiest) 🐳

1. **Install Docker Desktop for Windows**

2. **Run Redis Container:**

   ```powershell
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```

3. **Verify:**
   ```powershell
   docker ps
   # Should show redis container running
   ```

---

## Testing Your Celery Setup

### Step 1: Start Redis

**If using Memurai:**

```powershell
# Check if running
Get-Service Memurai

# Start if not running
Start-Service Memurai
```

**If using Docker:**

```powershell
docker start redis
```

**If using WSL:**

```bash
sudo service redis-server start
```

### Step 2: Test Redis Connection

```powershell
# Using Python
python -c "import redis; r = redis.Redis(host='localhost', port=6379); print(r.ping())"
# Should print: True
```

### Step 3: Start Celery Worker

Open a new terminal in your backend directory:

```powershell
# Activate virtual environment
myenv\Scripts\Activate

# Start Celery worker (Windows requires --pool=solo)
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

You should see output like:

```
-------------- celery@YOUR-PC v5.6.2 (dawn-chorus)
--- ***** -----
-- ******* ---- Windows-10-10.0.19045-SP0 2026-01-27 11:40:00
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         linear_backend:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ---- .> task events: OFF
--- ***** -----
-------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . cleanup_logs
  . daily_report_email
  . send_bulk_emails
  . send_email_task
  . send_issue_notification
  . send_password_reset_email
  . send_welcome_email

[2026-01-27 11:40:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2026-01-27 11:40:00,000: INFO/MainProcess] celery@YOUR-PC ready.
```

### Step 4: Test Email Task

Open another terminal:

```powershell
# Activate virtual environment
myenv\Scripts\Activate

# Start Python shell
python
```

In Python shell:

```python
from app.workers.email_tasks import send_welcome_email

# Queue a test email
task = send_welcome_email.delay("test@example.com", "TestUser")

# Check task ID
print(f"Task ID: {task.id}")

# Check status
print(f"Status: {task.status}")

# Wait for result (optional)
try:
    result = task.get(timeout=10)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
```

### Step 5: Start Flower (Monitoring UI) - Optional

Open another terminal:

```powershell
# Activate virtual environment
myenv\Scripts\Activate

# Start Flower
celery -A app.workers.celery_app flower --port=5555
```

Then open in browser: http://localhost:5555

---

## Running All Services Together

### Terminal 1: Redis (if using Docker)

```powershell
docker start redis
```

### Terminal 2: FastAPI Server

```powershell
cd c:\Users\ghild\OneDrive\Desktop\one-month\backend
myenv\Scripts\Activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3: Celery Worker

```powershell
cd c:\Users\ghild\OneDrive\Desktop\one-month\backend
myenv\Scripts\Activate
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

### Terminal 4: Celery Beat (for scheduled tasks) - Optional

```powershell
cd c:\Users\ghild\OneDrive\Desktop\one-month\backend
myenv\Scripts\Activate
celery -A app.workers.celery_app beat --loglevel=info
```

### Terminal 5: Flower (monitoring) - Optional

```powershell
cd c:\Users\ghild\OneDrive\Desktop\one-month\backend
myenv\Scripts\Activate
celery -A app.workers.celery_app flower --port=5555
```

---

## Quick Test Script

Create `test_celery.py` in your backend directory:

```python
from app.workers.email_tasks import send_email_task, send_welcome_email
import time

print("🚀 Testing Celery Email Worker...")

# Test 1: Simple email
print("\n📧 Test 1: Sending simple email...")
task1 = send_email_task.delay(
    "test@example.com",
    "Test Email",
    "<h1>Hello from Celery!</h1>"
)
print(f"   Task ID: {task1.id}")
print(f"   Status: {task1.status}")

# Test 2: Welcome email
print("\n👋 Test 2: Sending welcome email...")
task2 = send_welcome_email.delay("newuser@example.com", "John Doe")
print(f"   Task ID: {task2.id}")
print(f"   Status: {task2.status}")

# Wait and check results
print("\n⏳ Waiting for tasks to complete...")
time.sleep(5)

print(f"\n✅ Task 1 Status: {task1.status}")
print(f"✅ Task 2 Status: {task2.status}")

if task1.ready():
    print(f"   Task 1 Result: {task1.result}")
if task2.ready():
    print(f"   Task 2 Result: {task2.result}")

print("\n🎉 Test completed!")
```

Run it:

```powershell
python test_celery.py
```

---

## Troubleshooting

### Issue: "redis.exceptions.ConnectionError"

**Solution:**

- Make sure Redis is running
- Check if port 6379 is available
- Verify REDIS_URL in .env file

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:**

```powershell
# Set PYTHONPATH
$env:PYTHONPATH = "c:\Users\ghild\OneDrive\Desktop\one-month\backend"
```

Or add to your PowerShell profile permanently.

### Issue: Celery worker not picking up tasks

**Solution:**

- Restart the worker
- Check if task names match
- Verify Redis connection
- Check worker logs for errors

### Issue: "billiard.exceptions.TimeLimitExceeded"

**Solution:**

- Increase task timeout in celery_app.py
- Check if email server is responding
- Verify SMTP settings in email.py

---

## Production Deployment

For production, use Docker Compose (already configured in EMAIL_WORKER_GUIDE.md):

```powershell
docker-compose up -d
```

This will start:

- ✅ PostgreSQL database
- ✅ Redis
- ✅ FastAPI server
- ✅ Celery worker
- ✅ Celery beat
- ✅ Flower monitoring

---

## Next Steps

1. ✅ Install Redis (choose one option above)
2. ✅ Start Redis server
3. ✅ Test Celery worker
4. ✅ Integrate email tasks in your routes
5. ✅ Monitor with Flower
6. ✅ Deploy to production

**Happy Coding! 🚀**

# Rate Limiting Guide 🛡️

## Overview

This application implements rate limiting using `slowapi` with Redis backend to prevent API abuse and ensure fair usage.

## Configuration

### Rate Limits by Endpoint

| Endpoint                       | Limit      | Reason                        |
| ------------------------------ | ---------- | ----------------------------- |
| `POST /api/v1/auth/login`      | 5/minute   | Prevent brute force attacks   |
| `POST /api/v1/users`           | 10/minute  | Prevent spam account creation |
| `GET /api/v1/users/me`         | 100/minute | Allow normal profile access   |
| `POST /api/v1/users/me/avatar` | 30/minute  | Limit file uploads            |
| `POST /api/v1/issues`          | 30/minute  | Prevent issue spam            |
| `GET /api/v1/issues`           | 100/minute | Allow normal browsing         |
| `GET /api/v1/issues/search`    | 50/minute  | Moderate search usage         |
| **Global Default**             | 60/minute  | Catch-all for other endpoints |

---

## Setup

### 1. Install Dependencies

```bash
pip install slowapi==0.1.9
```

Already included in `requirements.txt`.

### 2. Redis Configuration

Rate limiting uses Redis (same instance as Celery, different database):

- **Celery**: Redis DB 0
- **Rate Limiting**: Redis DB 1

**Environment Variables:**

```env
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. Start Redis

```bash
# Using Docker (recommended)
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or use existing Redis for Celery
```

---

## How It Works

### 1. Middleware Integration

Rate limiting is integrated via `app.state.limiter` in `main.py`:

```python
from app.middleware.rate_limiter import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
```

### 2. Per-Endpoint Limits

Endpoints use the `@limiter.limit()` decorator:

```python
from app.middleware.rate_limiter import limiter
from fastapi import Request

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    # Login logic
```

**Important:** The `Request` parameter is required for rate limiting to work.

### 3. Rate Limit Key

Limits are applied **per IP address** using `get_remote_address` function.

---

## Error Response

When rate limit is exceeded, clients receive a `429 Too Many Requests` response:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "detail": "5 per 1 minute"
}
```

---

## Testing

### Manual Testing

**Test 1: Auth Rate Limit (5/minute)**

```bash
# Make 6 requests quickly
for i in {1..6}; do
  curl -X POST http://localhost:8080/api/v1/auth/login \
    -d "username=test@example.com&password=test123"
  echo "Request $i"
done
```

**Expected:** First 5 succeed, 6th returns 429.

**Test 2: User Creation (10/minute)**

```bash
# Make 11 requests
for i in {1..11}; do
  curl -X POST http://localhost:8080/api/v1/users \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"test$i@example.com\",\"password\":\"test123\"}"
  echo "Request $i"
done
```

**Expected:** First 10 succeed, 11th returns 429.

### Automated Testing

Run the test script:

```bash
python test_rate_limiting.py
```

---

## Monitoring

### Check Redis

View rate limit data in Redis:

```bash
# Connect to Redis
redis-cli

# Select rate limiting database
SELECT 1

# View all keys
KEYS *

# Check specific limit
GET "LIMITER/127.0.0.1/api/v1/auth/login"
```

### Server Logs

Rate limit violations are logged automatically by slowapi.

---

## Customization

### Change Limits

Edit the decorator in router files:

```python
# Before
@limiter.limit("5/minute")

# After (more strict)
@limiter.limit("3/minute")

# Or (more generous)
@limiter.limit("10/minute")
```

### Change Global Default

Edit `app/middleware/rate_limiter.py`:

```python
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://...",
    default_limits=["100/minute"],  # Changed from 60
)
```

### Multiple Limits

Apply multiple limits:

```python
@limiter.limit("5/minute")
@limiter.limit("100/hour")
async def endpoint(request: Request, ...):
    # Will enforce both limits
```

---

## Best Practices

### 1. Always Include Request Parameter

```python
# ✅ Correct
@limiter.limit("10/minute")
async def endpoint(request: Request, ...):
    pass

# ❌ Wrong - will not work
@limiter.limit("10/minute")
async def endpoint(...):
    pass
```

### 2. Order Matters

Place `@limiter.limit()` **after** `@router` decorator:

```python
# ✅ Correct
@router.post("/endpoint")
@limiter.limit("10/minute")
async def endpoint(request: Request, ...):
    pass

# ❌ Wrong
@limiter.limit("10/minute")
@router.post("/endpoint")
async def endpoint(request: Request, ...):
    pass
```

### 3. Adjust Based on Usage

- **Strict limits** for sensitive operations (auth, payments)
- **Generous limits** for read operations
- **Moderate limits** for writes

---

## Troubleshooting

### Issue: Rate limits not working

**Solution:**

1. Check Redis is running: `redis-cli ping`
2. Verify `Request` parameter in endpoint
3. Check decorator order
4. Restart server

### Issue: Too strict limits

**Solution:**
Increase limit in decorator:

```python
@limiter.limit("100/minute")  # Increased from 60
```

### Issue: Redis connection error

**Solution:**

1. Check Redis is running
2. Verify `REDIS_HOST` and `REDIS_PORT` in `.env`
3. Check Redis logs

---

## Production Considerations

### 1. Use Redis Cluster

For high availability:

```python
storage_uri="redis+cluster://redis-cluster:6379/1"
```

### 2. Monitor Rate Limit Hits

Track 429 responses in monitoring system.

### 3. Whitelist IPs

For trusted services:

```python
def custom_key_func(request: Request):
    if request.client.host in WHITELIST:
        return "whitelist"
    return get_remote_address(request)

limiter = Limiter(key_func=custom_key_func, ...)
```

### 4. Rate Limit by User

Instead of IP:

```python
def get_user_id(request: Request):
    # Extract from JWT token
    return request.state.user_id

limiter = Limiter(key_func=get_user_id, ...)
```

---

## Summary

✅ **Implemented:**

- slowapi with Redis backend
- Per-endpoint customization
- Custom error responses
- IP-based limiting

✅ **Benefits:**

- Prevents brute force attacks
- Stops API abuse
- Fair usage enforcement
- Production-ready

✅ **Limits Applied:**

- Auth: 5/min (strict)
- Writes: 10-30/min (moderate)
- Reads: 100/min (generous)
- Global: 60/min (default)

---

**Rate limiting is now active! 🛡️**

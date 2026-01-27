"""
Rate Limiter Configuration
Uses slowapi with Redis backend for distributed rate limiting
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Redis connection for rate limiting (DB 1, separate from Celery)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=1,  # Use different DB than Celery (DB 0)
    decode_responses=True,
)

# Initialize limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/1",
    default_limits=["60/minute"],  # Global default: 60 requests per minute
)


# Custom error handler for rate limit exceeded
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors
    Returns 429 status with helpful error message
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail),
        },
    )

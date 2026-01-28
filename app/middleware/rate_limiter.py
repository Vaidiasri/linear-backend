"""
Rate Limiter Configuration
Development: In-memory storage (single instance only)
Production: Redis backend for distributed rate limiting
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize limiter with in-memory storage (for development)
# For production, use Redis: storage_uri="redis://localhost:6379/1"
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",  # In-memory storage (development only)
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

from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..lib.database import get_db
from ..services.auth import AuthService
from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")  # Strict limit to prevent brute force
async def login(
    request: Request,
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login endpoint with rate limiting (5 requests/minute)"""
    return await AuthService.login(db, credentials=user_credentials)

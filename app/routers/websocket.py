import time
from typing import Dict, Tuple
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from .. import model, oauth2
from ..lib.database import get_db
from ..connectionManager import connection_manager

router = APIRouter()

# Simple in-memory cache for user auth: {token: (user_obj, timestamp)}
_user_auth_cache: Dict[str, Tuple[model.User, float]] = {}
CACHE_TTL = 60  # seconds


async def get_cached_user(token: str, db: AsyncSession) -> model.User | None:
    """
    Retrieve user from cache or DB based on token.
    Prevents DB hammering on repeated WebSocket reconnections.
    """
    now = time.time()

    # Check cache
    if token in _user_auth_cache:
        user, timestamp = _user_auth_cache[token]
        if now - timestamp < CACHE_TTL:
            return user
        else:
            del _user_auth_cache[token]  # Expired

    user_id: str | None = None
    try:
        # Decode Token
        payload = jwt.decode(token, oauth2.SECRET_KEY, algorithms=[oauth2.ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        print(f"WS Auth Failed: Invalid JWT for token endpoint")
        return None

    if not user_id:
        return None

    # DB Lookup
    # print(f"WS Auth DB Lookup: {user_id}")  # Commented out to reduce noise
    result = await db.execute(select(model.User).where(model.User.email == user_id))
    user = result.scalars().first()

    if user:
        # Update Cache
        _user_auth_cache[token] = (user, now)

    return user


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket Endpoint for Real-time Updates.
    - Explicitly accepts connection first to avoid 1006 errors.
    - Manually verifies token (cached).
    - Connects user to their Team channel.
    """
    await websocket.accept()
    # print(f"WS Accepted. Verifying Token: {token[:10]}...")

    user = None
    try:
        user = await get_cached_user(token, db)
    except Exception as e:
        print(f"WS Auth Exception: {e}")
        # Fall through to close

    # 3. Validation
    if not user:
        print(f"WS Auth Failed: Invalid Token or User")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Check for Admin Role
    # print(f"DEBUG: Checking Role for {user.email}") # Reduced noise

    if user.role == model.UserRole.ADMIN:
        # print(f"WS Connecting GLOBAL ADMIN: {user.email}")
        connection_manager.register_admin(websocket)
    else:
        # Standard Member Logic
        # print(f"DEBUG: Not Admin. Checking Team ID: {user.team_id}")
        if not user.team_id:
            print(f"WS Rejected: No team for {user.email}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # 4. Connect
        connection_manager.register(user.team_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # print(f"WS Disconnected: {user.email}")
        pass  # Normal disconnection
    except Exception as e:
        print(f"WS Error (unexpected) for {user.email}: {e}")
        # Add more details if possible, e.g. traceback
        import traceback

        traceback.print_exc()
    finally:
        # Ensure clean disconnect logic
        if user.role == model.UserRole.ADMIN:
            connection_manager.disconnect_admin(websocket)
        elif user and user.team_id:  # Check user exists and has team_id
            connection_manager.disconnect(user.team_id, websocket)

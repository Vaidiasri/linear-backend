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


async def get_current_user_ws(
    token: str = Query(...), db: AsyncSession = Depends(get_db)
) -> model.User:
    """
    Authenticate WebSocket connection via Query Parameter.
    Browser creates WS connection which doesn't support headers easily.
    """
    credentials_exception = WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)


    user_id: str | None = None
    try:
        # Decode Token
        payload = jwt.decode(token, oauth2.SECRET_KEY, algorithms=[oauth2.ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        pass  # Will fall through to check below

    if not user_id:
        raise credentials_exception

    # User existence check (Linear one-liner)
    result = await db.execute(select(model.User).where(model.User.email == user_id))
    user = result.scalars().first()

    if not user:
        raise credentials_exception

    return user


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user: model.User = Depends(get_current_user_ws),
):
    """
    WebSocket Endpoint for Real-time Updates.
    - Connects user to their Team channel.
    - Handles disconnection automatically.
    """
    # Reject if user has no team (Optional policy)
    if not user.team_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Use Connection Manager
    await connection_manager.connect(user.team_id, websocket)

    try:
        while True:
            # Keep connection alive & listen for client messages (if any)
            # Currently we only push data, but we need this loop to keep socket open.
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(user.team_id, websocket)

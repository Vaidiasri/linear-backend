"""
API V1 Router Aggregator
Combines all existing routers under /api/v1 prefix
# Force reload
"""

from fastapi import APIRouter
from app.routers import (
    user,
    auth,
    issue,
    team,
    project,
    comment,
    attached,
    dashboard,
    websocket,
    cycle,
)

# Create V1 API router
api_router = APIRouter()

# Include all V1 endpoints
api_router.include_router(user.router, tags=["V1 - Users"])
api_router.include_router(auth.router, tags=["V1 - Auth"])
api_router.include_router(issue.router, tags=["V1 - Issues"])
api_router.include_router(team.router, tags=["V1 - Teams"])
api_router.include_router(project.router, tags=["V1 - Projects"])
api_router.include_router(comment.router, tags=["V1 - Comments"])
api_router.include_router(attached.router, tags=["V1 - Attachments"])
api_router.include_router(dashboard.router, tags=["V1 - Dashboard"])
api_router.include_router(cycle.router, tags=["V1 - Cycles"])
api_router.include_router(websocket.router, tags=["V1 - WebSocket"])

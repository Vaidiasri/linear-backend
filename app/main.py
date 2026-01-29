from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
import logging

from .lib.database import engine, Base

# Iska matlab hai models wali file load karo taaki Base ko pata chale kitni tables hain
from . import model
from .routers import (
    user,
    auth,
    issue,
    team,
    project,
    comment,
    attached,
    dashboard,
    websocket,
)  # 1. Apne naye router folder ko import karo

# Import V1 API router
from .api.v1.api import api_router as api_v1_router

# Import rate limiting
from .middleware.rate_limiter import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from fastapi.staticfiles import StaticFiles
import os

# 0. Setup Logging
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,  # Ensure this config overrides any previous config
)


# 1. App ko initialize karo with enhanced metadata
app = FastAPI(
    title="Linear Backend API",
    description="Project management system with versioned API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================================
# API V1 - Recommended (Versioned Routes)
# ============================================================================
# ============================================================================
# API V1 - Recommended (Versioned Routes)
# ============================================================================
app.include_router(api_v1_router, prefix="/api/v1")

# Add CORS Middleware
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Vite fallback port
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Backward Compatibility - Deprecated (Will be removed in V2)
# ============================================================================
app.include_router(user.router, tags=["Users (Deprecated - Use /api/v1)"])
app.include_router(auth.router, tags=["Auth (Deprecated - Use /api/v1)"])
app.include_router(issue.router, tags=["Issues (Deprecated - Use /api/v1)"])
app.include_router(team.router, tags=["Teams (Deprecated - Use /api/v1)"])
app.include_router(project.router, tags=["Projects (Deprecated - Use /api/v1)"])
app.include_router(comment.router, tags=["Comments (Deprecated - Use /api/v1)"])
app.include_router(attached.router, tags=["Attachments (Deprecated - Use /api/v1)"])
app.include_router(dashboard.router, tags=["Dashboard (Deprecated - Use /api/v1)"])
app.include_router(websocket.router, tags=["WebSocket (Deprecated - Use /api/v1)"])


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please contact support."},
    )


# 2. Ek test route banao (Browser pe dikhega)
@app.get("/")
async def root():
    return {
        "message": "Linear Backend API",
        "version": "v1",
        "endpoints": {
            "v1_api": "/api/v1",
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        },
        "note": "Use /api/v1/* endpoints for versioned API. Old endpoints are deprecated.",
    }


# 3. Ek aur route banao health check ke liye
@app.get("/health")
async def health_check():
    return {"status": "online", "database": "checking..."}


@app.on_event("startup")
async def startup():
    # Alembic ab migrations handle karega, auto-create ki zarurat nahi
    print("Server started! Use 'alembic upgrade head' for migrations.")

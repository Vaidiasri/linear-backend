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
)  # 1. Apne naye router folder ko import karo


# 0. Setup Logging
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,  # Ensure this config overrides any previous config
)


# 1. App ko initialize karo
app = FastAPI(title="Linear Clone API")
# 2. Ye line sabse important hai!
# Isse saare signup routes main app se connect ho jayenge.
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(issue.router)
app.include_router(team.router)
app.include_router(project.router)
app.include_router(comment.router)
app.include_router(attached.router)


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
    return {"message": "Bhai, Linear Clone ka server ekdum mast chal raha hai!"}


# 3. Ek aur route banao health check ke liye
@app.get("/health")
async def health_check():
    return {"status": "online", "database": "checking..."}


@app.on_event("startup")
async def startup():
    # Alembic ab migrations handle karega, auto-create ki zarurat nahi
    print("Server started! Use 'alembic upgrade head' for migrations.")

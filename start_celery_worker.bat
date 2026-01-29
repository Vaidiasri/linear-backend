@echo off
REM Quick start script for Celery worker on Windows

echo ========================================
echo Starting Celery Worker
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call myenv\Scripts\activate.bat
)

echo.
echo Starting Celery worker with solo pool (Windows compatible)...
echo.
echo Press Ctrl+C to stop the worker
echo ========================================
echo.

celery -A app.workers.celery_app worker --loglevel=info --pool=solo

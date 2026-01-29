@echo off
REM Quick start script for Flower monitoring UI

echo ========================================
echo Starting Flower Monitoring UI
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call myenv\Scripts\activate.bat
)

echo.
echo Starting Flower on http://localhost:5555
echo.
echo Press Ctrl+C to stop Flower
echo ========================================
echo.

celery -A app.workers.celery_app flower --port=5555

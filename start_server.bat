@echo off
echo Starting FastAPI Server...
call myenv\Scripts\Activate
uvicorn app.main:app --reload
pause

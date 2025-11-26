@echo off
REM Start the PSI Backend Server
echo Starting PSI Backend Server...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause


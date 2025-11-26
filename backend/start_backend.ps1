# Start the PSI Backend Server
Write-Host "Starting PSI Backend Server..." -ForegroundColor Green
Set-Location $PSScriptRoot
& .\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload


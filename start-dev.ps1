Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting CareerLens AI (Resumetric) Full Stack App" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 2

Write-Host "Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "Servers launched in separate windows!" -ForegroundColor Yellow
Write-Host "Frontend:    http://localhost:5173" -ForegroundColor White
Write-Host "Backend API: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "Health:      http://127.0.0.1:8000/health" -ForegroundColor White

@echo off
echo ========================================================
echo   Starting CareerLens AI (Resumetric) Full Stack App
echo ========================================================
echo.

echo Starting FastAPI Backend on http://localhost:8000...
start "CareerLens AI - Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 2 /nobreak > nul

echo Starting Vite Frontend on http://localhost:5173...
start "CareerLens AI - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Application started!
echo Frontend: http://localhost:5173
echo Backend API: http://127.0.0.1:8000/docs
echo.
pause


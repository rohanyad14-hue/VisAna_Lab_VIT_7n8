@echo off
echo ========================================================
echo   Launching Assessment 8 - Docker Multi-Container Stack
echo   Visual Analytics Lab (VL2026270106069)
echo   Rohan Yadav (26MML0020)
echo ========================================================

echo [1/4] Starting Docker services via Docker Compose...
docker compose up -d

echo.
echo [2/4] Waiting for services to become healthy...
timeout /t 5 /nobreak >nul

echo.
echo [3/4] Docker Containers Status:
docker compose ps

echo.
echo [4/4] Opening VeloceAnalytics Dashboard in browser...
start http://localhost:8080/

echo.
echo ========================================================
echo   Stack is running:
echo   - Frontend: http://localhost:8080
echo   - Backend API: http://localhost:5000/api/health
echo   - Registry: http://localhost:5001/v2/_catalog
echo   - MySQL: localhost:3306 (salesdb)
echo ========================================================
pause

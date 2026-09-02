@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM AgriDarshak - Safe Process Termination (Targeted Ports Only)
REM ============================================================

TITLE AgriDarshak - Shutdown

echo.
echo ============================================================
echo    Stopping AgriDarshak Services...
echo ============================================================
echo.

set "BACKEND_FOUND=0"
set "FRONTEND_FOUND=0"

REM 1. Find and stop backend on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr /i "LISTENING"') do (
    set "BACKEND_FOUND=1"
    set "PID=%%a"
    if defined PID (
        if not "!PID!"=="0" (
            echo Stopping AgriDarshak Backend - PID !PID! on port 8000
            taskkill /F /PID !PID! >nul 2>&1
        )
    )
)

REM 2. Find and stop frontend on port 5173
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr /i "LISTENING"') do (
    set "FRONTEND_FOUND=1"
    set "PID=%%a"
    if defined PID (
        if not "!PID!"=="0" (
            echo Stopping AgriDarshak Frontend - PID !PID! on port 5173
            taskkill /F /PID !PID! >nul 2>&1
        )
    )
)

ping 127.0.0.1 -n 3 >nul

REM 3. Verify ports are released
set "BACKEND_STILL_RUNNING=0"
set "FRONTEND_STILL_RUNNING=0"

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr /i "LISTENING"') do (
    set "BACKEND_STILL_RUNNING=1"
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr /i "LISTENING"') do (
    set "FRONTEND_STILL_RUNNING=1"
)

echo.
if "!BACKEND_FOUND!"=="1" (
    if "!BACKEND_STILL_RUNNING!"=="0" (
        echo [OK] Stopped backend on port 8000
    ) else (
        echo [WARN] Backend on port 8000 is still releasing
    )
) else (
    echo [INFO] No backend service running on port 8000
)

if "!FRONTEND_FOUND!"=="1" (
    if "!FRONTEND_STILL_RUNNING!"=="0" (
        echo [OK] Stopped frontend on port 5173
    ) else (
        echo [WARN] Frontend on port 5173 is still releasing
    )
) else (
    echo [INFO] No frontend service running on port 5173
)

if "!BACKEND_FOUND!"=="0" if "!FRONTEND_FOUND!"=="0" (
    echo.
    echo No services running.
)

echo.
echo ============================================================
echo    AgriDarshak Shutdown Complete
echo ============================================================
echo.
pause

@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM AgriDarshak - One-Click Reliable Startup
REM ============================================================

TITLE AgriDarshak - Startup

echo.
echo ============================================================
echo    AGRIDARSHAK - EARLY WARNING ^& INTELLIGENCE SYSTEM
echo ============================================================
echo.

cd /d "%~dp0"

REM ============================================================
REM STEP 1: Safe Port Cleanup (Targeted PIDs only)
REM ============================================================
echo [1/4] Checking ports 8000 and 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr /i "LISTENING"') do (
    if not "%%a"=="0" (
        echo       Releasing occupied port 8000 - PID %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr /i "LISTENING"') do (
    if not "%%a"=="0" (
        echo       Releasing occupied port 5173 - PID %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)
ping 127.0.0.1 -n 2 >nul
echo       Ports verified.
echo.

REM ============================================================
REM STEP 2: Detect & Prepare Python Environment
REM ============================================================
echo [2/4] Configuring AgriDarshak Backend...

set "PYTHON_EXE="

if exist "backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%CD%\backend\.venv\Scripts\python.exe"
)
if not defined PYTHON_EXE if exist "backend\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%CD%\backend\venv\Scripts\python.exe"
)
if not defined PYTHON_EXE (
    where python >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Python not found in PATH! Please install Python 3.10+
        pause
        exit /b 1
    )
    echo       Creating Python virtual environment in backend\.venv...
    cd backend
    python -m venv .venv
    cd ..
    if exist "backend\.venv\Scripts\python.exe" (
        set "PYTHON_EXE=%CD%\backend\.venv\Scripts\python.exe"
    ) else (
        set "PYTHON_EXE=python"
    )
)

echo       Using Python: "!PYTHON_EXE!"

REM Check if backend requirements are installed
"!PYTHON_EXE!" -c "import fastapi, uvicorn, sqlalchemy, pydantic" >nul 2>&1
if !errorlevel! neq 0 (
    echo       Installing backend dependencies - requirements.txt...
    "!PYTHON_EXE!" -m pip install --quiet --upgrade pip
    "!PYTHON_EXE!" -m pip install -r backend\requirements.txt
)

REM Initialize SQLite database tables & seeds
if not exist "backend\crop_advisory.db" (
    echo       Initializing SQLite database...
    cd backend
    "!PYTHON_EXE!" init_database.py >nul 2>&1
    cd ..
)

REM Start Backend in separate window
echo       Starting AgriDarshak backend server on port 8000...
cd /d "%~dp0backend"
start "AgriDarshak Backend - http://127.0.0.1:8000" "!PYTHON_EXE!" app.py
cd /d "%~dp0"

echo.

REM ============================================================
REM STEP 3: Detect & Prepare Frontend Environment
REM ============================================================
echo [3/4] Configuring AgriDarshak Frontend...

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found in PATH! Please install Node.js 18+
    pause
    exit /b 1
)

if not exist "frontend\node_modules\" (
    echo       Installing frontend dependencies - npm install...
    cd frontend
    call npm install
    cd ..
)

REM Start Frontend in separate window
echo       Starting AgriDarshak frontend server on port 5173...
cd /d "%~dp0frontend"
start "AgriDarshak Frontend - http://127.0.0.1:5173" cmd /k "call npm run dev"
cd /d "%~dp0"

echo.

REM ============================================================
REM STEP 4: Service Readiness Checks & Health Polling
REM ============================================================
echo [4/4] Verifying Service Readiness...

REM Wait for Backend (max 60s)
echo       Waiting for backend at http://127.0.0.1:8000/docs...
set "BACKEND_READY=0"
for /L %%i in (1,1,60) do (
    if "!BACKEND_READY!"=="0" (
        "!PYTHON_EXE!" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=1)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "BACKEND_READY=1"
        ) else (
            ping 127.0.0.1 -n 2 >nul
        )
    )
)

if "!BACKEND_READY!"=="1" (
    echo       AgriDarshak backend ready - http://127.0.0.1:8000 [OK]
) else (
    echo       [WARN] Backend taking longer to respond. Proceeding...
)

REM Wait for Frontend (max 60s)
echo       Waiting for frontend at http://127.0.0.1:5173...
set "FRONTEND_READY=0"
for /L %%i in (1,1,60) do (
    if "!FRONTEND_READY!"=="0" (
        "!PYTHON_EXE!" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5173', timeout=1)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "FRONTEND_READY=1"
        ) else (
            ping 127.0.0.1 -n 2 >nul
        )
    )
)

if "!FRONTEND_READY!"=="1" (
    echo       AgriDarshak frontend ready - http://127.0.0.1:5173 [OK]
) else (
    echo       [WARN] Frontend taking longer to respond. Proceeding...
)

echo.
echo ============================================================
echo    SUCCESS! AgriDarshak is fully operational
echo ============================================================
echo.
echo   - Web Application: http://127.0.0.1:5173
echo   - Interactive API: http://127.0.0.1:8000/docs
echo.
echo   Opening AgriDarshak in your default browser...
start http://127.0.0.1:5173

echo.
echo Press any key to close this startup monitor window...
pause >nul

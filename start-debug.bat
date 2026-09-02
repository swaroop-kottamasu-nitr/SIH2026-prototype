@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM AgriDarshak - Debug Mode Startup (Verbose Output)
REM ============================================================

TITLE AgriDarshak - Debug Mode

echo.
echo ============================================================
echo    AGRIDARSHAK - DEBUG MODE STARTUP
echo ============================================================
echo.

cd /d "%~dp0"

REM Step 1: Safe Port Cleanup
echo [DEBUG] Step 1: Checking for active ports 8000 and 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr /i "LISTENING"') do (
    if not "%%a"=="0" (
        echo [DEBUG] Found process %%a on port 8000. Terminating...
        taskkill /F /PID %%a >nul 2>&1
    )
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr /i "LISTENING"') do (
    if not "%%a"=="0" (
        echo [DEBUG] Found process %%a on port 5173. Terminating...
        taskkill /F /PID %%a >nul 2>&1
    )
)
echo [DEBUG] Ports 8000 and 5173 are clear.
echo.

REM Step 2: Detect & Validate Python Environment
echo [DEBUG] Step 2: Locating Python virtual environment...
set "PYTHON_EXE="

if exist "backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%CD%\backend\.venv\Scripts\python.exe"
    echo [DEBUG] Detected backend\.venv\Scripts\python.exe
)
if not defined PYTHON_EXE if exist "backend\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%CD%\backend\venv\Scripts\python.exe"
    echo [DEBUG] Detected backend\venv\Scripts\python.exe
)
if not defined PYTHON_EXE (
    echo [DEBUG] Virtual environment not found. Checking system python...
    where python
    if !errorlevel! neq 0 (
        echo [ERROR] Python not found in system PATH.
        pause
        exit /b 1
    )
    echo [DEBUG] Creating virtual environment at backend\.venv...
    cd backend
    python -m venv .venv
    cd ..
    set "PYTHON_EXE=%CD%\backend\.venv\Scripts\python.exe"
)

echo [DEBUG] Python binary: "!PYTHON_EXE!"
"!PYTHON_EXE!" --version

echo [DEBUG] Verifying backend dependencies...
"!PYTHON_EXE!" -c "import fastapi, uvicorn, sqlalchemy, pydantic; print('[DEBUG] Core packages verified.')"
if !errorlevel! neq 0 (
    echo [DEBUG] Installing missing dependencies...
    "!PYTHON_EXE!" -m pip install -r backend\requirements.txt
)

echo [DEBUG] Starting FastAPI backend with LOG_LEVEL=debug...
cd /d "%~dp0backend"
start "AgriDarshak Backend [DEBUG] - Port 8000" cmd /k "title AgriDarshak Backend [DEBUG] && color 0B && set LOG_LEVEL=debug && "!PYTHON_EXE!" -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level debug"
cd /d "%~dp0"

echo.

REM Step 3: Frontend Environment
echo [DEBUG] Step 3: Validating Frontend Node environment...
where node
where npm
if %errorlevel% neq 0 (
    echo [ERROR] Node.js or npm not found in system PATH.
    pause
    exit /b 1
)

if not exist "frontend\node_modules\" (
    echo [DEBUG] Installing npm packages in frontend...
    cd frontend
    call npm install
    cd ..
)

echo [DEBUG] Starting Vite frontend server...
cd /d "%~dp0frontend"
start "AgriDarshak Frontend [DEBUG] - Port 5173" cmd /k "title AgriDarshak Frontend [DEBUG] && color 0E && npm run dev -- --debug"
cd /d "%~dp0"

echo.

REM Step 4: Health polling
echo [DEBUG] Step 4: Polling service health...
set "BACKEND_READY=0"
for /L %%i in (1,1,60) do (
    if "!BACKEND_READY!"=="0" (
        "!PYTHON_EXE!" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=1)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "BACKEND_READY=1"
            echo [DEBUG] Backend responded with HTTP 200 after %%i seconds.
        ) else (
            ping 127.0.0.1 -n 2 >nul
        )
    )
)

set "FRONTEND_READY=0"
for /L %%i in (1,1,60) do (
    if "!FRONTEND_READY!"=="0" (
        "!PYTHON_EXE!" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5173', timeout=1)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "FRONTEND_READY=1"
            echo [DEBUG] Frontend responded with HTTP 200 after %%i seconds.
        ) else (
            ping 127.0.0.1 -n 2 >nul
        )
    )
)

echo.
echo ============================================================
echo [DEBUG] All services running in debug mode.
echo - Web: http://127.0.0.1:5173
echo - API Docs: http://127.0.0.1:8000/docs
echo ============================================================
echo.
start http://127.0.0.1:5173
pause

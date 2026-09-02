@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM AgriDarshak - System Diagnostic Tool
REM ============================================================

TITLE AgriDarshak - System Diagnostics

echo.
echo ============================================================
echo    AGRIDARSHAK - SYSTEM DIAGNOSTICS REPORT
echo ============================================================
echo.

cd /d "%~dp0"

REM 1. Port 8000 (Backend)
echo [1/6] Checking Port 8000 (Backend)...
set "PORT_8000_IN_USE=0"
set "PORT_8000_PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr /i "LISTENING"') do (
    set "PORT_8000_IN_USE=1"
    set "PORT_8000_PID=%%a"
)
if "!PORT_8000_IN_USE!"=="1" (
    echo       [ACTIVE] Port 8000 is occupied by PID !PORT_8000_PID! - Backend is running
) else (
    echo       [FREE]   Port 8000 is currently available
)

REM 2. Port 5173 (Frontend)
echo [2/6] Checking Port 5173 (Frontend)...
set "PORT_5173_IN_USE=0"
set "PORT_5173_PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr /i "LISTENING"') do (
    set "PORT_5173_IN_USE=1"
    set "PORT_5173_PID=%%a"
)
if "!PORT_5173_IN_USE!"=="1" (
    echo       [ACTIVE] Port 5173 is occupied by PID !PORT_5173_PID! - Frontend is running
) else (
    echo       [FREE]   Port 5173 is currently available
)

REM 3. Python Environment & Backend Dependencies
echo [3/6] Checking Backend Python Environment...
set "PYTHON_EXE="
if exist "backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%CD%\backend\.venv\Scripts\python.exe"
    echo       [OK] Found virtual environment at backend\.venv
)
if not defined PYTHON_EXE if exist "backend\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%CD%\backend\venv\Scripts\python.exe"
    echo       [OK] Found virtual environment at backend\venv
)
if not defined PYTHON_EXE (
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=python"
        echo       [WARN] Using system Python - no isolated .venv detected
    ) else (
        echo       [FAIL] Python not found in PATH!
    )
)

if defined PYTHON_EXE (
    "!PYTHON_EXE!" -c "import fastapi, uvicorn, sqlalchemy, pydantic" >nul 2>&1
    if !errorlevel! equ 0 (
        echo       [OK] Core backend dependencies installed - FastAPI, Uvicorn, SQLAlchemy, Pydantic
    ) else (
        echo       [FAIL] Missing backend dependencies. Run 'pip install -r backend\requirements.txt'
    )
)

REM 4. Node Environment & Frontend Dependencies
echo [4/6] Checking Frontend Environment...
where node >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('node -v') do echo       [OK] Node.js installed - version %%v
) else (
    echo       [FAIL] Node.js not found in PATH!
)

if exist "frontend\node_modules\" (
    echo       [OK] Frontend dependencies installed - frontend\node_modules exists
) else (
    echo       [WARN] Frontend node_modules missing. Run 'npm install' inside frontend\
)

REM 5. Environment & API Configuration
echo [5/6] Checking Configuration (.env)...
if exist ".env" (
    echo       [OK] .env file exists in project root
    findstr /i "GEMINI_API_KEY" .env >nul 2>&1
    if !errorlevel! equ 0 (
        echo       [OK] GEMINI_API_KEY configuration entry detected
    ) else (
        echo       [INFO] GEMINI_API_KEY not configured. AgriDarshak will use deterministic Smart Advisory fallback.
    )
) else (
    echo       [INFO] No .env file found. System runs with default SQLite and Smart Advisory fallback mode.
)

REM 6. SQLite Database Connection
echo [6/6] Checking Database Connection...
if defined PYTHON_EXE (
    "!PYTHON_EXE!" -c "import sys, os; sys.path.insert(0, os.path.abspath('backend')); from database import engine; conn = engine.connect(); print('      [OK] Successfully connected to SQLite database'); conn.close()" 2>nul
    if !errorlevel! neq 0 (
        echo       [FAIL] Database connection error or missing tables.
    )
) else (
    echo       [SKIP] Cannot test database connection - Python unavailable
)

echo.
echo ============================================================
echo    DIAGNOSTICS COMPLETED
echo ============================================================
echo.
pause

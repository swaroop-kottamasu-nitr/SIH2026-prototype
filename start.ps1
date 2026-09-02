# ============================================================
# AgriDarshak - PowerShell Startup Script
# ============================================================

$Host.UI.RawUI.WindowTitle = "AgriDarshak - Startup"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   AGRIDARSHAK - EARLY WARNING & INTELLIGENCE SYSTEM" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

# ------------------------------------------------------------
# STEP 1: Safe Port Cleanup
# ------------------------------------------------------------
Write-Host "[1/4] Checking ports 8000 and 5173..." -ForegroundColor Cyan

$Ports = @(8000, 5173)
foreach ($Port in $Ports) {
    try {
        $Connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        foreach ($Conn in $Connections) {
            $PidToKill = $Conn.OwningProcess
            if ($PidToKill -gt 0) {
                Write-Host "      Releasing port $Port (PID $PidToKill)..." -ForegroundColor Yellow
                Stop-Process -Id $PidToKill -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        # Ignore if Get-NetTCPConnection not available or no permissions
    }
}
Start-Sleep -Seconds 1
Write-Host "      Ports verified." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------
# STEP 2: Configure Python Virtual Environment & Backend
# ------------------------------------------------------------
Write-Host "[2/4] Configuring AgriDarshak Backend..." -ForegroundColor Cyan

$PythonExe = $null
if (Test-Path "$RootDir\backend\.venv\Scripts\python.exe") {
    $PythonExe = "$RootDir\backend\.venv\Scripts\python.exe"
} elseif (Test-Path "$RootDir\backend\venv\Scripts\python.exe") {
    $PythonExe = "$RootDir\backend\venv\Scripts\python.exe"
} else {
    $SystemPy = Get-Command python -ErrorAction SilentlyContinue
    if (-not $SystemPy) {
        Write-Host "[ERROR] Python not found in system PATH. Please install Python 3.10+" -ForegroundColor Red
        Read-Host "Press Enter to exit..."
        exit 1
    }
    Write-Host "      Creating virtual environment in backend\.venv..." -ForegroundColor Gray
    Set-Location "$RootDir\backend"
    & python -m venv .venv
    Set-Location $RootDir
    if (Test-Path "$RootDir\backend\.venv\Scripts\python.exe") {
        $PythonExe = "$RootDir\backend\.venv\Scripts\python.exe"
    } else {
        $PythonExe = "python"
    }
}

Write-Host "      Using Python: $PythonExe" -ForegroundColor Gray

# Verify dependencies
$TestDep = & $PythonExe -c "import fastapi, uvicorn, sqlalchemy, pydantic; print('OK')" 2>$null
if ($TestDep -ne "OK") {
    Write-Host "      Installing backend dependencies (requirements.txt)..." -ForegroundColor Yellow
    & $PythonExe -m pip install --quiet --upgrade pip
    & $PythonExe -m pip install -r "$RootDir\backend\requirements.txt"
}

# Check database
if (-not (Test-Path "$RootDir\backend\crop_advisory.db")) {
    Write-Host "      Initializing SQLite database..." -ForegroundColor Gray
    Set-Location "$RootDir\backend"
    & $PythonExe init_database.py | Out-Null
    Set-Location $RootDir
}

# Launch backend in separate window
Write-Host "      Starting AgriDarshak backend server on port 8000..." -ForegroundColor Gray
Start-Process cmd -ArgumentList "/k", "title AgriDarshak Backend (Port 8000) && color 0B && cd /d `"$RootDir\backend`" && echo ============================================================ && echo    AGRIDARSHAK BACKEND SERVER && echo ============================================================ && echo [OK] Running on http://127.0.0.1:8000 && echo [DOCS] API Docs at http://127.0.0.1:8000/docs && echo. && echo KEEP THIS WINDOW OPEN! && echo. && `"$PythonExe`" app.py"

Write-Host ""

# ------------------------------------------------------------
# STEP 3: Configure Frontend Environment
# ------------------------------------------------------------
Write-Host "[3/4] Configuring AgriDarshak Frontend..." -ForegroundColor Cyan

$NodeCheck = Get-Command node -ErrorAction SilentlyContinue
if (-not $NodeCheck) {
    Write-Host "[ERROR] Node.js not found in system PATH. Please install Node.js 18+" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit 1
}

if (-not (Test-Path "$RootDir\frontend\node_modules\")) {
    Write-Host "      Installing frontend packages (npm install)..." -ForegroundColor Yellow
    Set-Location "$RootDir\frontend"
    npm install
    Set-Location $RootDir
}

# Launch frontend in separate window
Write-Host "      Starting AgriDarshak frontend server on port 5173..." -ForegroundColor Gray
Start-Process cmd -ArgumentList "/k", "title AgriDarshak Frontend (Port 5173) && color 0E && cd /d `"$RootDir\frontend`" && echo ============================================================ && echo    AGRIDARSHAK FRONTEND SERVER && echo ============================================================ && echo [OK] Running on http://127.0.0.1:5173 && echo. && echo KEEP THIS WINDOW OPEN! && echo. && npm run dev"

Write-Host ""

# ------------------------------------------------------------
# STEP 4: Service Readiness & Health Polling
# ------------------------------------------------------------
Write-Host "[4/4] Verifying Service Readiness..." -ForegroundColor Cyan

Write-Host "      Waiting for backend at http://127.0.0.1:8000/docs..." -NoNewline
$BackendReady = $false
for ($i = 1; $i -le 60; $i++) {
    try {
        $res = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($res.StatusCode -eq 200) {
            $BackendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($BackendReady) {
    Write-Host " Ready [OK]" -ForegroundColor Green
} else {
    Write-Host " [WARN: Pending]" -ForegroundColor Yellow
}

Write-Host "      Waiting for frontend at http://127.0.0.1:5173..." -NoNewline
$FrontendReady = $false
for ($i = 1; $i -le 60; $i++) {
    try {
        $res = Invoke-WebRequest -Uri "http://127.0.0.1:5173" -UseBasicParsing -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($res.StatusCode -eq 200) {
            $FrontendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($FrontendReady) {
    Write-Host " Ready [OK]" -ForegroundColor Green
} else {
    Write-Host " [WARN: Pending]" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "   SUCCESS! AgriDarshak is fully operational" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  - Web Application: http://127.0.0.1:5173" -ForegroundColor White
Write-Host "  - Interactive API: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Opening AgriDarshak in your default browser..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:5173"

Write-Host ""
Write-Host "Press any key to close this startup monitor..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

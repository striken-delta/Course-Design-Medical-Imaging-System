# Medical Imaging System - One-Click Startup Script
$host.UI.RawUI.WindowTitle = "Medical Imaging System"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Medical Imaging System" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = "$rootDir\backend"
$frontendDir = "$rootDir\frontend"
$venvPython = "$backendDir\venv\Scripts\python.exe"

# ====== Step 1: Check & setup backend environment ======
Write-Host ""
Write-Host "[1/4] Checking backend environment..." -ForegroundColor Green

if (-not (Test-Path $venvPython)) {
    Write-Host "  Python venv not found, creating..." -ForegroundColor Yellow
    python -m venv "$backendDir\venv"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to create venv. Is Python installed?" -ForegroundColor Red
        Read-Host
        exit 1
    }
    Write-Host "  Installing Python dependencies..." -ForegroundColor Yellow
    & "$backendDir\venv\Scripts\pip.exe" install -r "$backendDir\requirements.txt"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  WARNING: pip install may have failed. Check requirements.txt" -ForegroundColor Red
    }
}
Write-Host "  Backend environment ready." -ForegroundColor Green

# ====== Step 2: Check & setup frontend environment ======
Write-Host "[2/4] Checking frontend environment..." -ForegroundColor Green

if (-not (Test-Path "$frontendDir\node_modules")) {
    Write-Host "  node_modules not found, running npm install..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    Pop-Location
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  WARNING: npm install may have failed. Is Node.js installed?" -ForegroundColor Red
    }
}
Write-Host "  Frontend environment ready." -ForegroundColor Green

# ====== Step 3: Kill old processes on our ports ======
Write-Host "[3/4] Cleaning up old processes..." -ForegroundColor Green
foreach ($p in @(8000, 5173)) {
    netstat -ano 2>$null | Select-String ":$p " | Select-String "LISTENING" | ForEach-Object {
        $pidStr = ($_ -split '\s+')[-1]
        Stop-Process -Id $pidStr -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 1

# ====== Step 4: Start services ======
Write-Host "[4/4] Starting services..." -ForegroundColor Green

# Start Backend
Write-Host ""
Write-Host "  Starting Backend on port 8000..." -ForegroundColor Green
$backendCmd = "cd /d `"$backendDir`" && `"$venvPython`" -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Process cmd -ArgumentList "/k title Backend-API-8000 && echo Backend running on http://localhost:8000 && echo Close this window to stop backend && echo. && $backendCmd"

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "  Starting Frontend on port 5173..." -ForegroundColor Green
$frontendCmd = "cd /d `"$frontendDir`" && npx vite --host 0.0.0.0 --port 5173"
Start-Process cmd -ArgumentList "/k title Frontend-5173 && echo Frontend running on http://localhost:5173 && echo Close this window to stop frontend && echo. && $frontendCmd"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Backend  : http://localhost:8000" -ForegroundColor Green
Write-Host "  Frontend : http://localhost:5173" -ForegroundColor Green
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Admin    : admin123 / admin1234" -ForegroundColor White
Write-Host ""
Write-Host "  Two cmd windows are open:" -ForegroundColor Yellow
Write-Host "    [Backend-API-8000]  - do NOT close" -ForegroundColor Yellow
Write-Host "    [Frontend-5173]     - do NOT close" -ForegroundColor Yellow
Write-Host ""
Write-Host "  First run? Dependencies were auto-installed above." -ForegroundColor Gray
Write-Host "  Next run will skip installation and start instantly." -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Start-Process "http://localhost:5173"

Write-Host "  Browser opened. Keep both cmd windows running." -ForegroundColor White
Write-Host "  Press Enter here to KILL both services." -ForegroundColor Red
Read-Host

# Cleanup
foreach ($p in @(8000, 5173)) {
    netstat -ano 2>$null | Select-String ":$p " | Select-String "LISTENING" | ForEach-Object {
        $pidStr = ($_ -split '\s+')[-1]
        Stop-Process -Id $pidStr -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "  Both services stopped." -ForegroundColor Yellow
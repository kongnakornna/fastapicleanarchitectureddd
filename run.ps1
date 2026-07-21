#Requires -Version 5.1
<#
.SYNOPSIS
    ICMON Auto Repair - FastAPI DDD Project Runner
.DESCRIPTION
    Menu-driven script for common project operations
.NOTES
    Run: .\run.ps1
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Show-Menu {
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     ICMON Auto Repair - FastAPI DDD         ║" -ForegroundColor Cyan
    Write-Host "║     Project Runner Menu                      ║" -ForegroundColor Cyan
    Write-Host "╠══════════════════════════════════════════════╣" -ForegroundColor Cyan
    Write-Host "║                                              ║"
    Write-Host "║  [1]  Run Server (Dev)                       ║" -ForegroundColor Yellow
    Write-Host "║  [2]  Run Server (Prod)                      ║" -ForegroundColor Yellow
    Write-Host "║  [3]  Run Tests                              ║"
    Write-Host "║  [4]  Run Tests (Verbose)                    ║"
    Write-Host "║  [5]  Run Tests + Coverage                   ║"
    Write-Host "║  [6]  Run Lint                               ║"
    Write-Host "║  [7]  Run Lint + Fix                         ║"
    Write-Host "║  [8]  Run Type Check                         ║"
    Write-Host "║                                              ║"
    Write-Host "║  ── Database ──                              ║" -ForegroundColor Green
    Write-Host "║  [10] Migration: Auto Generate               ║"
    Write-Host "║  [11] Migration: Apply (Upgrade)             ║"
    Write-Host "║  [12] Migration: Rollback (Downgrade)        ║"
    Write-Host "║  [13] Migration: Current Version             ║"
    Write-Host "║  [14] Migration: History                     ║"
    Write-Host "║  [15] Migration: Stamp Head                  ║"
    Write-Host "║                                              ║"
    Write-Host "║  ── Docker ──                                ║" -ForegroundColor Blue
    Write-Host "║  [20] Docker: Start All                      ║"
    Write-Host "║  [21] Docker: Stop All                       ║"
    Write-Host "║  [22] Docker: Restart All                    ║"
    Write-Host "║  [23] Docker: Start DB Only                  ║"
    Write-Host "║  [24] Docker: Logs                           ║"
    Write-Host "║  [25] Docker: Status                         ║"
    Write-Host "║                                              ║"
    Write-Host "║  ── MQTT ──                                  ║" -ForegroundColor Magenta
    Write-Host "║  [30] MQTT: Test Subscribe                   ║"
    Write-Host "║  [31] MQTT: Test Publish                     ║"
    Write-Host "║                                              ║"
    Write-Host "║  ── Info ──                                  ║" -ForegroundColor Gray
    Write-Host "║  [40] Show Project Structure                 ║"
    Write-Host "║  [41] Show API Endpoints                     ║"
    Write-Host "║  [42] Show Database Tables                   ║"
    Write-Host "║  [43] Show Test Summary                      ║"
    Write-Host "║                                              ║"
    Write-Host "║  [0]  Exit                                   ║" -ForegroundColor Red
    Write-Host "║                                              ║"
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Invoke-AndWait {
    param([string]$Command, [string]$Message)
    Write-Host "`n$Message" -ForegroundColor Yellow
    Write-Host ("─" * 50) -ForegroundColor DarkGray
    Invoke-Expression $Command
    Write-Host ("─" * 50) -ForegroundColor DarkGray
    Write-Host "`nPress any key to continue..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# ── Main Loop ──
while ($true) {
    Show-Menu
    $choice = Read-Host "Select"

    switch ($choice) {

        # ── Server ──
        "1" {
            Write-Host "`nStarting dev server on http://127.0.0.1:8000 ..." -ForegroundColor Green
            Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
            python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "2" {
            Write-Host "`nStarting production server (4 workers)..." -ForegroundColor Green
            python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --workers 4
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }

        # ── Tests ──
        "3" { Invoke-AndWait "python -m pytest test/ -q --tb=short" "Running tests..." }
        "4" { Invoke-AndWait "python -m pytest test/ -v --tb=short" "Running tests (verbose)..." }
        "5" { Invoke-AndWait "python -m pytest test/ -q --tb=short --cov=app --cov-report=term-missing" "Running tests with coverage..." }

        # ── Lint ──
        "6" { Invoke-AndWait "python -m ruff check app/ test/" "Running ruff lint..." }
        "7" { Invoke-AndWait "python -m ruff check app/ test/ --fix" "Running ruff lint with auto-fix..." }
        "8" { Invoke-AndWait "python -m mypy app/ --ignore-missing-imports" "Running type check..." }

        # ── Migrations ──
        "10" {
            $msg = Read-Host "Migration message"
            Invoke-AndWait "python -m alembic revision --autogenerate -m `"$msg`"" "Generating migration..."
        }
        "11" { Invoke-AndWait "python -m alembic upgrade head" "Applying migrations..." }
        "12" { Invoke-AndWait "python -m alembic downgrade -1" "Rolling back one revision..." }
        "13" { Invoke-AndWait "python -m alembic current" "Current migration version:" }
        "14" { Invoke-AndWait "python -m alembic history --verbose" "Migration history:" }
        "15" { Invoke-AndWait "python -m alembic stamp head" "Stamping database to head..." }

        # ── Docker ──
        "20" { Invoke-AndWait "docker-compose up -d" "Starting all services..." }
        "21" { Invoke-AndWait "docker-compose down" "Stopping all services..." }
        "22" { Invoke-AndWait "docker-compose restart" "Restarting all services..." }
        "23" { Invoke-AndWait "docker-compose up -d postgres influxdb" "Starting DB services..." }
        "24" {
            Write-Host "`nShowing docker logs (Ctrl+C to stop)..." -ForegroundColor Yellow
            docker-compose logs -f
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "25" { Invoke-AndWait "docker-compose ps" "Docker status:" }

        # ── MQTT ──
        "30" {
            Write-Host "`nSubscribing to test/# (Ctrl+C to stop)..." -ForegroundColor Magenta
            & "C:\mosquitto\mosquitto_sub.exe" -t "test/#" -v
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "31" {
            $msg = Read-Host "Message (default: Hello MQTT)"
            if ([string]::IsNullOrEmpty($msg)) { $msg = "Hello MQTT" }
            & "C:\mosquitto\mosquitto_pub.exe" -t "test/hello" -m $msg
            Write-Host "Published: test/hello -> $msg" -ForegroundColor Green
            Start-Sleep -Seconds 1
        }

        # ── Info ──
        "40" {
            Invoke-AndWait "tree /F /A app\modules | findstr /V '__pycache__' | findstr /V '.pyc'" "Project structure:"
        }
        "41" { Invoke-AndWait "python scripts/info.py endpoints" "API Endpoints:" }
        "42" { Invoke-AndWait "python scripts/info.py tables" "Database tables:" }
        "43" { Invoke-AndWait "python -m pytest test/ -q --tb=no" "Test summary:" }

        # ── Exit ──
        "0" { exit }

        default {
            Write-Host "Invalid choice!" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}

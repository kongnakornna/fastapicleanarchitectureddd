# run-django.ps1 — รัน Django โดยใช้ venv ตรง (ไม่ต้อง activate)
[CmdletBinding()]
param(
    [int]$Port = 8001,
    [switch]$Install,
    [switch]$Migrate,
    [switch]$Shell
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$Py   = Join-Path $Venv "Scripts\python.exe"

# ─── Create venv ถ้ายังไม่มี ─────────────────────
if (-not (Test-Path $Py)) {
    Write-Host "[--] Creating venv..." -ForegroundColor Cyan
    python -m venv $Venv
    $Install = $true
}

# ─── Install ถ้าขอ หรือ venv ใหม่ ────────────────
if ($Install) {
    Write-Host "[--] Installing requirements..." -ForegroundColor Cyan
    & $Py -m pip install --upgrade pip
    & $Py -m pip install -r (Join-Path $Root "requirements.txt")
}

# ─── Migrate ─────────────────────────────────────
if ($Migrate) {
    Write-Host "[--] Migrating..." -ForegroundColor Cyan
    & $Py (Join-Path $Root "manage.py") migrate --noinput
}

# ─── Shell mode ──────────────────────────────────
if ($Shell) {
    & $Py (Join-Path $Root "manage.py") shell
    exit
}

# ─── Runserver ───────────────────────────────────
Write-Host "[OK] Starting Django on port $Port..." -ForegroundColor Green
Write-Host "     http://localhost:$Port/" -ForegroundColor Cyan
& $Py (Join-Path $Root "manage.py") runserver $Port
# recover.ps1 — Master recovery script for fastapiiot YOLO project
# รัน: powershell -ExecutionPolicy Bypass -File recover.ps1

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔧 FASTAPIIOT — MASTER RECOVERY" -ForegroundColor Cyan  
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ─── STEP 1: Kill stuck processes ───────────────────────────
Write-Host "[1/8] Killing stuck Python processes..." -ForegroundColor Yellow
Get-Process | Where-Object {
    $_.ProcessName -like "*python*" -or 
    $_.ProcessName -like "*uvicorn*"
} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "  ✓ Done" -ForegroundColor Green

# ─── STEP 2: Remove broken .venv ────────────────────────────
Write-Host "[2/8] Removing broken .venv..." -ForegroundColor Yellow
if (Test-Path .venv) {
    try {
        Remove-Item -Recurse -Force .venv -ErrorAction Stop
    } catch {
        Write-Host "  ! Normal delete failed, trying cmd rmdir..." -ForegroundColor DarkYellow
        cmd /c "rmdir /s /q .venv" 2>$null
    }
    Start-Sleep -Seconds 1
}
if (Test-Path .venv) {
    Write-Host "  ✗ Cannot delete .venv — closing all apps may help" -ForegroundColor Red
    Write-Host "  Hint: close VS Code, terminal, and any Explorer windows" -ForegroundColor DarkYellow
    exit 1
}
Write-Host "  ✓ Removed" -ForegroundColor Green

# ─── STEP 3: Create fresh venv with Python 3.11 ─────────────
Write-Host "[3/8] Creating venv with Python 3.11..." -ForegroundColor Yellow
$py311 = (py -3.11 -c "import sys; print(sys.executable)" 2>$null)
if (-not $py311) {
    Write-Host "  ✗ Python 3.11 not found" -ForegroundColor Red
    Write-Host "  Install with: winget install Python.Python.3.11" -ForegroundColor DarkYellow
    exit 1
}
py -3.11 -m venv .venv
if (-not (Test-Path .venv\Scripts\Activate.ps1)) {
    Write-Host "  ✗ venv creation failed" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Created at .venv" -ForegroundColor Green

# ─── STEP 4: Activate ────────────────────────────────────────
Write-Host "[4/8] Activating venv..." -ForegroundColor Yellow
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
. .\.venv\Scripts\Activate.ps1
$v = python --version 2>&1
Write-Host "  ✓ $v" -ForegroundColor Green

# ─── STEP 5: Upgrade pip ────────────────────────────────────
Write-Host "[5/8] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  ✓ Done" -ForegroundColor Green

# ─── STEP 6: Install dependencies (in order) ────────────────
Write-Host "[6/8] Installing dependencies (may take 5-10 min)..." -ForegroundColor Yellow

Write-Host "  → Web stack..." -ForegroundColor Gray
python -m pip install --quiet `
    "fastapi>=0.115" `
    "uvicorn[standard]" `
    "pydantic>=2.9,<3" `
    "pydantic-core>=2.23,<3" `
    "pydantic-settings" `
    "python-multipart"

Write-Host "  → Database..." -ForegroundColor Gray
python -m pip install --quiet `
    "sqlalchemy[asyncio]>=2.0" `
    "asyncpg>=0.29" `
    "alembic>=1.13"

Write-Host "  → Cache / Storage..." -ForegroundColor Gray
python -m pip install --quiet redis boto3

Write-Host "  → YOLO core..." -ForegroundColor Gray
python -m pip install --quiet `
    ultralytics `
    opencv-python `
    albumentations `
    Pillow `
    numpy

Write-Host "  → Export tools..." -ForegroundColor Gray
python -m pip install --quiet onnx onnxruntime

Write-Host "  → Utils..." -ForegroundColor Gray
python -m pip install --quiet structlog loguru

Write-Host "  → PyTorch (CPU)..." -ForegroundColor Gray
python -m pip install --quiet torch torchvision

Write-Host "  ✓ All installed" -ForegroundColor Green

# ─── STEP 7: Verify ─────────────────────────────────────────
Write-Host "[7/8] Verifying installations..." -ForegroundColor Yellow

$checks = @(
    @("fastapi", "FastAPI"),
    @("pydantic", "Pydantic"),
    @("sqlalchemy", "SQLAlchemy"),
    @("alembic", "Alembic"),
    @("ultralytics", "Ultralytics"),
    @("torch", "PyTorch")
)

$allOk = $true
foreach ($check in $checks) {
    $mod = $check[0]
    $name = $check[1]
    $result = python -c "import $mod; print('OK')" 2>&1
    if ($result -match "OK") {
        Write-Host "  ✓ $name" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $name — $result" -ForegroundColor Red
        $allOk = $false
    }
}

# ─── STEP 8: Summary ────────────────────────────────────────
Write-Host ""
Write-Host "[8/8] Summary" -ForegroundColor Yellow
Write-Host ""

if ($allOk) {
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✅ RECOVERY COMPLETE" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Python: $(python --version 2>&1)" -ForegroundColor White
    Write-Host "  venv:   $((Get-Location).Path)\.venv" -ForegroundColor White
    Write-Host ""
    Write-Host "  NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "    1. python fix_yolo_gen.py    # fix create_module_yolo.py" -ForegroundColor White
    Write-Host "    2. python create_module_yolo.py help" -ForegroundColor White
    Write-Host "    3. python create_module_yolo.py all --force" -ForegroundColor White
    Write-Host "    4. python -m alembic upgrade head" -ForegroundColor White
    Write-Host "    5. python -m uvicorn app.app:app --reload" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host "  ⚠️  SOME INSTALLS FAILED" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Try individual installs to see errors:" -ForegroundColor Yellow
    Write-Host "    python -m pip install <package>" -ForegroundColor White
    Write-Host ""
}
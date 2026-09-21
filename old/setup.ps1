# PowerShell Script สำหรับติดตั้ง FastAPI Project
# วิธีใช้: .\setup.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FastAPI Clean Architecture DDD Setup  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ตรวจสอบ uv
Write-Host "[1/6] ตรวจสอบ uv..." -ForegroundColor Yellow
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "  ไม่พบ uv - กำลังติดตั้ง..." -ForegroundColor Red
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # รีเฟรช PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
} else {
    Write-Host "  uv พร้อมใช้งาน" -ForegroundColor Green
}

# ตรวจสอบ Python
Write-Host "[2/6] ตรวจสอบ Python..." -ForegroundColor Yellow
$pythonVersion = uv python list | Select-String "3.13" | Select-Object -First 1
if (-not $pythonVersion) {
    Write-Host "  กำลังติดตั้ง Python 3.13..." -ForegroundColor Red
    uv python install 3.13
} else {
    Write-Host "  Python 3.13 พร้อมใช้งาน" -ForegroundColor Green
}

# สร้าง .env
Write-Host "[3/6] ตั้งค่า Environment Variables..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  สร้างไฟล์ .env จาก .env.example แล้ว" -ForegroundColor Green
        Write-Host "  กรุณาแก้ไขไฟล์ .env ก่อนรันแอปพลิเคชัน" -ForegroundColor Yellow
    } else {
        Write-Host "  ไม่พบไฟล์ .env.example" -ForegroundColor Red
    }
} else {
    Write-Host "  ไฟล์ .env มีอยู่แล้ว" -ForegroundColor Green
}

# ติดตั้ง dependencies
Write-Host "[4/6] ติดตั้ง dependencies..." -ForegroundColor Yellow
uv sync
if ($?) {
    Write-Host "  ติดตั้ง dependencies สำเร็จ" -ForegroundColor Green
} else {
    Write-Host "  เกิดข้อผิดพลาดในการติดตั้ง" -ForegroundColor Red
}

# ติดตั้ง dev dependencies
Write-Host "[5/6] ติดตั้ง dev dependencies..." -ForegroundColor Yellow
uv sync --group dev
if ($?) {
    Write-Host "  ติดตั้ง dev dependencies สำเร็จ" -ForegroundColor Green
} else {
    Write-Host "  เกิดข้อผิดพลาดในการติดตั้ง dev dependencies" -ForegroundColor Red
}

# ตรวจสอบการติดตั้ง
Write-Host "[6/6] ตรวจสอบการติดตั้ง..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Python version:" -ForegroundColor Cyan
uv run python -V
Write-Host ""
Write-Host "FastAPI version:" -ForegroundColor Cyan
uv run python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  การติดตั้งเสร็จสมบูรณ์!              " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "วิธีรันแอปพลิเคชัน:" -ForegroundColor Yellow
Write-Host "  uv run -- uvicorn app.app:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "เปิด browser: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

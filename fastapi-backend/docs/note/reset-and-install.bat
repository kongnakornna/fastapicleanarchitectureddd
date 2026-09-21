@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

:: ═══════════════════════════════════════════════════════
::  Reset & Reinstall — FastAPI Clean Architecture DDD
::  ใช้เมื่อ: asyncpg error, venv พัง, .env เพี้ยน
::  รันแบบ Administrator
:: ═══════════════════════════════════════════════════════

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%fastapi-backend"
set "TARGET_PY=3.13"

echo.
echo ═══════════════════════════════════════════════════════
echo   Reset ^& Reinstall — FastAPI Backend
echo ═══════════════════════════════════════════════════════
echo   Project root : %PROJECT_ROOT%
echo   Backend dir  : %BACKEND_DIR%
echo   Target Python: %TARGET_PY%
echo ═══════════════════════════════════════════════════════
echo.
pause

:: ─────────────────────────────────────────────
:: 1) ตรวจว่าเป็น Administrator
:: ─────────────────────────────────────────────
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ต้องรันแบบ Administrator
    echo         คลิกขวาไฟล์ .bat แล้วเลือก "Run as administrator"
    pause
    exit /b 1
)
echo [OK] รันแบบ Administrator
echo.

:: ─────────────────────────────────────────────
:: 2) ปิด process ที่ค้าง
:: ─────────────────────────────────────────────
echo ─── [1/8] ปิด process ที่ค้าง ───
taskkill /F /IM python.exe    >nul 2>&1
taskkill /F /IM pythonw.exe   >nul 2>&1
taskkill /F /IM uvicorn.exe   >nul 2>&1
taskkill /F /IM alembic.exe   >nul 2>&1
echo [OK] ปิด process แล้ว
echo.

:: ─────────────────────────────────────────────
:: 3) ลบ Docker resources ของ project
:: ─────────────────────────────────────────────
echo ─── [2/8] ลบ Docker resources ───
pushd "%PROJECT_ROOT%"
docker compose down -v --remove-orphans >nul 2>&1
docker builder prune -af >nul 2>&1
popd
echo [OK] ลบ Docker container/volume/cache แล้ว
echo.

:: ─────────────────────────────────────────────
:: 4) ลบ venv + cache เก่า
:: ─────────────────────────────────────────────
echo ─── [3/8] ลบ venv + cache เก่า ───
cd /d "%BACKEND_DIR%"

if exist ".venv" (
    rmdir /S /Q ".venv"
    echo   - ลบ .venv
)

for /d /r . %%d in (__pycache__) do (
    if exist "%%d" rmdir /S /Q "%%d"
)
echo   - ลบ __pycache__

for /d /r . %%d in (.pytest_cache) do (
    if exist "%%d" rmdir /S /Q "%%d"
)
echo   - ลบ .pytest_cache

for /d /r . %%d in (.ruff_cache) do (
    if exist "%%d" rmdir /S /Q "%%d"
)
echo   - ลบ .ruff_cache

del /S /Q *.pyc >nul 2>&1
del /S /Q *.pyo >nul 2>&1
echo   - ลบ .pyc / .pyo

uv cache clean >nul 2>&1
echo   - ลบ uv cache
echo [OK] ลบ cache แล้ว
echo.

:: ─────────────────────────────────────────────
:: 5) ติดตั้ง Python 3.13 ผ่าน uv
:: ─────────────────────────────────────────────
echo ─── [4/8] ติดตั้ง Python %TARGET_PY% ───

where uv >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ไม่พบ uv ใน PATH
    echo         ติดตั้ง uv ก่อน: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

uv python install %TARGET_PY%
if errorlevel 1 (
    echo [ERROR] ติดตั้ง Python %TARGET_PY% ไม่สำเร็จ
    pause
    exit /b 1
)
echo [OK] Python %TARGET_PY% พร้อมใช้
echo.

:: ─────────────────────────────────────────────
:: 6) Pin Python + แก้ requires-python
:: ─────────────────────────────────────────────
echo ─── [5/8] Pin Python %TARGET_PY% ───

uv python pin %TARGET_PY%
if errorlevel 1 (
    echo [ERROR] pin Python ไม่สำเร็จ
    pause
    exit /b 1
)

echo   - เขียน .python-version = %TARGET_PY%

:: backup pyproject.toml ก่อนแก้
if not exist "pyproject.toml.bak" (
    copy /Y "pyproject.toml" "pyproject.toml.bak" >nul
    echo   - backup pyproject.toml ^-^> pyproject.toml.bak
)

:: แก้ requires-python โดยใช้ PowerShell (batch ไม่ถนัด regex)
powershell -NoProfile -Command ^
  "(Get-Content 'pyproject.toml' -Raw) -replace 'requires-python\s*=\s*\">=3\.14\"', 'requires-python = \">=3.13,<3.14\"' | Set-Content 'pyproject.toml' -NoNewline"

echo   - แก้ requires-python = \">=3.13,<3.14\"
echo [OK] Pin แล้ว
echo.

:: ─────────────────────────────────────────────
:: 7) สร้าง .env จาก .env.example
:: ─────────────────────────────────────────────
echo ─── [6/8] เตรียม .env ───

if exist ".env" (
    echo   - พบ .env เดิม — backup เป็น .env.backup
    copy /Y ".env" ".env.backup" >nul
) else (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo   - copy .env.example ^-^> .env
    ) else (
        echo [WARN] ไม่พบ .env.example — ข้ามขั้นตอนนี้
    )
)
echo [OK] .env พร้อมใช้
echo.

:: ─────────────────────────────────────────────
:: 8) Sync dependencies
:: ─────────────────────────────────────────────
echo ─── [7/8] uv sync ───

uv sync --all-groups
if errorlevel 1 (
    echo [ERROR] uv sync ล้มเหลว
    pause
    exit /b 1
)
echo [OK] Sync dependencies แล้ว
echo.

:: ─────────────────────────────────────────────
:: 9) ตรวจสอบ
:: ─────────────────────────────────────────────
echo ─── [8/8] ตรวจสอบ ───

echo.
echo --- Python version ---
uv run python --version

echo.
echo --- asyncpg import ---
uv run python -c "import asyncpg; print('OK asyncpg', asyncpg.__version__)"
if errorlevel 1 (
    echo [ERROR] asyncpg import ไม่ผ่าน — ตรวจ Python version อีกครั้ง
    pause
    exit /b 1
)

echo.
echo --- Settings ---
uv run python -c "from app.core.settings import Settings; s=Settings(); print('OK settings — env:', s.APPLICATION_ENVIRONMENT, '| cache_ver:', s.REDIS_CACHE_VERSION)"

echo.
echo ═══════════════════════════════════════════════════════
echo   ✅ ติดตั้งเสร็จสมบูรณ์
echo ═══════════════════════════════════════════════════════
echo   ขั้นตอนถัดไป:
echo     1)  cd fastapi-backend
echo     2)  make migrate
echo     3)  make dev
echo ═══════════════════════════════════════════════════════
echo.

pause
endlocal
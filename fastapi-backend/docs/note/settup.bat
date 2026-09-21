@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title RUN - FastAPI Clean Architecture

pushd "%~dp0"

echo ============================================================
echo   RUN - FastAPI Clean Architecture DDD ERP IoT
echo ============================================================
echo.

REM --- อ่าน .env ---
set "PG_HOST=localhost"
set "PG_PORT=5437"
set "PG_USER=postgres"
set "PG_PASS=postgres"
set "PG_DB=ioterp"

if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "K=%%A"
        set "V=%%B"
        if "!K!"=="POSTGRESQL_HOST"     set "PG_HOST=!V!"
        if "!K!"=="POSTGRESQL_PORT"     set "PG_PORT=!V!"
        if "!K!"=="POSTGRESQL_USERNAME" set "PG_USER=!V!"
        if "!K!"=="POSTGRESQL_PASSWORD" set "PG_PASS=!V!"
        if "!K!"=="POSTGRESQL_DATABASE" set "PG_DB=!V!"
    )
)
set "PG_HOST=%PG_HOST:"=%"
set "PG_PORT=%PG_PORT:"=%"
set "PG_USER=%PG_USER:"=%"
set "PG_PASS=%PG_PASS:"=%"
set "PG_DB=%PG_DB:"=%"

echo [INFO] DB: %PG_USER%@%PG_HOST%:%PG_PORT%/%PG_DB%
echo.

REM --- 1) uv python pin ---
echo [1/7] uv python pin 3.13 ...
uv python pin 3.13
if errorlevel 1 goto :fail

REM --- 2) ลบ .venv ---
echo.
echo [2/7] ลบ .venv เก่า ...
if exist ".venv" rmdir /s /q ".venv"
echo       [OK]

REM --- 3) uv sync ---
echo.
echo [3/7] uv sync ...
uv sync
if errorlevel 1 goto :fail

REM --- 4) ตรวจ Base ---
echo.
echo [4/7] ตรวจ Base ...
uv run python -c "from app.core.database import Base as B1; from app.modules.shared.infrastructure.models import Base as B2; import sys; print('same Base:', B1 is B2); print('tables:', len(B1.metadata.tables)); sys.exit(0 if B1 is B2 and len(B1.metadata.tables) > 0 else 1)"
if errorlevel 1 (
    echo [FAIL] Base ไม่ใช่ตัวเดียวกัน หรือ tables = 0
    echo        แก้ app\core\database.py ให้ re-export Base จาก shared
    goto :fail
)

REM --- 5) ลบ migration พัง + reset DB ---
echo.
echo [5/7] ลบ migration พัง + reset DB ...
if exist "migrations\versions\2026_09_19_17_32_8fb0474d768a.py" del /q "migrations\versions\2026_09_19_17_32_8fb0474d768a.py"
if exist "migrations\versions\__pycache__" rmdir /s /q "migrations\versions\__pycache__"

set "PGPASSWORD=%PG_PASS%"
psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d postgres -c "DROP DATABASE IF EXISTS %PG_DB% WITH (FORCE);"
if errorlevel 1 goto :fail
psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d postgres -c "CREATE DATABASE %PG_DB%;"
if errorlevel 1 goto :fail
echo       [OK]

REM --- 6) Generate + upgrade ---
echo.
echo [6/7] Autogenerate + upgrade ...
del /q "migrations\versions\*.py" 2>nul
uv run alembic revision --autogenerate -m "init erp tables"
if errorlevel 1 goto :fail
uv run alembic upgrade head
if errorlevel 1 goto :fail
echo       [OK]

REM --- 7) รัน ---
echo.
echo [7/7] เริ่ม uvicorn ...
echo.
uv run uvicorn app.app:app --reload
set "RC=%ERRORLEVEL%"

popd
endlocal & exit /b %RC%

:fail
echo.
echo ============================================================
echo   ล้มเหลว - ตรวจสอบ error ข้างบน
echo ============================================================
popd
endlocal
exit /b 1

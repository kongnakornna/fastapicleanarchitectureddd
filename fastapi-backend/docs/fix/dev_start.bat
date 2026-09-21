@echo off
REM ============================================================
REM  dev_start.bat - Safe dev server start
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Starting Dev Server
echo ============================================================
echo.

if not exist "pyproject.toml" (
    echo [ERROR] pyproject.toml not found. Run from project root.
    exit /b 1
)

REM --- ตรวจสอบ Alembic ก่อน ---
echo [1/2] Checking Alembic status...
uv run alembic current 2>nul
if errorlevel 1 (
    echo [WARN] Alembic is out of sync!
    echo.
    set /p FIX="Do you want to stamp head now? (y/N): "
    if /i "!FIX!"=="y" (
        uv run alembic stamp head
        echo [OK] Stamped to head.
    ) else (
        echo [SKIP] Continuing anyway...
    )
)
echo.

REM --- Start server ---
echo [2/2] Starting Uvicorn...
echo.
uv run uvicorn app.app:app --reload --host 127.0.0.1 --port 8000

endlocal
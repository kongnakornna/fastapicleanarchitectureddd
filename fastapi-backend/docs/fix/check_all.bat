@echo off
REM ============================================================
REM  check_all.bat - Run full project health check
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Full Project Health Check
echo ============================================================
echo.

REM --- ตรวจสอบ environment ---
if not exist "pyproject.toml" (
    echo [ERROR] pyproject.toml not found. Run from project root.
    exit /b 1
)

REM --- Step 1: Sync dependencies ---
echo [1/5] Syncing dependencies...
uv sync
if errorlevel 1 (
    echo [ERROR] uv sync failed.
    exit /b 1
)
echo.

REM --- Step 2: Lint check ---
echo [2/5] Running Ruff lint...
uv run ruff check .
if errorlevel 1 (
    echo.
    echo [FAIL] Lint errors found. Run fix_lint.bat to auto-fix.
    exit /b 1
)
echo.

REM --- Step 3: Format check ---
echo [3/5] Checking code format...
uv run ruff format --check .
if errorlevel 1 (
    echo.
    echo [WARN] Format issues found. Run: uv run ruff format .
)
echo.

REM --- Step 4: Type check (optional) ---
echo [4/5] Running type check (mypy)...
if exist "mypy.ini" (
    uv run mypy app
    if errorlevel 1 (
        echo [WARN] Type check issues found.
    )
) else (
    echo   [SKIP] mypy.ini not found.
)
echo.

REM --- Step 5: Alembic status ---
echo [5/5] Checking Alembic migration status...
uv run alembic current 2>nul
if errorlevel 1 (
    echo [WARN] Alembic check failed - DB may be out of sync.
    echo        Run: uv run alembic stamp head
)
echo.

echo ============================================================
echo   [DONE] Health check complete!
echo ============================================================
echo.

endlocal
exit /b 0
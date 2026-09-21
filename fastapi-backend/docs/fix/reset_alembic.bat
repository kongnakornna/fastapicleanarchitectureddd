@echo off
REM ============================================================
REM  reset_alembic.bat - Reset Alembic revision (DEV ONLY!)
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   [WARNING] Alembic Reset - DEVELOPMENT ONLY
echo ============================================================
echo.
echo   This will:
echo     1. Clear the alembic_version table in the database
echo     2. Optionally delete all migration files
echo     3. Optionally regenerate migrations
echo.
echo   Database: postgresql://postgres:***@localhost:5437/ioterp
echo.
set /p CONFIRM="Are you sure? (yes/N): "
if /i not "!CONFIRM!"=="yes" (
    echo [CANCELLED]
    exit /b 0
)
echo.

REM --- Step 1: Clear alembic_version ---
echo [1/3] Clearing alembic_version table...
uv run python -c "from sqlalchemy import create_engine, text; import os; from dotenv import load_dotenv; load_dotenv(); url = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@localhost:5437/ioterp'); e = create_engine(url); c = e.connect(); c.execute(text('DELETE FROM alembic_version')); c.commit(); c.close(); print('  [OK] Cleared.')"
if errorlevel 1 (
    echo [ERROR] Failed to clear alembic_version. Check DATABASE_URL.
    exit /b 1
)
echo.

REM --- Step 2: Delete migrations (optional) ---
set /p DELMIG="Delete all migration files in migrations\versions\? (y/N): "
if /i "!DELMIG!"=="y" (
    echo [2/3] Deleting migration files...
    del /Q "migrations\versions\*.py" 2>nul
    echo   [OK] Deleted.
) else (
    echo [2/3] Keeping migration files.
)
echo.

REM --- Step 3: Regenerate (optional) ---
set /p GENMIG="Generate new migration from current models? (y/N): "
if /i "!GENMIG!"=="y" (
    echo [3/3] Generating migration...
    uv run alembic revision --autogenerate -m "auto sync"
    echo.
    echo Applying migration...
    uv run alembic upgrade head
) else (
    echo [3/3] Skipping generation.
    echo.
    echo If schema is already in sync, run:
    echo   uv run alembic stamp head
)

echo.
echo ============================================================
echo   [DONE]
echo ============================================================
echo.

endlocal
exit /b 0
@echo off
REM ============================================================
REM  FastAPI Backend Scaffold - Windows Launcher v3.0
REM  Stack: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Redis + Alembic
REM  Pattern: Clean Architecture + DDD (4 layers)
REM ============================================================
REM Usage:
REM   scaffold.bat                     Create base + health + example
REM   scaffold.bat --setup             Create + venv + pip
REM   scaffold.bat --run               Create + setup + uvicorn
REM   scaffold.bat --fix               Patch configs only
REM   scaffold.bat --clean             Remove generated files
REM   scaffold.bat --module NAME       Scaffold single module
REM   scaffold.bat --layer N           Scaffold entire layer (0-7)
REM   scaffold.bat --all               Scaffold all 65 modules
REM   scaffold.bat --list              List all modules
REM   scaffold.bat --validate          Validate scaffold
REM   scaffold.bat --dry-run           Show what would be created
REM   scaffold.bat --force             Overwrite existing files
REM ============================================================

setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo   FastAPI Backend Scaffold v3.0
echo ============================================================
echo.

where powershell >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PowerShell not found in PATH.
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo [WARN] Python not found in PATH. --setup/--run will fail.
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scaffold.ps1" %*
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE% EQU 0 (
    echo [OK] Scaffold completed successfully.
) else (
    echo [ERROR] Scaffold failed with code %EXITCODE%.
)
echo.

if "%~1"=="" pause
exit /b %EXITCODE%
@echo off
REM ============================================================
REM  fix_module_imports.bat
REM  Fix common module-level import problems:
REM    1. Missing `from __future__ import annotations`
REM       -> NameError: name 'X' is not defined (forward refs)
REM    2. Eager cross-layer imports in __init__.py
REM       -> cascade: infra.models -> presentation.routers -> ...
REM
REM  Usage:
REM    cd fastapi-backend
REM    fix_module_imports.bat [--dry-run] [--aggressive] [--module NAME]
REM
REM  Options:
REM    --dry-run     Show plan, write nothing
REM    --aggressive  Also clean sublayer __init__.py files
REM    --no-verify   Skip post-fix import smoke test
REM    --module NAME Only fix this module (repeatable)
REM ============================================================
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

if not exist "%ROOT%\app\modules" (
    echo [ERROR] app\modules not found under %ROOT%
    echo         Run this from the fastapi-backend folder.
    pause
    exit /b 1
)

set "PSARGS="
:parse
if "%~1"=="" goto :run
set "A=%~1"
if /i "%A%"=="--dry-run"    set "A=-DryRun"
if /i "%A%"=="--aggressive" set "A=-Aggressive"
if /i "%A%"=="--no-verify"  set "A=-NoVerify"
if /i "%A%"=="--module" (
    shift
    set "PSARGS=!PSARGS! -Module "%~1""
    shift
    goto :parse
)
set "PSARGS=!PSARGS! !A!"
shift
goto :parse

:run
echo ROOT = %ROOT%
echo ARGS = %PSARGS%
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\fix_module_imports.ps1" -Root "%ROOT%" %PSARGS%

set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (
    echo [ERROR] fix_module_imports.ps1 exit=%RC%
    pause
    exit /b %RC%
)
echo ============================================================
echo  DONE
echo ============================================================
echo  Next:
echo    uv run python -c "import app.app"
echo    make migrate
echo    make dev
echo ============================================================
pause
exit /b 0
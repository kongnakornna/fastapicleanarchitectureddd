@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

if not exist "%ROOT%\app\modules\shared\domain\entities.py" (
    echo [ERROR] run this from the fastapi-backend folder
    pause
    exit /b 1
)

set "PSARGS="
:parse
if "%~1"=="" goto :run
set "A=%~1"
if /i "%A%"=="--dry-run"   set "A=-DryRun"
if /i "%A%"=="--no-verify" set "A=-NoVerify"
if /i "%A%"=="--help"      set "A=-Help"
if /i "%A%"=="-h"          set "A=-Help"
set "PSARGS=!PSARGS! !A!"
shift
goto :parse

:run
echo ROOT = %ROOT%
echo ARGS = %PSARGS%
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\fix_shared_circular_import.ps1" -Root "%ROOT%" %PSARGS%

set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
    echo [ERROR] exit code %RC%
    pause
    exit /b %RC%
)
echo.
echo ============================================================
echo  DONE
echo ============================================================
pause
exit /b 0

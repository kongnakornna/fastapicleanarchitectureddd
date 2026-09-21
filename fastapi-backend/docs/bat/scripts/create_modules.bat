@echo off
REM ============================================================
REM  create_modules.bat
REM  Wrapper — เรียก PowerShell เพื่อสร้าง/อัปเดต module structure
REM  Wrapper — call PowerShell to create/update module structure
REM
REM  Usage:
REM    create_modules.bat <module> [layer] [prefix] [options]
REM
REM  Options:
REM    --sql        Generate SQL migrations (V001/V002/V003)
REM    --tests      Generate test pyramid
REM    --docs       Generate README + API docs
REM    --routes     Print routing registration snippet
REM    --postman    Generate Postman collection
REM    --all        All of the above
REM
REM    --update     Update existing files (default behavior)
REM    --force      Update all without prompting (implies --update)
REM    --skip       Skip existing files (old behavior)
REM    --no-backup  Do not create .bak before update
REM    --quiet      No prompts, auto-update everything
REM ============================================================
chcp 65001 >nul

if "%~1"==""        goto :usage
if /i "%~1"=="help" goto :usage
if /i "%~1"=="-h"   goto :usage
if /i "%~1"=="--help" goto :usage

REM Translate --xxx to -Xxx for PowerShell switches
set "PSARGS="
:parse
if "%~1"=="" goto :run
set "A=%~1"
if "%A:~0,2%"=="--" (
    set "A=-%A:~2%"
)
set "PSARGS=%PSARGS% %A%"
shift
goto :parse

:run
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_modules.ps1" %PSARGS%
set EXITCODE=%ERRORLEVEL%
if %EXITCODE% NEQ 0 (
    echo.
    echo [ERROR] create_modules.ps1 exited with code %EXITCODE%
)
echo.
pause
exit /b %EXITCODE%

:usage
echo.
echo ============================================================
echo  create_modules.bat — Module Generator (DDD + Clean Arch)
echo ============================================================
echo.
echo Usage:
echo   create_modules.bat ^<module^> [layer] [prefix] [options]
echo.
echo Arguments:
echo   module    Module name (lowercase, e.g. inventory, payment)
echo   layer     Layer number 0-7  (default: 2)
echo   prefix    3-char DB prefix   (default: first 3 of module)
echo.
echo Feature options:
echo   --sql        Generate SQL migrations (V001/V002/V003)
echo   --tests      Generate test pyramid
echo   --docs       Generate README + API docs
echo   --routes     Print routing registration snippet
echo   --postman    Generate Postman collection
echo   --all        All of the above
echo.
echo Update options:
echo   --update     Update existing files (default behavior)
echo   --force      Update all without prompting
echo   --skip       Skip existing files
echo   --no-backup  Do not create .bak before update
echo   --quiet      No prompts, auto-update everything
echo.
echo Examples:
echo   create_modules.bat inventory 3 inv --all
echo   create_modules.bat money 2 mon --all --force
echo   create_modules.bat money 2 mon --update
echo   create_modules.bat money 2 mon --skip
echo   create_modules.bat help
echo.
echo ============================================================
echo.
pause
exit /b 0
@echo off
REM ============================================================
REM  Run SINGLE module (interactive prompt)
REM ============================================================
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ============================================================
echo   FastAPI Scaffold - Single Module
echo ============================================================
echo.

REM If module name passed as arg, use it
if not "%~1"=="" (
    set MODULE=%~1
    goto :run
)

echo Enter module name (e.g. audit, money, tenancy):
set /p MODULE="Module: "

if "%MODULE%"=="" (
    echo [ERROR] Module name is required.
    exit /b 1
)

:run
echo.
echo Running module: %MODULE%
echo.

call "%~dp0scaffold.bat" --module %MODULE%
exit /b %ERRORLEVEL%
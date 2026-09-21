@echo off
REM ============================================================
REM  Run ALL layers (0-7) = 65 modules
REM ============================================================
setlocal EnableExtensions

cd /d "%~dp0"

echo.
echo ============================================================
echo   Running ALL Layers (0-7) - 65 modules
echo ============================================================
echo.

call "%~dp0run-layer-0.bat"
if errorlevel 1 goto :fail
call "%~dp0run-layer-1.bat"
if errorlevel 1 goto :fail
call "%~dp0run-layer-2.bat"
if errorlevel 1 goto :fail
call "%~dp0run-layer-3.bat"
if errorlevel 1 goto :fail
call "%~dp0run-layer-4.bat"
if errorlevel 1 goto :fail
call "%~dp0run-layer-5.bat"
if errorlevel 1 goto :fail
call "%~dp0run-layer-6.bat"
if errorlevel 1 goto :fail
call "%~dp0run-layer-7.bat"
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo   [OK] ALL layers completed
echo ============================================================
exit /b 0

:fail
echo.
echo ============================================================
echo   [ERROR] A layer failed. Stopping.
echo ============================================================
exit /b 1
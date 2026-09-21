@echo off
REM Layer 1 - Foundation (8 modules)
cd /d "%~dp0"
echo.
echo ============================================================
echo   Layer 1 - Foundation (8 modules)
echo ============================================================
call "%~dp0scaffold.bat" --layer 1
exit /b %ERRORLEVEL%
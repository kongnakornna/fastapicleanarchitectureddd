@echo off
REM Layer 6 - Monitoring (8 modules)
cd /d "%~dp0"
echo.
echo ============================================================
echo   Layer 6 - Monitoring (8 modules)
echo ============================================================
call "%~dp0scaffold.bat" --layer 6
exit /b %ERRORLEVEL%
@echo off
REM Layer 0 - Core (6 modules)
cd /d "%~dp0"
echo.
echo ============================================================
echo   Layer 0 - Core (6 modules)
echo ============================================================
call "%~dp0scaffold.bat" --layer 0
exit /b %ERRORLEVEL%
@echo off
REM Layer 4 - Operations (13 modules)
cd /d "%~dp0"
echo.
echo ============================================================
echo   Layer 4 - Operations (13 modules)
echo ============================================================
call "%~dp0scaffold.bat" --layer 4
exit /b %ERRORLEVEL%
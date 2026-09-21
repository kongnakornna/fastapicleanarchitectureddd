@echo off
REM Layer 2 - Money Path (7 modules)
cd /d "%~dp0"
echo.
echo ============================================================
echo   Layer 2 - Money Path (7 modules)
echo ============================================================
call "%~dp0scaffold.bat" --layer 2
exit /b %ERRORLEVEL%
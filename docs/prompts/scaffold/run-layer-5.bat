@echo off
REM Layer 5 - Intelligence (7 modules)
cd /d "%~dp0"
echo.
echo ============================================================
echo   Layer 5 - Intelligence (7 modules)
echo ============================================================
call "%~dp0scaffold.bat" --layer 5
exit /b %ERRORLEVEL%
@echo off
REM Layer 7 - Templates (3 modules)
cd /d "%~dp0"
echo.
echo ============================================================
echo   Layer 7 - Templates (3 modules)
echo ============================================================
call "%~dp0scaffold.bat" --layer 7
exit /b %ERRORLEVEL%
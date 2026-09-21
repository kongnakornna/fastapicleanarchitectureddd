@echo off
REM Layer 3 - Goods Path (13 modules)
cd /d "%~dp0"
echo.
echo ============================================================
echo   Layer 3 - Goods Path (13 modules)
echo ============================================================
call "%~dp0scaffold.bat" --layer 3
exit /b %ERRORLEVEL%
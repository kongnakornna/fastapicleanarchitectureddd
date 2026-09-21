@echo off
REM ============================================================
REM  Run uvicorn dev server
REM ============================================================
cd /d "%~dp0"
call scaffold.bat --run
exit /b %ERRORLEVEL%
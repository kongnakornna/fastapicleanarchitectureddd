@echo off
REM ============================================================
REM  Setup venv + install dependencies
REM ============================================================
cd /d "%~dp0"
call scaffold.bat --setup
exit /b %ERRORLEVEL%
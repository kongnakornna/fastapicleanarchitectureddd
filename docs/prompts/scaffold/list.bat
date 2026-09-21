@echo off
REM ============================================================
REM  List all modules
REM ============================================================
cd /d "%~dp0"
call scaffold.bat --list
exit /b %ERRORLEVEL%
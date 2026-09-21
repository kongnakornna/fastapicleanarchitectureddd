@echo off
REM ============================================================
REM  Clean all generated files
REM ============================================================
cd /d "%~dp0"
call scaffold.bat --clean
exit /b %ERRORLEVEL%
@echo off
REM ============================================================
REM  create_modules.bat
REM  Wrapper — เรียก PowerShell เพื่อสร้าง module structure
REM ============================================================
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_modules.ps1"
pause
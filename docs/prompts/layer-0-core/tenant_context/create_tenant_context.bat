@echo off
REM ============================================================
REM  create_tenant_context.bat
REM  Wrapper — เรียก PowerShell สร้าง module tenant_context
REM ============================================================
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_tenant_context.ps1"
pause
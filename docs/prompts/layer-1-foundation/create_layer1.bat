@echo off
REM ============================================================
REM  create_layer1.bat
REM  Wrapper — เรียก PowerShell สร้าง modules Layer 1 ทั้งหมด
REM ============================================================
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_layer1.ps1"
pause
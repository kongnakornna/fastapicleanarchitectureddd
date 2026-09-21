@echo off
chcp 65001 >nul
title FastAPI Clean Architecture DDD Setup

echo ========================================
echo   FastAPI Clean Architecture DDD Setup  
echo ========================================
echo.

REM ตรวจสอบ uv
echo [1/6] ตรวจสอบ uv...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo   ไม่พบ uv - กำลังติดตั้ง...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
) else (
    echo   uv พร้อมใช้งาน
)

REM ตรวจสอบ Python
echo [2/6] ตรวจสอบ Python...
uv python list | findstr "3.13" >nul
if %errorlevel% neq 0 (
    echo   กำลังติดตั้ง Python 3.13...
    uv python install 3.13
) else (
    echo   Python 3.13 พร้อมใช้งาน
)

REM สร้าง .env
echo [3/6] ตั้งค่า Environment Variables...
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo   สร้างไฟล์ .env จาก .env.example แล้ว
        echo   กรุณาแก้ไขไฟล์ .env ก่อนรันแอปพลิเคชัน
    ) else (
        echo   ไม่พบไฟล์ .env.example
    )
) else (
    echo   ไฟล์ .env มีอยู่แล้ว
)

REM ติดตั้ง dependencies
echo [4/6] ติดตั้ง dependencies...
call uv sync

REM ติดตั้ง dev dependencies
echo [5/6] ติดตั้ง dev dependencies...
call uv sync --group dev

REM ตรวจสอบการติดตั้ง
echo [6/6] ตรวจสอบการติดตั้ง...
echo.
echo Python version:
call uv run python -V
echo.
echo FastAPI version:
call uv run python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
echo.

echo ========================================
echo   การติดตั้งเสร็จสมบูรณ์!              
echo ========================================
echo.
echo วิธีรันแอปพลิเคชัน:
echo   uv run -- uvicorn app.app:app --reload
echo.
echo เปิด browser: http://localhost:8000/docs
echo.
pause

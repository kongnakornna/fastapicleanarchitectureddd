@echo off
setlocal
chcp 65001 >nul

REM ============================================================
REM  dev.bat
REM  Clean venv -> uv sync -> pin python 3.13 -> migrate -> run
REM  ใช้:  scripts\dev.bat
REM       scripts\dev.bat clean    (ลบ venv ก่อน)
REM       scripts\dev.bat fresh    (ลบ venv + reset DB)
REM ============================================================

pushd "%~dp0\.."

set "MODE=%~1"
if "%MODE%"=="" set "MODE=normal"

echo ============================================================
echo  FastAPI Dev Bootstrap  [mode=%MODE%]
echo ============================================================
echo.

REM --- ตรวจ uv ---
where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] ไม่พบ uv — ติดตั้งก่อน: https://docs.astral.sh/uv/
    popd & exit /b 1
)

REM --- fresh = clean + reset-db ---
if /I "%MODE%"=="fresh" (
    echo [MODE=fresh] จะ reset DB ด้วย...
    call "%~dp0reset-db.bat" /y
    if errorlevel 1 (
        echo [ERROR] reset-db ล้มเหลว
        popd & exit /b 1
    )
    set "MODE=clean"
)

REM --- clean venv ---
if /I "%MODE%"=="clean" (
    echo [1/4] ลบ .venv เก่า ...
    if exist ".venv" rmdir /s /q ".venv"
    echo [OK] ลบ .venv แล้ว
)

REM --- pin python ---
echo [2/4] Pin Python 3.13 ...
uv python pin 3.13
if errorlevel 1 (
    echo [WARN] pin python ล้มเหลว — ใช้เวอร์ชันเดิม
)

REM --- sync ---
echo [3/4] uv sync ...
uv sync
if errorlevel 1 (
    echo [ERROR] uv sync ล้มเหลว
    popd & exit /b 1
)

REM --- migrate (เฉพาะโหมด fresh, ถ้าไม่ fresh ให้ข้ามได้) ---
if /I "%MODE%"=="fresh" (
    echo [SKIP] migrate ถูกทำใน reset-db แล้ว
) else (
    echo [4/4] (ทางเลือก) จะรัน alembic upgrade head ไหม? ถ้าไม่ต้องการกด N
    choice /c YN /n /m "Upgrade migration? [Y/N]: "
    if errorlevel 2 goto :run
    uv run alembic upgrade head
)

:run
echo.
echo ============================================================
echo  เริ่ม uvicorn ...
echo ============================================================
uv run uvicorn app.app:app --reload
set "RC=%ERRORLEVEL%"

popd
endlocal & exit /b %RC%
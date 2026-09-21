@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

REM ============================================================
REM  reset-db.bat
REM  Drop DB -> ลบ migration เก่า -> generate ใหม่ -> upgrade
REM  ใช้:  scripts\reset-db.bat        (ถามยืนยัน)
REM       scripts\reset-db.bat /y     (ไม่ถาม)
REM ============================================================

REM --- ย้ายไปที่ root ของ fastapi-backend ---
pushd "%~dp0\.."
set "PROJECT_ROOT=%CD%"
echo [INFO] Project root: %PROJECT_ROOT%
echo.

REM --- อ่านค่า .env (เฉพาะที่ต้องการ) ---
set "PG_HOST=localhost"
set "PG_PORT=5437"
set "PG_USER=postgres"
set "PG_PASS=postgres"
set "PG_DB=ioterp"

if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "KEY=%%A"
        set "VAL=%%B"
        if "!KEY!"=="POSTGRESQL_HOST"     set "PG_HOST=!VAL!"
        if "!KEY!"=="POSTGRESQL_PORT"     set "PG_PORT=!VAL!"
        if "!KEY!"=="POSTGRESQL_USERNAME" set "PG_USER=!VAL!"
        if "!KEY!"=="POSTGRESQL_PASSWORD" set "PG_PASS=!VAL!"
        if "!KEY!"=="POSTGRESQL_DATABASE" set "PG_DB=!VAL!"
    )
)

REM ตัด quote ถ้ามี
set "PG_HOST=%PG_HOST:"=%"
set "PG_PORT=%PG_PORT:"=%"
set "PG_USER=%PG_USER:"=%"
set "PG_PASS=%PG_PASS:"=%"
set "PG_DB=%PG_DB:"=%"

echo [INFO] Target DB: %PG_USER%@%PG_HOST%:%PG_PORT%/%PG_DB%
echo.

REM --- ยืนยัน ---
if /I not "%~1"=="/y" (
    set /p "CONFIRM=⚠️  จะ DROP database '%PG_DB%' และลบ migration ทั้งหมด. พิมพ์ YES เพื่อยืนยัน: "
    if /I not "!CONFIRM!"=="YES" (
        echo [CANCEL] ยกเลิก
        popd
        exit /b 1
    )
)

REM --- ตรวจ psql ---
where psql >nul 2>nul
if errorlevel 1 (
    echo [ERROR] ไม่พบ psql ใน PATH
    echo         เพิ่ม C:\Program Files\PostgreSQL\17\bin เข้า PATH แล้วลองใหม่
    popd
    exit /b 1
)

REM --- ตรวจ uv ---
where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] ไม่พบ uv ใน PATH
    popd
    exit /b 1
)

set "PGPASSWORD=%PG_PASS%"

REM ============================================================
REM STEP 1: DROP + CREATE DATABASE
REM ============================================================
echo.
echo [STEP 1/5] Drop + recreate database '%PG_DB%' ...
psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d postgres -v ON_ERROR_STOP=1 ^
     -c "DROP DATABASE IF EXISTS %PG_DB% WITH (FORCE);"
if errorlevel 1 (
    echo [ERROR] DROP DATABASE ล้มเหลว
    popd & exit /b 1
)

psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d postgres -v ON_ERROR_STOP=1 ^
     -c "CREATE DATABASE %PG_DB%;"
if errorlevel 1 (
    echo [ERROR] CREATE DATABASE ล้มเหลว
    popd & exit /b 1
)

REM ============================================================
REM STEP 2: ลบ migration เก่า
REM ============================================================
echo.
echo [STEP 2/5] ลบ migration เก่าใน migrations\versions ...
if exist "migrations\versions\*.py" (
    del /q "migrations\versions\*.py"
)
if exist "migrations\versions\__pycache__" (
    rmdir /s /q "migrations\versions\__pycache__"
)
echo [OK] ลบแล้ว

REM ============================================================
REM STEP 3: ตรวจ metadata เห็น models
REM ============================================================
echo.
echo [STEP 3/5] ตรวจสอบว่า Base.metadata เห็น models ...
uv run python -c "from app.infrastructure.database.base import Base; print('[OK] tables:', len(Base.metadata.tables)); [print(' -', t) for t in sorted(Base.metadata.tables)]"
if errorlevel 1 (
    echo [ERROR] import Base หรือ models ล้มเหลว
    echo         แก้ path ใน migrations\env.py ให้ตรงกับโปรเจกต์ก่อน
    popd & exit /b 1
)

REM ============================================================
REM STEP 4: Autogenerate
REM ============================================================
echo.
echo [STEP 4/5] Autogenerate initial migration ...
uv run alembic revision --autogenerate -m "init erp tables"
if errorlevel 1 (
    echo [ERROR] autogenerate ล้มเหลว
    popd & exit /b 1
)

REM ตรวจว่าไม่มี copy1 / ชื่อเก่าหลงเหลือ
echo [CHECK] หา copy1 / fastapi_clean_architecture_ddd_template ใน migration ใหม่ ...
findstr /S /I /M "copy1 fastapi_clean_architecture_ddd_template" "migrations\versions\*.py" >nul
if not errorlevel 1 (
    echo [WARN] ยังเจอชื่อ index/table เก่าใน migration ใหม่
    echo        ตรวจ migrations\env.py ว่า target_metadata = Base.metadata จริง
)

REM ============================================================
REM STEP 5: Upgrade head
REM ============================================================
echo.
echo [STEP 5/5] Upgrade to head ...
uv run alembic upgrade head
if errorlevel 1 (
    echo [ERROR] alembic upgrade ล้มเหลว
    popd & exit /b 1
)

REM --- แสดงผล ---
echo.
echo ============================================================
echo [DONE] Migration สำเร็จ
echo ============================================================
echo.
echo Tables:
psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d %PG_DB% -c "\dt"
echo.
echo Indexes:
psql -h %PG_HOST% -p %PG_PORT% -U %PG_USER% -d %PG_DB% -c "\di"

popd
endlocal
exit /b 0
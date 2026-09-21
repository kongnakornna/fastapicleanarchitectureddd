@echo off
REM ═══════════════════════════════════════════════════════════════
REM  create_modules.bat
REM  Wrapper — เรียก PowerShell เพื่อสร้าง/แก้ไข module
REM  (Generic Module Generator for ERP+CRM+IoT)
REM
REM  USAGE:
REM    create_modules.bat <action> <module> [layer] [prefix] [options]
REM
REM  ACTIONS:
REM    new       สร้าง module ใหม่ (4 layers + __init__)
REM    sql       สร้าง SQL migrations V001/V002/V003
REM    routes    Register router + model
REM    test      สร้าง tests (unit/integration/property/manual)
REM    docs      สร้าง docs (README + API)
REM    template  Generate OpenCode prompt ตาม Template A-G
REM    all       ทำทุกอย่าง
REM    help      แสดง help
REM
REM  OPTIONS:
REM    --sql     สร้าง SQL
REM    --tests   สร้าง tests
REM    --docs    สร้าง docs
REM    --routes  register router + model
REM    --force   เขียนทับไฟล์เดิม
REM    --template=A|B|C|D|E|F|G
REM
REM  EXAMPLES:
REM    create_modules.bat new inventory 3 inv --sql --tests --docs --routes
REM    create_modules.bat template A inventory 3 inv
REM    create_modules.bat sql invoice inv
REM    create_modules.bat all sales 4 sal --force
REM    create_modules.bat help
REM ═══════════════════════════════════════════════════════════════

chcp 65001 >nul
setlocal EnableDelayedExpansion

REM ─── หา PowerShell ─────────────────────────────────────────
where powershell >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PowerShell not found in PATH
    exit /b 1
)

set "PS_SCRIPT=%~dp0create_module.ps1"
if not exist "%PS_SCRIPT%" (
    echo [ERROR] create_module.ps1 not found at:
    echo        %PS_SCRIPT%
    echo.
    echo กรุณาวาง create_module.ps1 ไว้โฟลเดอร์เดียวกับ create_modules.bat
    exit /b 1
)

REM ─── ไม่มี argument → แสดง help ───────────────────────────
if "%~1"=="" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" -Action help
    goto :end
)

REM ─── ส่งต่อ argument ทั้งหมด ───────────────────────────────
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*
set "EXITCODE=%ERRORLEVEL%"

:end
echo.
if not "%EXITCODE%"=="0" (
    echo [ERROR] Exit code %EXITCODE%
) else (
    echo [DONE] Completed successfully.
)
echo.
pause
endlocal
exit /b %EXITCODE%
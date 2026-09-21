@echo off
REM ============================================================
REM  Verify that all 65 modules exist
REM ============================================================
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set BACKEND=..\..\fastapi-backend
set MODULES=%BACKEND%\app\modules

if not exist "%MODULES%" (
    echo [ERROR] Modules directory not found: %MODULES%
    exit /b 1
)

echo.
echo ============================================================
echo   Verifying 65 modules
echo ============================================================
echo.

set EXPECTED=65
set FOUND=0
set MISSING=

REM Expected module list
for %%M in (
    money tenant_context audit idempotency config events
    tenancy authentication user employee customer supplier product pricing
    order invoice ledger payment accounting_gateway tax reconciliation
    inventory warehouse deviceiot production recipe quality waste
    procurement traceability agriculture crop soil irrigation
    transport delivery route gps retail pos shift
    line_channel promotion loyalty crm campaign support
    reporting analytics forecast kpi satisfaction recommendation oee
    iot cctv monitoring backup alerting audit_viewer maintenance energy
    health example blank
) do (
    if exist "%MODULES%\%%M" (
        set /a FOUND+=1
    ) else (
        set MISSING=!MISSING! %%M
        echo    [MISSING] %%M
    )
)

echo.
echo ============================================================
echo   Found:   %FOUND% / %EXPECTED%
if not "!MISSING!"=="" (
    echo   Missing:!MISSING!
)
echo ============================================================
echo.

if %FOUND% EQU %EXPECTED% (
    echo [OK] All 65 modules present.
    exit /b 0
) else (
    echo [ERR] Missing modules detected.
    exit /b 1
)
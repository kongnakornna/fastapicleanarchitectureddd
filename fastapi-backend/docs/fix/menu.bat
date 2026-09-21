@echo off
REM ============================================================
REM  menu.bat - Project utility menu
REM ============================================================

:menu
cls
echo.
echo ============================================================
echo   FastAPI Project - Utility Menu
echo ============================================================
echo.
echo   [1] Fix lint errors         (fix_lint.bat)
echo   [2] Full health check       (check_all.bat)
echo   [3] Start dev server        (dev_start.bat)
echo   [4] Reset Alembic           (reset_alembic.bat)
echo   [5] Run tests
echo   [6] Run migrations only
echo   [7] Format code only
echo   [8] Sync dependencies
echo   [0] Exit
echo.
echo ============================================================
set /p CHOICE="Select option: "

if "%CHOICE%"=="1" ( call fix_lint.bat & pause & goto menu )
if "%CHOICE%"=="2" ( call check_all.bat & pause & goto menu )
if "%CHOICE%"=="3" ( call dev_start.bat & pause & goto menu )
if "%CHOICE%"=="4" ( call reset_alembic.bat & pause & goto menu )
if "%CHOICE%"=="5" ( uv run pytest & pause & goto menu )
if "%CHOICE%"=="6" ( uv run alembic upgrade head & pause & goto menu )
if "%CHOICE%"=="7" ( uv run ruff format . & pause & goto menu )
if "%CHOICE%"=="8" ( uv sync & pause & goto menu )
if "%CHOICE%"=="0" ( exit /b 0 )

echo Invalid choice.
timeout /t 2 >nul
goto menu
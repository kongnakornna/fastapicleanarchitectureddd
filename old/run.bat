@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:menu
cls
echo ╔══════════════════════════════════════════════╗
echo ║     ICMON Auto Repair - FastAPI DDD         ║
echo ║     Project Runner Menu                      ║
echo ╠══════════════════════════════════════════════╣
echo ║                                              ║
echo ║  [1]  Run Server (Dev)                       ║
echo ║  [2]  Run Server (Prod)                      ║
echo ║  [3]  Run Tests                              ║
echo ║  [4]  Run Tests (Verbose)                    ║
echo ║  [5]  Run Tests + Coverage                   ║
echo ║  [6]  Run Lint                               ║
echo ║  [7]  Run Lint + Fix                         ║
echo ║  [8]  Run Type Check                         ║
echo ║                                              ║
echo ║  ── Database ──                              ║
echo ║  [10] Migration: Auto Generate               ║
echo ║  [11] Migration: Apply (Upgrade)             ║
echo ║  [12] Migration: Rollback (Downgrade)        ║
echo ║  [13] Migration: Current Version             ║
echo ║  [14] Migration: History                     ║
echo ║  [15] Migration: Stamp Head                  ║
echo ║                                              ║
echo ║  ── Docker ──                                ║
echo ║  [20] Docker: Start All                      ║
echo ║  [21] Docker: Stop All                       ║
echo ║  [22] Docker: Restart All                    ║
echo ║  [23] Docker: Start DB Only                  ║
echo ║  [24] Docker: Logs                           ║
echo ║  [25] Docker: Status                         ║
echo ║                                              ║
echo ║  ── MQTT ──                                  ║
echo ║  [30] MQTT: Start Mosquitto                  ║
echo ║  [31] MQTT: Stop Mosquitto                   ║
echo ║  [32] MQTT: Test Subscribe                   ║
echo ║  [33] MQTT: Test Publish                     ║
echo ║                                              ║
echo ║  ── Info ──                                  ║
echo ║  [40] Show Project Structure                 ║
echo ║  [41] Show API Endpoints                     ║
echo ║  [42] Show Database Tables                   ║
echo ║  [43] Show All Module Sizes                  ║
echo ║                                              ║
echo ║  [0]  Exit                                   ║
echo ║                                              ║
echo ╚══════════════════════════════════════════════╝
echo.
set /p choice="Select: "

if "%choice%"=="1" goto run_server
if "%choice%"=="2" goto run_server_prod
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto run_tests_verbose
if "%choice%"=="5" goto run_tests_coverage
if "%choice%"=="6" goto run_lint
if "%choice%"=="7" goto run_lint_fix
if "%choice%"=="8" goto run_typecheck
if "%choice%"=="10" goto migration_generate
if "%choice%"=="11" goto migration_upgrade
if "%choice%"=="12" goto migration_downgrade
if "%choice%"=="13" goto migration_current
if "%choice%"=="14" goto migration_history
if "%choice%"=="15" goto migration_stamp
if "%choice%"=="20" goto docker_start
if "%choice%"=="21" goto docker_stop
if "%choice%"=="22" goto docker_restart
if "%choice%"=="23" goto docker_start_db
if "%choice%"=="24" goto docker_logs
if "%choice%"=="25" goto docker_status
if "%choice%"=="30" goto mqtt_start
if "%choice%"=="31" goto mqtt_stop
if "%choice%"=="32" goto mqtt_test_sub
if "%choice%"=="33" goto mqtt_test_pub
if "%choice%"=="40" goto show_structure
if "%choice%"=="41" goto show_endpoints
if "%choice%"=="42" goto show_tables
if "%choice%"=="43" goto show_modules
if "%choice%"=="0" exit /b

echo Invalid choice!
timeout /t 2 >nul
goto menu

:: ============================================================
:: RUN SERVER
:: ============================================================

:run_server
echo Starting dev server on http://127.0.0.1:8000 ...
echo Press Ctrl+C to stop
python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
pause
goto menu

:run_server_prod
echo Starting production server...
python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 --workers 4
pause
goto menu

:: ============================================================
:: TESTS
:: ============================================================

:run_tests
cls
echo Running tests...
echo.
python -m pytest test/ -q --tb=short
echo.
pause
goto menu

:run_tests_verbose
cls
echo Running tests (verbose)...
echo.
python -m pytest test/ -v --tb=short
echo.
pause
goto menu

:run_tests_coverage
cls
echo Running tests with coverage...
echo.
python -m pytest test/ -q --tb=short --cov=app --cov-report=term-missing
echo.
pause
goto menu

:: ============================================================
:: LINT / TYPE CHECK
:: ============================================================

:run_lint
cls
echo Running ruff lint...
echo.
python -m ruff check app/ test/
echo.
pause
goto menu

:run_lint_fix
cls
echo Running ruff lint with auto-fix...
echo.
python -m ruff check app/ test/ --fix
echo.
pause
goto menu

:run_typecheck
cls
echo Running type check...
echo.
python -m mypy app/ --ignore-missing-imports
echo.
pause
goto menu

:: ============================================================
:: DATABASE MIGRATIONS
:: ============================================================

:migration_generate
echo.
set /p msg="Migration message: "
python -m alembic revision --autogenerate -m "%msg%"
echo.
pause
goto menu

:migration_upgrade
echo.
echo Applying migrations to head...
python -m alembic upgrade head
echo.
pause
goto menu

:migration_downgrade
echo.
echo Downgrading one revision...
python -m alembic downgrade -1
echo.
pause
goto menu

:migration_current
echo.
python -m alembic current
echo.
pause
goto menu

:migration_history
echo.
python -m alembic history --verbose
echo.
pause
goto menu

:migration_stamp
echo.
echo Stamping database to head...
python -m alembic stamp head
echo.
pause
goto menu

:: ============================================================
:: DOCKER
:: ============================================================

:docker_start
cls
echo Starting all services...
docker-compose up -d
echo.
pause
goto menu

:docker_stop
cls
echo Stopping all services...
docker-compose down
echo.
pause
goto menu

:docker_restart
cls
echo Restarting all services...
docker-compose restart
echo.
pause
goto menu

:docker_start_db
cls
echo Starting PostgreSQL + InfluxDB...
docker-compose up -d postgres influxdb
echo.
pause
goto menu

:docker_logs
cls
echo Showing docker logs (Ctrl+C to stop)...
docker-compose logs -f
echo.
pause
goto menu

:docker_status
cls
echo Docker status:
docker-compose ps
echo.
pause
goto menu

:: ============================================================
:: MQTT
:: ============================================================

:mqtt_start
cls
echo Starting Mosquitto...
"C:\mosquitto\mosquitto.exe" -c "C:\mosquitto\mosquitto.conf" -d
if %errorlevel%==0 (
    echo Mosquitto started
) else (
    echo Failed to start. Check C:\mosquitto\
)
echo.
pause
goto menu

:mqtt_stop
cls
echo Stopping Mosquitto...
taskkill /F /IM mosquitto.exe 2>nul
if %errorlevel%==0 (
    echo Mosquitto stopped
) else (
    echo Mosquitto not running
)
echo.
pause
goto menu

:mqtt_test_sub
cls
echo Subscribing to test/# (Ctrl+C to stop)...
"C:\mosquitto\mosquitto_sub.exe" -t "test/#" -v
echo.
pause
goto menu

:mqtt_test_pub
cls
echo Publishing test message...
"C:\mosquitto\mosquitto_pub.exe" -t "test/hello" -m "Hello MQTT from ICMON"
echo Published: test/hello -> "Hello MQTT from ICMON"
echo.
pause
goto menu

:: ============================================================
:: INFO
:: ============================================================

:show_structure
cls
echo Project Structure:
echo.
tree /F /A app\modules | findstr /V "__pycache__" | findstr /V ".pyc"
echo.
pause
goto menu

:show_endpoints
cls
echo API Endpoints:
echo.
python scripts/info.py endpoints
echo.
pause
goto menu

:show_tables
cls
echo Database tables:
echo.
python scripts/info.py tables
echo.
pause
goto menu

:show_modules
cls
echo Module sizes:
echo.
python scripts/info.py modules
echo.
pause
goto menu

@echo off
REM ═══════════════════════════════════════════════════════════════
REM scripts/create_modules.bat
REM TH: Scaffold module DDD + Clean Arch สำหรับ Windows
REM EN: DDD + Clean Arch module scaffolder for Windows
REM ═══════════════════════════════════════════════════════════════
setlocal EnableDelayedExpansion

REM ─── Colors ─────────────────────────────────────
for /F %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "BLUE=%ESC%[94m"
set "RESET=%ESC%[0m"

REM ─── Vars ───────────────────────────────────────
set "PROJECT_ROOT=%~dp0.."
set "SKILL_ROOT=%~dp0.."

REM ═══════════════════════════════════════════════════════════════
REM Main entry
REM ═══════════════════════════════════════════════════════════════
if "%~1"=="" goto :usage
if /I "%~1"=="help" goto :usage
if /I "%~1"=="-h" goto :usage
if /I "%~1"=="--help" goto :usage

set "CMD=%~1"
shift

if /I "%CMD%"=="new"      goto :cmd_new
if /I "%CMD%"=="all"      goto :cmd_all
if /I "%CMD%"=="template" goto :cmd_template
if /I "%CMD%"=="sql"      goto :cmd_sql
if /I "%CMD%"=="routes"   goto :cmd_routes
if /I "%CMD%"=="test"     goto :cmd_test
if /I "%CMD%"=="docs"     goto :cmd_docs
if /I "%CMD%"=="debug"    goto :cmd_debug

echo %RED%[ERROR]%RESET% Unknown command: %CMD%
goto :usage


REM ═══════════════════════════════════════════════════════════════
REM COMMAND: new <module> <layer> <prefix> [--sql --tests --docs --routes --force]
REM ═══════════════════════════════════════════════════════════════
:cmd_new
set "MODULE=%~1"
set "LAYER=%~2"
set "PREFIX=%~3"
shift & shift & shift

if "%MODULE%"=="" (
  echo %RED%[ERROR]%RESET% Missing module name.
  echo Usage: create_modules.bat new ^<module^> ^<layer^> ^<prefix^> [flags]
  exit /b 1
)
if "%LAYER%"=="" set "LAYER=0"
if "%PREFIX%"=="" (
  REM derive prefix = first 3 chars of module
  set "PREFIX=!MODULE:~0,3!"
)

REM ─── Parse flags ────────────────────────────────
set "FLAG_SQL=0"
set "FLAG_TESTS=0"
set "FLAG_DOCS=0"
set "FLAG_ROUTES=0"
set "FLAG_FORCE=0"

:parse_new_flags
if "%~1"=="" goto :parse_new_done
if /I "%~1"=="--sql"    set "FLAG_SQL=1"
if /I "%~1"=="--tests"  set "FLAG_TESTS=1"
if /I "%~1"=="--docs"   set "FLAG_DOCS=1"
if /I "%~1"=="--routes" set "FLAG_ROUTES=1"
if /I "%~1"=="--force"  set "FLAG_FORCE=1"
shift
goto :parse_new_flags
:parse_new_done

call :banner "CREATE MODULE: %MODULE%"
call :kv "module"  "%MODULE%"
call :kv "layer"   "%LAYER%"
call :kv "prefix"  "%PREFIX%"
call :kv "sql"     "%FLAG_SQL%"
call :kv "tests"   "%FLAG_TESTS%"
call :kv "docs"    "%FLAG_DOCS%"
call :kv "routes"  "%FLAG_ROUTES%"
echo.

call :ensure_module_dirs "%MODULE%"
call :write_module_files "%MODULE%" "%LAYER%" "%PREFIX%"

if "%FLAG_SQL%"=="1"    call :write_sql_files "%MODULE%" "%PREFIX%"
if "%FLAG_TESTS%"=="1"  call :write_test_files "%MODULE%"
if "%FLAG_DOCS%"=="1"   call :write_docs_files "%MODULE%" "%LAYER%" "%PREFIX%"
if "%FLAG_ROUTES%"=="1" call :print_routes_hint "%MODULE%"

echo.
echo %GREEN%[OK]%RESET% Module '%MODULE%' scaffolded.
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM COMMAND: all <module> <layer> <prefix> [--force]
REM ═══════════════════════════════════════════════════════════════
:cmd_all
set "MODULE=%~1"
set "LAYER=%~2"
set "PREFIX=%~3"
shift & shift & shift

if "%MODULE%"=="" (
  echo %RED%[ERROR]%RESET% Missing module name.
  exit /b 1
)
if "%LAYER%"=="" set "LAYER=0"
if "%PREFIX%"=="" set "PREFIX=!MODULE:~0,3!"

set "FLAG_FORCE=0"
:parse_all_flags
if "%~1"=="" goto :parse_all_done
if /I "%~1"=="--force" set "FLAG_FORCE=1"
shift
goto :parse_all_flags
:parse_all_done

call :banner "CREATE ALL: %MODULE%"
call :ensure_module_dirs "%MODULE%"
call :write_module_files "%MODULE%" "%LAYER%" "%PREFIX%"
call :write_sql_files "%MODULE%" "%PREFIX%"
call :write_test_files "%MODULE%"
call :write_docs_files "%MODULE%" "%LAYER%" "%PREFIX%"
call :print_routes_hint "%MODULE%"

echo.
echo %GREEN%[OK]%RESET% All sections scaffolded for '%MODULE%'.
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM COMMAND: template <A-G> <module> <layer> <prefix>
REM ═══════════════════════════════════════════════════════════════
:cmd_template
set "T=%~1"
set "MODULE=%~2"
set "LAYER=%~3"
set "PREFIX=%~4"

if "%T%"=="" (
  echo %RED%[ERROR]%RESET% Missing template letter (A-G).
  exit /b 1
)
if "%MODULE%"=="" (
  echo %RED%[ERROR]%RESET% Missing module name.
  exit /b 1
)

call :banner "TEMPLATE %T%: %MODULE%"
echo %BLUE%[INFO]%RESET% Emit prompt for: claude "/python-ddd-clean-arch"
echo.
echo ----------------------------------------
echo TEMPLATE %T% - Module: %MODULE% - Layer: %LAYER% - Prefix: %PREFIX%
echo ----------------------------------------
echo.
echo Paste เนื้อหาจาก reference/11-cheatsheet.md (Universal Header) แล้วเพิ่ม:
echo   - Task Type: %T%
echo   - Module: %MODULE%
echo   - Layer: %LAYER%
echo   - Prefix: %PREFIX%
echo.
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM COMMAND: sql <module> <prefix>
REM ═══════════════════════════════════════════════════════════════
:cmd_sql
set "MODULE=%~1"
set "PREFIX=%~2"
if "%MODULE%"=="" ( echo %RED%[ERROR]%RESET% Missing module. & exit /b 1 )
if "%PREFIX%"=="" set "PREFIX=!MODULE:~0,3!"
call :banner "SQL: %MODULE%"
call :write_sql_files "%MODULE%" "%PREFIX%"
echo %GREEN%[OK]%RESET% SQL files written.
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM COMMAND: routes <module>
REM ═══════════════════════════════════════════════════════════════
:cmd_routes
set "MODULE=%~1"
if "%MODULE%"=="" ( echo %RED%[ERROR]%RESET% Missing module. & exit /b 1 )
call :banner "ROUTES: %MODULE%"
call :print_routes_hint "%MODULE%"
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM COMMAND: test <module>
REM ═══════════════════════════════════════════════════════════════
:cmd_test
set "MODULE=%~1"
if "%MODULE%"=="" ( echo %RED%[ERROR]%RESET% Missing module. & exit /b 1 )
call :banner "TESTS: %MODULE%"
call :write_test_files "%MODULE%"
echo %GREEN%[OK]%RESET% Test files written.
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM COMMAND: docs <module> <layer> <prefix>
REM ═══════════════════════════════════════════════════════════════
:cmd_docs
set "MODULE=%~1"
set "LAYER=%~2"
set "PREFIX=%~3"
if "%MODULE%"=="" ( echo %RED%[ERROR]%RESET% Missing module. & exit /b 1 )
if "%LAYER%"=="" set "LAYER=0"
if "%PREFIX%"=="" set "PREFIX=!MODULE:~0,3!"
call :banner "DOCS: %MODULE%"
call :write_docs_files "%MODULE%" "%LAYER%" "%PREFIX%"
echo %GREEN%[OK]%RESET% Docs written.
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM COMMAND: debug <module>
REM ═══════════════════════════════════════════════════════════════
:cmd_debug
set "MODULE=%~1"
if "%MODULE%"=="" ( echo %RED%[ERROR]%RESET% Missing module. & exit /b 1 )
call :banner "DEBUG: %MODULE%"
echo %YELLOW%[DEBUG]%RESET% ใช้ checklist นี้:
echo   - [ ] Reproducible test (RED)
echo   - [ ] Root cause file:line
echo   - [ ] Fix minimal
echo   - [ ] Regression test (GREEN)
echo   - [ ] Coverage ไม่ลด
echo   - [ ] trace_id ครบทุก layer
echo   - [ ] ไม่มี PII ใน log
echo.
echo Commands:
echo   LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload
echo   pytest -vv --tb=long --log-cli-level=DEBUG -k "%MODULE%"
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM USAGE
REM ═══════════════════════════════════════════════════════════════
:usage
echo.
echo %BLUE%python-ddd-clean-arch - Scaffolder%RESET%
echo.
echo USAGE:
echo   create_modules.bat ^<command^> [args] [flags]
echo.
echo COMMANDS:
echo   new ^<module^> ^<layer^> ^<prefix^> [--sql --tests --docs --routes --force]
echo   all ^<module^> ^<layer^> ^<prefix^> [--force]
echo   template ^<A-G^> ^<module^> ^<layer^> ^<prefix^>
echo   sql ^<module^> ^<prefix^>
echo   routes ^<module^>
echo   test ^<module^>
echo   docs ^<module^> ^<layer^> ^<prefix^>
echo   debug ^<module^>
echo   help
echo.
echo EXAMPLES:
echo   create_modules.bat new inventory 3 inv --sql --tests --docs --routes
echo   create_modules.bat all sales 4 sal
echo   create_modules.bat template A invoice 2 inv
echo.
exit /b 0


REM ═══════════════════════════════════════════════════════════════
REM Helpers
REM ═══════════════════════════════════════════════════════════════
:banner
echo.
echo %BLUE%========================================%RESET%
echo %BLUE% %~1%RESET%
echo %BLUE%========================================%RESET%
exit /b 0

:kv
echo   %YELLOW%%~1%RESET% = %~2
exit /b 0

:ensure_module_dirs
set "M=%~1"
set "BASE=%PROJECT_ROOT%\app\modules\%M%"
for %%D in (domain application infrastructure presentation) do (
  if not exist "%BASE%\%%D" (
    mkdir "%BASE%\%%D" 2>nul
    echo   %GREEN%+%RESET% %BASE%\%%D
  )
)
if not exist "%BASE%\__init__.py" (
  echo.> "%BASE%\__init__.py"
  echo   %GREEN%+%RESET% %BASE%\__init__.py
)
exit /b 0

:write_module_files
set "M=%~1"
set "L=%~2"
set "P=%~3"
set "BASE=%PROJECT_ROOT%\app\modules\%M%"

REM ─── domain/ ──────────────────────────────────────
for %%F in (entities.py value_objects.py enums.py events.py exceptions.py __init__.py) do (
  if not exist "%BASE%\domain\%%F" (
    echo.> "%BASE%\domain\%%F"
    echo   %GREEN%+%RESET% domain\%%F
  )
)
REM ─── application/ ─────────────────────────────────
for %%F in (interfaces.py use_cases.py mappers.py exceptions.py utils.py __init__.py) do (
  if not exist "%BASE%\application\%%F" (
    echo.> "%BASE%\application\%%F"
    echo   %GREEN%+%RESET% application\%%F
  )
)
REM ─── infrastructure/ ──────────────────────────────
for %%F in (models.py repositories.py caches.py services.py __init__.py) do (
  if not exist "%BASE%\infrastructure\%%F" (
    echo.> "%BASE%\infrastructure\%%F"
    echo   %GREEN%+%RESET% infrastructure\%%F
  )
)
REM ─── presentation/ ────────────────────────────────
for %%F in (routers.py schemas.py docs.py dependencies.py __init__.py) do (
  if not exist "%BASE%\presentation\%%F" (
    echo.> "%BASE%\presentation\%%F"
    echo   %GREEN%+%RESET% presentation\%%F
  )
)
exit /b 0

:write_sql_files
set "M=%~1"
set "P=%~2"
set "DIR=%PROJECT_ROOT%\db\migrations"
if not exist "%DIR%" mkdir "%DIR%" 2>nul
for %%V in (V001__create_%M%.sql V002__seed_%M%.sql V003__rollback_%M%.sql) do (
  if not exist "%DIR%\%%V" (
    echo.-- Module: %M% ^| Prefix: %P% > "%DIR%\%%V"
    echo.   %GREEN%+%RESET% db\migrations\%%V
  )
)
exit /b 0

:write_test_files
set "M=%~1"
set "DIR=%PROJECT_ROOT%\tests"
if not exist "%DIR%\unit"          mkdir "%DIR%\unit" 2>nul
if not exist "%DIR%\integration"   mkdir "%DIR%\integration" 2>nul
if not exist "%DIR%\property"      mkdir "%DIR%\property" 2>nul
if not exist "%DIR%\manual"        mkdir "%DIR%\manual" 2>nul

if not exist "%DIR%\unit\test_%M%.py" (
  echo.> "%DIR%\unit\test_%M%.py"
  echo   %GREEN%+%RESET% tests\unit\test_%M%.py
)
if not exist "%DIR%\unit\test_%M%_use_cases.py" (
  echo.> "%DIR%\unit\test_%M%_use_cases.py"
  echo   %GREEN%+%RESET% tests\unit\test_%M%_use_cases.py
)
if not exist "%DIR%\integration\test_%M%_repository.py" (
  echo.> "%DIR%\integration\test_%M%_repository.py"
  echo   %GREEN%+%RESET% tests\integration\test_%M%_repository.py
)
if not exist "%DIR%\property\test_%M%_invariants.py" (
  echo.> "%DIR%\property\test_%M%_invariants.py"
  echo   %GREEN%+%RESET% tests\property\test_%M%_invariants.py
)
if not exist "%DIR%\manual\manual_test_%M%.md" (
  echo.# Manual Test - %M% > "%DIR%\manual\manual_test_%M%.md"
  echo   %GREEN%+%RESET% tests\manual\manual_test_%M%.md
)
exit /b 0

:write_docs_files
set "M=%~1"
set "L=%~2"
set "P=%~3"
set "DIR=%PROJECT_ROOT%\docs"
if not exist "%DIR%" mkdir "%DIR%" 2>nul
if not exist "%DIR%\README_%M%.md" (
  echo.# Module: %M% ^(Layer %L%, Prefix %P%^) > "%DIR%\README_%M%.md"
  echo   %GREEN%+%RESET% docs\README_%M%.md
)
if not exist "%DIR%\API_%M%.md" (
  echo.# API Reference - %M% > "%DIR%\API_%M%.md"
  echo   %GREEN%+%RESET% docs\API_%M%.md
)
exit /b 0

:print_routes_hint
set "M=%~1"
echo.
echo %YELLOW%[ROUTES]%RESET% เพิ่มที่ %PROJECT_ROOT%\app\routes.py:
echo    from app.modules.%M%.presentation.routers import router as %M%_router
echo    api_router.include_router(%M%_router)
echo.
echo %YELLOW%[ROUTES]%RESET% เพิ่มที่ %PROJECT_ROOT%\migrations\env.py:
echo    from app.modules.%M%.infrastructure.models import %M%Model  # noqa: F401
exit /b 0
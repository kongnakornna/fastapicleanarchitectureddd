set SKIP_FLAG=
if exist "app\modules" (
    dir /b /a-d "app\modules" 2>nul | findstr . >nul
    if not errorlevel 1 (
        echo [INFO] app\modules exists — adding --skip-configs
        set SKIP_FLAG=--skip-configs
    )
)
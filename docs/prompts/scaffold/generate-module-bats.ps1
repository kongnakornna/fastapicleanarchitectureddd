# ============================================================
#  generate-module-bats.ps1
#  Auto-generate modules/<name>.bat for all 65 modules
# ============================================================

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptRoot

$ModulesDir = Join-Path $ScriptRoot "modules"
if (-not (Test-Path $ModulesDir)) {
    New-Item -ItemType Directory -Force -Path $ModulesDir | Out-Null
}

# --- Full module list ---
$AllModules = @(
    # Layer 0
    "money","tenant_context","audit","idempotency","config","events",
    # Layer 1
    "tenancy","authentication","user","employee","customer","supplier","product","pricing",
    # Layer 2
    "order","invoice","ledger","payment","accounting_gateway","tax","reconciliation",
    # Layer 3
    "inventory","warehouse","deviceiot","production","recipe","quality","waste",
    "procurement","traceability","agriculture","crop","soil","irrigation",
    # Layer 4
    "transport","delivery","route","gps","retail","pos","shift",
    "line_channel","promotion","loyalty","crm","campaign","support",
    # Layer 5
    "reporting","analytics","forecast","kpi","satisfaction","recommendation","oee",
    # Layer 6
    "iot","cctv","monitoring","backup","alerting","audit_viewer","maintenance","energy",
    # Layer 7
    "health","example","blank"
)

$EOL = "`r`n"
$created = 0

foreach ($mod in $AllModules) {
    $batPath = Join-Path $ModulesDir "$mod.bat"
    $content = @(
        '@echo off',
        'REM ============================================================',
        "REM  Run module: $mod",
        'REM ============================================================',
        'cd /d "%~dp0.."',
        'echo.',
        'echo ============================================================',
        "echo   Running module: $mod",
        'echo ============================================================',
        "call scaffold.bat --module $mod",
        'exit /b %ERRORLEVEL%',
        ''
    ) -join $EOL

    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($batPath, $content, $utf8)
    Write-Host "   [OK] modules/$mod.bat" -ForegroundColor Green
    $created++
}

Write-Host ""
Write-Host "Generated $created module .bat files" -ForegroundColor Cyan
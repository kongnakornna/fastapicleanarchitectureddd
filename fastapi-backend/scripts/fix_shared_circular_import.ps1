<#
.SYNOPSIS
    fix_shared_circular_import.ps1
    Fix circular import: domain/entities.py <-> domain/value_objects.py

.DESCRIPTION
    Creates app/modules/shared/domain/exceptions.py and rewires the
    imports so DomainError lives in exactly one place, with no cycle.

    Idempotent: safe to re-run. Backs up every touched file to
    <name>.bak.<yyyyMMddHHmmss>.

.PARAMETER Root
    Project root (folder containing app\, migrations\, .venv\)

.PARAMETER DryRun
    Print the plan; write nothing.

.PARAMETER NoVerify
    Skip the post-fix import smoke test.
#>
[CmdletBinding()]
param(
    [string]$Root    = (Get-Location).Path,
    [switch]$DryRun,
    [switch]$NoVerify
)

$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────
$domain   = Join-Path $Root "app\modules\shared\domain"
$app      = Join-Path $Root "app\modules\shared\application"
$entities = Join-Path $domain "entities.py"
$vos      = Join-Path $domain "value_objects.py"
$excNew   = Join-Path $domain "exceptions.py"
$appExc   = Join-Path $app    "exceptions.py"

foreach ($f in @($entities, $vos, $appExc)) {
    if (-not (Test-Path $f)) {
        throw "required file missing: $f"
    }
}

$ts      = Get-Date -Format "yyyyMMddHHmmss"
$utf8    = New-Object System.Text.UTF8Encoding($false)
$importNew = "from app.modules.shared.domain.exceptions import DomainError, DomainErrors  # noqa: F401"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " fix_shared_circular_import.ps1"          -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Root   : $Root"
Write-Host " Domain : $domain"
Write-Host " DryRun : $DryRun"
Write-Host " Backup : *.bak.$ts"
Write-Host "--------------------------------------------" -ForegroundColor Cyan

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
function Backup-File {
    param([string]$Path)
    if ($DryRun) { Write-Host "  [DRY]  backup $(Split-Path $Path -Leaf)" -ForegroundColor DarkGray; return }
    $bak = "$Path.bak.$ts"
    Copy-Item -LiteralPath $Path -Destination $bak
    Write-Host "  [BAK]  $(Split-Path $Path -Leaf)  ->  $(Split-Path $bak -Leaf)" -ForegroundColor DarkYellow
}

function Write-Text {
    param([string]$Path, [string]$Content)
    if ($DryRun) { Write-Host "  [DRY]  write  $(Split-Path $Path -Leaf)" -ForegroundColor DarkGray; return }
    [System.IO.File]::WriteAllText($Path, $Content, $utf8)
}

function Read-Text {
    param([string]$Path)
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

# ─────────────────────────────────────────────────────────────
# Step 1 — create domain/exceptions.py
# ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "--- [1/4] domain/exceptions.py ---" -ForegroundColor Yellow

if (Test-Path $excNew) {
    Write-Host "  [SKIP] already exists: $excNew" -ForegroundColor DarkYellow
    Write-Host "         (delete it manually if you want to regenerate)"
} else {
    $excContent = @'
"""Shared domain exceptions — ข้อยกเว้นโดเมนกลาง

TH: แยกออกมาเพื่อตัด circular import ระหว่าง
    domain/entities.py  <->  domain/value_objects.py
EN: Split out to break the circular import between
    domain/entities.py  <->  domain/value_objects.py
"""
from __future__ import annotations


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดระดับโดเมน"""

    def __init__(self, message: str = "Domain error") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class DomainErrors:
    """DomainErrors — รวม error code ของโดเมน"""

    NOT_FOUND   = "DOMAIN_NOT_FOUND"
    INVALID     = "DOMAIN_INVALID"
    DUPLICATE   = "DOMAIN_DUPLICATE"
    CONFLICT    = "DOMAIN_CONFLICT"


__all__ = ["DomainError", "DomainErrors"]
'@
    Write-Text -Path $excNew -Content $excContent
    Write-Host "  [OK]   created $excNew" -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────────
# Step 2 — patch domain/value_objects.py
# ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "--- [2/4] value_objects.py ---" -ForegroundColor Yellow

Backup-File $vos
$c = Read-Text $vos
$before = $c

# Order matters: absolute path first, then relative
$c = $c -replace 'from\s+app\.modules\.shared\.domain\.entities\s+import\s+DomainError',
                'from app.modules.shared.domain.exceptions import DomainError'
$c = $c -replace 'from\s+\.entities\s+import\s+DomainError',
                'from .exceptions import DomainError'

if ($c -eq $before) {
    Write-Host "  [WARN] no import line matched — check file manually" -ForegroundColor DarkYellow
} else {
    Write-Text -Path $vos -Content $c
    Write-Host "  [OK]   rewired import -> .exceptions" -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────────
# Step 3 — patch domain/entities.py
# ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "--- [3/4] entities.py ---" -ForegroundColor Yellow

Backup-File $entities
$c = Read-Text $entities

# 3a. Remove local `class DomainError...` and `class DomainErrors...`
#     Regex: from ^class DomainError<s?> to the next top-level class/def/@
$classRe = '(?ms)^class\s+DomainErrors?\b.*?(?=^(?:class|def|@)|\z)'
$hadLocal = ($c -match '(?m)^class\s+DomainErrors?\b')
if ($hadLocal) {
    $c = [regex]::Replace($c, $classRe, '')
    # collapse 3+ blank lines to 2
    $c = $c -replace '(\r?\n){3,}', "`r`n`r`n"
    Write-Host "  [OK]   removed local DomainError/DomainErrors class defs" -ForegroundColor Green
} else {
    Write-Host "  [INFO] no local class defs found (already moved?)" -ForegroundColor DarkYellow
}

# 3b. Insert the new import after the last top-level import
if ($c -notmatch 'from\s+app\.modules\.shared\.domain\.exceptions\s+import') {
    $lines = $c -split "`r?`n"
    $insertAt = 0
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^(import|from)\s') { $insertAt = $i + 1 }
    }
    $newLines = @()
    if ($insertAt -gt 0) { $newLines += $lines[0..($insertAt - 1)] }
    $newLines += $importNew
    if ($insertAt -lt $lines.Count) { $newLines += $lines[$insertAt..($lines.Count - 1)] }
    $c = ($newLines -join "`n")
    Write-Host "  [OK]   inserted import at line $($insertAt + 1)" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] import already present" -ForegroundColor DarkYellow
}

Write-Text -Path $entities -Content $c

# ─────────────────────────────────────────────────────────────
# Step 4 — patch application/exceptions.py
# ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "--- [4/4] application/exceptions.py ---" -ForegroundColor Yellow

Backup-File $appExc
$c = Read-Text $appExc
$before = $c

$c = $c -replace 'from\s+app\.modules\.shared\.domain\.entities\s+import\s+DomainError,\s*DomainErrors',
                'from app.modules.shared.domain.exceptions import DomainError, DomainErrors'
$c = $c -replace 'from\s+app\.modules\.shared\.domain\.entities\s+import\s+DomainError\b(?!,)',
                'from app.modules.shared.domain.exceptions import DomainError'
$c = $c -replace 'from\s+\.\.domain\.entities\s+import\s+DomainError,\s*DomainErrors',
                'from ..domain.exceptions import DomainError, DomainErrors'
$c = $c -replace 'from\s+\.\.domain\.entities\s+import\s+DomainError\b(?!,)',
                'from ..domain.exceptions import DomainError'

if ($c -eq $before) {
    Write-Host "  [WARN] no import line matched" -ForegroundColor DarkYellow
} else {
    Write-Text -Path $appExc -Content $c
    Write-Host "  [OK]   rewired import -> ..domain.exceptions" -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────────
# Verify
# ─────────────────────────────────────────────────────────────
if ($DryRun) {
    Write-Host ""
    Write-Host "[DRY-RUN] nothing was written." -ForegroundColor Magenta
    exit 0
}

if ($NoVerify) {
    Write-Host ""
    Write-Host "[SKIP] verification disabled (-NoVerify)" -ForegroundColor DarkYellow
    exit 0
}

Write-Host ""
Write-Host "--- Verifying imports ---" -ForegroundColor Yellow

$py  = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "  [SKIP] .venv\Scripts\python.exe not found — verify manually:" -ForegroundColor DarkYellow
    Write-Host "         uv run python -c ""import app.app""" -ForegroundColor DarkGray
    exit 0
}

$checks = @(
    @{ Name = "domain/exceptions.py";        Code = "from app.modules.shared.domain.exceptions import DomainError, DomainErrors" },
    @{ Name = "domain/value_objects.py";     Code = "from app.modules.shared.domain.value_objects import *" },
    @{ Name = "domain/entities.py";          Code = "from app.modules.shared.domain.entities import DomainError" },
    @{ Name = "application/exceptions.py";   Code = "from app.modules.shared.application.exceptions import StandardException" }
)

$fail = 0
foreach ($chk in $checks) {
    $out = & $py -c "$($chk.Code); print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0 -and "$out" -match 'OK') {
        Write-Host "  [OK]   $($chk.Name)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $($chk.Name)" -ForegroundColor Red
        Write-Host "         $out" -ForegroundColor DarkRed
        $fail++
    }
}

# Full-app smoke test (best-effort)
$appOut = & $py -c "import app.app; print('APP_OK')" 2>&1
if ($LASTEXITCODE -eq 0 -and "$appOut" -match 'APP_OK') {
    Write-Host "  [OK]   import app.app" -ForegroundColor Green
} else {
    Write-Host "  [WARN] import app.app failed:" -ForegroundColor DarkYellow
    Write-Host "         $appOut" -ForegroundColor DarkGray
}

Write-Host ""
if ($fail -gt 0) {
    Write-Host "[ERROR] $fail import check(s) failed." -ForegroundColor Red
    Write-Host "        Restore from *.bak.$ts if needed." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] all imports resolved — cycle broken." -ForegroundColor Green
exit 0

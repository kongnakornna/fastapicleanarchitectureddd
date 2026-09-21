<#
.SYNOPSIS
    fix_module_imports.ps1
    Fix common module-level import problems in a DDD FastAPI project.

.DESCRIPTION
    Problem 1 — Missing `from __future__ import annotations`
        Python evaluates annotations eagerly. Forward refs like
            def f(self, other: Money) -> None
        crash with NameError if `Money` isn't defined yet at class body
        execution time. Adding `from __future__ import annotations` makes
        ALL annotations lazy (string-based), so forward refs work.

    Problem 2 — Eager cross-layer imports in __init__.py
        `import app.modules.X.infrastructure.models` runs
        app/modules/X/__init__.py first. If that init does
        `from .presentation.routers import router`, the whole presentation
        layer loads — which pulls application, then domain, causing
        cascades and circular-import errors.

    Fix strategy:
        - value_objects.py: insert `from __future__ import annotations`
          right after module docstring (idempotent).
        - module __init__.py + sublayer __init__.py: comment out cross-layer
          eager imports with a marker, so the file still imports other
          submodules directly.

.PARAMETER Root
    Project root (folder containing app\, migrations\, .venv\).

.PARAMETER DryRun
    Print plan, write nothing.

.PARAMETER NoVerify
    Skip post-fix import smoke test.

.PARAMETER Aggressive
    Also clean sublayer __init__.py (domain/, application/, etc.).

.PARAMETER Module
    Only fix these module names. Default = all.
#>
[CmdletBinding()]
param(
    [string]$Root = "",
    [switch]$DryRun,
    [switch]$NoVerify,
    [switch]$Aggressive,
    [string[]]$Module = @()
)

$ErrorActionPreference = "Stop"

# ── Resolve root ─────────────────────────────────────────────
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = (Get-Location).Path }
$Root = $Root.TrimEnd('\','/')
if (-not (Test-Path (Join-Path $Root "app\modules"))) {
    throw "app\modules not found under $Root"
}

$modulesRoot = Join-Path $Root "app\modules"
$utf8   = New-Object System.Text.UTF8Encoding($false)
$ts     = Get-Date -Format "yyyyMMddHHmmss"

# ── Header ───────────────────────────────────────────────────
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " fix_module_imports.ps1"                    -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Root        : $Root"
Write-Host " DryRun      : $DryRun"
Write-Host " Aggressive  : $Aggressive"
Write-Host " Filter      : $(if ($Module.Count) { $Module -join ', ' } else { '(all)' })"
Write-Host " Backup      : *.bak.$ts"
Write-Host "--------------------------------------------" -ForegroundColor Cyan

# ── Helpers ──────────────────────────────────────────────────
$script:stats = [ordered]@{
    FilesScanned = 0
    FutureAdded  = 0
    InitCleaned  = 0
    Skipped      = 0
    Warned       = 0
}

function Backup-File([string]$Path) {
    if ($DryRun) { return }
    $bak = "$Path.bak.$ts"
    if (-not (Test-Path $bak)) {
        Copy-Item -LiteralPath $Path -Destination $bak
    }
}

function Read-Utf8([string]$Path) {
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Write-Utf8([string]$Path, [string]$Content) {
    if ($DryRun) { return }
    [System.IO.File]::WriteAllText($Path, $Content, $utf8)
}

# Insert `from __future__ import annotations` after shebang / coding /
# blank lines / module docstring. Returns the new content.
function Add-FutureAnnotations([string]$Content) {
    if ($Content -match '(?m)^from\s+__future__\s+import\s+annotations') {
        return $null   # already present
    }

    $lines = $Content -split "`r?`n"
    $i = 0

    # shebang
    if ($i -lt $lines.Count -and $lines[$i] -match '^#!') { $i++ }
    # coding comment
    if ($i -lt $lines.Count -and $lines[$i] -match '^#.*coding[:=]') { $i++ }
    # blank lines + comments before docstring
    while ($i -lt $lines.Count -and ($lines[$i] -match '^\s*$' -or $lines[$i] -match '^\s*#')) { $i++ }

    # module docstring?
    if ($i -lt $lines.Count -and $lines[$i] -match '^\s*("""|'''''')') {
        $openQuote = if ($lines[$i] -match '"""') { '"""' } else { "'''" }
        $first     = $lines[$i]
        # single-line docstring: opening and closing on same line
        $openIdx   = $first.IndexOf($openQuote)
        $closeIdx  = $first.IndexOf($openQuote, $openIdx + $openQuote.Length)
        if ($closeIdx -ge 0) {
            $i++
        } else {
            $i++
            while ($i -lt $lines.Count -and $lines[$i] -notmatch [regex]::Escape($openQuote)) {
                $i++
            }
            if ($i -lt $lines.Count) { $i++ }   # skip closing line
        }
    }

    $head = if ($i -gt 0) { $lines[0..($i-1)] } else { @() }
    $tail = if ($i -lt $lines.Count) { $lines[$i..($lines.Count-1)] } else { @() }

    $new = @()
    $new += $head
    $new += "from __future__ import annotations"
    $new += ""
    $new += $tail
    return ($new -join "`n")
}

# Comment out cross-layer eager imports inside an __init__.py.
#   top-level module init  ->  from .presentation / .infrastructure / .application / .domain
#   sublayer init          ->  from ..presentation / ..infrastructure / ..application / ..domain
# Returns new content, or $null if nothing changed.
function Clean-InitEagerImports([string]$Path, [string]$Content) {
    $isTopLevel = (Split-Path $Path -Leaf) -eq "__init__.py" -and
                  (Split-Path (Split-Path $Path -Parent) -Leaf) -eq "modules"

    $patterns = if ($isTopLevel) {
        @(
            '^from\s+\.presentation\b',
            '^from\s+\.infrastructure\b',
            '^from\s+\.application\b',
            '^from\s+\.domain\b'
        )
    } else {
        @(
            '^from\s+\.\.presentation\b',
            '^from\s+\.\.infrastructure\b',
            '^from\s+\.\.application\b',
            '^from\s+\.\.domain\b'
        )
    }

    $lines = $Content -split "`r?`n"
    $changed = $false
    $out = New-Object System.Collections.Generic.List[string]

    foreach ($ln in $lines) {
        $hit = $false
        foreach ($p in $patterns) {
            if ($ln -match $p) { $hit = $true; break }
        }
        if ($hit -and $ln -notmatch '^\s*#') {
            $out.Add("# [AUTO-DISABLED by fix_module_imports.ps1] $ln")
            $out.Add("#   reason: eager cross-layer import at package init causes")
            $out.Add("#           a load cascade (infra.models -> presentation -> ...).")
            $out.Add("#   fix:    import directly at the call site instead, e.g.")
            $out.Add("#           from app.modules.X.presentation.routers import router")
            $changed = $true
        } else {
            $out.Add($ln)
        }
    }

    if (-not $changed) { return $null }
    return ($out -join "`n")
}

# ── Discover modules ─────────────────────────────────────────
$mods = Get-ChildItem $modulesRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "__pycache__" }

if ($Module.Count -gt 0) {
    $mods = $mods | Where-Object { $Module -contains $_.Name }
}

if (-not $mods) {
    Write-Host "[WARN] no modules to process" -ForegroundColor Yellow
    exit 0
}

Write-Host " Modules     : $($mods.Name -join ', ')"
Write-Host "--------------------------------------------" -ForegroundColor Cyan

# ── Pass 1: value_objects.py (future annotations) ────────────
Write-Host ""
Write-Host "--- [1/2] Add `from __future__ import annotations` ---" -ForegroundColor Yellow

foreach ($m in $mods) {
    $vo = Join-Path $m.FullName "domain\value_objects.py"
    if (-not (Test-Path $vo)) {
        Write-Host "  [SKIP] $($m.Name): no domain\value_objects.py" -ForegroundColor DarkYellow
        $script:stats.Skipped++
        continue
    }
    $script:stats.FilesScanned++

    $c = Read-Utf8 $vo
    $new = Add-FutureAnnotations $c

    if ($null -eq $new) {
        Write-Host "  [OK]   $($m.Name): already has future import" -ForegroundColor DarkGray
        $script:stats.Skipped++
        continue
    }

    if ($DryRun) {
        Write-Host "  [DRY]  $($m.Name): would add future import" -ForegroundColor DarkCyan
    } else {
        Backup-File $vo
        Write-Utf8 $vo $new
        Write-Host "  [FIX]  $($m.Name): inserted future import" -ForegroundColor Green
    }
    $script:stats.FutureAdded++
}

# ── Pass 2: __init__.py cleanup ──────────────────────────────
Write-Host ""
Write-Host "--- [2/2] Clean cross-layer eager imports in __init__.py ---" -ForegroundColor Yellow

$initTargets = @()
foreach ($m in $mods) {
    # top-level module __init__
    $initTargets += (Join-Path $m.FullName "__init__.py")

    if ($Aggressive) {
        foreach ($sub in @("domain","application","infrastructure","presentation")) {
            $initTargets += (Join-Path $m.FullName "$sub\__init__.py")
        }
    }
}

foreach ($p in $initTargets) {
    if (-not (Test-Path $p)) { continue }
    $script:stats.FilesScanned++

    $rel = $p.Replace($Root + "\", "")
    $c = Read-Utf8 $p
    $new = Clean-InitEagerImports -Path $p -Content $c

    if ($null -eq $new) {
        Write-Host "  [OK]   $rel (clean)" -ForegroundColor DarkGray
        continue
    }

    if ($DryRun) {
        Write-Host "  [DRY]  $rel (would comment out cross-layer imports)" -ForegroundColor DarkCyan
    } else {
        Backup-File $p
        Write-Utf8 $p $new
        Write-Host "  [FIX]  $rel (disabled cross-layer imports)" -ForegroundColor Green
    }
    $script:stats.InitCleaned++
}

# ── Summary ──────────────────────────────────────────────────
Write-Host ""
Write-Host "--- Summary ---" -ForegroundColor Cyan
Write-Host "  files scanned     : $($script:stats.FilesScanned)"
Write-Host "  future imports    : $($script:stats.FutureAdded)"
Write-Host "  inits cleaned     : $($script:stats.InitCleaned)"
Write-Host "  skipped / ok      : $($script:stats.Skipped)"
if ($script:stats.Warned -gt 0) {
    Write-Host "  warnings          : $($script:stats.Warned)" -ForegroundColor DarkYellow
}

if ($DryRun) {
    Write-Host ""
    Write-Host "[DRY-RUN] nothing was written." -ForegroundColor Magenta
    exit 0
}

# ── Verify ───────────────────────────────────────────────────
if ($NoVerify) {
    Write-Host ""
    Write-Host "[SKIP] verification disabled (-NoVerify)" -ForegroundColor DarkYellow
    exit 0
}

Write-Host ""
Write-Host "--- Verifying imports ---" -ForegroundColor Yellow

$py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "  [SKIP] .venv python not found — verify manually:" -ForegroundColor DarkYellow
    Write-Host "         uv run python -c ""import app.app""" -ForegroundColor DarkGray
    exit 0
}

$fail = 0

# Test each module's value_objects can be imported standalone
foreach ($m in $mods) {
    $vo = Join-Path $m.FullName "domain\value_objects.py"
    if (-not (Test-Path $vo)) { continue }

    $code = "import app.modules.$($m.Name).domain.value_objects; print('OK')"
    $out  = & $py -c $code 2>&1
    if ($LASTEXITCODE -eq 0 -and "$out" -match 'OK') {
        Write-Host "  [OK]   $($m.Name).domain.value_objects" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $($m.Name).domain.value_objects" -ForegroundColor Red
        Write-Host "         $out" -ForegroundColor DarkRed
        $fail++
    }
}

# Full-app smoke test
$appOut = & $py -c "import app.app; print('APP_OK')" 2>&1
if ($LASTEXITCODE -eq 0 -and "$appOut" -match 'APP_OK') {
    Write-Host "  [OK]   import app.app" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] import app.app" -ForegroundColor Red
    Write-Host "         $appOut" -ForegroundColor DarkRed
    $fail++
}

Write-Host ""
if ($fail -gt 0) {
    Write-Host "[ERROR] $fail check(s) failed." -ForegroundColor Red
    Write-Host "        Backups: *.bak.$ts" -ForegroundColor DarkYellow
    exit 1
}

Write-Host "[OK] all imports resolved." -ForegroundColor Green
exit 0
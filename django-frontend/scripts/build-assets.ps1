<#
.SYNOPSIS
    Build assets/ → static/ (ไม่ต้องใช้ Node.js)
.DESCRIPTION
    - SCSS → CSS      : ใช้ sass CLI (ถ้าลง) หรือข้าม
    - TS   → JS       : ใช้ esbuild (ถ้าลง) หรือ fallback copy
    - CSS  → CSS      : copy ตรง
    - SVG  → SVG      : copy + minify
    - fonts → fonts   : copy ตรง
#>
[CmdletBinding()]
param(
    [string]$Root = $PSScriptRoot + "\..",
    [switch]$Watch
)

$ErrorActionPreference = "Stop"

function Write-Ok   { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Info { param($m) Write-Host "  [--] $m" -ForegroundColor Cyan }
function Write-Warn { param($m) Write-Host "  [!!] $m" -ForegroundColor Yellow }

$assets = Join-Path $Root "assets"
$static = Join-Path $Root "static"

if (-not (Test-Path $assets)) {
    Write-Warn "assets/ not found: $assets"
    exit 0
}

# ─── Ensure output dirs ─────────────────────────────────────────
$dirs = @(
    "$static\css", "$static\js\vendor",
    "$static\img\avatars", "$static\fonts"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}

# ─── Helper: copy tree with filter ──────────────────────────────
function Copy-Tree {
    param(
        [string]$Source,
        [string]$Dest,
        [string[]]$Include = @("*.*")
    )
    if (-not (Test-Path $Source)) { return 0 }
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null

    $count = 0
    Get-ChildItem $Source -File -Include $Include -Recurse | ForEach-Object {
        $rel = $_.FullName.Substring($Source.Length).TrimStart('\','/')
        $out = Join-Path $Dest $rel
        $outDir = Split-Path -Parent $out
        if (-not (Test-Path $outDir)) {
            New-Item -ItemType Directory -Path $outDir -Force | Out-Null
        }
        Copy-Item $_.FullName $out -Force
        $count++
    }
    return $count
}

# ═══════════════════════════════════════════════════════════════
# 1. CSS (copy ตรง)
# ═══════════════════════════════════════════════════════════════
Write-Info "CSS..."
$cssSrc = Join-Path $assets "css"
$n = Copy-Tree -Source $cssSrc -Dest "$static\css" -Include @("*.css")
Write-Ok "  $n .css files copied"

# ═══════════════════════════════════════════════════════════════
# 2. SCSS (compile ถ้ามี sass)
# ═══════════════════════════════════════════════════════════════
Write-Info "SCSS..."
$scssFiles = Get-ChildItem $cssSrc -Filter "*.scss" -ErrorAction SilentlyContinue
if ($scssFiles) {
    $sass = Get-Command sass -ErrorAction SilentlyContinue
    if ($sass) {
        foreach ($f in $scssFiles) {
            $out = Join-Path "$static\css" "$($f.BaseName).css"
            & sass $f.FullName $out --style=compressed 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Ok "  $($f.Name) → $($f.BaseName).css"
            } else {
                Write-Warn "  sass failed for $($f.Name)"
            }
        }
    } else {
        Write-Warn "  sass CLI not found — skip SCSS (install: npm i -g sass)"
    }
} else {
    Write-Ok "  no .scss files"
}

# ═══════════════════════════════════════════════════════════════
# 3. JS/TS (bundle ถ้ามี esbuild, ไม่งั้น copy)
# ═══════════════════════════════════════════════════════════════
Write-Info "JS/TS..."
$jsSrc = Join-Path $assets "js"
$esbuild = Get-Command esbuild -ErrorAction SilentlyContinue

$tsEntry = Join-Path $jsSrc "app.ts"
$jsEntry = Join-Path $jsSrc "app.js"

if ($esbuild -and (Test-Path $tsEntry)) {
    & esbuild $tsEntry --bundle --minify --target=es2020 `
        --outfile="$static\js\app.min.js" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "  app.ts → app.min.js (bundled)"
    } else {
        Write-Warn "  esbuild failed for app.ts"
    }
} elseif ($esbuild -and (Test-Path $jsEntry)) {
    & esbuild $jsEntry --bundle --minify --target=es2020 `
        --outfile="$static\js\app.min.js" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "  app.js → app.min.js (bundled)"
    }
} else {
    Write-Warn "  esbuild not found — copy .js as-is (no bundling)"
    # copy .js ตรง (แต่ต้องเป็น IIFE ไม่ใช่ ESM)
    Get-ChildItem $jsSrc -Filter "*.js" -File | ForEach-Object {
        $out = Join-Path "$static\js" $_.Name
        Copy-Item $_.FullName $out -Force
    }
    # copy .min.js ด้วยถ้ามี
    Get-ChildItem $jsSrc -Filter "*.min.js" -File | ForEach-Object {
        $out = Join-Path "$static\js" $_.Name
        Copy-Item $_.FullName $out -Force
    }
    Write-Ok "  JS files copied"
}

# ─── Copy pre-minified fallback (ถ้ามี static/js/app.min.js อยู่แล้วให้คงไว้)
$existingMin = Join-Path "$static\js" "app.min.js"
if ((Test-Path $existingMin) -and -not (Test-Path "$static\js\app.min.js")) {
    Write-Ok "  app.min.js already exists"
}

# ═══════════════════════════════════════════════════════════════
# 4. SVG (copy + basic minify)
# ═══════════════════════════════════════════════════════════════
Write-Info "SVG..."
$imgSrc = Join-Path $assets "img"
if (Test-Path $imgSrc) {
    # copy tree
    Get-ChildItem $imgSrc -Filter "*.svg" -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($imgSrc.Length).TrimStart('\','/')
        $out = Join-Path "$static\img" $rel
        $outDir = Split-Path -Parent $out
        if (-not (Test-Path $outDir)) {
            New-Item -ItemType Directory -Path $outDir -Force | Out-Null
        }
        # minify: ลบ newlines + spaces ซ้ำ
        $svg = Get-Content $_.FullName -Raw
        $svg = $svg -replace ">\s+<", "><" -replace "\s{2,}", " "
        [System.IO.File]::WriteAllText($out, $svg, [System.Text.UTF8Encoding]::new($false))
    }
    $svgCount = (Get-ChildItem $imgSrc -Filter "*.svg" -Recurse -File).Count
    Write-Ok "  $svgCount .svg files copied + minified"
} else {
    Write-Ok "  no .svg files"
}

# ═══════════════════════════════════════════════════════════════
# 5. Fonts (copy ตรง)
# ═══════════════════════════════════════════════════════════════
Write-Info "Fonts..."
$fontSrc = Join-Path $assets "fonts"
if (Test-Path $fontSrc) {
    $n = Copy-Tree -Source $fontSrc -Dest "$static\fonts" `
        -Include @("*.woff2","*.woff","*.ttf","*.otf")
    Write-Ok "  $n font files copied"
} else {
    Write-Ok "  no fonts"
}

# ═══════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════
Write-Host ""
Write-Ok "Build complete → static/"
Write-Host ""
Write-Host "  static/css/    $((Get-ChildItem "$static\css" -File -ErrorAction SilentlyContinue).Count) files" -ForegroundColor DarkGray
Write-Host "  static/js/     $((Get-ChildItem "$static\js" -File -Recurse -ErrorAction SilentlyContinue).Count) files" -ForegroundColor DarkGray
Write-Host "  static/img/    $((Get-ChildItem "$static\img" -File -Recurse -ErrorAction SilentlyContinue).Count) files" -ForegroundColor DarkGray
Write-Host "  static/fonts/  $((Get-ChildItem "$static\fonts" -File -Recurse -ErrorAction SilentlyContinue).Count) files" -ForegroundColor DarkGray

# module_docs_swagger.ps1
# Generate docs + swagger tag + postman collection for a module.
$ErrorActionPreference = "Stop"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$ts = Get-Date -Format "yyyyMMddHHmmss"

# ---------- parse args (no param block; --xxx works) ----------
$ModuleName = ""
$Root       = $PSScriptRoot
$Docs       = $false
$Swagger    = $false
$Postman    = $false
$Force      = $false
$DryRun     = $false
$NoVerify   = $false
$ShowHelp   = $false
$BaseUrl    = "http://localhost:8000"
$ApiPrefix  = "/api/v1"

$i = 0
while ($i -lt $args.Count) {
    $a = [string]$args[$i]
    switch -regex ($a) {
        '^--?(help|h)$'    { $ShowHelp = $true; $i++; continue }
        '^--?docs$'        { $Docs     = $true; $i++; continue }
        '^--?swagger$'     { $Swagger  = $true; $i++; continue }
        '^--?postman$'     { $Postman  = $true; $i++; continue }
        '^--?all$'         { $Docs=$true; $Swagger=$true; $Postman=$true; $i++; continue }
        '^--?force$'       { $Force    = $true; $i++; continue }
        '^--?dry-?run$'    { $DryRun   = $true; $i++; continue }
        '^--?no-?verify$'  { $NoVerify = $true; $i++; continue }
        '^--?base-?url$'   { $i++; if ($i -lt $args.Count) { $BaseUrl = [string]$args[$i] }; $i++; continue }
        '^--?api-?prefix$' { $i++; if ($i -lt $args.Count) { $ApiPrefix = [string]$args[$i] }; $i++; continue }
        '^--?root$'        { $i++; if ($i -lt $args.Count) { $Root = [string]$args[$i] }; $i++; continue }
        '^-' { $i++; continue }
        default {
            if ([string]::IsNullOrWhiteSpace($ModuleName)) { $ModuleName = $a }
            $i++
        }
    }
}

# ---------- helpers ----------
function Say  { param($m,$c="White") Write-Host $m -ForegroundColor $c }
function Ok   { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Fix  { param($m) Write-Host "  [FIX]  $m" -ForegroundColor Green }
function Warn { param($m) Write-Host "  [WARN] $m" -ForegroundColor Yellow }
function Skip { param($m) Write-Host "  [SKIP] $m" -ForegroundColor DarkYellow }
function Dry  { param($m) Write-Host "  [DRY]  $m" -ForegroundColor DarkCyan }
function Err  { param($m) Write-Host "  [ERR]  $m" -ForegroundColor Red }

function Read-Utf8([string]$p) { [IO.File]::ReadAllText($p,[Text.Encoding]::UTF8) }
function Write-Utf8([string]$p,[string]$c) {
    if ($DryRun) { return }
    $d = Split-Path $p -Parent
    if ($d -and -not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
    [IO.File]::WriteAllText($p, $c, $utf8)
}
function Backup-File([string]$p) {
    if ($DryRun) { return }
    $bak = "$p.bak.$ts"
    if (-not (Test-Path $bak)) { Copy-Item -LiteralPath $p -Destination $bak }
    Write-Host "  [BAK]  $([IO.Path]::GetFileName($p))" -ForegroundColor DarkYellow
}

# ---------- help ----------
if ($ShowHelp -or [string]::IsNullOrWhiteSpace($ModuleName)) {
    Write-Host ""
    Write-Host "module_docs_swagger.bat <module> [options]"
    Write-Host ""
    Write-Host "  Options:"
    Write-Host "    --docs       docs\README_<mod>.md + docs\API_<mod>.md"
    Write-Host "    --swagger    Wire OpenAPI tag in app\app.py"
    Write-Host "    --postman    docs\postman\<mod>.postman_collection.json"
    Write-Host "    --all        All of the above"
    Write-Host "    --force      Overwrite existing files"
    Write-Host "    --dry-run    Show plan, write nothing"
    Write-Host "    --no-verify  Skip import smoke test"
    Write-Host "    --base-url U Postman base URL (default http://localhost:8000)"
    Write-Host "    --api-prefix P API prefix (default /api/v1)"
    Write-Host ""
    exit 0
}

if (-not ($Docs -or $Swagger -or $Postman)) {
    $Docs = $true; $Swagger = $true; $Postman = $true
}
if (-not (Test-Path (Join-Path $Root "app\modules"))) {
    Err "app\modules not found under $Root"
    exit 1
}

# ---------- introspect ----------
function Get-ModuleInfo {
    param([string]$Name)
    $Name = $Name.ToLower().Trim()
    $class = (Get-Culture).TextInfo.ToTitleCase($Name.Replace('_',' ')).Replace(' ','')
    $modRoot = Join-Path $Root "app\modules\$Name"
    if (-not (Test-Path $modRoot)) { throw "module folder not found: app\modules\$Name" }

    $modelFile  = Join-Path $modRoot "infrastructure\models.py"
    $routerFile = Join-Path $modRoot "presentation\routers.py"

    $prefix = $Name.Substring(0, [Math]::Min(3, $Name.Length))
    $schema = "tenant_$prefix"
    $table  = "${Name}s"
    $columns = @()

    if (Test-Path $modelFile) {
        $mc = Read-Utf8 $modelFile
        if ($mc -match '__tablename__\s*=\s*["'']([^"'']+)["'']')   { $table  = $Matches[1] }
        if ($mc -match '["'']schema["'']\s*:\s*["'']([^"'']+)["'']') { $schema = $Matches[1] }
        if ($schema -match '^tenant_(\w+)$') { $prefix = $Matches[1] }

        $rx = '(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*Mapped\[([^\]]+)\]\s*=\s*mapped_column\((.*?)\)\s*$'
        foreach ($m in [regex]::Matches($mc, $rx)) {
            $columns += [pscustomobject]@{
                Name    = $m.Groups[1].Value.TrimEnd('_')
                Type    = ($m.Groups[2].Value -replace '\s+',' ')
                PK      = ($m.Groups[3].Value -match 'primary_key\s*=\s*True')
                NotNull = ($m.Groups[3].Value -match 'nullable\s*=\s*False')
            }
        }
    }

    $endpoints = @()
    if (Test-Path $routerFile) {
        $rc = Read-Utf8 $routerFile
        $rprefix = "/$Name"
        if ($rc -match 'APIRouter\([^\)]*prefix\s*=\s*["'']([^"'']+)["'']') { $rprefix = $Matches[1] }

        $rx = '(?m)^@router\.(get|post|patch|put|delete)\(\s*["'']([^"'']*)["'']([\s\S]*?)\)\s*\r?\n(?:async\s+)?def\s+(\w+)'
        foreach ($m in [regex]::Matches($rc, $rx)) {
            $summary = ""
            if ($m.Groups[3].Value -match 'summary\s*=\s*["'']([^"'']+)["'']') { $summary = $Matches[1] }
            $status = "200"
            if ($m.Groups[3].Value -match 'status_code\s*=\s*(?:status\.)?HTTP_(\d+)_\w+') { $status = $Matches[1] }
            $endpoints += [pscustomobject]@{
                Verb    = $m.Groups[1].Value.ToUpper()
                Path    = ($rprefix.TrimEnd('/') + '/' + $m.Groups[2].Value.TrimStart('/')).Replace('//','/')
                Summary = if ($summary) { $summary } else { "$($m.Groups[1].Value.ToUpper()) $($m.Groups[2].Value)" }
                Func    = $m.Groups[4].Value
                Status  = $status
            }
        }
    }

    return [pscustomobject]@{
        Name = $Name; Class = $class; Root = $modRoot
        ModelFile = $modelFile; RouterFile = $routerFile
        ModelClass = "${class}Model"; RouterName = "${Name}_router"
        Prefix = $prefix; Schema = $schema; Table = $table
        Columns = $columns; Endpoints = $endpoints
        Created = (Get-Date -Format "yyyy-MM-dd")
    }
}

# ---------- header ----------
Say "" 
Say "============================================" "Cyan"
Say " module_docs_swagger.ps1" "Cyan"
Say "============================================" "Cyan"

try { $mi = Get-ModuleInfo $ModuleName } catch { Err $_; exit 1 }

Say " Module    : $($mi.Name)"
Say " Class     : $($mi.Class)"
Say " Schema    : $($mi.Schema)"
Say " Table     : $($mi.Table)"
Say " Columns   : $($mi.Columns.Count)"
Say " Endpoints : $($mi.Endpoints.Count)"
Say " Docs      : $Docs"
Say " Swagger   : $Swagger"
Say " Postman   : $Postman"
Say " Force     : $Force"
Say " DryRun    : $DryRun"
Say "--------------------------------------------" "Cyan"

# ---------- README ----------
function Write-Readme {
    $target = Join-Path $Root "docs\README_$($mi.Name).md"
    if ((Test-Path $target) -and -not $Force) { Skip "docs\README_$($mi.Name).md exists (--force)"; return }

    $colRows = ($mi.Columns | ForEach-Object {
        $k = if ($_.PK) { "PK" } else { "" }
        $n = if ($_.NotNull) { "NOT NULL" } else { "" }
        "| $($_.Name) | $($_.Type) | $k | $n |"
    }) -join "`n"

    $epRows = ($mi.Endpoints | ForEach-Object {
        "| $($_.Verb) | $($_.Path) | $($_.Summary) | $($_.Status) |"
    }) -join "`n"

    $tpl = @'
# Module: __MODULE__

> Schema: `__SCHEMA__` | Table: `__TABLE__`
> Generated: __DATE__

## Purpose

TH: describe the purpose of module `__MODULE__`
EN: describe the purpose of module `__MODULE__`

## Database

**Schema:** `__SCHEMA__`
**Table:**  `__TABLE__`

| Column | Type | Key | Constraints |
|---|---|---|---|
__COLS__

## SQL Migrations

Files under `migrations/versions/db/`:

    migrations/versions/db/V001__create___MODULE__.sql
    migrations/versions/db/V002__seed___MODULE__.sql
    migrations/versions/db/V003__rollback___MODULE__.sql

Generate more:

    module_sql_router.bat update __MODULE__ --desc "add tax rate"

## API Endpoints

| Method | Path | Summary | Status |
|---|---|---|---|
__EPS__

## Postman

Import `docs/postman/__MODULE__.postman_collection.json`

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | __DATE__ | initial release |
'@

    $content = $tpl.Replace('__MODULE__', $mi.Name).
                    Replace('__SCHEMA__', $mi.Schema).
                    Replace('__TABLE__',  $mi.Table).
                    Replace('__DATE__',   $mi.Created).
                    Replace('__COLS__',   $colRows).
                    Replace('__EPS__',    $epRows)

    if ($DryRun) { Dry "would write docs\README_$($mi.Name).md"; return }
    Write-Utf8 $target $content
    Fix "docs\README_$($mi.Name).md"
}

# ---------- API doc ----------
function Write-ApiDoc {
    $target = Join-Path $Root "docs\API_$($mi.Name).md"
    if ((Test-Path $target) -and -not $Force) { Skip "docs\API_$($mi.Name).md exists (--force)"; return }

    $blocks = ""
    foreach ($ep in $mi.Endpoints) {
        $blocks += "`n### $($ep.Verb) $($ep.Path)`n`n"
        $blocks += "$($ep.Summary)`n`n"
        $blocks += "- Status: ``$($ep.Status)```n"
        $blocks += "- Handler: ``$($ep.Func)```n`n"
    }

    $tpl = @'
# API Reference - __CLASS__

**Base URL:** `__BASE__`
**Module:** __MODULE__
**Generated:** __DATE__

## Authentication

All endpoints require:

    Authorization: Bearer <JWT>

POST/PATCH/DELETE also require:

    Idempotency-Key: <uuid-v4>

## Endpoints

__BLOCKS__

## Error Responses

| Status | Meaning |
|---|---|
| 400 | Domain error |
| 401 | Missing or invalid token |
| 403 | Insufficient scope |
| 404 | Entity not found |
| 409 | Duplicate code / version conflict |
| 422 | Validation error |

## OpenAPI

- Interactive: __BASE_URL__/docs
- Machine:     __BASE_URL__/openapi.json
'@

    $content = $tpl.Replace('__CLASS__',    $mi.Class).
                    Replace('__MODULE__',   $mi.Name).
                    Replace('__BASE__',     "$BaseUrl$ApiPrefix").
                    Replace('__BASE_URL__', $BaseUrl).
                    Replace('__DATE__',     $mi.Created).
                    Replace('__BLOCKS__',   $blocks)

    if ($DryRun) { Dry "would write docs\API_$($mi.Name).md"; return }
    Write-Utf8 $target $content
    Fix "docs\API_$($mi.Name).md"
}

# ---------- Postman ----------
function Write-Postman {
    $dir = Join-Path $Root "docs\postman"
    $target = Join-Path $dir "$($mi.Name).postman_collection.json"
    if ((Test-Path $target) -and -not $Force) { Skip "docs\postman\$($mi.Name).postman_collection.json exists (--force)"; return }

    $items = @()
    foreach ($ep in $mi.Endpoints) {
        $headers = @( @{ key = "Content-Type"; value = "application/json" } )
        if ($ep.Verb -in @("POST","PATCH","PUT","DELETE")) {
            $headers += @{ key = "Idempotency-Key"; value = '{{$guid}}' }
        }
        $path = $ep.Path -replace '\{entity_id\}','{{entity_id}}' -replace '\{id\}','{{entity_id}}'
        $url = "{{base_url}}$path"

        $req = [ordered]@{ method = $ep.Verb; header = $headers; url = $url }
        if ($ep.Verb -in @("POST","PATCH","PUT")) {
            $body = '{}'
            if ($ep.Verb -eq "POST") { $body = '{"code":"X-001","name":"Sample","amount":"100.00","currency":"THB"}' }
            if ($ep.Verb -eq "PATCH"){ $body = '{"name":"Updated Name"}' }
            $req.body = @{ mode = "raw"; raw = $body; options = @{ raw = @{ language = "json" } } }
        }
        $items += [ordered]@{
            name    = "$($mi.Class) - $($ep.Verb) $($ep.Path)"
            request = $req
        }
    }

    $collection = [ordered]@{
        info = [ordered]@{
            name = "ERPIoT - $($mi.Class)"
            _postman_id = [guid]::NewGuid().ToString()
            schema = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        }
        variable = @(
            @{ key = "base_url";  value = $BaseUrl },
            @{ key = "token";     value = "" },
            @{ key = "tenant_id"; value = "00000000-0000-0000-0000-000000000001" },
            @{ key = "entity_id"; value = "" }
        )
        auth = @{
            type = "bearer"
            bearer = @(@{ key = "token"; value = "{{token}}"; type = "string" })
        }
        item = $items
    }

    $json = $collection | ConvertTo-Json -Depth 12
    if ($DryRun) { Dry "would write docs\postman\$($mi.Name).postman_collection.json"; return }
    Write-Utf8 $target $json
    Fix "docs\postman\$($mi.Name).postman_collection.json"
}

# ---------- Swagger tag ----------
function Wire-SwaggerTag {
    Say ""
    Say "--- swagger ---" "Yellow"

    $appFile = Join-Path $Root "app\app.py"
    if (-not (Test-Path $appFile)) { Skip "app\app.py not found"; return }

    $content = Read-Utf8 $appFile
    $tagName = $mi.Class

    if ($content -match "[""']name[""']\s*:\s*[""']$([regex]::Escape($tagName))[""']") {
        Skip "openapi tag '$tagName' already present"
        return
    }

    $m = [regex]::Match($content, '(?s)openapi_tags\s*=\s*\[(.*?)\]')
    if (-not $m.Success) {
        Warn "no openapi_tags=[...] in app\app.py"
        Warn "add manually:"
        Say "      {`"name`": `"$tagName`", `"description`": `"$($mi.Name) module`"}," "DarkGray"
        return
    }

    $tagEntry = "        {`"name`": `"$tagName`", `"description`": `"$($mi.Name) module - schema $($mi.Schema), table $($mi.Table)`"},"
    $at = $m.Index + $m.Value.IndexOf('[') + 1
    $new = $content.Substring(0, $at) + "`n" + $tagEntry + "`n" + $content.Substring($at)

    if ($DryRun) { Dry "would add openapi tag '$tagName'"; return }
    Backup-File $appFile
    Write-Utf8 $appFile $new
    Fix "added openapi tag '$tagName' to app\app.py"
}

# ---------- run ----------
if ($Docs) {
    Say ""
    Say "--- docs ---" "Yellow"
    Write-Readme
    Write-ApiDoc
}
if ($Swagger) { Wire-SwaggerTag }
if ($Postman) {
    Say ""
    Say "--- postman ---" "Yellow"
    Write-Postman
}

# ---------- verify ----------
if (-not $NoVerify -and -not $DryRun) {
    Say ""
    Say "--- verify ---" "Yellow"
    $py = Join-Path $Root ".venv\Scripts\python.exe"
    if (-not (Test-Path $py)) {
        Skip "no .venv python - verify manually: uv run python -c ""import app.app"""
    } else {
        $out = & $py -c "import app.app; print('APP_OK')" 2>&1
        if ($LASTEXITCODE -eq 0 -and "$out" -match 'APP_OK') { Ok "import app.app" }
        else { Err "import app.app failed:"; Say "    $out" "DarkRed" }
    }
}

Say ""
Say "============================================" "Cyan"
if ($DryRun) { Say " DRY-RUN - nothing written" "Magenta" }
else         { Say " DONE - $($mi.Name) documented" "Green" }
Say "============================================" "Cyan"
exit 0
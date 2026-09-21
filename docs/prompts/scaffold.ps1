# ============================================================
#  FastAPI Backend Scaffold - PowerShell Driver v3.0
#  Stack: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Redis + Alembic
#  Pattern: Clean Architecture + DDD (4 layers)
#  Fix: duplicate modules, path resolution, CRLF, force mode
# ============================================================

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptRoot

# --- Version ---
$ScriptVersion = "3.0.0"
$StartTime = Get-Date

# --- Paths ---
$BackendRoot   = Join-Path $ScriptRoot "..\..\fastapi-backend"
$BackendRoot   = [System.IO.Path]::GetFullPath($BackendRoot)
$AppDir        = Join-Path $BackendRoot "app"
$ModulesDir    = Join-Path $AppDir "modules"
$CoreDir       = Join-Path $AppDir "core"
$SharedDir     = Join-Path $AppDir "shared"
$TestsDir      = Join-Path $BackendRoot "tests"
$MigrationsDir = Join-Path $BackendRoot "db\migrations"

# --- Flags ---
$script:DryRun = $false
$script:Force  = $false
$script:Stats  = @{ Created = 0; Skipped = 0; Failed = 0 }
$script:EOL    = "`r`n"

# ============================================================
#  Module Registry (Layer -> Modules)
# ============================================================
$ModuleRegistry = [ordered]@{
    0 = @("money","tenant_context","audit","idempotency","config","events")
    1 = @("tenancy","authentication","user","employee","customer","supplier","product","pricing")
    2 = @("order","invoice","ledger","payment","accounting_gateway","tax","reconciliation")
    3 = @("inventory","warehouse","deviceiot","production","recipe","quality","waste",
          "procurement","traceability","agriculture","crop","soil","irrigation")
    4 = @("transport","delivery","route","gps","retail","pos","shift",
          "line_channel","promotion","loyalty","crm","campaign","support")
    5 = @("reporting","analytics","forecast","kpi","satisfaction","recommendation","oee")
    6 = @("iot","cctv","monitoring","backup","alerting","audit_viewer","maintenance","energy")
    7 = @("health","example","blank")
}

# ============================================================
#  Module Metadata
# ============================================================
$ModuleMeta = @{
    # ---- Layer 0: Core ----
    "money"              = @{ Prefix="mny";  Entities=@("Money","VAT","ExchangeRate");                Layer=0; Schema="tenant_mny" }
    "tenant_context"     = @{ Prefix="tctx"; Entities=@("TenantContext","RequestContext");           Layer=0; Schema="tenant_tctx" }
    "audit"              = @{ Prefix="aud";  Entities=@("AuditLog","ChangeSet");                     Layer=0; Schema="tenant_aud" }
    "idempotency"        = @{ Prefix="idem"; Entities=@("IdempotencyRecord","IdempotencyKey");       Layer=0; Schema="tenant_idem" }
    "config"             = @{ Prefix="cfg";  Entities=@("ConfigEntry","ConfigKey");                  Layer=0; Schema="tenant_cfg" }
    "events"             = @{ Prefix="evt";  Entities=@("DomainEvent","EventEnvelope");              Layer=0; Schema="tenant_evt" }

    # ---- Layer 1: Foundation ----
    "tenancy"            = @{ Prefix="ten";  Entities=@("Tenant","TenantPlan");                      Layer=1; Schema="public" }
    "authentication"     = @{ Prefix="auth"; Entities=@("Credential","Session","Token");             Layer=1; Schema="tenant_auth" }
    "user"               = @{ Prefix="usr";  Entities=@("User","Role","Permission");                 Layer=1; Schema="tenant_usr" }
    "employee"           = @{ Prefix="emp";  Entities=@("Employee","Department","Position");         Layer=1; Schema="tenant_emp" }
    "customer"           = @{ Prefix="cus";  Entities=@("Customer","CustomerGroup","Address");       Layer=1; Schema="tenant_cus" }
    "supplier"           = @{ Prefix="sup";  Entities=@("Supplier","SupplierCategory");              Layer=1; Schema="tenant_sup" }
    "product"            = @{ Prefix="prd";  Entities=@("Product","Category","SKU","Barcode");       Layer=1; Schema="tenant_prd" }
    "pricing"            = @{ Prefix="prc";  Entities=@("PriceList","PriceRule","Discount");         Layer=1; Schema="tenant_prc" }

    # ---- Layer 2: Money Path ----
    "order"              = @{ Prefix="ord";  Entities=@("Order","OrderLine");                        Layer=2; Schema="tenant_ord" }
    "invoice"            = @{ Prefix="inv";  Entities=@("Invoice","InvoiceLine");                    Layer=2; Schema="tenant_inv" }
    "ledger"             = @{ Prefix="led";  Entities=@("JournalEntry","LedgerAccount");             Layer=2; Schema="tenant_led" }
    "payment"            = @{ Prefix="pay";  Entities=@("Payment","PaymentAllocation");              Layer=2; Schema="tenant_pay" }
    "accounting_gateway" = @{ Prefix="acg";  Entities=@("AccountingSync");                           Layer=2; Schema="tenant_acg" }
    "tax"                = @{ Prefix="tax";  Entities=@("TaxRule","TaxReport");                      Layer=2; Schema="tenant_tax" }
    "reconciliation"     = @{ Prefix="rec";  Entities=@("Reconciliation","MatchRecord");             Layer=2; Schema="tenant_rec" }

    # ---- Layer 3: Goods Path ----
    "inventory"          = @{ Prefix="invt"; Entities=@("StockItem","StockMove");                    Layer=3; Schema="tenant_invt" }
    "warehouse"          = @{ Prefix="wh";   Entities=@("Warehouse","Location");                     Layer=3; Schema="tenant_wh" }
    "deviceiot"          = @{ Prefix="dev";  Entities=@("Device","SerialNumber");                    Layer=3; Schema="tenant_dev" }
    "production"         = @{ Prefix="prod"; Entities=@("ProductionOrder");                          Layer=3; Schema="tenant_prod" }
    "recipe"             = @{ Prefix="rcp";  Entities=@("Recipe","Ingredient");                      Layer=3; Schema="tenant_rcp" }
    "quality"            = @{ Prefix="qc";   Entities=@("QCInspection");                             Layer=3; Schema="tenant_qc" }
    "waste"              = @{ Prefix="wst";  Entities=@("WasteRecord");                              Layer=3; Schema="tenant_wst" }
    "procurement"        = @{ Prefix="proc"; Entities=@("PurchaseOrder");                            Layer=3; Schema="tenant_proc" }
    "traceability"       = @{ Prefix="trc";  Entities=@("TraceRecord");                              Layer=3; Schema="tenant_trc" }
    "agriculture"        = @{ Prefix="agr";  Entities=@("Farm","Plot","Harvest");                    Layer=3; Schema="tenant_agr" }
    "crop"               = @{ Prefix="crp";  Entities=@("Crop","Variety");                           Layer=3; Schema="tenant_crp" }
    "soil"               = @{ Prefix="soil"; Entities=@("SoilTest");                                 Layer=3; Schema="tenant_soil" }
    "irrigation"         = @{ Prefix="irr";  Entities=@("IrrigationPlan");                           Layer=3; Schema="tenant_irr" }

    # ---- Layer 4: Operations ----
    "transport"          = @{ Prefix="trn";  Entities=@("Vehicle","Driver","Trip");                  Layer=4; Schema="tenant_trn" }
    "delivery"           = @{ Prefix="dlv";  Entities=@("Delivery","POD");                           Layer=4; Schema="tenant_dlv" }
    "route"              = @{ Prefix="rte";  Entities=@("Route","Stop");                             Layer=4; Schema="tenant_rte" }
    "gps"                = @{ Prefix="gps";  Entities=@("Location","Geofence");                      Layer=4; Schema="tenant_gps" }
    "retail"             = @{ Prefix="rtl";  Entities=@("Store");                                    Layer=4; Schema="tenant_rtl" }
    "pos"                = @{ Prefix="pos";  Entities=@("POSTerminal","Transaction");                Layer=4; Schema="tenant_pos" }
    "shift"              = @{ Prefix="shf";  Entities=@("Shift","Assignment");                       Layer=4; Schema="tenant_shf" }
    "line_channel"       = @{ Prefix="line"; Entities=@("LINEMessage");                              Layer=4; Schema="tenant_line" }
    "promotion"          = @{ Prefix="promo";Entities=@("Promotion","Rule");                         Layer=4; Schema="tenant_promo" }
    "loyalty"            = @{ Prefix="loy";  Entities=@("LoyaltyAccount","Tier");                    Layer=4; Schema="tenant_loy" }
    "crm"                = @{ Prefix="crm";  Entities=@("Lead","Deal","Activity");                   Layer=4; Schema="tenant_crm" }
    "campaign"           = @{ Prefix="cmp";  Entities=@("Campaign");                                 Layer=4; Schema="tenant_cmp" }
    "support"            = @{ Prefix="sup2"; Entities=@("Ticket");                                   Layer=4; Schema="tenant_sup2" }

    # ---- Layer 5: Intelligence ----
    "reporting"          = @{ Prefix="rpt";  Entities=@("Report","Schedule");                        Layer=5; Schema="tenant_rpt" }
    "analytics"          = @{ Prefix="anl";  Entities=@("Metric","Snapshot");                        Layer=5; Schema="tenant_anl" }
    "forecast"           = @{ Prefix="fc";   Entities=@("Forecast","ForecastEvent","ForecastAuditLog","ForecastKPI"); Layer=5; Schema="tenant_fc" }
    "kpi"                = @{ Prefix="kpi";  Entities=@("KPI","KPIValue");                           Layer=5; Schema="tenant_kpi" }
    "satisfaction"       = @{ Prefix="csat"; Entities=@("Survey","Response");                        Layer=5; Schema="tenant_csat" }
    "recommendation"     = @{ Prefix="reco"; Entities=@("Recommendation");                           Layer=5; Schema="tenant_reco" }
    "oee"                = @{ Prefix="oee";  Entities=@("OEE","OEERecord");                          Layer=5; Schema="tenant_oee" }

    # ---- Layer 6: Monitoring ----
    "iot"                = @{ Prefix="iot";  Entities=@("SensorReading","Threshold");                Layer=6; Schema="tenant_iot" }
    "cctv"               = @{ Prefix="cctv"; Entities=@("Camera","Recording");                       Layer=6; Schema="tenant_cctv" }
    "monitoring"         = @{ Prefix="mon";  Entities=@("HealthCheck","Metric");                     Layer=6; Schema="tenant_mon" }
    "backup"             = @{ Prefix="bkp";  Entities=@("BackupJob","Snapshot");                     Layer=6; Schema="tenant_bkp" }
    "alerting"           = @{ Prefix="alr";  Entities=@("Alert","AlertRule");                        Layer=6; Schema="tenant_alr" }
    "audit_viewer"       = @{ Prefix="av";   Entities=@();                                           Layer=6; Schema="tenant_av" }
    "maintenance"        = @{ Prefix="mnt";  Entities=@("MaintenanceSchedule","WorkOrder");          Layer=6; Schema="tenant_mnt" }
    "energy"             = @{ Prefix="eng";  Entities=@("EnergyReading","Tariff");                   Layer=6; Schema="tenant_eng" }

    # ---- Layer 7: Templates ----
    "health"             = @{ Prefix="hlth"; Entities=@("HealthStatus","ComponentHealth");           Layer=7; Schema="" }
    "example"            = @{ Prefix="ex";   Entities=@("ExampleEntity");                            Layer=7; Schema="tenant_ex" }
    "blank"              = @{ Prefix="blk";  Entities=@("BlankEntity");                              Layer=7; Schema="tenant_blk" }
}

# ============================================================
#  Helpers
# ============================================================
function Write-Section($msg) {
    Write-Host ""
    Write-Host "--- $msg ---" -ForegroundColor Cyan
}
function Write-Ok($msg)   { Write-Host "   [OK]   $msg" -ForegroundColor Green;    $script:Stats.Created++ }
function Write-Skip($msg) { Write-Host "   [SKIP] $msg" -ForegroundColor DarkGray; $script:Stats.Skipped++ }
function Write-Warn($msg) { Write-Host "   [WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "   [ERR]  $msg" -ForegroundColor Red;      $script:Stats.Failed++ }
function Write-Dry($msg)  { Write-Host "   [DRY]  $msg" -ForegroundColor Magenta }

function New-FileIfMissing {
    param(
        [string]$Path,
        [string]$Content = ""
    )
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) {
        if ($script:DryRun) {
            Write-Dry "mkdir $dir"
        } else {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
        }
    }

    if ((Test-Path $Path) -and (-not $script:Force)) {
        Write-Skip "$Path"
        return $false
    }

    if ($script:DryRun) {
        Write-Dry "would write $Path"
        return $true
    }

    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8)
    Write-Ok "$Path"
    return $true
}

function New-DirIfMissing {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        if ($script:DryRun) {
            Write-Dry "mkdir $Path"
        } else {
            New-Item -ItemType Directory -Force -Path $Path | Out-Null
            Write-Ok "mkdir $Path"
        }
    } else {
        Write-Skip "exists $Path"
    }
}

# ============================================================
#  New-BaseStructure
# ============================================================
function New-BaseStructure {
    Write-Section "Creating base structure"

    $dirs = @(
        $BackendRoot, $AppDir, $CoreDir, $SharedDir, $ModulesDir,
        $TestsDir,
        (Join-Path $TestsDir "unit"),
        (Join-Path $TestsDir "integration"),
        (Join-Path $TestsDir "property"),
        (Join-Path $TestsDir "manual"),
        $MigrationsDir,
        (Join-Path $BackendRoot "scripts"),
        (Join-Path $BackendRoot "docs")
    )
    foreach ($d in $dirs) { New-DirIfMissing -Path $d }

    # --- pyproject.toml ---
    $pyprojectLines = @(
        '[project]',
        'name = "fastapi-clean-architecture-ddd-erp-iot"',
        'version = "0.1.0"',
        'description = "ERP + CRM + IoT for SME - Clean Architecture + DDD"',
        'readme = "README.md"',
        'requires-python = ">=3.11"',
        'license = { text = "MIT" }',
        'dependencies = [',
        '    "fastapi>=0.110",',
        '    "uvicorn[standard]>=0.27",',
        '    "pydantic>=2.6",',
        '    "pydantic-settings>=2.2",',
        '    "sqlalchemy[asyncio]>=2.0",',
        '    "asyncpg>=0.29",',
        '    "alembic>=1.13",',
        '    "redis>=5.0",',
        '    "cachetools>=5.3",',
        '    "python-jose[cryptography]>=3.3",',
        '    "passlib[argon2]>=1.7",',
        '    "structlog>=24.1",',
        '    "httpx>=0.27",',
        '    "python-multipart>=0.0.9",',
        '    "tenacity>=8.2",',
        ']',
        '',
        '[project.optional-dependencies]',
        'dev = [',
        '    "pytest>=8.0",',
        '    "pytest-asyncio>=0.23",',
        '    "pytest-cov>=5.0",',
        '    "hypothesis>=6.100",',
        '    "testcontainers[postgres,redis]>=4.0",',
        '    "ruff>=0.3",',
        '    "mypy>=1.10",',
        '    "pre-commit>=3.7",',
        ']',
        '',
        '[build-system]',
        'requires = ["setuptools>=68", "wheel"]',
        'build-backend = "setuptools.build_meta"',
        '',
        '[tool.setuptools.packages.find]',
        'where = ["."]',
        'include = ["app*"]',
        '',
        '[tool.pytest.ini_options]',
        'asyncio_mode = "auto"',
        'testpaths = ["tests"]',
        'addopts = "-v --tb=short"',
        'filterwarnings = ["ignore::DeprecationWarning"]',
        '',
        '[tool.coverage.run]',
        'source = ["app"]',
        'omit = ["*/tests/*", "*/migrations/*"]',
        '',
        '[tool.ruff]',
        'line-length = 100',
        'target-version = "py311"',
        '',
        '[tool.ruff.lint]',
        'select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]',
        'ignore = ["E501", "B008"]',
        '',
        '[tool.mypy]',
        'python_version = "3.11"',
        'strict = false',
        'warn_return_any = true',
        'warn_unused_configs = true',
        'ignore_missing_imports = true'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot "pyproject.toml") -Content ($pyprojectLines -join $script:EOL) | Out-Null

    # --- .env.example ---
    $envLines = @(
        '# Application',
        'APP_NAME=erp-iot-api',
        'APP_ENV=development',
        'LOG_LEVEL=INFO',
        'SECRET_KEY=change-me-in-production-use-strong-key',
        '',
        '# Database',
        'DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/erp',
        'DB_POOL_SIZE=20',
        'DB_MAX_OVERFLOW=40',
        'DB_ECHO=false',
        '',
        '# Redis',
        'REDIS_URL=redis://localhost:6379/0',
        'REDIS_MAX_CONNECTIONS=100',
        '',
        '# JWT',
        'JWT_SECRET=change-me-too',
        'JWT_ALGORITHM=HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES=15',
        'REFRESH_TOKEN_EXPIRE_DAYS=7',
        '',
        '# Multi-tenancy',
        'DEFAULT_TENANT_ID=00000000-0000-0000-0000-000000000001',
        '',
        '# External Services',
        'KAFKA_BOOTSTRAP=localhost:9092',
        'MQTT_BROKER=localhost:1883',
        'INFLUXDB_URL=http://localhost:8086',
        'INFLUXDB_TOKEN=change-me',
        'INFLUXDB_ORG=erp',
        'INFLUXDB_BUCKET=iot',
        '',
        '# Feature Flags',
        'FEATURE_AUDIT=true',
        'FEATURE_IDEMPOTENCY=true',
        'FEATURE_EVENTS=true',
        'CACHE_ENABLED=true'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot ".env.example") -Content ($envLines -join $script:EOL) | Out-Null

    # --- README.md ---
    $readmeLines = @(
        '# FastAPI Clean Architecture - ERP + CRM + IoT',
        '',
        'Multi-tenant ERP for SME built with **Clean Architecture + DDD**.',
        '',
        '## Stack',
        '',
        '- **FastAPI** 0.110+ (async)',
        '- **SQLAlchemy** 2.0 (async) + **Alembic**',
        '- **Pydantic** v2 + **pydantic-settings**',
        '- **PostgreSQL** 15+ (schema-per-tenant + RLS)',
        '- **Redis** 7 (cache + idempotency)',
        '- **structlog** (structured logging)',
        '',
        '## Quick Start',
        '',
        '```bat',
        'scaffold.bat              REM create base + health + example',
        'scaffold.bat --all        REM scaffold all 65 modules',
        'scaffold.bat --setup      REM venv + pip install',
        'scaffold.bat --run        REM uvicorn dev server',
        '```',
        '',
        '## Structure',
        '',
        '```',
        'fastapi-backend/',
        '  app/',
        '    core/           # config, logging, security, router registration',
        '    shared/         # base entity/model, session, tenant ctx',
        '    modules/        # 65 modules x 4 layers',
        '      <module>/',
        '        domain/         # entities, VOs, enums, events',
        '        application/    # use cases, interfaces, mappers',
        '        infrastructure/ # models, repos, caches, services',
        '        presentation/   # routers, schemas, dependencies',
        '    main.py         # FastAPI entrypoint',
        '  tests/',
        '    unit/ integration/ property/ manual/',
        '  db/migrations/<module>/V001..V003.sql',
        '  pyproject.toml',
        '  .env.example',
        '```',
        '',
        '## Modules (65 total, 8 layers)',
        '',
        '| Layer | Name | Count |',
        '|---|---|---|',
        '| 0 | Core | 6 |',
        '| 1 | Foundation | 8 |',
        '| 2 | Money Path | 7 |',
        '| 3 | Goods Path | 13 |',
        '| 4 | Operations | 13 |',
        '| 5 | Intelligence | 7 |',
        '| 6 | Monitoring | 8 |',
        '| 7 | Templates | 3 |',
        '',
        '## Run',
        '',
        '```bash',
        'uvicorn app.main:app --reload --port 8000',
        '# OpenAPI: http://localhost:8000/docs',
        '```',
        '',
        '## Layer Rules',
        '',
        '- **Domain**: pure, no framework imports',
        '- **Application**: use cases, 3-branch error handling',
        '- **Infrastructure**: repos (2-branch), caches (never-raise)',
        '- **Presentation**: FastAPI routers, Pydantic schemas',
        '- **Money Path / Goods Path**: idempotent + audit + read-back'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot "README.md") -Content ($readmeLines -join $script:EOL) | Out-Null

    # --- .gitignore ---
    $gitignoreLines = @(
        '__pycache__/',
        '*.py[cod]',
        '*.so',
        '.venv/',
        'venv/',
        'env/',
        '.env',
        '.env.local',
        '.pytest_cache/',
        '.ruff_cache/',
        '.mypy_cache/',
        '.coverage',
        'htmlcov/',
        '*.egg-info/',
        'dist/',
        'build/',
        '.DS_Store',
        'Thumbs.db',
        '*.log',
        '*.db',
        '*.sqlite3'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot ".gitignore") -Content ($gitignoreLines -join $script:EOL) | Out-Null

    # --- .editorconfig ---
    $editorconfigLines = @(
        'root = true',
        '',
        '[*]',
        'charset = utf-8',
        'end_of_line = lf',
        'insert_final_newline = true',
        'trim_trailing_whitespace = true',
        'indent_style = space',
        'indent_size = 4',
        '',
        '[*.py]',
        'indent_size = 4',
        'max_line_length = 100',
        '',
        '[*.{yml,yaml,json}]',
        'indent_size = 2',
        '',
        '[*.md]',
        'trim_trailing_whitespace = false',
        '',
        '[*.{bat,cmd}]',
        'end_of_line = crlf'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot ".editorconfig") -Content ($editorconfigLines -join $script:EOL) | Out-Null

    # --- docker-compose.yml ---
    $dockerComposeLines = @(
        'version: "3.9"',
        '',
        'services:',
        '  postgres:',
        '    image: postgres:16-alpine',
        '    environment:',
        '      POSTGRES_USER: postgres',
        '      POSTGRES_PASSWORD: postgres',
        '      POSTGRES_DB: erp',
        '    ports:',
        '      - "5432:5432"',
        '    volumes:',
        '      - pgdata:/var/lib/postgresql/data',
        '    healthcheck:',
        '      test: ["CMD-SHELL", "pg_isready -U postgres"]',
        '      interval: 5s',
        '      timeout: 5s',
        '      retries: 5',
        '',
        '  redis:',
        '    image: redis:7-alpine',
        '    ports:',
        '      - "6379:6379"',
        '    command: redis-server --appendonly yes',
        '    volumes:',
        '      - redisdata:/data',
        '    healthcheck:',
        '      test: ["CMD", "redis-cli", "ping"]',
        '      interval: 5s',
        '      timeout: 5s',
        '      retries: 5',
        '',
        'volumes:',
        '  pgdata:',
        '  redisdata:'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot "docker-compose.yml") -Content ($dockerComposeLines -join $script:EOL) | Out-Null

    # --- alembic.ini ---
    $alembicLines = @(
        '[alembic]',
        'script_location = db/migrations',
        'prepend_sys_path = .',
        'sqlalchemy.url =',
        '',
        '[loggers]',
        'keys = root,sqlalchemy,alembic',
        '',
        '[handlers]',
        'keys = console',
        '',
        '[formatters]',
        'keys = generic',
        '',
        '[logger_root]',
        'level = WARN',
        'handlers = console',
        'qualname =',
        '',
        '[logger_sqlalchemy]',
        'level = WARN',
        'handlers =',
        'qualname = sqlalchemy.engine',
        '',
        '[logger_alembic]',
        'level = INFO',
        'handlers =',
        'qualname = alembic',
        '',
        '[handler_console]',
        'class = StreamHandler',
        'args = (sys.stderr,)',
        'level = NOTSET',
        'formatter = generic',
        '',
        '[formatter_generic]',
        'format = %(levelname)-5.5s [%(name)s] %(message)s',
        'datefmt = %H:%M:%S'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot "alembic.ini") -Content ($alembicLines -join $script:EOL) | Out-Null

    # --- .pre-commit-config.yaml ---
    $preCommitLines = @(
        'repos:',
        '  - repo: https://github.com/pre-commit/pre-commit-hooks',
        '    rev: v4.6.0',
        '    hooks:',
        '      - id: trailing-whitespace',
        '      - id: end-of-file-fixer',
        '      - id: check-yaml',
        '      - id: check-added-large-files',
        '  - repo: https://github.com/astral-sh/ruff-pre-commit',
        '    rev: v0.4.0',
        '    hooks:',
        '      - id: ruff',
        '        args: [--fix]',
        '      - id: ruff-format'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot ".pre-commit-config.yaml") -Content ($preCommitLines -join $script:EOL) | Out-Null
}

# ============================================================
#  New-AppStructure
# ============================================================
function New-AppStructure {
    Write-Section "Creating app structure"

    # --- app/__init__.py ---
    New-FileIfMissing -Path (Join-Path $AppDir "__init__.py") `
        -Content ('"""FastAPI Clean Architecture - ERP + CRM + IoT."""' + $script:EOL + '__version__ = "0.1.0"' + $script:EOL) | Out-Null

    # --- app/main.py ---
    $mainLines = @(
        '# app/main.py - FastAPI entrypoint',
        'from contextlib import asynccontextmanager',
        '',
        'from fastapi import FastAPI',
        'from fastapi.middleware.cors import CORSMiddleware',
        '',
        'from app.core.config import settings',
        'from app.core.logging import setup_logging, logger',
        'from app.core.routers import register_routers',
        '',
        '',
        '@asynccontextmanager',
        'async def lifespan(app: FastAPI):',
        '    """Application lifespan - startup/shutdown."""',
        '    setup_logging(settings.log_level)',
        '    logger.info("app.startup", env=settings.app_env, version="0.1.0")',
        '    yield',
        '    logger.info("app.shutdown")',
        '',
        '',
        'def create_app() -> FastAPI:',
        '    """Application factory."""',
        '    app = FastAPI(',
        '        title=settings.app_name,',
        '        version="0.1.0",',
        '        docs_url="/docs",',
        '        redoc_url="/redoc",',
        '        openapi_url="/openapi.json",',
        '        lifespan=lifespan,',
        '    )',
        '',
        '    app.add_middleware(',
        '        CORSMiddleware,',
        '        allow_origins=["*"],',
        '        allow_credentials=True,',
        '        allow_methods=["*"],',
        '        allow_headers=["*"],',
        '    )',
        '',
        '    register_routers(app)',
        '',
        '    @app.get("/", tags=["Root"])',
        '    async def root():',
        '        return {',
        '            "service": settings.app_name,',
        '            "version": "0.1.0",',
        '            "status": "ok",',
        '        }',
        '',
        '    return app',
        '',
        '',
        'app = create_app()'
    )
    New-FileIfMissing -Path (Join-Path $AppDir "main.py") -Content ($mainLines -join $script:EOL) | Out-Null

    # --- core/__init__.py ---
    New-FileIfMissing -Path (Join-Path $CoreDir "__init__.py") `
        -Content ('"""Core - config, logging, security, router registration."""' + $script:EOL) | Out-Null

    # --- core/config.py ---
    $configLines = @(
        '# app/core/config.py - Pydantic Settings',
        'from functools import lru_cache',
        '',
        'from pydantic_settings import BaseSettings, SettingsConfigDict',
        '',
        '',
        'class Settings(BaseSettings):',
        '    """Application settings loaded from environment."""',
        '',
        '    model_config = SettingsConfigDict(',
        '        env_file=".env",',
        '        env_file_encoding="utf-8",',
        '        extra="ignore",',
        '        case_sensitive=False,',
        '    )',
        '',
        '    # --- Application ---',
        '    app_name: str = "erp-iot-api"',
        '    app_env: str = "development"',
        '    log_level: str = "INFO"',
        '    secret_key: str = "change-me"',
        '',
        '    # --- Database ---',
        '    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/erp"',
        '    db_pool_size: int = 20',
        '    db_max_overflow: int = 40',
        '    db_echo: bool = False',
        '',
        '    # --- Redis ---',
        '    redis_url: str = "redis://localhost:6379/0"',
        '    redis_max_connections: int = 100',
        '',
        '    # --- JWT ---',
        '    jwt_secret: str = "change-me"',
        '    jwt_algorithm: str = "HS256"',
        '    access_token_expire_minutes: int = 15',
        '    refresh_token_expire_days: int = 7',
        '',
        '    # --- Multi-tenancy ---',
        '    default_tenant_id: str = "00000000-0000-0000-0000-000000000001"',
        '',
        '    # --- External ---',
        '    kafka_bootstrap: str = "localhost:9092"',
        '    mqtt_broker: str = "localhost:1883"',
        '    influxdb_url: str = "http://localhost:8086"',
        '    influxdb_token: str = "change-me"',
        '    influxdb_org: str = "erp"',
        '    influxdb_bucket: str = "iot"',
        '',
        '    # --- Feature Flags ---',
        '    feature_audit: bool = True',
        '    feature_idempotency: bool = True',
        '    feature_events: bool = True',
        '    cache_enabled: bool = True',
        '',
        '',
        '@lru_cache',
        'def get_settings() -> Settings:',
        '    """Cached settings singleton."""',
        '    return Settings()',
        '',
        '',
        'settings = get_settings()'
    )
    New-FileIfMissing -Path (Join-Path $CoreDir "config.py") -Content ($configLines -join $script:EOL) | Out-Null

    # --- core/logging.py ---
    $logLines = @(
        '# app/core/logging.py - structlog configuration',
        'import logging',
        'import sys',
        '',
        'import structlog',
        '',
        '',
        'def setup_logging(level: str = "INFO") -> None:',
        '    """Configure structured logging."""',
        '    logging.basicConfig(',
        '        format="%(message)s",',
        '        stream=sys.stdout,',
        '        level=level,',
        '    )',
        '',
        '    structlog.configure(',
        '        processors=[',
        '            structlog.contextvars.merge_contextvars,',
        '            structlog.processors.add_log_level,',
        '            structlog.processors.TimeStamper(fmt="iso", utc=True),',
        '            structlog.processors.StackInfoRenderer(),',
        '            structlog.processors.format_exc_info,',
        '            structlog.processors.JSONRenderer(),',
        '        ],',
        '        wrapper_class=structlog.make_filtering_bound_logger(',
        '            logging.getLevelName(level)',
        '        ),',
        '        logger_factory=structlog.PrintLoggerFactory(),',
        '        cache_logger_on_first_use=True,',
        '    )',
        '',
        '',
        'logger = structlog.get_logger()'
    )
    New-FileIfMissing -Path (Join-Path $CoreDir "logging.py") -Content ($logLines -join $script:EOL) | Out-Null

    # --- core/security.py ---
    $securityLines = @(
        '# app/core/security.py - JWT helpers',
        'from datetime import datetime, timedelta, timezone',
        'from typing import Any',
        '',
        'from jose import JWTError, jwt',
        '',
        'from app.core.config import settings',
        '',
        '',
        'def create_access_token(',
        '    subject: str,',
        '    tenant_id: str,',
        '    extra: dict[str, Any] | None = None,',
        ') -> str:',
        '    """Create JWT access token."""',
        '    now = datetime.now(timezone.utc)',
        '    payload: dict[str, Any] = {',
        '        "sub": subject,',
        '        "tid": tenant_id,',
        '        "typ": "access",',
        '        "iat": now,',
        '        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),',
        '    }',
        '    if extra:',
        '        payload.update(extra)',
        '    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)',
        '',
        '',
        'def decode_token(token: str) -> dict[str, Any]:',
        '    """Decode and verify JWT."""',
        '    return jwt.decode(',
        '        token,',
        '        settings.jwt_secret,',
        '        algorithms=[settings.jwt_algorithm],',
        '    )'
    )
    New-FileIfMissing -Path (Join-Path $CoreDir "security.py") -Content ($securityLines -join $script:EOL) | Out-Null

    # --- core/routers.py ---
    $routersLines = @(
        '# app/core/routers.py - auto-register module routers',
        'import importlib',
        'from pathlib import Path',
        '',
        'from fastapi import FastAPI',
        '',
        'from app.core.logging import logger',
        '',
        '',
        'def register_routers(app: FastAPI) -> None:',
        '    """Auto-discover and register all module routers."""',
        '    modules_dir = Path(__file__).parent.parent / "modules"',
        '    if not modules_dir.exists():',
        '        logger.warning("modules.dir.not.found", path=str(modules_dir))',
        '        return',
        '',
        '    registered: list[str] = []',
        '    for mod_dir in sorted(modules_dir.iterdir()):',
        '        if not mod_dir.is_dir() or mod_dir.name.startswith("_"):',
        '            continue',
        '        router_module = f"app.modules.{mod_dir.name}.presentation.routers"',
        '        try:',
        '            mod = importlib.import_module(router_module)',
        '            router = getattr(mod, "router", None)',
        '            if router is not None:',
        '                app.include_router(router)',
        '                registered.append(mod_dir.name)',
        '        except ModuleNotFoundError:',
        '            logger.debug("router.skip", module=mod_dir.name)',
        '        except Exception as e:',
        '            logger.warning("router.load.failed", module=mod_dir.name, error=str(e))',
        '',
        '    logger.info("routers.registered", count=len(registered), modules=registered)'
    )
    New-FileIfMissing -Path (Join-Path $CoreDir "routers.py") -Content ($routersLines -join $script:EOL) | Out-Null
}

# ============================================================
#  New-SharedStructure
# ============================================================
function New-SharedStructure {
    Write-Section "Creating shared structure"

    New-FileIfMissing -Path (Join-Path $SharedDir "__init__.py") `
        -Content ('"""Shared - base classes, session, tenant context, exceptions."""' + $script:EOL) | Out-Null

    # --- shared/database.py ---
    $dbLines = @(
        '# app/shared/database.py - async SQLAlchemy session',
        'from collections.abc import AsyncIterator',
        '',
        'from sqlalchemy.ext.asyncio import (',
        '    AsyncSession,',
        '    async_sessionmaker,',
        '    create_async_engine,',
        ')',
        '',
        'from app.core.config import settings',
        '',
        'engine = create_async_engine(',
        '    settings.database_url,',
        '    pool_size=settings.db_pool_size,',
        '    max_overflow=settings.db_max_overflow,',
        '    echo=settings.db_echo,',
        '    pool_pre_ping=True,',
        ')',
        '',
        'AsyncSessionLocal = async_sessionmaker(',
        '    bind=engine,',
        '    class_=AsyncSession,',
        '    expire_on_commit=False,',
        '    autoflush=False,',
        ')',
        '',
        '',
        'async def get_session() -> AsyncIterator[AsyncSession]:',
        '    """FastAPI dependency - yields async DB session."""',
        '    async with AsyncSessionLocal() as session:',
        '        try:',
        '            yield session',
        '            await session.flush()',
        '        except Exception:',
        '            await session.rollback()',
        '            raise'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "database.py") -Content ($dbLines -join $script:EOL) | Out-Null

    # --- shared/redis.py ---
    $redisLines = @(
        '# app/shared/redis.py - Redis client singleton',
        'from functools import lru_cache',
        '',
        'import redis.asyncio as aioredis',
        '',
        'from app.core.config import settings',
        '',
        '',
        '@lru_cache',
        'def get_redis() -> aioredis.Redis:',
        '    """Cached Redis client."""',
        '    return aioredis.from_url(',
        '        settings.redis_url,',
        '        encoding="utf-8",',
        '        decode_responses=True,',
        '        max_connections=settings.redis_max_connections,',
        '    )',
        '',
        '',
        'async def close_redis() -> None:',
        '    """Close Redis connection."""',
        '    client = get_redis()',
        '    await client.close()'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "redis.py") -Content ($redisLines -join $script:EOL) | Out-Null

    # --- shared/base_entity.py ---
    $beLines = @(
        '# app/shared/base_entity.py - Base dataclass entity',
        'from dataclasses import dataclass, field',
        'from datetime import datetime, timezone',
        'from uuid import uuid4',
        '',
        '',
        'def utcnow() -> datetime:',
        '    """Timezone-aware UTC now."""',
        '    return datetime.now(timezone.utc)',
        '',
        '',
        '@dataclass',
        'class BaseEntity:',
        '    """Base entity - all domain entities inherit from this."""',
        '',
        '    id: str = field(default_factory=lambda: str(uuid4()))',
        '    tenant_id: str = ""',
        '    version: int = 1',
        '    created_at: datetime = field(default_factory=utcnow)',
        '    updated_at: datetime = field(default_factory=utcnow)'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "base_entity.py") -Content ($beLines -join $script:EOL) | Out-Null

    # --- shared/base_model.py ---
    $bmLines = @(
        '# app/shared/base_model.py - SQLAlchemy declarative base',
        'from sqlalchemy import Column, DateTime, Integer, func',
        'from sqlalchemy.dialects.postgresql import UUID as PGUUID',
        'from sqlalchemy.orm import declarative_base',
        '',
        'Base = declarative_base()',
        '',
        '',
        'class TenantMixin:',
        '    """Mixin for multi-tenant tables."""',
        '',
        '    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)',
        '    version = Column(Integer, nullable=False, default=1)',
        '    created_at = Column(DateTime(timezone=True), server_default=func.now())',
        '    updated_at = Column(',
        '        DateTime(timezone=True),',
        '        server_default=func.now(),',
        '        onupdate=func.now(),',
        '    )'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "base_model.py") -Content ($bmLines -join $script:EOL) | Out-Null

    # --- shared/tenant_context.py ---
    $tcLines = @(
        '# app/shared/tenant_context.py - contextvars for tenant isolation',
        'from contextvars import ContextVar',
        'from dataclasses import dataclass',
        '',
        '',
        '@dataclass(frozen=True)',
        'class TenantContext:',
        '    """Immutable tenant context."""',
        '',
        '    tenant_id: str',
        '    user_id: str | None = None',
        '    correlation_id: str = ""',
        '',
        '    @property',
        '    def schema_name(self) -> str:',
        '        return f"tenant_{self.tenant_id}"',
        '',
        '',
        '_ctx: ContextVar[TenantContext | None] = ContextVar("tenant_ctx", default=None)',
        '',
        '',
        'def set_context(ctx: TenantContext) -> None:',
        '    """Set current tenant context."""',
        '    _ctx.set(ctx)',
        '',
        '',
        'def get_context() -> TenantContext:',
        '    """Get current tenant context (raises if not set)."""',
        '    ctx = _ctx.get()',
        '    if ctx is None:',
        '        raise RuntimeError("Tenant context not set")',
        '    return ctx',
        '',
        '',
        'def clear_context() -> None:',
        '    """Clear tenant context."""',
        '    _ctx.set(None)'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "tenant_context.py") -Content ($tcLines -join $script:EOL) | Out-Null

    # --- shared/exceptions.py ---
    $excLines = @(
        '# app/shared/exceptions.py - base exceptions (3-branch pattern)',
        '',
        '',
        'class StandardException(Exception):',
        '    """Base for all application exceptions."""',
        '    code: str = "STD_ERROR"',
        '',
        '    def __init__(self, message: str = "") -> None:',
        '        self.message = message or self.__class__.__name__',
        '        super().__init__(self.message)',
        '',
        '',
        'class DomainException(StandardException):',
        '    """Raised when a domain rule is violated."""',
        '    code = "DOMAIN_ERROR"',
        '',
        '',
        'class ApplicationException(StandardException):',
        '    """Raised by use cases."""',
        '    code = "APP_ERROR"',
        '',
        '',
        'class InfrastructureException(StandardException):',
        '    """Raised by repositories / external services."""',
        '    code = "INFRA_ERROR"',
        '',
        '',
        'class NotFoundException(ApplicationException):',
        '    """Resource not found."""',
        '    code = "NOT_FOUND"',
        '',
        '',
        'class ConflictException(ApplicationException):',
        '    """Resource conflict."""',
        '    code = "CONFLICT"',
        '',
        '',
        'class ValidationException(ApplicationException):',
        '    """Input validation failed."""',
        '    code = "VALIDATION_ERROR"'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "exceptions.py") -Content ($excLines -join $script:EOL) | Out-Null

    # --- shared/pagination.py ---
    $pgLines = @(
        '# app/shared/pagination.py - pagination helpers',
        'from dataclasses import dataclass',
        '',
        '',
        '@dataclass(frozen=True)',
        'class Page:',
        '    """Page result."""',
        '',
        '    items: list',
        '    total: int',
        '    page: int',
        '    limit: int',
        '',
        '    @property',
        '    def total_pages(self) -> int:',
        '        return max(1, (self.total + self.limit - 1) // self.limit)',
        '',
        '    @property',
        '    def has_next(self) -> bool:',
        '        return self.page < self.total_pages',
        '',
        '    @property',
        '    def has_prev(self) -> bool:',
        '        return self.page > 1'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "pagination.py") -Content ($pgLines -join $script:EOL) | Out-Null
}

# ============================================================
#  New-Module
# ============================================================
function New-Module {
    param([string]$ModuleName)

    if (-not $ModuleMeta.ContainsKey($ModuleName)) {
        Write-Err "Unknown module: $ModuleName"
        return $false
    }

    $meta     = $ModuleMeta[$ModuleName]
    $prefix   = $meta.Prefix
    $layer    = $meta.Layer
    $entities = $meta.Entities
    $entList  = ($entities -join ', ')
    $schema   = $meta.Schema

    Write-Section "Module: $ModuleName (prefix=$prefix, layer=$layer)"

    $modRoot = Join-Path $ModulesDir $ModuleName

    # --- module __init__.py ---
    $modInit = @(
        '"""Module ' + $ModuleName + ' - Layer ' + $layer + ' (Clean Architecture + DDD)."""',
        '__version__ = "1.0.0"'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "__init__.py") -Content $modInit | Out-Null

    # ============ DOMAIN ============
    New-FileIfMissing -Path (Join-Path $modRoot "domain\__init__.py") `
        -Content ('"""' + $ModuleName + ' domain layer - pure business logic."""' + $script:EOL) | Out-Null

    $domainExc = @(
        '# ' + $ModuleName + '/domain/exceptions.py',
        'from app.shared.exceptions import DomainException',
        '',
        '',
        'class DomainError(DomainException):',
        '    """Domain rule violation for ' + $ModuleName + '."""',
        '    code = "' + $prefix + '_DOMAIN_ERROR"'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "domain\exceptions.py") -Content $domainExc | Out-Null

    $entityLines = @(
        '# ' + $ModuleName + '/domain/entities.py',
        '# Entities: ' + $entList,
        'from dataclasses import dataclass',
        'from datetime import datetime, timezone',
        '',
        'from app.shared.base_entity import BaseEntity',
        '',
        'from .exceptions import DomainError',
        '',
        '',
        'def _utcnow() -> datetime:',
        '    return datetime.now(timezone.utc)',
        '',
        '',
        '# TODO: Add domain entities for: ' + $entList,
        '# Example:',
        '#',
        '# @dataclass',
        '# class ' + $ModuleName + 'Entity(BaseEntity):',
        '#     code: str = ""',
        '#     name: str = ""',
        '#',
        '#     def __post_init__(self):',
        '#         self._validate()',
        '#',
        '#     def _validate(self) -> None:',
        '#         if not self.code:',
        '#             raise DomainError("Code is required")'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "domain\entities.py") -Content $entityLines | Out-Null

    $voLines = @(
        '# ' + $ModuleName + '/domain/value_objects.py',
        'from dataclasses import dataclass',
        '',
        'from .exceptions import DomainError',
        '',
        '',
        '# TODO: Add value objects'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "domain\value_objects.py") -Content $voLines | Out-Null

    $enumLines = @(
        '# ' + $ModuleName + '/domain/enums.py',
        'from enum import Enum',
        '',
        '',
        '# TODO: Add enums'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "domain\enums.py") -Content $enumLines | Out-Null

    $eventLines = @(
        '# ' + $ModuleName + '/domain/events.py - domain event names',
        '',
        '# TODO: Add domain event names',
        '# Example:',
        '# ' + $ModuleName + 'Created = "' + $ModuleName + 'Created"'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "domain\events.py") -Content $eventLines | Out-Null

    # ============ APPLICATION ============
    New-FileIfMissing -Path (Join-Path $modRoot "application\__init__.py") `
        -Content ('"""' + $ModuleName + ' application layer - use cases + ports."""' + $script:EOL) | Out-Null

    $ifaceLines = @(
        '# ' + $ModuleName + '/application/interfaces.py - ports (Protocol)',
        'from typing import Protocol',
        '',
        '',
        '# TODO: Define repository / cache / publisher protocols'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "application\interfaces.py") -Content $ifaceLines | Out-Null

    $appExcLines = @(
        '# ' + $ModuleName + '/application/exceptions.py',
        'from app.shared.exceptions import ApplicationException, NotFoundException',
        '',
        '',
        'class ' + $ModuleName + 'Exception(ApplicationException):',
        '    code = "' + $prefix + '_APP_ERROR"',
        '',
        '',
        'class ' + $ModuleName + 'NotFoundException(NotFoundException):',
        '    code = "' + $prefix + '_NOT_FOUND"'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "application\exceptions.py") -Content $appExcLines | Out-Null

    $ucLines = @(
        '# ' + $ModuleName + '/application/use_cases.py',
        'from app.core.logging import logger',
        'from app.shared.exceptions import (',
        '    StandardException,',
        '    DomainException,',
        '    ApplicationException,',
        ')',
        '',
        '',
        'class ' + $ModuleName + 'Exception(ApplicationException):',
        '    code = "' + $prefix + '_APP_ERROR"',
        '',
        '',
        'class ' + $ModuleName + 'UseCases:',
        '    """Use cases for ' + $ModuleName + ' (3-branch error handling)."""',
        '',
        '    def __init__(self, repo, cache=None, events=None, audit=None):',
        '        self.repo = repo',
        '        self.cache = cache',
        '        self.events = events',
        '        self.audit = audit',
        '',
        '    # TODO: Add use case methods'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "application\use_cases.py") -Content $ucLines | Out-Null

    $mapperLines = @(
        '# ' + $ModuleName + '/application/mappers.py',
        '',
        '',
        'class ' + $ModuleName + 'Mapper:',
        '    """Maps domain entity <-> ORM model <-> pydantic schema."""',
        '    pass'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "application\mappers.py") -Content $mapperLines | Out-Null

    New-FileIfMissing -Path (Join-Path $modRoot "application\utils.py") `
        -Content ('# ' + $ModuleName + '/application/utils.py' + $script:EOL + $script:EOL + '# TODO: helper functions' + $script:EOL) | Out-Null

    # ============ INFRASTRUCTURE ============
    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\__init__.py") `
        -Content ('"""' + $ModuleName + ' infrastructure layer."""' + $script:EOL) | Out-Null

    $modelLines = @(
        '# ' + $ModuleName + '/infrastructure/models.py',
        'from sqlalchemy import Column, String',
        'from sqlalchemy.dialects.postgresql import UUID as PGUUID',
        '',
        'from app.shared.base_model import Base, TenantMixin',
        '',
        '',
        '# TODO: Add SQLAlchemy models for: ' + $entList,
        '# Example:',
        '#',
        '# class ' + $ModuleName + 'Model(Base, TenantMixin):',
        '#     __tablename__ = "' + $ModuleName + '_items"',
        '#     __table_args__ = {"schema": "' + $schema + '"}',
        '#',
        '#     id = Column(PGUUID(as_uuid=True), primary_key=True)',
        '#     code = Column(String(50), nullable=False)'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\models.py") -Content $modelLines | Out-Null

    $repoLines = @(
        '# ' + $ModuleName + '/infrastructure/repositories.py',
        'from app.core.logging import logger',
        'from app.shared.exceptions import InfrastructureException',
        '',
        '',
        'class ' + $ModuleName + 'RepositoryException(InfrastructureException):',
        '    code = "' + $prefix + '_REPO_ERROR"',
        '',
        '',
        'class Postgres' + $ModuleName + 'Repository:',
        '    """Postgres repository for ' + $ModuleName + ' (2-branch error handling)."""',
        '',
        '    def __init__(self, session, tenant_id: str):',
        '        self.session = session',
        '        self.tenant_id = tenant_id',
        '',
        '    # async def save(self, entity): ...',
        '    # async def get_by_id(self, id_): ...',
        '    # async def list(self, filters, page, limit): ...'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\repositories.py") -Content $repoLines | Out-Null

    $cacheLines = @(
        '# ' + $ModuleName + '/infrastructure/caches.py',
        '# Cache never raises.',
        'from app.core.logging import logger',
        '',
        '',
        'class Redis' + $ModuleName + 'Cache:',
        '    """Redis cache for ' + $ModuleName + ' (never-raise)."""',
        '',
        '    def __init__(self, redis_client):',
        '        self.redis = redis_client',
        '',
        '    async def get(self, key: str):',
        '        try:',
        '            return await self.redis.get(f"' + $prefix + ':{key}")',
        '        except Exception as e:',
        '            logger.warning("' + $prefix + '.cache.get.failed", error=str(e))',
        '            return None',
        '',
        '    async def set(self, key: str, value: str, ttl: int = 300) -> None:',
        '        try:',
        '            await self.redis.setex(f"' + $prefix + ':{key}", ttl, value)',
        '        except Exception as e:',
        '            logger.warning("' + $prefix + '.cache.set.failed", error=str(e))',
        '',
        '    async def delete(self, key: str) -> None:',
        '        try:',
        '            await self.redis.delete(f"' + $prefix + ':{key}")',
        '        except Exception as e:',
        '            logger.warning("' + $prefix + '.cache.del.failed", error=str(e))'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\caches.py") -Content $cacheLines | Out-Null

    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\services.py") `
        -Content ('# ' + $ModuleName + '/infrastructure/services.py' + $script:EOL + '# External services (Kafka, InfluxDB, MQTT, etc.)' + $script:EOL) | Out-Null

    # ============ PRESENTATION ============
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\__init__.py") `
        -Content ('"""' + $ModuleName + ' presentation layer."""' + $script:EOL) | Out-Null

    $routerLines = @(
        '# ' + $ModuleName + '/presentation/routers.py',
        'from fastapi import APIRouter, Depends',
        '',
        'from .dependencies import get_' + $ModuleName + '_use_cases',
        '',
        'router = APIRouter(prefix="/api/v1/' + $ModuleName + '", tags=["' + $ModuleName + '"])',
        '',
        '',
        '# TODO: Add endpoints'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\routers.py") -Content $routerLines | Out-Null

    $schemaLines = @(
        '# ' + $ModuleName + '/presentation/schemas.py',
        'from pydantic import BaseModel, ConfigDict',
        '',
        '',
        'class ' + $ModuleName + 'Create(BaseModel):',
        '    pass',
        '',
        '',
        'class ' + $ModuleName + 'Response(BaseModel):',
        '    model_config = ConfigDict(from_attributes=True)'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\schemas.py") -Content $schemaLines | Out-Null

    $docsLines = @(
        'router_docs = {',
        '    "tags": ["' + $ModuleName + '"],',
        '    "description": "Module ' + $ModuleName + ' (Layer ' + $layer + ')",',
        '}'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\docs.py") -Content $docsLines | Out-Null

    $depLines = @(
        '# ' + $ModuleName + '/presentation/dependencies.py',
        'from fastapi import Depends',
        '',
        'from app.shared.database import get_session',
        'from ..application.use_cases import ' + $ModuleName + 'UseCases',
        'from ..infrastructure.repositories import Postgres' + $ModuleName + 'Repository',
        '',
        '',
        'async def get_' + $ModuleName + '_use_cases(',
        '    session=Depends(get_session),',
        ') -> ' + $ModuleName + 'UseCases:',
        '    """DI provider for ' + $ModuleName + ' use cases."""',
        '    tenant_id = "00000000-0000-0000-0000-000000000001"  # TODO: from tenant context',
        '    repo = Postgres' + $ModuleName + 'Repository(session, tenant_id)',
        '    return ' + $ModuleName + 'UseCases(repo=repo)'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\dependencies.py") -Content $depLines | Out-Null

    # ============ SQL MIGRATIONS ============
    if ($schema -and $schema -ne "") {
        $sql1Lines = @(
            '-- ' + $ModuleName + ' - create schema',
            'BEGIN;',
            'CREATE SCHEMA IF NOT EXISTS ' + $schema + ';',
            '-- TODO: CREATE TABLE ' + $schema + '.<table> (...);',
            'COMMIT;'
        ) -join $script:EOL
        New-FileIfMissing -Path (Join-Path $MigrationsDir "$ModuleName\V001__create_$prefix.sql") -Content $sql1Lines | Out-Null

        $sql2Lines = @(
            '-- ' + $ModuleName + ' - seed',
            'BEGIN;',
            '-- TODO: INSERT seed data',
            'COMMIT;'
        ) -join $script:EOL
        New-FileIfMissing -Path (Join-Path $MigrationsDir "$ModuleName\V002__seed_$prefix.sql") -Content $sql2Lines | Out-Null

        $sql3Lines = @(
            '-- ' + $ModuleName + ' - rollback',
            'BEGIN;',
            'DROP SCHEMA IF EXISTS ' + $schema + ' CASCADE;',
            'COMMIT;'
        ) -join $script:EOL
        New-FileIfMissing -Path (Join-Path $MigrationsDir "$ModuleName\V003__rollback_$prefix.sql") -Content $sql3Lines | Out-Null
    }

    # ============ TESTS ============
    $testName = "test_$ModuleName"

    $unitLines = @(
        '# tests/unit/' + $testName + '.py',
        'import pytest',
        '',
        '',
        'class Test' + $ModuleName + 'Domain:',
        '    def test_placeholder(self):',
        '        assert True'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $TestsDir "unit\$testName.py") -Content $unitLines | Out-Null

    $intLines = @(
        '# tests/integration/' + $testName + '_repository.py',
        'import pytest',
        '',
        'pytestmark = pytest.mark.asyncio',
        '',
        '',
        'async def test_repository_placeholder():',
        '    assert True'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $TestsDir "integration\${testName}_repository.py") -Content $intLines | Out-Null

    $propLines = @(
        '# tests/property/' + $testName + '_invariants.py',
        'from hypothesis import given, strategies as st',
        '',
        '',
        '@given(st.integers())',
        'def test_placeholder(n):',
        '    assert isinstance(n, int)'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $TestsDir "property\${testName}_invariants.py") -Content $propLines | Out-Null

    $manLines = @(
        '# Manual Test Cases - ' + $ModuleName,
        '',
        '## TC-01: Placeholder',
        '| Step | Action | Expected | Result |',
        '|---|---|---|---|',
        '| 1 | TODO | TODO | Pass / Fail |'
    ) -join $script:EOL
    New-FileIfMissing -Path (Join-Path $TestsDir "manual\manual_$testName.md") -Content $manLines | Out-Null

    Write-Host "   -> module '$ModuleName' done" -ForegroundColor Green
    return $true
}

# ============================================================
#  Invoke Functions
# ============================================================
function Invoke-Create {
    Write-Host ""
    Write-Host "Create base scaffold" -ForegroundColor Cyan
    New-BaseStructure
    New-AppStructure
    New-SharedStructure
    New-Module -ModuleName "health"
    New-Module -ModuleName "example"
}

function Invoke-Setup {
    Write-Host ""
    Write-Host "Setup venv + pip" -ForegroundColor Cyan
    Push-Location $BackendRoot
    try {
        if (-not (Test-Path "venv")) {
            Write-Section "Creating venv"
            python -m venv venv
            Write-Ok "venv created"
        } else {
            Write-Skip "venv exists"
        }
        $py = ".\venv\Scripts\python.exe"
        Write-Section "Upgrading pip"
        & $py -m pip install --upgrade pip

        Write-Section "Installing project (editable + dev)"
        & $py -m pip install -e ".[dev]"
    } finally {
        Pop-Location
    }
}

function Invoke-Run {
    Push-Location $BackendRoot
    try {
        Write-Host ""
        Write-Host "Starting uvicorn on :8000" -ForegroundColor Cyan
        & ".\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000
    } finally {
        Pop-Location
    }
}

function Invoke-Fixes {
    Write-Section "Applying fixes"
    $envFile = Join-Path $BackendRoot ".env"
    $envExample = Join-Path $BackendRoot ".env.example"
    if ((Test-Path $envExample) -and (-not (Test-Path $envFile))) {
        Copy-Item $envExample $envFile
        Write-Ok "created .env from .env.example"
    } else {
        Write-Skip ".env exists or .env.example missing"
    }
}

function Invoke-Clean {
    Write-Host ""
    Write-Host "Cleaning generated files" -ForegroundColor Cyan
    if (Test-Path $BackendRoot) {
        Remove-Item -Recurse -Force $BackendRoot
        Write-Ok "removed $BackendRoot"
    } else {
        Write-Skip "$BackendRoot does not exist"
    }
}

function Invoke-List {
    Write-Host ""
    Write-Host "Available Modules (65 total, 8 layers)" -ForegroundColor Cyan
    Write-Host ""
    foreach ($l in 0..7) {
        $mods = $ModuleRegistry[$l]
        Write-Host ("Layer {0} ({1} modules):" -f $l, $mods.Count) -ForegroundColor Yellow
        foreach ($m in $mods) {
            $meta = $ModuleMeta[$m]
            Write-Host ("   - {0,-22} prefix={1,-6} layer={2}" -f $m, $meta.Prefix, $meta.Layer)
        }
        Write-Host ""
    }
}

function Invoke-Validate {
    Write-Host ""
    Write-Host "Validating scaffold" -ForegroundColor Cyan
    $missing = @()
    $required = @(
        (Join-Path $BackendRoot "pyproject.toml"),
        (Join-Path $BackendRoot ".env.example"),
        (Join-Path $BackendRoot "README.md"),
        (Join-Path $AppDir "main.py"),
        (Join-Path $CoreDir "config.py"),
        (Join-Path $CoreDir "logging.py"),
        (Join-Path $SharedDir "database.py"),
        (Join-Path $SharedDir "base_entity.py"),
        (Join-Path $SharedDir "base_model.py"),
        (Join-Path $SharedDir "tenant_context.py"),
        (Join-Path $SharedDir "exceptions.py")
    )
    foreach ($f in $required) {
        if (-not (Test-Path $f)) {
            $missing += $f
            Write-Err "missing: $f"
        } else {
            Write-Ok "exists: $f"
        }
    }
    if ($missing.Count -eq 0) {
        Write-Host ""
        Write-Host "   [OK] Scaffold is valid!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host ("   [ERR] {0} file(s) missing" -f $missing.Count) -ForegroundColor Red
    }
}

# ============================================================
#  Main
# ============================================================
$mode    = "create"
$modName = $null
$layer   = $null

for ($i = 0; $i -lt $Args.Count; $i++) {
    switch ($Args[$i]) {
        "--create"   { $mode = "create" }
        "--setup"    { $mode = "setup" }
        "--run"      { $mode = "run" }
        "--fix"      { $mode = "fix" }
        "--clean"    { $mode = "clean" }
        "--all"      { $mode = "all" }
        "--list"     { $mode = "list" }
        "--validate" { $mode = "validate" }
        "--dry-run"  { $script:DryRun = $true }
        "--force"    { $script:Force  = $true }
        "--module"   { if ($i+1 -lt $Args.Count) { $modName = $Args[++$i] } }
        "--layer"    { if ($i+1 -lt $Args.Count) { $layer   = $Args[++$i] } }
        default      { Write-Warn "unknown arg: $($Args[$i])" }
    }
}

try {
    switch ($mode) {
        "create"   { Invoke-Create }
        "setup"    { Invoke-Create; Invoke-Setup }
        "run"      { Invoke-Create; Invoke-Setup; Invoke-Run }
        "fix"      { Invoke-Fixes }
        "clean"    { Invoke-Clean }
        "list"     { Invoke-List }
        "validate" { Invoke-Validate }
        "all" {
            New-BaseStructure
            New-AppStructure
            New-SharedStructure
            foreach ($l in 0..7) {
                foreach ($m in $ModuleRegistry[$l]) {
                    New-Module -ModuleName $m
                }
            }
            Invoke-Fixes
        }
    }

    if ($modName) {
        New-BaseStructure
        New-AppStructure
        New-SharedStructure
        New-Module -ModuleName $modName
    }
    if ($layer -ne $null) {
        New-BaseStructure
        New-AppStructure
        New-SharedStructure
        $l = [int]$layer
        if ($ModuleRegistry.Contains($l)) {
            foreach ($m in $ModuleRegistry[$l]) {
                New-Module -ModuleName $m
            }
        } else {
            Write-Err "unknown layer: $layer (expected 0-7)"
            exit 1
        }
    }
}
catch {
    Write-Err $_.Exception.Message
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkRed
    exit 1
}

# --- Summary ---
$elapsed = (Get-Date) - $StartTime
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ("  Created: {0}" -f $script:Stats.Created) -ForegroundColor Green
Write-Host ("  Skipped: {0}" -f $script:Stats.Skipped) -ForegroundColor DarkGray
Write-Host ("  Failed:  {0}" -f $script:Stats.Failed)  -ForegroundColor Red
Write-Host ("  Elapsed: {0:N2}s" -f $elapsed.TotalSeconds) -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Done." -ForegroundColor Green
Write-Host ""
exit 0
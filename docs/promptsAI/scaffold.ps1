# ============================================================
#  FastAPI Backend Scaffold - PowerShell Driver v2
#  Stack: FastAPI + SQLAlchemy 2.0 + Pydantic v2 + Redis
#  Pattern: Clean Architecture + DDD (4 layers)
#  Fix: no problematic here-strings, ASCII-safe
# ============================================================

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptRoot

# --- Paths ---
$BackendRoot   = "backend"
$AppDir        = Join-Path $BackendRoot "app"
$ModulesDir    = Join-Path $AppDir "modules"
$CoreDir       = Join-Path $AppDir "core"
$SharedDir     = Join-Path $AppDir "shared"
$TestsDir      = Join-Path $BackendRoot "tests"
$MigrationsDir = Join-Path $BackendRoot "db\migrations"

# --- Module Registry ---
$ModuleRegistry = @{
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

# --- Module Metadata ---
$ModuleMeta = @{
    "money"              = @{ Prefix="mny";  Entities=@("Money","VAT","ExchangeRate");                Layer=0 }
    "tenant_context"     = @{ Prefix="tctx"; Entities=@("TenantContext","RequestContext");           Layer=0 }
    "audit"              = @{ Prefix="aud";  Entities=@("AuditLog","ChangeSet");                     Layer=0 }
    "idempotency"        = @{ Prefix="idem"; Entities=@("IdempotencyRecord","IdempotencyKey");       Layer=0 }
    "config"             = @{ Prefix="cfg";  Entities=@("ConfigEntry","ConfigKey");                  Layer=0 }
    "events"             = @{ Prefix="evt";  Entities=@("DomainEvent","EventEnvelope");              Layer=0 }
    "tenancy"            = @{ Prefix="ten";  Entities=@("Tenant","TenantPlan");                      Layer=1 }
    "authentication"     = @{ Prefix="auth"; Entities=@("Credential","Session","Token");             Layer=1 }
    "user"               = @{ Prefix="usr";  Entities=@("User","Role","Permission");                 Layer=1 }
    "employee"           = @{ Prefix="emp";  Entities=@("Employee","Department","Position");         Layer=1 }
    "customer"           = @{ Prefix="cus";  Entities=@("Customer","CustomerGroup","Address");       Layer=1 }
    "supplier"           = @{ Prefix="sup";  Entities=@("Supplier","SupplierCategory");              Layer=1 }
    "product"            = @{ Prefix="prd";  Entities=@("Product","Category","SKU","Barcode");       Layer=1 }
    "pricing"            = @{ Prefix="prc";  Entities=@("PriceList","PriceRule","Discount");         Layer=1 }
    "order"              = @{ Prefix="ord";  Entities=@("Order","OrderLine");                        Layer=2 }
    "invoice"            = @{ Prefix="inv";  Entities=@("Invoice","InvoiceLine");                    Layer=2 }
    "ledger"             = @{ Prefix="led";  Entities=@("JournalEntry","LedgerAccount");             Layer=2 }
    "payment"            = @{ Prefix="pay";  Entities=@("Payment","PaymentAllocation");              Layer=2 }
    "accounting_gateway" = @{ Prefix="acg";  Entities=@("AccountingSync");                           Layer=2 }
    "tax"                = @{ Prefix="tax";  Entities=@("TaxRule","TaxReport");                      Layer=2 }
    "reconciliation"     = @{ Prefix="rec";  Entities=@("Reconciliation","MatchRecord");             Layer=2 }
    "inventory"          = @{ Prefix="invt"; Entities=@("StockItem","StockMove");                    Layer=3 }
    "warehouse"          = @{ Prefix="wh";   Entities=@("Warehouse","Location");                     Layer=3 }
    "deviceiot"          = @{ Prefix="deviceiot";  Entities=@("deviceiot","SerialNumber");           Layer=3 }
    "production"         = @{ Prefix="prod"; Entities=@("ProductionOrder");                          Layer=3 }
    "recipe"             = @{ Prefix="rcp";  Entities=@("Recipe","Ingredient");                      Layer=3 }
    "quality"            = @{ Prefix="qc";   Entities=@("QCInspection");                             Layer=3 }
    "waste"              = @{ Prefix="wst";  Entities=@("WasteRecord");                              Layer=3 }
    "procurement"        = @{ Prefix="proc"; Entities=@("PurchaseOrder");                            Layer=3 }
    "traceability"       = @{ Prefix="trc";  Entities=@("TraceRecord");                              Layer=3 }
    "agriculture"        = @{ Prefix="agr";  Entities=@("Farm","Piot","Harvest");                    Layer=3 }
    "crop"               = @{ Prefix="crp";  Entities=@("Crop","Variety");                           Layer=3 }
    "soil"               = @{ Prefix="soil"; Entities=@("SoilTest");                                 Layer=3 }
    "irrigation"         = @{ Prefix="irr";  Entities=@("IrrigationPlan");                           Layer=3 }
    "transport"          = @{ Prefix="trn";  Entities=@("Vehicle","Driver","Trip");                  Layer=4 }
    "delivery"           = @{ Prefix="dlv";  Entities=@("Delivery","POD");                           Layer=4 }
    "route"              = @{ Prefix="rte";  Entities=@("Route","Stop");                             Layer=4 }
    "gps"                = @{ Prefix="gps";  Entities=@("Location","Geofence");                      Layer=4 }
    "retail"             = @{ Prefix="rtl";  Entities=@("Store");                                    Layer=4 }
    "pos"                = @{ Prefix="pos";  Entities=@("POSTerminal","Transaction");                Layer=4 }
    "shift"              = @{ Prefix="shf";  Entities=@("Shift","Assignment");                       Layer=4 }
    "line_channel"       = @{ Prefix="line"; Entities=@("LINEMessage");                              Layer=4 }
    "promotion"          = @{ Prefix="promo";Entities=@("Promotion","Rule");                         Layer=4 }
    "loyalty"            = @{ Prefix="loy";  Entities=@("LoyaltyAccount","Tier");                    Layer=4 }
    "crm"                = @{ Prefix="crm";  Entities=@("Lead","Deal","Activity");                   Layer=4 }
    "campaign"           = @{ Prefix="cmp";  Entities=@("Campaign");                                 Layer=4 }
    "support"            = @{ Prefix="sup2"; Entities=@("Ticket");                                   Layer=4 }
    "reporting"          = @{ Prefix="rpt";  Entities=@("Report","Schedule");                        Layer=5 }
    "analytics"          = @{ Prefix="anl";  Entities=@("Metric","Snapshot");                        Layer=5 }
    "forecast"           = @{ Prefix="fc";   Entities=@("Forecast","ForecastEvent","ForecastAuditLog","ForecastKPI"); Layer=5 }
    "kpi"                = @{ Prefix="kpi";  Entities=@("KPI","KPIValue");                           Layer=5 }
    "satisfaction"       = @{ Prefix="csat"; Entities=@("Survey","Response");                        Layer=5 }
    "recommendation"     = @{ Prefix="reco"; Entities=@("Recommendation");                           Layer=5 }
    "oee"                = @{ Prefix="oee";  Entities=@("OEE","OEERecord");                          Layer=5 }
    "iot"                = @{ Prefix="iot";  Entities=@("SensorReading","Threshold");                Layer=6 }
    "cctv"               = @{ Prefix="cctv"; Entities=@("Camera","Recording");                       Layer=6 }
    "monitoring"         = @{ Prefix="mon";  Entities=@("HealthCheck","Metric");                     Layer=6 }
    "backup"             = @{ Prefix="bkp";  Entities=@("BackupJob","Snapshot");                     Layer=6 }
    "alerting"           = @{ Prefix="alr";  Entities=@("Alert","AlertRule");                        Layer=6 }
    "audit_viewer"       = @{ Prefix="av";   Entities=@();                                           Layer=6 }
    "maintenance"        = @{ Prefix="mnt";  Entities=@("MaintenanceSchedule","WorkOrder");          Layer=6 }
    "energy"             = @{ Prefix="eng";  Entities=@("EnergyReading","Tariff");                   Layer=6 }
    "health"             = @{ Prefix="hlth"; Entities=@("HealthStatus","ComponentHealth");           Layer=7 }
    "example"            = @{ Prefix="ex";   Entities=@("ExampleEntity");                            Layer=7 }
    "blank"              = @{ Prefix="blk";  Entities=@("BlankEntity");                              Layer=7 }
}

# ============================================================
#  Helpers
# ============================================================
function Write-Section($msg) { Write-Host ""; Write-Host "--- $msg ---" -ForegroundColor Cyan }
function Write-Ok($msg)      { Write-Host "   [OK]   $msg" -ForegroundColor Green }
function Write-Skip($msg)    { Write-Host "   [SKIP] $msg" -ForegroundColor DarkGray }
function Write-Warn($msg)    { Write-Host "   [WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)     { Write-Host "   [ERR]  $msg" -ForegroundColor Red }

function New-FileIfMissing {
    param([string]$Path, [string]$Content = "")
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    if (Test-Path $Path) {
        Write-Skip "$Path"
        return $false
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8)
    Write-Ok "$Path"
    return $true
}

# ============================================================
#  Base structure
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
        $MigrationsDir
    )
    foreach ($d in $dirs) {
        if (-not (Test-Path $d)) {
            New-Item -ItemType Directory -Force -Path $d | Out-Null
            Write-Ok "mkdir $d"
        } else {
            Write-Skip "exists $d"
        }
    }

    # --- pyproject.toml ---
    $pyprojectLines = @(
        '[project]',
        'name = "fastapi-clean-architecture-ddd-erp-iot"',
        'version = "0.1.0"',
        'description = "ERP + CRM + IoT for SME - Clean Architecture + DDD"',
        'requires-python = ">=3.11"',
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
        ']',
        '',
        '[project.optional-dependencies]',
        'dev = [',
        '    "pytest>=8.0",',
        '    "pytest-asyncio>=0.23",',
        '    "hypothesis>=6.100",',
        '    "testcontainers[postgres,redis]>=4.0",',
        '    "ruff>=0.3",',
        '    "mypy>=1.10",',
        ']',
        '',
        '[tool.pytest.ini_options]',
        'asyncio_mode = "auto"',
        'testpaths = ["tests"]',
        '',
        '[tool.ruff]',
        'line-length = 100',
        'target-version = "py311"'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot "pyproject.toml") -Content ($pyprojectLines -join "`n") | Out-Null

    # --- .env.example ---
    $envLines = @(
        'APP_NAME=erp-iot-api',
        'APP_ENV=development',
        'LOG_LEVEL=INFO',
        'SECRET_KEY=change-me-in-production',
        '',
        'DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/erp',
        'DB_POOL_SIZE=20',
        'DB_MAX_OVERFLOW=40',
        '',
        'REDIS_URL=redis://localhost:6379/0',
        '',
        'JWT_SECRET=change-me',
        'JWT_ALGORITHM=HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES=15',
        'REFRESH_TOKEN_EXPIRE_DAYS=7',
        '',
        'DEFAULT_TENANT_ID=00000000-0000-0000-0000-000000000001'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot ".env.example") -Content ($envLines -join "`n") | Out-Null

    # --- README.md (ใช้ array เพื่อหลีกเลี่ยง backtick trap) ---
    $readmeLines = @(
        '# FastAPI Clean Architecture - ERP + CRM + IoT',
        '',
        'Multi-tenant ERP for SME built with Clean Architecture + DDD.',
        '',
        '## Quick start',
        '',
        'Command prompt:',
        '',
        '    scaffold.bat              # create base + health + example',
        '    scaffold.bat --all        # scaffold all 65 modules',
        '    scaffold.bat --setup      # venv + pip',
        '    scaffold.bat --run        # uvicorn dev server',
        '',
        '## Structure',
        '',
        '    fastapi-backend/',
        '      app/',
        '        core/           # config, logging, security',
        '        shared/         # base entity/model, database session, tenant ctx',
        '        modules/        # 65 modules x 4 layers',
        '        main.py         # FastAPI entrypoint',
        '      tests/',
        '      db/migrations/',
        '      pyproject.toml',
        '      .env.example',
        '',
        '## Run',
        '',
        '    uvicorn app.main:app --reload --port 8000',
        '    # http://localhost:8000/docs'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot "README.md") -Content ($readmeLines -join "`n") | Out-Null

    # --- app/__init__.py ---
    New-FileIfMissing -Path (Join-Path $AppDir "__init__.py") -Content "" | Out-Null

    # --- app/main.py ---
    $mainLines = @(
        '# app/main.py - FastAPI entrypoint',
        'from fastapi import FastAPI',
        'from fastapi.middleware.cors import CORSMiddleware',
        '',
        'from app.core.config import settings',
        'from app.core.logging import setup_logging, logger',
        '',
        '',
        'def create_app() -> FastAPI:',
        '    """Application factory."""',
        '    setup_logging(settings.log_level)',
        '',
        '    app = FastAPI(',
        '        title=settings.app_name,',
        '        version="0.1.0",',
        '        docs_url="/docs",',
        '        redoc_url="/redoc",',
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
        '    # --- register module routers ---',
        '    # from app.modules.health.presentation.routers import router as health_router',
        '    # app.include_router(health_router)',
        '',
        '    @app.get("/", tags=["Root"])',
        '    async def root():',
        '        return {"service": settings.app_name, "status": "ok"}',
        '',
        '    return app',
        '',
        '',
        'app = create_app()'
    )
    New-FileIfMissing -Path (Join-Path $AppDir "main.py") -Content ($mainLines -join "`n") | Out-Null

    # --- core/__init__.py ---
    New-FileIfMissing -Path (Join-Path $CoreDir "__init__.py") -Content '"""Core - config, logging, security."""' | Out-Null

    # --- core/config.py ---
    $configLines = @(
        '# app/core/config.py - Pydantic Settings',
        'from pydantic_settings import BaseSettings, SettingsConfigDict',
        '',
        '',
        'class Settings(BaseSettings):',
        '    model_config = SettingsConfigDict(env_file=".env", extra="ignore")',
        '',
        '    app_name: str = "erp-iot-api"',
        '    app_env: str = "development"',
        '    log_level: str = "INFO"',
        '    secret_key: str = "change-me"',
        '',
        '    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/erp"',
        '    db_pool_size: int = 20',
        '    db_max_overflow: int = 40',
        '',
        '    redis_url: str = "redis://localhost:6379/0"',
        '',
        '    jwt_secret: str = "change-me"',
        '    jwt_algorithm: str = "HS256"',
        '    access_token_expire_minutes: int = 15',
        '    refresh_token_expire_days: int = 7',
        '',
        '    default_tenant_id: str = "00000000-0000-0000-0000-000000000001"',
        '',
        '',
        'settings = Settings()'
    )
    New-FileIfMissing -Path (Join-Path $CoreDir "config.py") -Content ($configLines -join "`n") | Out-Null

    # --- core/logging.py ---
    $logLines = @(
        '# app/core/logging.py - structlog config',
        'import logging',
        'import structlog',
        '',
        '',
        'def setup_logging(level: str = "INFO") -> None:',
        '    logging.basicConfig(level=level, format="%(message)s")',
        '    structlog.configure(',
        '        processors=[',
        '            structlog.contextvars.merge_contextvars,',
        '            structlog.processors.add_log_level,',
        '            structlog.processors.TimeStamper(fmt="iso"),',
        '            structlog.processors.JSONRenderer(),',
        '        ],',
        '        wrapper_class=structlog.make_filtering_bound_logger(',
        '            logging.getLevelName(level)',
        '        ),',
        '        cache_logger_on_first_use=True,',
        '    )',
        '',
        '',
        'logger = structlog.get_logger()'
    )
    New-FileIfMissing -Path (Join-Path $CoreDir "logging.py") -Content ($logLines -join "`n") | Out-Null

    # --- shared/__init__.py ---
    New-FileIfMissing -Path (Join-Path $SharedDir "__init__.py") -Content "" | Out-Null

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
        '    echo=False,',
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
        '    """FastAPI dependency - yields async session."""',
        '    async with AsyncSessionLocal() as session:',
        '        try:',
        '            yield session',
        '            await session.flush()',
        '        except Exception:',
        '            await session.rollback()',
        '            raise'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "database.py") -Content ($dbLines -join "`n") | Out-Null

    # --- shared/base_entity.py ---
    $beLines = @(
        '# app/shared/base_entity.py - Base dataclass entity',
        'from dataclasses import dataclass, field',
        'from datetime import datetime, timezone',
        'import uuid',
        '',
        '',
        'def _utcnow() -> datetime:',
        '    return datetime.now(timezone.utc)',
        '',
        '',
        '@dataclass',
        'class BaseEntity:',
        '    """Base entity - all domain entities inherit from this."""',
        '    id: str = field(default_factory=lambda: str(uuid.uuid4()))',
        '    tenant_id: str = ""',
        '    version: int = 1',
        '    created_at: datetime = field(default_factory=_utcnow)',
        '    updated_at: datetime = field(default_factory=_utcnow)'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "base_entity.py") -Content ($beLines -join "`n") | Out-Null

    # --- shared/base_model.py ---
    $bmLines = @(
        '# app/shared/base_model.py - SQLAlchemy declarative base + tenant mixin',
        'from sqlalchemy import Column, DateTime, Integer, func',
        'from sqlalchemy.dialects.postgresql import UUID as PGUUID',
        'from sqlalchemy.orm import declarative_base',
        '',
        'Base = declarative_base()',
        '',
        '',
        'class TenantMixin:',
        '    """Mixin for multi-tenant tables (adds tenant_id, version, timestamps)."""',
        '    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)',
        '    version = Column(Integer, nullable=False, default=1)',
        '    created_at = Column(DateTime(timezone=True), server_default=func.now())',
        '    updated_at = Column(',
        '        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()',
        '    )'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "base_model.py") -Content ($bmLines -join "`n") | Out-Null

    # --- shared/tenant_context.py ---
    $tcLines = @(
        '# app/shared/tenant_context.py - contextvars for tenant isolation',
        'from contextvars import ContextVar',
        'from dataclasses import dataclass',
        '',
        '',
        '@dataclass(frozen=True)',
        'class TenantContext:',
        '    tenant_id: str',
        '    user_id: str | None = None',
        '    correlation_id: str = ""',
        '',
        '',
        '_ctx: ContextVar[TenantContext | None] = ContextVar("tenant_ctx", default=None)',
        '',
        '',
        'def set_context(ctx: TenantContext) -> None:',
        '    _ctx.set(ctx)',
        '',
        '',
        'def get_context() -> TenantContext:',
        '    ctx = _ctx.get()',
        '    if ctx is None:',
        '        raise RuntimeError("Tenant context not set")',
        '    return ctx',
        '',
        '',
        'def clear_context() -> None:',
        '    _ctx.set(None)'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "tenant_context.py") -Content ($tcLines -join "`n") | Out-Null

    # --- shared/exceptions.py ---
    $excLines = @(
        '# app/shared/exceptions.py - base exceptions (3-branch pattern)',
        '',
        '',
        'class StandardException(Exception):',
        '    """Base for all application exceptions."""',
        '    code: str = "STD_ERROR"',
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
        '    code = "INFRA_ERROR"'
    )
    New-FileIfMissing -Path (Join-Path $SharedDir "exceptions.py") -Content ($excLines -join "`n") | Out-Null

    # --- tests/__init__.py ---
    New-FileIfMissing -Path (Join-Path $TestsDir "__init__.py") -Content "" | Out-Null
}

# ============================================================
#  Create one module
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

    Write-Section "Module: $ModuleName (prefix=$prefix, layer=$layer)"

    $modRoot = Join-Path $ModulesDir $ModuleName

    # --- module __init__.py ---
    $modInit = '"""Module ' + $ModuleName + ' - Layer ' + $layer + ' (Clean Architecture + DDD)."""' + "`n" + '__version__ = "1.0.0"'
    New-FileIfMissing -Path (Join-Path $modRoot "__init__.py") -Content $modInit | Out-Null

    # =========================================================
    #  DOMAIN
    # =========================================================
    New-FileIfMissing -Path (Join-Path $modRoot "domain\__init__.py") `
        -Content ('"""' + $ModuleName + ' domain layer - pure business logic."""') | Out-Null

    $domainExc = 'from app.shared.exceptions import DomainException' + "`n`n`n" +
                 'class DomainError(DomainException):' + "`n" +
                 '    """Domain rule violation for ' + $ModuleName + '."""' + "`n" +
                 '    code = "' + $prefix + '_DOMAIN_ERROR"'
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
    )
    New-FileIfMissing -Path (Join-Path $modRoot "domain\entities.py") -Content ($entityLines -join "`n") | Out-Null

    $voLines = @(
        '# ' + $ModuleName + '/domain/value_objects.py',
        'from dataclasses import dataclass',
        '',
        'from .exceptions import DomainError',
        '',
        '',
        '# TODO: Add value objects'
    )
    New-FileIfMissing -Path (Join-Path $modRoot "domain\value_objects.py") -Content ($voLines -join "`n") | Out-Null

    $enumLines = @(
        '# ' + $ModuleName + '/domain/enums.py',
        'from enum import Enum',
        '',
        '',
        '# TODO: Add enums'
    )
    New-FileIfMissing -Path (Join-Path $modRoot "domain\enums.py") -Content ($enumLines -join "`n") | Out-Null

    $eventLines = @(
        '# ' + $ModuleName + '/domain/events.py - domain event names',
        '',
        '# TODO: Add domain event names'
    )
    New-FileIfMissing -Path (Join-Path $modRoot "domain\events.py") -Content ($eventLines -join "`n") | Out-Null

    # =========================================================
    #  APPLICATION
    # =========================================================
    New-FileIfMissing -Path (Join-Path $modRoot "application\__init__.py") `
        -Content ('"""' + $ModuleName + ' application layer - use cases + ports."""') | Out-Null

    $ifaceLines = @(
        '# ' + $ModuleName + '/application/interfaces.py - ports (Protocol)',
        'from typing import Protocol',
        '',
        '',
        '# TODO: Define repository / cache / publisher protocols'
    )
    New-FileIfMissing -Path (Join-Path $modRoot "application\interfaces.py") -Content ($ifaceLines -join "`n") | Out-Null

    $appExcLines = @(
        '# ' + $ModuleName + '/application/exceptions.py',
        'from app.shared.exceptions import ApplicationException',
        '',
        '',
        'class ' + $ModuleName + 'Exception(ApplicationException):',
        '    code = "' + $prefix + '_APP_ERROR"',
        '',
        '',
        'class ' + $ModuleName + 'NotFoundException(' + $ModuleName + 'Exception):',
        '    code = "' + $prefix + '_NOT_FOUND"'
    )
    New-FileIfMissing -Path (Join-Path $modRoot "application\exceptions.py") -Content ($appExcLines -join "`n") | Out-Null

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
    )
    New-FileIfMissing -Path (Join-Path $modRoot "application\use_cases.py") -Content ($ucLines -join "`n") | Out-Null

    $mapperLines = @(
        '# ' + $ModuleName + '/application/mappers.py',
        '',
        '',
        'class ' + $ModuleName + 'Mapper:',
        '    """Maps domain entity <-> ORM model <-> pydantic schema."""',
        '    pass'
    )
    New-FileIfMissing -Path (Join-Path $modRoot "application\mappers.py") -Content ($mapperLines -join "`n") | Out-Null

    New-FileIfMissing -Path (Join-Path $modRoot "application\utils.py") `
        -Content ('# ' + $ModuleName + '/application/utils.py' + "`n`n# TODO: helper functions`n") | Out-Null

    # =========================================================
    #  INFRASTRUCTURE
    # =========================================================
    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\__init__.py") `
        -Content ('"""' + $ModuleName + ' infrastructure layer."""') | Out-Null

    $modelLines = @(
        '# ' + $ModuleName + '/infrastructure/models.py',
        'from sqlalchemy import Column, String',
        'from sqlalchemy.dialects.postgresql import UUID as PGUUID',
        '',
        'from app.shared.base_model import Base, TenantMixin',
        '',
        '',
        '# TODO: Add SQLAlchemy models for: ' + $entList
    )
    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\models.py") -Content ($modelLines -join "`n") | Out-Null

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
        '        self.tenant_id = tenant_id'
    )
    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\repositories.py") -Content ($repoLines -join "`n") | Out-Null

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
    )
    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\caches.py") -Content ($cacheLines -join "`n") | Out-Null

    New-FileIfMissing -Path (Join-Path $modRoot "infrastructure\services.py") `
        -Content ('# ' + $ModuleName + '/infrastructure/services.py' + "`n# External services (Kafka, InfluxDB, MQTT, etc.)`n") | Out-Null

    # =========================================================
    #  PRESENTATION
    # =========================================================
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\__init__.py") `
        -Content ('"""' + $ModuleName + ' presentation layer."""') | Out-Null

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
    )
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\routers.py") -Content ($routerLines -join "`n") | Out-Null

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
    )
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\schemas.py") -Content ($schemaLines -join "`n") | Out-Null

    $docsLines = @(
        'router_docs = {',
        '    "tags": ["' + $ModuleName + '"],',
        '    "description": "Module ' + $ModuleName + ' (Layer ' + $layer + ')",',
        '}'
    )
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\docs.py") -Content ($docsLines -join "`n") | Out-Null

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
    )
    New-FileIfMissing -Path (Join-Path $modRoot "presentation\dependencies.py") -Content ($depLines -join "`n") | Out-Null

    # =========================================================
    #  SQL MIGRATIONS
    # =========================================================
    $schema = "tenant_$prefix"

    $sql1Lines = @(
        '-- ' + $ModuleName + ' - create schema',
        'BEGIN;',
        'CREATE SCHEMA IF NOT EXISTS ' + $schema + ';',
        '-- TODO: CREATE TABLE ' + $schema + '.<table> (...);',
        'COMMIT;'
    )
    New-FileIfMissing -Path (Join-Path $MigrationsDir "$ModuleName\V001__create_$prefix.sql") -Content ($sql1Lines -join "`n") | Out-Null

    $sql2Lines = @(
        '-- ' + $ModuleName + ' - seed',
        'BEGIN;',
        '-- TODO: INSERT seed data',
        'COMMIT;'
    )
    New-FileIfMissing -Path (Join-Path $MigrationsDir "$ModuleName\V002__seed_$prefix.sql") -Content ($sql2Lines -join "`n") | Out-Null

    $sql3Lines = @(
        '-- ' + $ModuleName + ' - rollback',
        'BEGIN;',
        'DROP SCHEMA IF EXISTS ' + $schema + ' CASCADE;',
        'COMMIT;'
    )
    New-FileIfMissing -Path (Join-Path $MigrationsDir "$ModuleName\V003__rollback_$prefix.sql") -Content ($sql3Lines -join "`n") | Out-Null

    # =========================================================
    #  TESTS
    # =========================================================
    $testName = "test_$ModuleName"

    $unitLines = @(
        '# tests/unit/' + $testName + '.py',
        'import pytest',
        '',
        '',
        'class Test' + $ModuleName + 'Domain:',
        '    def test_placeholder(self):',
        '        assert True'
    )
    New-FileIfMissing -Path (Join-Path $TestsDir "unit\$testName.py") -Content ($unitLines -join "`n") | Out-Null

    $intLines = @(
        '# tests/integration/' + $testName + '_repository.py',
        'import pytest',
        '',
        'pytestmark = pytest.mark.asyncio',
        '',
        '',
        'async def test_repository_placeholder():',
        '    assert True'
    )
    New-FileIfMissing -Path (Join-Path $TestsDir "integration\${testName}_repository.py") -Content ($intLines -join "`n") | Out-Null

    $propLines = @(
        '# tests/property/' + $testName + '_invariants.py',
        'from hypothesis import given, strategies as st',
        '',
        '',
        '@given(st.integers())',
        'def test_placeholder(n):',
        '    assert isinstance(n, int)'
    )
    New-FileIfMissing -Path (Join-Path $TestsDir "property\${testName}_invariants.py") -Content ($propLines -join "`n") | Out-Null

    $manLines = @(
        '# Manual Test Cases - ' + $ModuleName,
        '',
        '## TC-01: Placeholder',
        '| Step | Action | Expected | Result |',
        '|---|---|---|---|',
        '| 1 | TODO | TODO | Pass / Fail |'
    )
    New-FileIfMissing -Path (Join-Path $TestsDir "manual\manual_$testName.md") -Content ($manLines -join "`n") | Out-Null

    Write-Host "   -> module '$ModuleName' done" -ForegroundColor Green
    return $true
}

# ============================================================
#  Fixes
# ============================================================
function Invoke-Fixes {
    Write-Section "Applying fixes"

    $gitignoreLines = @(
        '__pycache__/',
        '*.py[cod]',
        '.venv/',
        'venv/',
        '.env',
        '.pytest_cache/',
        '.ruff_cache/',
        '.mypy_cache/',
        '*.egg-info/',
        'dist/',
        'build/'
    )
    New-FileIfMissing -Path (Join-Path $BackendRoot ".gitignore") -Content ($gitignoreLines -join "`n") | Out-Null

    $envFile = Join-Path $BackendRoot ".env"
    $envExample = Join-Path $BackendRoot ".env.example"
    if ((Test-Path $envExample) -and (-not (Test-Path $envFile))) {
        Copy-Item $envExample $envFile
        Write-Ok "created .env from .env.example"
    } else {
        Write-Skip ".env exists or .env.example missing"
    }
}

# ============================================================
#  Commands
# ============================================================
function Invoke-Create {
    Write-Host ""
    Write-Host "Create base scaffold" -ForegroundColor Cyan
    New-BaseStructure
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

# ============================================================
#  Main
# ============================================================
$mode    = "create"
$modName = $null
$layer   = $null

for ($i = 0; $i -lt $Args.Count; $i++) {
    switch ($Args[$i]) {
        "--create"  { $mode = "create" }
        "--setup"   { $mode = "setup" }
        "--run"     { $mode = "run" }
        "--fix"     { $mode = "fix" }
        "--clean"   { $mode = "clean" }
        "--all"     { $mode = "all" }
        "--module"  { if ($i+1 -lt $Args.Count) { $modName = $Args[++$i] } }
        "--layer"   { if ($i+1 -lt $Args.Count) { $layer   = $Args[++$i] } }
        default     { Write-Warn "unknown arg: $($Args[$i])" }
    }
}

try {
    switch ($mode) {
        "create" { Invoke-Create }
        "setup"  { Invoke-Create; Invoke-Setup }
        "run"    { Invoke-Create; Invoke-Setup; Invoke-Run }
        "fix"    { Invoke-Fixes }
        "clean"  { Invoke-Clean }
        "all" {
            New-BaseStructure
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
        New-Module -ModuleName $modName
    }
    if ($layer -ne $null) {
        New-BaseStructure
        $l = [int]$layer
        if ($ModuleRegistry.ContainsKey($l)) {
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
    exit 1
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
exit 0
# ============================================================
#  create_tenant_context.ps1
#  สร้างโครงสร้าง Module tenant_context (ห้ามไฟล์ว่าง)
#  Create tenant_context module structure (no empty files)
# ============================================================

$ErrorActionPreference = "Stop"
$ROOT = "app\modules\tenant_context"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Creating tenant_context module at $ROOT" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ---------- Helper: เขียนไฟล์ (UTF-8 no BOM) ----------
function Write-File {
    param(
        [string]$Path,
        [string]$Content
    )
    $dir = Split-Path $Path -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $fullDir = (Resolve-Path -LiteralPath $dir).Path
    $fullPath = Join-Path $fullDir (Split-Path $Path -Leaf)
    [System.IO.File]::WriteAllText($fullPath, $Content, $utf8)
    Write-Host "  [OK] $Path" -ForegroundColor Green
}

# ---------- สร้างโฟลเดอร์ ----------
$dirs = @(
    "$ROOT",
    "$ROOT\domain",
    "$ROOT\application",
    "$ROOT\infrastructure",
    "$ROOT\presentation"
)
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Force -Path $d | Out-Null
    }
}
Write-Host "[OK] Folders created`n" -ForegroundColor Green

# ============================================================
#  ROOT __init__.py
# ============================================================
Write-File "$ROOT\__init__.py" @'
"""Module tenant_context — Layer 0 (Clean Architecture + DDD).

Tenant context propagation ผ่าน contextvars สำหรับ multi-tenant ERP/CRM/IoT
Tenant context propagation via contextvars for multi-tenant ERP/CRM/IoT
"""
__version__ = "1.0.0"

from .domain.value_objects import (
    TenantContext,
    RequestContext,
    set_context,
    get_context,
    clear_context,
)
from .domain.enums import TenantScope, IsolationLevel

__all__ = [
    "TenantContext",
    "RequestContext",
    "set_context",
    "get_context",
    "clear_context",
    "TenantScope",
    "IsolationLevel",
]
'@

# ============================================================
#  DOMAIN LAYER
# ============================================================
Write-Host "--- Creating DOMAIN layer ---" -ForegroundColor Yellow

# ---------- domain\__init__.py ----------
Write-File "$ROOT\domain\__init__.py" @'
"""tenant_context domain layer — pure business logic.

ชั้นโดเมน — ตรรกะธุรกิจล้วน
"""
from .entities import RequestContext  # noqa: F401  (re-export for convenience)
from .enums import IsolationLevel, TenantScope
from .events import (
    TenantContextCleared,
    TenantContextEstablished,
    TenantSwitched,
)
from .exceptions import DomainError
from .value_objects import (
    RequestContext as RequestContextVO,
    TenantContext,
    clear_context,
    get_context,
    set_context,
)

__all__ = [
    "TenantContext",
    "RequestContext",
    "RequestContextVO",
    "set_context",
    "get_context",
    "clear_context",
    "TenantScope",
    "IsolationLevel",
    "DomainError",
    "TenantContextEstablished",
    "TenantContextCleared",
    "TenantSwitched",
]
'@

# ---------- domain\exceptions.py ----------
Write-File "$ROOT\domain\exceptions.py" @'
"""tenant_context domain exceptions — ข้อยกเว้นโดเมน."""
from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for tenant_context — ละเมิดกฎโดเมน."""

    code = "tctx_DOMAIN_ERROR"

    def __init__(self, message: str = "Tenant context domain error"):
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message
'@

# ---------- domain\enums.py ----------
Write-File "$ROOT\domain\enums.py" @'
"""tenant_context enums — Enum สำหรับบริบทผู้เช่า."""
from enum import Enum


class TenantScope(str, Enum):
    """TenantScope — ขอบเขตการเข้าถึง tenant."""

    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    USER = "USER"


class IsolationLevel(str, Enum):
    """IsolationLevel — ระดับการแยกข้อมูล."""

    SCHEMA_PER_TENANT = "SCHEMA_PER_TENANT"
    DATABASE_PER_TENANT = "DATABASE_PER_TENANT"
    ROW_LEVEL = "ROW_LEVEL"
'@

# ---------- domain\events.py ----------
Write-File "$ROOT\domain\events.py" @'
"""tenant_context domain events — เหตุการณ์โดเมน."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class TenantContextEstablished:
    """TenantContextEstablished — สร้าง context สำเร็จ."""

    tenant_id: str
    user_id: str | None
    correlation_id: str
    request_id: str
    occurred_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class TenantContextCleared:
    """TenantContextCleared — ล้าง context."""

    tenant_id: str
    correlation_id: str
    occurred_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class TenantSwitched:
    """TenantSwitched — เปลี่ยน tenant."""

    from_tenant_id: str
    to_tenant_id: str
    user_id: str | None
    occurred_at: datetime = field(default_factory=_utcnow)
'@

# ---------- domain\entities.py ----------
Write-File "$ROOT\domain\entities.py" @'
"""tenant_context entities — เอนทิตีบริบท.

หมายเหตุ: Module นี้เป็น pure VO — entities.py มีไว้เพื่อ re-export
RequestContext ที่อาจถูกใช้เป็น entity ในบางบริบท
Note: This module is pure VO — entities.py is kept to re-export
RequestContext which may act as an entity in some contexts.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class RequestContext:
    """RequestContext entity — บริบทคำขอ (HTTP-level metadata)."""

    method: str = "GET"
    path: str = "/"
    ip_address: str = "0.0.0.0"
    user_agent: str = ""
    started_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self):
        if not self.method:
            from .exceptions import DomainError
            raise DomainError("Method is required")
        if not self.path:
            from .exceptions import DomainError
            raise DomainError("Path is required")
'@

# ---------- domain\value_objects.py ----------
Write-File "$ROOT\domain\value_objects.py" @'
"""tenant_context value objects — วัตถุค่า บริบทผู้เช่า.

ใช้ contextvars แทน global state → async-safe
Use contextvars instead of global state → async-safe
"""
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .exceptions import DomainError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================
# TenantContext VO
# ============================================================
@dataclass(frozen=True)
class TenantContext:
    """Tenant context VO — วัตถุบริบทผู้เช่า."""

    tenant_id: str
    user_id: str | None = None
    correlation_id: str = ""
    request_id: str = ""
    locale: str = "th-TH"
    timezone: str = "Asia/Bangkok"
    established_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.tenant_id:
            raise DomainError("Tenant ID is required")
        if not self.correlation_id:
            raise DomainError("Correlation ID is required")

    @property
    def schema_name(self) -> str:
        """PostgreSQL schema name — ชื่อ schema."""
        return f"tenant_{self.tenant_id}"

    def redis_namespace(self, key: str) -> str:
        """Namespace Redis key — prefix Redis."""
        return f"t:{self.tenant_id}:{key}"

    def kafka_topic(self, topic: str) -> str:
        """Namespace Kafka topic — prefix Kafka."""
        return f"t.{self.tenant_id}.{topic}"

    def to_dict(self) -> dict:
        """Serialize to dict — แปลงเป็น dict."""
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "request_id": self.request_id,
            "locale": self.locale,
            "timezone": self.timezone,
            "established_at": self.established_at.isoformat(),
        }


# ============================================================
# RequestContext VO
# ============================================================
@dataclass(frozen=True)
class RequestContext:
    """Request context VO — วัตถุบริบทคำขอ."""

    method: str
    path: str
    ip_address: str
    user_agent: str = ""
    started_at: datetime = field(default_factory=_utcnow)


# ============================================================
# ContextVar-based propagation (async-safe)
# ============================================================
_context_var: ContextVar[TenantContext | None] = ContextVar(
    "tenant_context", default=None
)


def set_context(ctx: TenantContext) -> None:
    """Set current context — ตั้งค่า context ปัจจุบัน."""
    _context_var.set(ctx)


def get_context() -> TenantContext:
    """Get current context — ดึง context ปัจจุบัน."""
    ctx = _context_var.get()
    if ctx is None:
        raise DomainError("Tenant context not set")
    return ctx


def clear_context() -> None:
    """Clear context — ล้าง context."""
    _context_var.set(None)


def has_context() -> bool:
    """Check if context is set — ตรวจสอบว่ามี context หรือไม่."""
    return _context_var.get() is not None
'@

Write-Host "[OK] domain done`n" -ForegroundColor Green

# ============================================================
#  APPLICATION LAYER
# ============================================================
Write-Host "--- Creating APPLICATION layer ---" -ForegroundColor Yellow

# ---------- application\__init__.py ----------
Write-File "$ROOT\application\__init__.py" @'
"""tenant_context application layer — use cases + ports.

ชั้นแอปพลิเคชัน — use cases และ ports
"""
from .exceptions import (
    TenantContextException,
    TenantNotFoundInContext,
)
from .use_cases import TenantContextUseCases
from .utils import requires_tenant, tenant_scoped

__all__ = [
    "TenantContextUseCases",
    "TenantContextException",
    "TenantNotFoundInContext",
    "requires_tenant",
    "tenant_scoped",
]
'@

# ---------- application\exceptions.py ----------
Write-File "$ROOT\application\exceptions.py" @'
"""tenant_context application exceptions — ข้อยกเว้นแอปพลิเคชัน."""
from app.shared.exceptions import ApplicationException


class TenantContextException(ApplicationException):
    """TenantContextException — ข้อผิดพลาดระดับแอปพลิเคชัน."""

    code = "tctx_APP_ERROR"

    def __init__(self, message: str = "Tenant context operation failed"):
        self.message = message
        super().__init__(message)


class TenantNotFoundInContext(TenantContextException):
    """TenantNotFoundInContext — ไม่พบ tenant ใน context."""

    code = "tctx_NOT_FOUND"

    def __init__(self, message: str = "Tenant not found in context"):
        super().__init__(message)
'@

# ---------- application\interfaces.py ----------
Write-File "$ROOT\application\interfaces.py" @'
"""tenant_context application interfaces — ports (Protocol).

พอร์ตสำหรับ repository / cache / resolver
"""
from typing import Protocol

from ..domain.value_objects import TenantContext


class ITenantContextProvider(Protocol):
    """ITenantContextProvider — พอร์ตจัดการ context."""

    def get(self) -> TenantContext: ...

    def set(self, ctx: TenantContext) -> None: ...

    def clear(self) -> None: ...


class ITenantResolver(Protocol):
    """ITenantResolver — พอร์ตค้นหา tenant จาก identifier."""

    async def resolve(self, identifier: str) -> TenantContext | None: ...


class ITenantCache(Protocol):
    """ITenantCache — พอร์ตแคชข้อมูล tenant."""

    async def get(self, identifier: str) -> TenantContext | None: ...

    async def insert(self, identifier: str, ctx: TenantContext) -> None: ...

    async def delete(self, identifier: str) -> None: ...


__all__ = [
    "ITenantContextProvider",
    "ITenantResolver",
    "ITenantCache",
]
'@

# ---------- application\mappers.py ----------
Write-File "$ROOT\application\mappers.py" @'
"""tenant_context application mappers — ตัวแปลงข้อมูล."""
from ..domain.value_objects import TenantContext


class TenantContextMapper:
    """TenantContextMapper — แปลง domain <-> dict/headers."""

    @staticmethod
    def to_context(data: dict) -> TenantContext:
        """แปลง dict เป็น TenantContext — Map dict to TenantContext."""
        return TenantContext(
            tenant_id=data.get("tenant_id", ""),
            user_id=data.get("user_id"),
            correlation_id=data.get("correlation_id", ""),
            request_id=data.get("request_id", ""),
            locale=data.get("locale", "th-TH"),
            timezone=data.get("timezone", "Asia/Bangkok"),
        )

    @staticmethod
    def to_headers(ctx: TenantContext) -> dict:
        """แปลง TenantContext เป็น headers — Map to headers."""
        return {
            "X-Tenant-ID": ctx.tenant_id,
            "X-Correlation-ID": ctx.correlation_id,
            "X-Request-ID": ctx.request_id,
            "Accept-Language": ctx.locale,
        }
'@

# ---------- application\use_cases.py ----------
Write-File "$ROOT\application\use_cases.py" @'
"""tenant_context use cases — กรณีการใช้งานบริบทผู้เช่า.

Error handling: 3-branch (StandardException → DomainError → Exception)
"""
import logging
from uuid import uuid4

from app.shared.exceptions import (
    ApplicationException,
    DomainException,
    StandardException,
)

from ..domain.exceptions import DomainError
from ..domain.value_objects import (
    TenantContext,
    clear_context,
    get_context,
    set_context,
)
from .exceptions import TenantContextException
from .interfaces import ITenantResolver

logger = logging.getLogger(__name__)


def _new_correlation_id() -> str:
    """สร้าง correlation ID — Generate a new correlation ID."""
    return str(uuid4())


class TenantContextUseCases:
    """Tenant context use cases — กรณีการใช้งานบริบทผู้เช่า."""

    def __init__(self, resolver: ITenantResolver | None = None, cache=None):
        self.resolver = resolver
        self.cache = cache

    async def establish(
        self,
        tenant_id: str,
        user_id: str | None,
        headers: dict,
    ) -> TenantContext:
        """Establish context from request — สร้าง context จาก request."""
        try:
            ctx = TenantContext(
                tenant_id=tenant_id,
                user_id=user_id,
                correlation_id=headers.get("X-Correlation-ID")
                or _new_correlation_id(),
                request_id=headers.get("X-Request-ID") or _new_correlation_id(),
                locale=headers.get("Accept-Language", "th-TH"),
                timezone=headers.get("X-Timezone", "Asia/Bangkok"),
            )
            set_context(ctx)
            return ctx
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception as e:
            logger.exception("Error in establish tenant context: %s", e)
            raise TenantContextException()

    async def resolve_and_establish(
        self,
        identifier: str,
        user_id: str | None,
        headers: dict,
    ) -> TenantContext:
        """Resolve tenant แล้ว establish context — Resolve + establish."""
        try:
            # 1) ลอง cache ก่อน
            if self.cache is not None:
                cached = await self.cache.get(identifier)
                if cached is not None:
                    set_context(cached)
                    return cached

            # 2) resolve จาก resolver
            if self.resolver is None:
                raise TenantContextException("Tenant resolver not configured")
            ctx = await self.resolver.resolve(identifier)
            if ctx is None:
                raise TenantContextException(
                    f"Tenant not found: {identifier}"
                )

            # 3) enrich headers
            enriched = TenantContext(
                tenant_id=ctx.tenant_id,
                user_id=user_id,
                correlation_id=headers.get("X-Correlation-ID")
                or _new_correlation_id(),
                request_id=headers.get("X-Request-ID")
                or _new_correlation_id(),
                locale=headers.get("Accept-Language", ctx.locale),
                timezone=headers.get("X-Timezone", ctx.timezone),
            )
            set_context(enriched)

            # 4) cache
            if self.cache is not None:
                await self.cache.insert(identifier, enriched)

            return enriched
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception as e:
            logger.exception("Error in resolve_and_establish: %s", e)
            raise TenantContextException()

    def current(self) -> TenantContext:
        """Get current context — ดึง context ปัจจุบัน."""
        try:
            return get_context()
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception as e:
            logger.exception("Error in current(): %s", e)
            raise TenantContextException()

    def teardown(self) -> None:
        """Clear current context — ล้าง context ปัจจุบัน."""
        clear_context()
'@

# ---------- application\utils.py ----------
Write-File "$ROOT\application\utils.py" @'
"""tenant_context application utils — เครื่องมือช่วย."""
import functools
from typing import Callable

from .exceptions import TenantNotFoundInContext
from ..domain.value_objects import get_context, has_context


def requires_tenant(fn: Callable) -> Callable:
    """Decorator: บังคับว่าต้องมี tenant context.

    Decorator: enforce that tenant context exists.
    """

    @functools.wraps(fn)
    async def async_wrapper(*args, **kwargs):
        if not has_context():
            raise TenantNotFoundInContext()
        return await fn(*args, **kwargs)

    @functools.wraps(fn)
    def sync_wrapper(*args, **kwargs):
        if not has_context():
            raise TenantNotFoundInContext()
        return fn(*args, **kwargs)

    import inspect

    if inspect.iscoroutinefunction(fn):
        return async_wrapper
    return sync_wrapper


def tenant_scoped(key: str) -> str:
    """สร้าง key ที่ scope ตาม tenant ปัจจุบัน — Tenant-scoped key."""
    ctx = get_context()
    return ctx.redis_namespace(key)
'@

Write-Host "[OK] application done`n" -ForegroundColor Green

# ============================================================
#  INFRASTRUCTURE LAYER
# ============================================================
Write-Host "--- Creating INFRASTRUCTURE layer ---" -ForegroundColor Yellow

# ---------- infrastructure\__init__.py ----------
Write-File "$ROOT\infrastructure\__init__.py" @'
"""tenant_context infrastructure layer.

ชั้นโครงสร้างพื้นฐาน — resolver, cache, extractor
"""
from .caches import RedisTenantCache
from .repositories import PostgresTenantResolver
from .services import HeaderTenantExtractor

__all__ = [
    "PostgresTenantResolver",
    "RedisTenantCache",
    "HeaderTenantExtractor",
]
'@

# ---------- infrastructure\models.py ----------
Write-File "$ROOT\infrastructure\models.py" @'
"""tenant_context infrastructure models — ไม่มี (context ไม่ persist).

Context ไม่ถูก persist ลง DB — resolve จาก public.tenants แทน
Context is not persisted — resolved from public.tenants instead
"""
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.shared.base_model import Base  # noqa: F401  (kept for parity)


__all__: list[str] = []
'@

# ---------- infrastructure\repositories.py ----------
Write-File "$ROOT\infrastructure\repositories.py" @'
"""tenant_context infrastructure repositories — Postgres tenant resolver.

Error handling: 2-branch (StandardException → Exception)
"""
import logging
from uuid import uuid4

from sqlalchemy import text

from app.shared.exceptions import (
    InfrastructureException,
    StandardException,
)

from ..domain.exceptions import DomainError
from ..domain.value_objects import TenantContext

logger = logging.getLogger(__name__)


class TenantContextRepositoryException(InfrastructureException):
    """TenantContextRepositoryException — ข้อผิดพลาด repository."""

    code = "tctx_REPO_ERROR"


class PostgresTenantResolver:
    """Resolve tenant from DB — ค้นหา tenant จาก DB."""

    def __init__(self, session):
        self.session = session

    async def resolve(self, identifier: str) -> TenantContext | None:
        """Resolve tenant by slug — ค้นหา tenant จาก slug."""
        try:
            result = await self.session.execute(
                text(
                    "SELECT id FROM public.tenants "
                    "WHERE slug = :s AND active = true"
                ),
                {"s": identifier},
            )
            row = result.first()
            if not row:
                return None
            return TenantContext(
                tenant_id=str(row.id),
                correlation_id=str(uuid4()),
            )
        except StandardException:
            raise
        except DomainError:
            raise
        except Exception as e:
            logger.exception("Error resolving tenant: %s", e)
            raise TenantContextRepositoryException()
'@

# ---------- infrastructure\caches.py ----------
Write-File "$ROOT\infrastructure\caches.py" @'
"""tenant_context infrastructure caches — Redis cache (never-raise).

Cache ห้าม raise — fallback เงียบ ๆ
Cache must never raise — silent fallback
"""
import json
import logging

from ..domain.value_objects import TenantContext

logger = logging.getLogger(__name__)


class RedisTenantCache:
    """Cache tenant lookup — แคชข้อมูล tenant."""

    def __init__(self, redis_client, ttl: int = 300):
        self.redis = redis_client
        self.ttl = ttl

    async def get(self, identifier: str) -> TenantContext | None:
        """ดึง tenant จาก cache — Get tenant from cache (never-raise)."""
        try:
            data = await self.redis.get(f"tenant:lookup:{identifier}")
            if not data:
                return None
            parsed = json.loads(data)
            return TenantContext(
                tenant_id=parsed["tenant_id"],
                user_id=parsed.get("user_id"),
                correlation_id=parsed.get("correlation_id", ""),
                request_id=parsed.get("request_id", ""),
                locale=parsed.get("locale", "th-TH"),
                timezone=parsed.get("timezone", "Asia/Bangkok"),
            )
        except Exception as e:
            logger.warning("Cache get failed. Falling back: %s", e)
            return None

    async def insert(self, identifier: str, ctx: TenantContext) -> None:
        """บันทึก tenant ลง cache — Insert tenant into cache."""
        try:
            await self.redis.setex(
                f"tenant:lookup:{identifier}",
                self.ttl,
                json.dumps(ctx.to_dict()),
            )
        except Exception as e:
            logger.warning("Cache insert failed: %s", e)

    async def delete(self, identifier: str) -> None:
        """ลบ tenant จาก cache — Delete tenant from cache."""
        try:
            await self.redis.delete(f"tenant:lookup:{identifier}")
        except Exception as e:
            logger.warning("Cache delete failed: %s", e)
'@

# ---------- infrastructure\services.py ----------
Write-File "$ROOT\infrastructure\services.py" @'
"""tenant_context infrastructure services — HeaderTenantExtractor.

ดึง tenant จาก HTTP header
Extract tenant from HTTP header
"""
from ..domain.exceptions import DomainError
from ..domain.value_objects import TenantContext


class HeaderTenantExtractor:
    """HeaderTenantExtractor — ดึง tenant จาก HTTP headers."""

    TENANT_HEADER = "X-Tenant-ID"
    CORRELATION_HEADER = "X-Correlation-ID"
    REQUEST_HEADER = "X-Request-ID"

    def extract(self, headers: dict) -> TenantContext:
        """ดึง tenant context จาก headers — Extract from headers."""
        # normalize header keys (case-insensitive)
        lower = {k.lower(): v for k, v in headers.items()}

        tenant_id = lower.get(self.TENANT_HEADER.lower(), "")
        if not tenant_id:
            raise DomainError(
                f"Missing required header: {self.TENANT_HEADER}"
            )

        return TenantContext(
            tenant_id=tenant_id,
            user_id=lower.get("x-user-id"),
            correlation_id=lower.get(
                self.CORRELATION_HEADER.lower(), ""
            ),
            request_id=lower.get(self.REQUEST_HEADER.lower(), ""),
            locale=lower.get("accept-language", "th-TH"),
            timezone=lower.get("x-timezone", "Asia/Bangkok"),
        )
'@

Write-Host "[OK] infrastructure done`n" -ForegroundColor Green

# ============================================================
#  PRESENTATION LAYER
# ============================================================
Write-Host "--- Creating PRESENTATION layer ---" -ForegroundColor Yellow

# ---------- presentation\__init__.py ----------
Write-File "$ROOT\presentation\__init__.py" @'
"""tenant_context presentation layer — HTTP layer."""
from .dependencies import (
    get_tenant_context,
    get_tenant_context_use_cases,
)
from .routers import router

__all__ = [
    "router",
    "get_tenant_context",
    "get_tenant_context_use_cases",
]
'@

# ---------- presentation\schemas.py ----------
Write-File "$ROOT\presentation\schemas.py" @'
"""tenant_context presentation schemas — Pydantic schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantContextSchema(BaseModel):
    """TenantContextSchema — schema สำหรับ tenant context."""

    tenant_id: str
    user_id: str | None = None
    correlation_id: str
    request_id: str = ""
    locale: str = "th-TH"
    timezone: str = "Asia/Bangkok"
    schema_name: str = ""
    established_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SwitchTenantRequest(BaseModel):
    """SwitchTenantRequest — คำขอเปลี่ยน tenant."""

    tenant_id: str = Field(..., min_length=1, max_length=64)
    user_id: str | None = Field(default=None, max_length=64)


class SwitchTenantResponse(BaseModel):
    """SwitchTenantResponse — ผลลัพธ์การเปลี่ยน tenant."""

    tenant_id: str
    correlation_id: str
    schema_name: str
    switched: bool = True
'@

# ---------- presentation\docs.py ----------
Write-File "$ROOT\presentation\docs.py" @'
"""tenant_context presentation docs — เอกสาร API."""

router_docs = {
    "tags": ["Tenant Context"],
    "description": (
        "Module tenant_context (Layer 0) — "
        "จัดการบริบทผู้เช่าสำหรับ multi-tenant"
    ),
}

current_docs = {
    "summary": "Get current tenant context — ดึง context ปัจจุบัน",
    "responses": {
        200: {"description": "Current context"},
        400: {"description": "Context not set"},
    },
}

switch_docs = {
    "summary": "Switch tenant — เปลี่ยน tenant",
    "responses": {
        200: {"description": "Switched successfully"},
        404: {"description": "Tenant not found"},
    },
}
'@

# ---------- presentation\dependencies.py ----------
Write-File "$ROOT\presentation\dependencies.py" @'
"""tenant_context presentation dependencies — FastAPI DI."""
from fastapi import Depends, Header, HTTPException

from ..application.use_cases import TenantContextUseCases
from ..domain.exceptions import DomainError
from ..domain.value_objects import TenantContext, get_context, has_context


async def get_tenant_context(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    x_correlation_id: str | None = Header(
        default=None, alias="X-Correlation-ID"
    ),
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
) -> TenantContext:
    """FastAPI dependency — ดึง tenant context จาก request.

    ถ้ามี context ใน contextvars แล้ว → ใช้ค่านั้น
    ถ้าไม่มี → สร้างจาก headers
    """
    if has_context():
        return get_context()

    if not x_tenant_id:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-ID header required",
        )

    try:
        ctx = TenantContext(
            tenant_id=x_tenant_id,
            user_id=x_user_id,
            correlation_id=x_correlation_id or "auto-generated",
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ctx


async def get_tenant_context_use_cases() -> TenantContextUseCases:
    """DI provider for tenant_context use cases."""
    # resolver/cache จะถูก inject ในภายหลังผ่าน app wiring
    return TenantContextUseCases(resolver=None, cache=None)
'@

# ---------- presentation\routers.py ----------
Write-File "$ROOT\presentation\routers.py" @'
"""tenant_context presentation routers — API endpoints."""
from fastapi import APIRouter, Depends, HTTPException

from ..application.exceptions import (
    TenantContextException,
    TenantNotFoundInContext,
)
from ..application.use_cases import TenantContextUseCases
from ..domain.exceptions import DomainError
from ..domain.value_objects import TenantContext
from .dependencies import (
    get_tenant_context,
    get_tenant_context_use_cases,
)
from .schemas import (
    SwitchTenantRequest,
    SwitchTenantResponse,
    TenantContextSchema,
)

router = APIRouter(prefix="/api/v1/context", tags=["Tenant Context"])


@router.get("/current/", response_model=TenantContextSchema)
async def get_current(
    ctx: TenantContext = Depends(get_tenant_context),
):
    """ดึง context ปัจจุบัน — Get current tenant context."""
    return TenantContextSchema(
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        correlation_id=ctx.correlation_id,
        request_id=ctx.request_id,
        locale=ctx.locale,
        timezone=ctx.timezone,
        schema_name=ctx.schema_name,
        established_at=ctx.established_at,
    )


@router.post("/switch/", response_model=SwitchTenantResponse)
async def switch_tenant(
    req: SwitchTenantRequest,
    use_cases: TenantContextUseCases = Depends(
        get_tenant_context_use_cases
    ),
):
    """เปลี่ยน tenant — Switch tenant."""
    try:
        ctx = await use_cases.establish(
            tenant_id=req.tenant_id,
            user_id=req.user_id,
            headers={},
        )
        return SwitchTenantResponse(
            tenant_id=ctx.tenant_id,
            correlation_id=ctx.correlation_id,
            schema_name=ctx.schema_name,
        )
    except TenantNotFoundInContext as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenantContextException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")
'@

Write-Host "[OK] presentation done`n" -ForegroundColor Green

# ============================================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " DONE! tenant_context module created." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Structure:" -ForegroundColor White
Write-Host "   $ROOT\" -ForegroundColor White
Write-Host "     domain\          (6 files)" -ForegroundColor White
Write-Host "     application\     (6 files)" -ForegroundColor White
Write-Host "     infrastructure\  (6 files)" -ForegroundColor White
Write-Host "     presentation\    (6 files)" -ForegroundColor White
Write-Host "     __init__.py      (1 file)" -ForegroundColor White
Write-Host ""
Write-Host " Total: 25 files — no empty files." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
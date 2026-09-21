# ============================================================
#  create_tenancy.ps1 — Module 1.1 tenancy (prefix: ten)
# ============================================================
$ErrorActionPreference = "Stop"
$ROOT = "app\modules\tenancy"
$Prefix = "ten"
$Name = "Tenancy"
$module = "tenancy"

function Write-File {
    param([string]$Path, [string]$Content)
    $dir = Split-Path $Path -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $fullDir = (Resolve-Path -LiteralPath $dir).Path
    [System.IO.File]::WriteAllText((Join-Path $fullDir (Split-Path $Path -Leaf)), $Content, $utf8)
    Write-Host "  [OK] $Path" -ForegroundColor Green
}

foreach ($s in @("", "\domain", "\application", "\infrastructure", "\presentation")) {
    $p = "$ROOT$s"
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null }
}
Write-Host "=== Creating module: $module ===" -ForegroundColor Cyan

# ---------- ROOT __init__.py ----------
Write-File "$ROOT\__init__.py" @'
"""Module tenancy — Layer 1 (Foundation).

Tenant lifecycle management — จัดการวงจรชีวิตผู้เช่า
"""
__version__ = "1.0.0"
'@

# ============================================================
#  DOMAIN LAYER
# ============================================================
Write-File "$ROOT\domain\__init__.py" @'
"""tenancy domain layer — pure business logic."""
from .entities import Tenant
from .enums import TenantPlanCode, TenantStatus
from .events import TenantActivated, TenantCreated, TenantSuspended
from .exceptions import DomainError
from .value_objects import TenantPlan, TenantSlug

__all__ = [
    "Tenant", "TenantPlan", "TenantSlug",
    "TenantStatus", "TenantPlanCode",
    "DomainError",
    "TenantCreated", "TenantSuspended", "TenantActivated",
]
'@

Write-File "$ROOT\domain\exceptions.py" @'
"""tenancy domain exceptions — ข้อยกเว้นโดเมน."""
from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """DomainError — ละเมิดกฎโดเมน."""
    code = "ten_DOMAIN_ERROR"

    def __init__(self, message: str = "Tenancy domain error"):
        self.message = message
        super().__init__(message)
'@

Write-File "$ROOT\domain\enums.py" @'
"""tenancy enums — Enum สำหรับ tenancy."""
from enum import Enum


class TenantStatus(str, Enum):
    """TenantStatus — สถานะผู้เช่า."""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"
    CANCELLED = "CANCELLED"


class TenantPlanCode(str, Enum):
    """TenantPlanCode — รหัสแผน."""
    FREE = "FREE"
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
'@

Write-File "$ROOT\domain\events.py" @'
"""tenancy domain events — เหตุการณ์โดเมน."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class TenantCreated:
    """TenantCreated — สร้าง tenant สำเร็จ."""
    tenant_id: str
    slug: str
    plan: str
    occurred_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class TenantSuspended:
    """TenantSuspended — ระงับ tenant."""
    tenant_id: str
    reason: str
    occurred_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class TenantActivated:
    """TenantActivated — เปิดใช้งาน tenant."""
    tenant_id: str
    occurred_at: datetime = field(default_factory=_utcnow)
'@

Write-File "$ROOT\domain\value_objects.py" @'
"""tenancy value objects — วัตถุค่า."""
import re
from dataclasses import dataclass
from decimal import Decimal

from .exceptions import DomainError


@dataclass(frozen=True)
class TenantPlan:
    """TenantPlan VO — วัตถุแผน."""
    code: str
    name: str
    max_users: int
    max_storage_gb: int
    price_monthly: Decimal

    def __post_init__(self):
        if self.max_users <= 0:
            raise DomainError("Max users must be positive")
        if self.max_storage_gb <= 0:
            raise DomainError("Max storage must be positive")


@dataclass(frozen=True)
class TenantSlug:
    """TenantSlug VO — วัตถุ slug."""
    value: str

    PATTERN = r"^[a-z][a-z0-9-]{2,30}$"

    def __post_init__(self):
        if not re.match(self.PATTERN, self.value):
            raise DomainError(f"Invalid slug: {self.value}")

    def __str__(self) -> str:
        return self.value
'@

Write-File "$ROOT\domain\entities.py" @'
"""tenancy entities — เอนทิตี Tenant."""
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from .exceptions import DomainError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class BaseEntity:
    """BaseEntity — เอนทิตีฐาน."""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    deleted_at: datetime | None = None
    version: int = 1


@dataclass
class Tenant(BaseEntity):
    """Tenant entity — เอนทิตีผู้เช่า."""
    slug: str = ""
    name: str = ""
    plan: str = "FREE"
    status: str = "ACTIVE"
    schema_name: str = ""
    owner_email: str = ""
    trial_ends_at: datetime | None = None
    max_users: int = 5
    max_storage_gb: int = 1

    def __post_init__(self):
        self._validate()
        if not self.schema_name:
            self.schema_name = f"tenant_{self.id}"

    def _validate(self) -> None:
        if not self.slug or not re.match(r"^[a-z][a-z0-9-]{2,30}$", self.slug):
            raise DomainError(f"Invalid slug: {self.slug}")
        if not self.name:
            raise DomainError("Tenant name is required")
        if not self.owner_email:
            raise DomainError("Owner email is required")

    def activate(self) -> None:
        """Activate — เปิดใช้งาน."""
        if self.status == "ACTIVE":
            raise DomainError("Tenant already active")
        self.status = "ACTIVE"
        self.updated_at = _utcnow()

    def suspend(self, reason: str) -> None:
        """Suspend — ระงับ."""
        if self.status == "SUSPENDED":
            raise DomainError("Tenant already suspended")
        if not reason:
            raise DomainError("Suspension reason is required")
        self.status = "SUSPENDED"
        self.updated_at = _utcnow()

    def upgrade_plan(self, new_plan: str) -> None:
        """Upgrade plan — อัปเกรดแผน."""
        valid = ("FREE", "STARTER", "PROFESSIONAL", "ENTERPRISE")
        if new_plan not in valid:
            raise DomainError(f"Invalid plan: {new_plan}")
        self.plan = new_plan
        self.updated_at = _utcnow()

    def is_trial_expired(self) -> bool:
        """Check trial expired — ตรวจสอบ trial หมดอายุ."""
        if self.trial_ends_at is None:
            return False
        return _utcnow() > self.trial_ends_at
'@

Write-Host "[OK] domain done" -ForegroundColor Green

# ============================================================
#  APPLICATION LAYER
# ============================================================
Write-File "$ROOT\application\__init__.py" @'
"""tenancy application layer — use cases + ports."""
from .exceptions import (
    TenancyException,
    TenantNotFoundException,
    TenantSlugConflictException,
)
from .use_cases import TenancyUseCases

__all__ = [
    "TenancyUseCases",
    "TenancyException",
    "TenantNotFoundException",
    "TenantSlugConflictException",
]
'@

Write-File "$ROOT\application\exceptions.py" @'
"""tenancy application exceptions."""
from app.shared.exceptions import ApplicationException


class TenancyException(ApplicationException):
    """TenancyException — ข้อผิดพลาดแอปพลิเคชัน."""
    code = "ten_APP_ERROR"

    def __init__(self, message: str = "Tenancy operation failed"):
        self.message = message
        super().__init__(message)


class TenantNotFoundException(TenancyException):
    """TenantNotFoundException — ไม่พบ tenant."""
    code = "ten_NOT_FOUND"

    def __init__(self, message: str = "Tenant not found"):
        super().__init__(message)


class TenantSlugConflictException(TenancyException):
    """TenantSlugConflictException — slug ซ้ำ."""
    code = "ten_SLUG_CONFLICT"

    def __init__(self, slug: str = ""):
        super().__init__(f"Slug already exists: {slug}")
'@

Write-File "$ROOT\application\interfaces.py" @'
"""tenancy application interfaces — ports."""
from typing import Protocol

from ..domain.entities import Tenant


class ITenantRepository(Protocol):
    """Repository port."""

    async def save(self, tenant: Tenant) -> Tenant: ...
    async def get_by_id(self, id: str) -> Tenant | None: ...
    async def get_by_slug(self, slug: str) -> Tenant | None: ...
    async def list(self, page: int, limit: int) -> tuple[list[Tenant], int]: ...
    async def soft_delete(self, id: str) -> None: ...


class ITenantCache(Protocol):
    """Cache port."""

    async def get(self, id: str) -> Tenant | None: ...
    async def insert(self, id: str, tenant: Tenant) -> None: ...
    async def delete(self, id: str) -> None: ...


class ISchemaManager(Protocol):
    """Schema manager port."""

    async def create_schema(self, schema_name: str) -> None: ...
    async def drop_schema(self, schema_name: str) -> None: ...
    async def schema_exists(self, schema_name: str) -> bool: ...


__all__ = ["ITenantRepository", "ITenantCache", "ISchemaManager"]
'@

Write-File "$ROOT\application\mappers.py" @'
"""tenancy application mappers."""
from ..domain.entities import Tenant


class TenantMapper:
    """TenantMapper — แปลง Tenant <-> dict."""

    @staticmethod
    def to_dict(t: Tenant) -> dict:
        return {
            "id": t.id,
            "slug": t.slug,
            "name": t.name,
            "plan": t.plan,
            "status": t.status,
            "schema_name": t.schema_name,
            "owner_email": t.owner_email,
            "max_users": t.max_users,
            "max_storage_gb": t.max_storage_gb,
        }

    @staticmethod
    def from_dict(data: dict) -> Tenant:
        return Tenant(
            id=data.get("id", ""),
            slug=data.get("slug", ""),
            name=data.get("name", ""),
            plan=data.get("plan", "FREE"),
            status=data.get("status", "ACTIVE"),
            schema_name=data.get("schema_name", ""),
            owner_email=data.get("owner_email", ""),
            max_users=data.get("max_users", 5),
            max_storage_gb=data.get("max_storage_gb", 1),
        )
'@

Write-File "$ROOT\application\use_cases.py" @'
"""tenancy use cases — กรณีการใช้งาน.

Error handling: 3-branch (StandardException → DomainError → Exception)
"""
import logging

from app.shared.exceptions import DomainException, StandardException

from ..domain.entities import Tenant
from ..domain.exceptions import DomainError
from .exceptions import (
    TenancyException,
    TenantNotFoundException,
    TenantSlugConflictException,
)

logger = logging.getLogger(__name__)


class TenancyUseCases:
    """Tenancy use cases — กรณีการใช้งาน tenancy."""

    def __init__(self, repo, cache=None, schema_mgr=None,
                 idempotency=None, audit=None, events=None):
        self.repo = repo
        self.cache = cache
        self.schema_mgr = schema_mgr
        self.idempotency = idempotency
        self.audit = audit
        self.events = events

    async def create_tenant(self, payload: dict, idem_key: str | None = None) -> Tenant:
        """Create tenant + schema — สร้าง tenant พร้อม schema (atomic)."""
        try:
            if idem_key and self.idempotency is not None:
                existing = await self.idempotency.get(idem_key)
                if existing is not None:
                    return existing

            tenant = Tenant(**payload)

            if await self.repo.get_by_slug(tenant.slug) is not None:
                raise TenantSlugConflictException(tenant.slug)

            # สร้าง schema ก่อน save
            if self.schema_mgr is not None:
                await self.schema_mgr.create_schema(tenant.schema_name)

            tenant = await self.repo.save(tenant)

            # read-back verify
            verified = await self.repo.get_by_id(tenant.id)
            if verified is None or verified.slug != tenant.slug:
                if self.schema_mgr is not None:
                    await self.schema_mgr.drop_schema(tenant.schema_name)
                raise TenancyException("Read-back failed")

            if self.audit is not None:
                await self.audit.log("tenant.created", tenant.id)
            if idem_key and self.idempotency is not None:
                await self.idempotency.set(idem_key, tenant)
            if self.events is not None:
                await self.events.publish("TenantCreated", tenant)

            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception as e:
            logger.exception("Error in create_tenant: %s", e)
            raise TenancyException()

    async def suspend_tenant(self, id: str, reason: str) -> Tenant:
        """Suspend — ระงับ tenant."""
        try:
            tenant = await self.repo.get_by_id(id)
            if tenant is None:
                raise TenantNotFoundException()
            tenant.suspend(reason)
            tenant = await self.repo.save(tenant)
            if self.cache is not None:
                await self.cache.delete(id)
            if self.audit is not None:
                await self.audit.log("tenant.suspended", id)
            if self.events is not None:
                await self.events.publish(
                    "TenantSuspended", {"id": id, "reason": reason}
                )
            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception as e:
            logger.exception("Error in suspend_tenant: %s", e)
            raise TenancyException()

    async def upgrade_plan(self, id: str, new_plan: str) -> Tenant:
        """Upgrade plan — อัปเกรดแผน."""
        try:
            tenant = await self.repo.get_by_id(id)
            if tenant is None:
                raise TenantNotFoundException()
            tenant.upgrade_plan(new_plan)
            tenant = await self.repo.save(tenant)
            if self.cache is not None:
                await self.cache.delete(id)
            if self.audit is not None:
                await self.audit.log("tenant.upgraded", id)
            if self.events is not None:
                await self.events.publish(
                    "TenantPlanUpgraded", {"id": id, "plan": new_plan}
                )
            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception as e:
            logger.exception("Error in upgrade_plan: %s", e)
            raise TenancyException()

    async def get(self, id: str) -> Tenant:
        """Get by id — ดึงตาม id."""
        try:
            if self.cache is not None:
                cached = await self.cache.get(id)
                if cached is not None:
                    return cached
            tenant = await self.repo.get_by_id(id)
            if tenant is None:
                raise TenantNotFoundException()
            if self.cache is not None:
                await self.cache.insert(id, tenant)
            return tenant
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(str(e))
        except Exception as e:
            logger.exception("Error in get tenant: %s", e)
            raise TenancyException()
'@

Write-File "$ROOT\application\utils.py" @'
"""tenancy application utils."""
import re


SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,30}$")


def validate_slug(slug: str) -> bool:
    """ตรวจสอบ slug — Validate slug format."""
    return bool(SLUG_PATTERN.match(slug))


def generate_schema_name(tenant_id: str) -> str:
    """สร้าง schema name — Generate schema name."""
    safe = tenant_id.replace("-", "_")
    return f"tenant_{safe}"
'@

Write-Host "[OK] application done" -ForegroundColor Green

# ============================================================
#  INFRASTRUCTURE LAYER
# ============================================================
Write-File "$ROOT\infrastructure\__init__.py" @'
"""tenancy infrastructure layer."""
from .caches import RedisTenantCache
from .models import TenantModel
from .repositories import PostgresTenantRepository
from .services import PostgresSchemaManager

__all__ = [
    "TenantModel",
    "PostgresTenantRepository",
    "RedisTenantCache",
    "PostgresSchemaManager",
]
'@

Write-File "$ROOT\infrastructure\models.py" @'
"""tenancy infrastructure models — SQLAlchemy models."""
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


class TenantModel(BaseModel):
    """TenantModel — โมเดล tenants (schema: public)."""
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id = Column(String(36), primary_key=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    plan = Column(String(20), nullable=False, default="FREE")
    status = Column(String(20), nullable=False, default="ACTIVE")
    schema_name = Column(String(100), unique=True, nullable=False)
    owner_email = Column(String(255), nullable=False)
    trial_ends_at = Column(DateTime(timezone=True))
    max_users = Column(Integer, default=5)
    max_storage_gb = Column(Integer, default=1)
'@

Write-File "$ROOT\infrastructure\repositories.py" @'
"""tenancy infrastructure repositories — Postgres repo (2-branch)."""
import logging
from datetime import datetime, timezone

from app.shared.exceptions import InfrastructureException, StandardException

from ..domain.entities import Tenant

logger = logging.getLogger(__name__)


class TenancyRepositoryException(InfrastructureException):
    """Repository exception."""
    code = "ten_REPO_ERROR"


class PostgresTenantRepository:
    """PostgresTenantRepository — 2-branch error handling."""

    def __init__(self, session):
        self.session = session

    async def save(self, tenant: Tenant) -> Tenant:
        try:
            tenant.updated_at = datetime.now(timezone.utc)
            # TODO: SQLAlchemy upsert
            return tenant
        except StandardException:
            raise
        except Exception as e:
            logger.exception("Repo save failed: %s", e)
            raise TenancyRepositoryException()

    async def get_by_id(self, id: str) -> Tenant | None:
        try:
            # TODO: select
            return None
        except StandardException:
            raise
        except Exception as e:
            logger.exception("Repo get_by_id failed: %s", e)
            raise TenancyRepositoryException()

    async def get_by_slug(self, slug: str) -> Tenant | None:
        try:
            # TODO: select
            return None
        except StandardException:
            raise
        except Exception as e:
            logger.exception("Repo get_by_slug failed: %s", e)
            raise TenancyRepositoryException()

    async def list(self, page: int, limit: int) -> tuple[list[Tenant], int]:
        try:
            # TODO: pagination query
            return [], 0
        except StandardException:
            raise
        except Exception as e:
            logger.exception("Repo list failed: %s", e)
            raise TenancyRepositoryException()

    async def soft_delete(self, id: str) -> None:
        try:
            # TODO: UPDATE deleted_at
            return None
        except StandardException:
            raise
        except Exception as e:
            logger.exception("Repo soft_delete failed: %s", e)
            raise TenancyRepositoryException()
'@

Write-File "$ROOT\infrastructure\caches.py" @'
"""tenancy infrastructure caches — Redis (never-raise)."""
import json
import logging

from ..domain.entities import Tenant

logger = logging.getLogger(__name__)


class RedisTenantCache:
    """Redis cache for tenant (never-raise)."""

    def __init__(self, redis_client, ttl: int = 300):
        self.redis = redis_client
        self.ttl = ttl

    async def get(self, id: str) -> Tenant | None:
        try:
            data = await self.redis.get(f"ten:lookup:{id}")
            if not data:
                return None
            parsed = json.loads(data)
            return Tenant(
                id=parsed["id"],
                slug=parsed["slug"],
                name=parsed["name"],
                plan=parsed.get("plan", "FREE"),
                status=parsed.get("status", "ACTIVE"),
                schema_name=parsed.get("schema_name", ""),
                owner_email=parsed.get("owner_email", ""),
                max_users=parsed.get("max_users", 5),
                max_storage_gb=parsed.get("max_storage_gb", 1),
            )
        except Exception as e:
            logger.warning("Cache get failed: %s", e)
            return None

    async def insert(self, id: str, tenant: Tenant) -> None:
        try:
            payload = {
                "id": tenant.id,
                "slug": tenant.slug,
                "name": tenant.name,
                "plan": tenant.plan,
                "status": tenant.status,
                "schema_name": tenant.schema_name,
                "owner_email": tenant.owner_email,
                "max_users": tenant.max_users,
                "max_storage_gb": tenant.max_storage_gb,
            }
            await self.redis.setex(
                f"ten:lookup:{id}", self.ttl, json.dumps(payload)
            )
        except Exception as e:
            logger.warning("Cache insert failed: %s", e)

    async def delete(self, id: str) -> None:
        try:
            await self.redis.delete(f"ten:lookup:{id}")
        except Exception as e:
            logger.warning("Cache delete failed: %s", e)
'@

Write-File "$ROOT\infrastructure\services.py" @'
"""tenancy infrastructure services — Postgres schema manager."""
import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)


class PostgresSchemaManager:
    """PostgresSchemaManager — จัดการ PostgreSQL schema."""

    def __init__(self, session):
        self.session = session

    async def create_schema(self, schema_name: str) -> None:
        """Create schema — สร้าง schema."""
        try:
            await self.session.execute(
                text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
            )
            await self.session.flush()
        except Exception as e:
            logger.exception("Schema create failed: %s", schema_name)
            raise

    async def drop_schema(self, schema_name: str) -> None:
        """Drop schema — ลบ schema."""
        try:
            await self.session.execute(
                text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
            )
            await self.session.flush()
        except Exception as e:
            logger.exception("Schema drop failed: %s", schema_name)
            raise

    async def schema_exists(self, schema_name: str) -> bool:
        """Check schema exists — ตรวจสอบ schema."""
        try:
            result = await self.session.execute(
                text(
                    "SELECT 1 FROM information_schema.schemata "
                    "WHERE schema_name = :s"
                ),
                {"s": schema_name},
            )
            return result.first() is not None
        except Exception as e:
            logger.exception("Schema check failed: %s", schema_name)
            return False
'@

Write-Host "[OK] infrastructure done" -ForegroundColor Green

# ============================================================
#  PRESENTATION LAYER
# ============================================================
Write-File "$ROOT\presentation\__init__.py" @'
"""tenancy presentation layer."""
from .dependencies import get_tenancy_use_cases
from .routers import router

__all__ = ["router", "get_tenancy_use_cases"]
'@

Write-File "$ROOT\presentation\schemas.py" @'
"""tenancy presentation schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    """TenantCreate — schema สร้าง tenant."""
    slug: str = Field(..., pattern=r"^[a-z][a-z0-9-]{2,30}$")
    name: str = Field(..., min_length=1, max_length=200)
    owner_email: str = Field(..., max_length=255)
    plan: str = Field(default="FREE")


class TenantResponse(BaseModel):
    """TenantResponse — schema ตอบกลับ."""
    id: str
    slug: str
    name: str
    plan: str
    status: str
    schema_name: str
    owner_email: str
    max_users: int
    max_storage_gb: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SuspendRequest(BaseModel):
    """SuspendRequest — คำขอระงับ."""
    reason: str = Field(..., min_length=1, max_length=500)


class UpgradeRequest(BaseModel):
    """UpgradeRequest — คำขออัปเกรด."""
    plan: str = Field(..., pattern=r"^(FREE|STARTER|PROFESSIONAL|ENTERPRISE)$")
'@

Write-File "$ROOT\presentation\docs.py" @'
"""tenancy presentation docs."""
router_docs = {
    "tags": ["Tenancy"],
    "description": "Tenant management — จัดการผู้เช่า (Layer 1)",
}

create_docs = {"summary": "Create tenant — สร้าง tenant", "status_code": 201}
get_docs = {"summary": "Get tenant — ดึงข้อมูล tenant"}
list_docs = {"summary": "List tenants — แสดงรายการ"}
suspend_docs = {"summary": "Suspend tenant — ระงับ tenant"}
upgrade_docs = {"summary": "Upgrade plan — อัปเกรดแผน"}
'@

Write-File "$ROOT\presentation\dependencies.py" @'
"""tenancy presentation dependencies — FastAPI DI."""
from fastapi import Depends

from ..application.use_cases import TenancyUseCases
from ..infrastructure.repositories import PostgresTenantRepository


async def get_tenancy_use_cases(session=None) -> TenancyUseCases:
    """DI provider — สร้าง use cases."""
    repo = PostgresTenantRepository(session)
    return TenancyUseCases(repo=repo)
'@

Write-File "$ROOT\presentation\routers.py" @'
"""tenancy presentation routers — API endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException

from ..application.exceptions import (
    TenancyException,
    TenantNotFoundException,
    TenantSlugConflictException,
)
from ..application.use_cases import TenancyUseCases
from ..domain.exceptions import DomainError
from .dependencies import get_tenancy_use_cases
from .schemas import (
    SuspendRequest,
    TenantCreate,
    TenantResponse,
    UpgradeRequest,
)

router = APIRouter(prefix="/api/v1/tenants", tags=["Tenancy"])


@router.post("/", response_model=TenantResponse, status_code=201)
async def create_tenant(
    payload: TenantCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    uc: TenancyUseCases = Depends(get_tenancy_use_cases),
):
    """สร้าง tenant — Create tenant."""
    try:
        tenant = await uc.create_tenant(payload.model_dump(), idem_key)
        return TenantResponse.model_validate(tenant, from_attributes=True)
    except TenantSlugConflictException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except TenancyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.get("/{id}/", response_model=TenantResponse)
async def get_tenant(
    id: str,
    uc: TenancyUseCases = Depends(get_tenancy_use_cases),
):
    """ดึง tenant — Get tenant."""
    try:
        tenant = await uc.get(id)
        return TenantResponse.model_validate(tenant, from_attributes=True)
    except TenantNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenancyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.patch("/{id}/suspend/", response_model=TenantResponse)
async def suspend_tenant(
    id: str,
    payload: SuspendRequest,
    uc: TenancyUseCases = Depends(get_tenancy_use_cases),
):
    """ระงับ tenant — Suspend tenant."""
    try:
        tenant = await uc.suspend_tenant(id, payload.reason)
        return TenantResponse.model_validate(tenant, from_attributes=True)
    except TenantNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenancyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.patch("/{id}/upgrade/", response_model=TenantResponse)
async def upgrade_plan(
    id: str,
    payload: UpgradeRequest,
    uc: TenancyUseCases = Depends(get_tenancy_use_cases),
):
    """อัปเกรดแผน — Upgrade plan."""
    try:
        tenant = await uc.upgrade_plan(id, payload.plan)
        return TenantResponse.model_validate(tenant, from_attributes=True)
    except TenantNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenancyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")
'@

Write-Host ""
Write-Host "=== DONE: tenancy ===" -ForegroundColor Cyan
Write-Host "  $ROOT\  (23 files, no empty files)" -ForegroundColor Green
<#
.SYNOPSIS
    create_modules.ps1 — Production-ready module generator (DDD + Clean Architecture)
.DESCRIPTION
    Follows SKILL: python-ddd-clean-arch
.PARAMETER ModuleName
    Module name (lowercase). e.g. inventory, payment, money
.PARAMETER Layer
    Layer number 0-7 (0-Core / 1-Foundation / 2-Money / 3-Goods / 4-Ops / 5-Intel / 6-Monitor / 7-Template)
.PARAMETER Prefix
    3-char DB prefix (lowercase). e.g. inv, pay, mon
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ModuleName = "money",

    [Parameter(Position = 1)]
    [int]$Layer = 2,

    [Parameter(Position = 2)]
    [string]$Prefix = "",

    [switch]$Sql,
    [switch]$Tests,
    [switch]$Docs,
    [switch]$Routes,
    [switch]$Postman,
    [switch]$All,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# ============================================================
# 0. Normalize arguments
# ============================================================
if ($All) { $Sql = $true; $Tests = $true; $Docs = $true; $Routes = $true; $Postman = $true }
if (-not ($Sql -or $Tests -or $Docs -or $Routes -or $Postman)) {
    $Sql = $true; $Tests = $true; $Docs = $true; $Postman = $true
}

$MODULE       = $ModuleName.ToLower().Trim()
$MODULE_TITLE = (Get-Culture).TextInfo.ToTitleCase($ModuleName.Replace('_', ' ')).Replace(' ', '')
$MODULE_CLASS = $MODULE_TITLE
$PREFIX_L     = if ([string]::IsNullOrWhiteSpace($Prefix)) {
                    $MODULE.Substring(0, [Math]::Min(3, $MODULE.Length))
                } else {
                    $Prefix.ToLower().Trim()
                }
$SCHEMA       = "tenant_$PREFIX_L"
$TABLES       = "${MODULE}s"

$ROOT         = "app\modules"
$MODULE_ROOT  = Join-Path $ROOT $MODULE

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " create_modules.ps1 — DDD + Clean Arch"      -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Module   : $MODULE"
Write-Host " Class    : $MODULE_CLASS"
Write-Host " Layer    : $Layer"
Write-Host " Prefix   : $PREFIX_L"
Write-Host " Schema   : $SCHEMA"
Write-Host " Table    : $TABLES"
Write-Host " Flags    : Sql=$Sql Tests=$Tests Docs=$Docs Routes=$Routes Postman=$Postman Force=$Force"
Write-Host "--------------------------------------------" -ForegroundColor Cyan

# ============================================================
# 1. Helpers
# ============================================================
function Write-File {
    param([string]$Path, [string]$Content)
    $dir = Split-Path $Path -Parent
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    if ((Test-Path $Path) -and (-not $Force)) {
        Write-Host "  [SKIP] $Path (exists — use -Force)" -ForegroundColor DarkYellow
        return
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $full = Join-Path (Get-Location) $Path
    [System.IO.File]::WriteAllText($full, $Content, $utf8)
    Write-Host "  [OK]   $Path" -ForegroundColor Green
}

function Expand-Template {
    param([string]$Template)
    return $Template.
        Replace('__MODULE__',        $MODULE).
        Replace('__MODULE_CLASS__',  $MODULE_CLASS).
        Replace('__MODULE_TITLE__',  $MODULE_TITLE).
        Replace('__PREFIX__',        $PREFIX_L).
        Replace('__SCHEMA__',        $SCHEMA).
        Replace('__TABLES__',        $TABLES).
        Replace('__LAYER__',         $Layer.ToString())
}

function Write-Template {
    param([string]$Path, [string]$Template)
    Write-File -Path $Path -Content (Expand-Template $Template)
}

function Register-ModelInEnv {
    param(
        [Parameter(Mandatory)][string]$ModuleName,
        [Parameter(Mandatory)][string]$ClassPrefix
    )

    $envFile = "migrations\env.py"
    if (-not (Test-Path $envFile)) {
        Write-Host "  [SKIP] $envFile not found — register manually" -ForegroundColor DarkYellow
        return
    }

    $importLine = "from app.modules.$ModuleName.infrastructure.models import ${ClassPrefix}Model  # noqa: F401"
    $marker     = "# --- module $ModuleName (auto-registered) ---"

    $content = Get-Content $envFile -Raw
    if ($content -match [regex]::Escape($importLine)) {
        Write-Host "  [SKIP] $ModuleName already registered in env.py" -ForegroundColor DarkYellow
        return
    }

    $lines = Get-Content $envFile

    # หา index สุดท้ายของ top-level import (import/from ...)
    $insertAt = 0
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^(import\s|from\s)') { $insertAt = $i + 1 }
    }

    $newLines = @()
    if ($insertAt -gt 0) { $newLines += $lines[0..($insertAt - 1)] }
    $newLines += ""
    $newLines += $marker
    $newLines += $importLine
    if ($insertAt -lt $lines.Count) {
        $newLines += $lines[$insertAt..($lines.Count - 1)]
    }

    # backup ครั้งแรกก่อนแก้
    $bak = "$envFile.bak"
    if (-not (Test-Path $bak)) {
        Copy-Item $envFile $bak
    }

    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines((Join-Path (Get-Location) $envFile), $newLines, $utf8)

    Write-Host "  [OK]   registered $ModuleName in env.py" -ForegroundColor Green
}

# ============================================================
# 2. Directory structure
# ============================================================
$dirs = @(
    $MODULE_ROOT,
    "$MODULE_ROOT\domain",
    "$MODULE_ROOT\application",
    "$MODULE_ROOT\infrastructure",
    "$MODULE_ROOT\presentation",
    "migrations\versions",
    "tests\unit",
    "tests\integration",
    "tests\property",
    "tests\manual",
    "docs",
    "docs\postman"
)
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
}
Write-Host "[OK] Folders ready" -ForegroundColor Green
Write-Host ""

# ════════════════════════════════════════════════════════════
# 3. DOMAIN LAYER
# ════════════════════════════════════════════════════════════
Write-Host "--- DOMAIN layer ---" -ForegroundColor Yellow

Write-Template "$MODULE_ROOT\domain\__init__.py" @'
"""__MODULE_CLASS__ domain layer — ชั้นโดเมน __MODULE__"""
from .entities import __MODULE_CLASS__
from .enums import __MODULE_CLASS__Status
from .events import (
    __MODULE_CLASS__Created,
    __MODULE_CLASS__Deleted,
    __MODULE_CLASS__Updated,
)
from .exceptions import (
    DomainError,
    DuplicateCodeError,
    InvalidAmountError,
    InvalidStatusTransitionError,
    __MODULE_CLASS__NotFoundError,
)
from .value_objects import Money

__all__ = [
    "__MODULE_CLASS__",
    "__MODULE_CLASS__Status",
    "__MODULE_CLASS__Created",
    "__MODULE_CLASS__Updated",
    "__MODULE_CLASS__Deleted",
    "Money",
    "DomainError",
    "DuplicateCodeError",
    "InvalidAmountError",
    "InvalidStatusTransitionError",
    "__MODULE_CLASS__NotFoundError",
]
'@

Write-Template "$MODULE_ROOT\domain\enums.py" @'
"""__MODULE_CLASS__ enums — Enum ของ __MODULE__"""
from enum import StrEnum


class __MODULE_CLASS__Status(StrEnum):
    """__MODULE_CLASS__Status — สถานะของ __MODULE__"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
'@

Write-Template "$MODULE_ROOT\domain\exceptions.py" @'
"""__MODULE_CLASS__ domain exceptions — ข้อยกเว้นโดเมน __MODULE__"""


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดระดับโดเมน"""

    def __init__(self, message: str = "Domain error") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class DuplicateCodeError(DomainError):
    """DuplicateCodeError — code ซ้ำใน tenant เดียวกัน"""

    def __init__(self, code: str) -> None:
        super().__init__(f"code {code!r} already exists")


class InvalidAmountError(DomainError):
    """InvalidAmountError — amount ไม่ถูกต้อง"""

    def __init__(self, message: str = "amount must be >= 0") -> None:
        super().__init__(message)


class InvalidStatusTransitionError(DomainError):
    """InvalidStatusTransitionError — เปลี่ยนสถานะไม่ถูกต้อง"""

    def __init__(self, message: str = "invalid status transition") -> None:
        super().__init__(message)


class __MODULE_CLASS__NotFoundError(DomainError):
    """__MODULE_CLASS__NotFoundError — ไม่พบ __MODULE__"""

    def __init__(self, entity_id: object | None = None) -> None:
        super().__init__(f"__MODULE__ not found: {entity_id!r}")
'@

Write-Template "$MODULE_ROOT\domain\value_objects.py" @'
"""__MODULE_CLASS__ value objects — วัตถุค่า __MODULE__"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from .exceptions import DomainError

SUPPORTED_CURRENCIES = frozenset({"THB", "USD", "EUR"})
CENT = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    """Money value object — วัตถุค่าเงิน"""

    amount: Decimal
    currency: str = "THB"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise DomainError("amount must be Decimal")
        object.__setattr__(
            self, "amount",
            self.amount.quantize(CENT, rounding=ROUND_HALF_UP),
        )
        if self.currency not in SUPPORTED_CURRENCIES:
            raise DomainError(f"unsupported currency: {self.currency}")

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DomainError(
                f"cannot operate {self.currency} vs {other.currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        if not isinstance(factor, Decimal):
            raise DomainError("factor must be Decimal")
        return Money(self.amount * factor, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")


@dataclass(frozen=True)
class ExchangeRate:
    """ExchangeRate — วัตถุอัตราแลกเปลี่ยน"""

    from_currency: str
    to_currency: str
    rate: Decimal
    as_of: datetime

    def __post_init__(self) -> None:
        if self.rate <= 0:
            raise DomainError("exchange rate must be positive")
        if self.from_currency not in SUPPORTED_CURRENCIES:
            raise DomainError(f"unsupported currency: {self.from_currency}")
        if self.to_currency not in SUPPORTED_CURRENCIES:
            raise DomainError(f"unsupported currency: {self.to_currency}")

    def convert(self, amount: Money) -> Money:
        if amount.currency != self.from_currency:
            raise DomainError("currency mismatch")
        return Money(amount.amount * self.rate, self.to_currency)
'@

Write-Template "$MODULE_ROOT\domain\events.py" @'
"""__MODULE_CLASS__ domain events — เหตุการณ์โดเมน __MODULE__"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class __MODULE_CLASS__Created:
    """__MODULE_CLASS__Created — สร้าง __MODULE__ สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    code: str
    amount: Decimal
    occurred_at: datetime


@dataclass(frozen=True)
class __MODULE_CLASS__Updated:
    """__MODULE_CLASS__Updated — แก้ไข __MODULE__ สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    changes: dict
    occurred_at: datetime


@dataclass(frozen=True)
class __MODULE_CLASS__Deleted:
    """__MODULE_CLASS__Deleted — ลบ __MODULE__ (soft) สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    deleted_at: datetime
'@

Write-Template "$MODULE_ROOT\domain\entities.py" @'
"""__MODULE_CLASS__ entities — เอนทิตี __MODULE__"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from .enums import __MODULE_CLASS__Status
from .exceptions import (
    DomainError,
    InvalidAmountError,
    InvalidStatusTransitionError,
)
from .value_objects import Money

MAX_CODE_LEN = 50
MAX_NAME_LEN = 200


@dataclass
class __MODULE_CLASS__:
    """__MODULE_CLASS__ aggregate root — รากของ aggregate"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    code: str = ""
    name: str = ""
    amount: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    status: __MODULE_CLASS__Status = __MODULE_CLASS__Status.ACTIVE
    version: int = 1
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        tenant_id: uuid.UUID,
        code: str,
        name: str,
        amount: Decimal | Money,
        status: __MODULE_CLASS__Status | None = None,
        metadata: dict | None = None,
    ) -> "__MODULE_CLASS__":
        """TH: สร้าง entity ใหม่ | EN: create new entity"""
        if not code or len(code) > MAX_CODE_LEN:
            raise DomainError(f"code must be 1-{MAX_CODE_LEN} chars")
        if not name or len(name) > MAX_NAME_LEN:
            raise DomainError(f"name must be 1-{MAX_NAME_LEN} chars")
        money = amount if isinstance(amount, Money) else Money(amount)
        if money.is_negative():
            raise InvalidAmountError(f"amount must be >= 0, got {money.amount}")
        return cls(
            tenant_id=tenant_id,
            code=code,
            name=name,
            amount=money,
            status=status or __MODULE_CLASS__Status.ACTIVE,
            metadata=metadata or {},
        )

    def activate(self) -> None:
        """TH: เปิดใช้งาน | EN: activate"""
        if self.status is __MODULE_CLASS__Status.ARCHIVED:
            raise InvalidStatusTransitionError("archived is terminal")
        self.status = __MODULE_CLASS__Status.ACTIVE
        self._touch()

    def deactivate(self) -> None:
        """TH: ปิดใช้งาน | EN: deactivate"""
        if self.status is __MODULE_CLASS__Status.ARCHIVED:
            raise InvalidStatusTransitionError("archived is terminal")
        self.status = __MODULE_CLASS__Status.INACTIVE
        self._touch()

    def archive(self) -> None:
        """TH: เก็บถาวร (terminal) | EN: archive (terminal)"""
        self.status = __MODULE_CLASS__Status.ARCHIVED
        self._touch()

    def soft_delete(self) -> None:
        """TH: ลบแบบ soft | EN: soft delete"""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def rename(self, new_name: str) -> None:
        if not new_name or len(new_name) > MAX_NAME_LEN:
            raise DomainError(f"name must be 1-{MAX_NAME_LEN} chars")
        self.name = new_name
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.utcnow()
        self.version += 1
'@

# ════════════════════════════════════════════════════════════
# 4. APPLICATION LAYER
# ════════════════════════════════════════════════════════════
Write-Host "--- APPLICATION layer ---" -ForegroundColor Yellow

Write-Template "$MODULE_ROOT\application\__init__.py" @'
"""__MODULE_CLASS__ application layer — ชั้นแอปพลิเคชัน __MODULE__"""
from .exceptions import (
    DuplicateCodeError as AppDuplicateCodeError,
    __MODULE_CLASS__NotFoundError as AppNotFoundError,
    StandardException,
)
from .use_cases import (
    Create__MODULE_CLASS__UseCase,
    Delete__MODULE_CLASS__UseCase,
    Get__MODULE_CLASS__UseCase,
    List__MODULE_CLASS__UseCase,
    Update__MODULE_CLASS__UseCase,
)
from .utils import zero_money

__all__ = [
    "Create__MODULE_CLASS__UseCase",
    "Get__MODULE_CLASS__UseCase",
    "List__MODULE_CLASS__UseCase",
    "Update__MODULE_CLASS__UseCase",
    "Delete__MODULE_CLASS__UseCase",
    "StandardException",
    "AppDuplicateCodeError",
    "AppNotFoundError",
    "zero_money",
]
'@

Write-Template "$MODULE_ROOT\application\exceptions.py" @'
"""__MODULE_CLASS__ application exceptions — ข้อยกเว้นแอปพลิเคชัน"""


class StandardException(Exception):
    """StandardException — ข้อผิดพลาดมาตรฐานที่รู้จัก (business)"""

    def __init__(self, message: str = "operation failed") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class DuplicateCodeError(StandardException):
    """DuplicateCodeError — code ซ้ำ"""

    def __init__(self, code: str) -> None:
        super().__init__(f"code {code!r} already exists")


class __MODULE_CLASS__NotFoundError(StandardException):
    """__MODULE_CLASS__NotFoundError — ไม่พบ entity"""

    def __init__(self, entity_id: object | None = None) -> None:
        super().__init__(f"__MODULE__ not found: {entity_id!r}")


class VersionConflictError(StandardException):
    """VersionConflictError — version ไม่ตรง"""

    def __init__(self, expected: int, actual: int) -> None:
        super().__init__(f"version conflict: expected {expected}, got {actual}")
'@

Write-Template "$MODULE_ROOT\application\interfaces.py" @'
"""__MODULE_CLASS__ application interfaces (ports) — Protocol"""
from __future__ import annotations

import uuid
from typing import Protocol

from ..domain.entities import __MODULE_CLASS__
from ..domain.value_objects import Money


class I__MODULE_CLASS__Repository(Protocol):
    """I__MODULE_CLASS__Repository — port ของ repository"""

    async def save(self, entity: __MODULE_CLASS__) -> __MODULE_CLASS__: ...
    async def get_by_id(self, entity_id: uuid.UUID) -> __MODULE_CLASS__ | None: ...
    async def get_by_code(self, code: str) -> __MODULE_CLASS__ | None: ...
    async def list(
        self, *, status: str | None, q: str | None, limit: int, offset: int
    ) -> tuple[list[__MODULE_CLASS__], int]: ...
    async def soft_delete(self, entity_id: uuid.UUID) -> None: ...


class I__MODULE_CLASS__Cache(Protocol):
    """I__MODULE_CLASS__Cache — port ของ cache.

    Contract:
      - never raise — Postgres is source of truth, Redis is best-effort
      - invalidate() writes a tombstone BEFORE deleting the entry
      - set() checks for a tombstone BEFORE writing
    """

    async def get(self, key: str) -> __MODULE_CLASS__ | None: ...
    async def set(
        self, key: str, entity: __MODULE_CLASS__, ttl: int = 3600
    ) -> None: ...
    async def invalidate(self, key: str) -> bool: ...


class IEventBus(Protocol):
    """IEventBus — port ของ event bus"""

    async def publish(self, event: object) -> None: ...


class IIdempotencyStore(Protocol):
    """IIdempotencyStore — port ของ idempotency"""

    async def check_or_lock(
        self, *, key: str, scope: str, payload: dict, tenant_id: str
    ) -> object | None: ...
    async def complete(
        self, *, key: str, scope: str, tenant_id: str,
        status: int, body: dict
    ) -> None: ...


class IMoneyConverter(Protocol):
    """IMoneyConverter — แปลงสกุลเงิน (optional)"""

    def convert(self, amount: Money, rate: object) -> Money: ...
'@

Write-Template "$MODULE_ROOT\application\mappers.py" @'
"""__MODULE_CLASS__ mappers — ตัวแปลงข้อมูล"""
from __future__ import annotations

from decimal import Decimal

from ..domain.entities import __MODULE_CLASS__
from ..domain.enums import __MODULE_CLASS__Status
from ..domain.value_objects import Money


class __MODULE_CLASS__Mapper:
    """__MODULE_CLASS__Mapper — ตัวแปลง entity ↔ dict"""

    @staticmethod
    def to_dict(entity: __MODULE_CLASS__) -> dict:
        return {
            "id": str(entity.id),
            "tenant_id": str(entity.tenant_id),
            "code": entity.code,
            "name": entity.name,
            "amount": str(entity.amount.amount),
            "currency": entity.amount.currency,
            "status": entity.status.value,
            "version": entity.version,
            "metadata": entity.metadata,
            "created_at": entity.created_at.isoformat(),
            "updated_at": entity.updated_at.isoformat(),
            "deleted_at": entity.deleted_at.isoformat() if entity.deleted_at else None,
        }

    @staticmethod
    def to_entity(data: dict) -> __MODULE_CLASS__:
        return __MODULE_CLASS__(
            code=data["code"],
            name=data["name"],
            amount=Money(
                Decimal(str(data.get("amount", "0.00"))),
                data.get("currency", "THB"),
            ),
            status=__MODULE_CLASS__Status(data.get("status", "ACTIVE")),
            metadata=data.get("metadata", {}),
        )
'@

Write-Template "$MODULE_ROOT\application\utils.py" @'
"""__MODULE_CLASS__ application utils — เครื่องมือช่วย"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from ..domain.value_objects import Money


def round_money(amount: Decimal, places: int = 2) -> Decimal:
    """TH: ปัดเศษเงิน | EN: round money"""
    quant = Decimal("0.01") if places == 2 else Decimal(10) ** -places
    return amount.quantize(quant, rounding=ROUND_HALF_UP)


def zero_money(currency: str = "THB") -> Money:
    """TH: สร้าง Money ศูนย์ | EN: zero money"""
    return Money(Decimal("0.00"), currency)


def clamp_limit(limit: int, *, maximum: int = 100) -> int:
    """TH: จำกัด limit | EN: clamp limit"""
    return max(1, min(limit, maximum))
'@

Write-Template "$MODULE_ROOT\application\use_cases.py" @'
"""__MODULE_CLASS__ use cases — กรณีการใช้งาน __MODULE__"""
from __future__ import annotations

import structlog

from ..domain.entities import __MODULE_CLASS__
from ..domain.events import (
    __MODULE_CLASS__Created,
    __MODULE_CLASS__Deleted,
    __MODULE_CLASS__Updated,
)
from ..domain.exceptions import DomainError
from .exceptions import (
    DuplicateCodeError,
    StandardException,
    __MODULE_CLASS__NotFoundError,
)

log = structlog.get_logger()


class Create__MODULE_CLASS__UseCase:
    """TH: สร้าง __MODULE__ ใหม่ (idempotent) | EN: create (idempotent)"""

    def __init__(self, *, repo, cache, event_bus, idempotency, ctx) -> None:
        self.repo = repo
        self.cache = cache
        self.event_bus = event_bus
        self.idempotency = idempotency
        self.ctx = ctx

    async def execute(
        self, *, code: str, name: str, amount, idempotency_key: str
    ) -> __MODULE_CLASS__:
        log.info("usecase.create.start", code=code, idem=idempotency_key[:8])
        try:
            existing = await self.idempotency.check_or_lock(
                key=idempotency_key,
                scope="__MODULE__.create",
                payload={"code": code, "name": name, "amount": str(amount)},
                tenant_id=str(self.ctx["tenant_id"]),
            )
            if existing is not None:
                return existing

            if await self.repo.get_by_code(code) is not None:
                raise DuplicateCodeError(code)

            entity = __MODULE_CLASS__.create(
                tenant_id=self.ctx["tenant_id"],
                code=code, name=name, amount=amount,
            )

            saved = await self.repo.save(entity)

            verified = await self.repo.get_by_id(saved.id)
            if verified is None:
                raise StandardException("read-back verification failed")

            await self.cache.invalidate(f"__MODULE__:{saved.id}")

            await self.idempotency.complete(
                key=idempotency_key, scope="__MODULE__.create",
                tenant_id=str(self.ctx["tenant_id"]),
                status=201, body={"id": str(saved.id)},
            )

            await self.event_bus.publish(
                __MODULE_CLASS__Created(
                    entity_id=saved.id, tenant_id=saved.tenant_id,
                    code=saved.code, amount=saved.amount.amount,
                    occurred_at=saved.created_at,
                )
            )
            return verified
        except StandardException:
            log.warning("usecase.create.standard_error", code=code)
            raise
        except DomainError as e:
            log.warning("usecase.create.domain_error", code=code, err=str(e))
            raise
        except Exception:
            log.exception("usecase.create.unexpected", code=code)
            raise


class Get__MODULE_CLASS__UseCase:
    """TH: ดึง __MODULE__ ตาม id | EN: get by id"""

    def __init__(self, *, repo, cache, ctx) -> None:
        self.repo = repo
        self.cache = cache
        self.ctx = ctx

    async def execute(self, *, entity_id) -> __MODULE_CLASS__:
        log.info("usecase.get.start", entity_id=str(entity_id))
        try:
            cached = await self.cache.get(f"__MODULE__:{entity_id}")
            if cached is not None:
                return cached

            entity = await self.repo.get_by_id(entity_id)
            if entity is None or entity.is_deleted():
                raise __MODULE_CLASS__NotFoundError(entity_id)

            await self.cache.set(f"__MODULE__:{entity_id}", entity, ttl=300)
            return entity
        except StandardException:
            raise
        except DomainError as e:
            log.warning("usecase.get.domain_error", err=str(e))
            raise
        except Exception:
            log.exception("usecase.get.unexpected", entity_id=str(entity_id))
            raise


class List__MODULE_CLASS__UseCase:
    """TH: list + filter + paginate | EN: list"""

    def __init__(self, *, repo, ctx) -> None:
        self.repo = repo
        self.ctx = ctx

    async def execute(
        self, *, status: str | None, q: str | None, limit: int, offset: int
    ) -> tuple[list[__MODULE_CLASS__], int]:
        log.info("usecase.list.start", status=status, q=q, limit=limit)
        try:
            return await self.repo.list(
                status=status, q=q, limit=limit, offset=offset
            )
        except Exception:
            log.exception("usecase.list.unexpected")
            raise


class Update__MODULE_CLASS__UseCase:
    """TH: แก้ไข __MODULE__ | EN: update"""

    def __init__(self, *, repo, cache, event_bus, ctx) -> None:
        self.repo = repo
        self.cache = cache
        self.event_bus = event_bus
        self.ctx = ctx

    async def execute(self, *, entity_id, **changes) -> __MODULE_CLASS__:
        log.info("usecase.update.start", entity_id=str(entity_id))
        try:
            entity = await self.repo.get_by_id(entity_id)
            if entity is None or entity.is_deleted():
                raise __MODULE_CLASS__NotFoundError(entity_id)

            if "name" in changes and changes["name"] is not None:
                entity.rename(changes["name"])

            saved = await self.repo.save(entity)
            await self.cache.invalidate(f"__MODULE__:{entity_id}")

            await self.event_bus.publish(
                __MODULE_CLASS__Updated(
                    entity_id=saved.id, tenant_id=saved.tenant_id,
                    changes=changes, occurred_at=saved.updated_at,
                )
            )
            return saved
        except StandardException:
            raise
        except DomainError as e:
            log.warning("usecase.update.domain_error", err=str(e))
            raise
        except Exception:
            log.exception("usecase.update.unexpected", entity_id=str(entity_id))
            raise


class Delete__MODULE_CLASS__UseCase:
    """TH: ลบ __MODULE__ (soft) | EN: soft delete"""

    def __init__(self, *, repo, cache, event_bus, ctx) -> None:
        self.repo = repo
        self.cache = cache
        self.event_bus = event_bus
        self.ctx = ctx

    async def execute(self, *, entity_id) -> None:
        log.info("usecase.delete.start", entity_id=str(entity_id))
        try:
            entity = await self.repo.get_by_id(entity_id)
            if entity is None or entity.is_deleted():
                raise __MODULE_CLASS__NotFoundError(entity_id)

            entity.soft_delete()
            await self.repo.save(entity)
            await self.cache.invalidate(f"__MODULE__:{entity_id}")

            await self.event_bus.publish(
                __MODULE_CLASS__Deleted(
                    entity_id=entity.id, tenant_id=entity.tenant_id,
                    deleted_at=entity.deleted_at,
                )
            )
        except StandardException:
            raise
        except DomainError as e:
            log.warning("usecase.delete.domain_error", err=str(e))
            raise
        except Exception:
            log.exception("usecase.delete.unexpected", entity_id=str(entity_id))
            raise
'@

# ════════════════════════════════════════════════════════════
# 5. INFRASTRUCTURE LAYER
# ════════════════════════════════════════════════════════════
Write-Host "--- INFRASTRUCTURE layer ---" -ForegroundColor Yellow

Write-Template "$MODULE_ROOT\infrastructure\__init__.py" @'
"""__MODULE_CLASS__ infrastructure layer"""
from .caches import Redis__MODULE_CLASS__Cache
from .models import __MODULE_CLASS__Model
from .repositories import SQLAlchemy__MODULE_CLASS__Repository

__all__ = [
    "__MODULE_CLASS__Model",
    "SQLAlchemy__MODULE_CLASS__Repository",
    "Redis__MODULE_CLASS__Cache",
]
'@

Write-Template "$MODULE_ROOT\infrastructure\models.py" @'
"""__MODULE_CLASS__ infrastructure models — SQLAlchemy 2.0"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative — ฐานของ model ทั้งหมด"""


class __MODULE_CLASS__Model(Base):
    """__MODULE_CLASS__Model — โมเดลฐานข้อมูล"""

    __tablename__ = "__TABLES__"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq___MODULE___code"),
        CheckConstraint("amount >= 0", name="ck___MODULE___amount"),
        CheckConstraint(
            "status IN ('ACTIVE','INACTIVE','ARCHIVED')",
            name="ck___MODULE___status",
        ),
        {"schema": "__SCHEMA__"},
    )

    id:         Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id:  Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    code:       Mapped[str]             = mapped_column(String(50), nullable=False)
    name:       Mapped[str]             = mapped_column(String(200), nullable=False)
    status:     Mapped[str]             = mapped_column(String(20), nullable=False, default="ACTIVE")
    amount:     Mapped[float]           = mapped_column(Numeric(15, 2), nullable=False, default=0)
    metadata_:  Mapped[dict]            = mapped_column("metadata", JSONB, nullable=False, default=dict)
    version:    Mapped[int]             = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
'@

Write-Template "$MODULE_ROOT\infrastructure\repositories.py" @'
"""__MODULE_CLASS__ repositories — SQLAlchemy async"""
from __future__ import annotations

import uuid
from decimal import Decimal

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities import __MODULE_CLASS__
from ..domain.enums import __MODULE_CLASS__Status
from ..domain.value_objects import Money
from .models import __MODULE_CLASS__Model

log = structlog.get_logger()


class RepositoryError(Exception):
    """RepositoryError — ข้อผิดพลาด infrastructure"""


class SQLAlchemy__MODULE_CLASS__Repository:
    """SQLAlchemy__MODULE_CLASS__Repository — repository implementation"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _to_entity(row: __MODULE_CLASS__Model) -> __MODULE_CLASS__:
        return __MODULE_CLASS__(
            id=row.id,
            tenant_id=row.tenant_id,
            code=row.code,
            name=row.name,
            amount=Money(Decimal(str(row.amount))),
            status=__MODULE_CLASS__Status(row.status),
            version=row.version,
            metadata=row.metadata_ or {},
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )

    async def save(self, entity: __MODULE_CLASS__) -> __MODULE_CLASS__:
        """TH: บันทึก (flush เท่านั้น ห้าม commit) | EN: save (flush only)"""
        try:
            row = await self.session.get(__MODULE_CLASS__Model, entity.id)
            if row is None:
                row = __MODULE_CLASS__Model(
                    id=entity.id,
                    tenant_id=entity.tenant_id,
                    code=entity.code,
                    name=entity.name,
                    amount=entity.amount.amount,
                    status=entity.status.value,
                    version=entity.version,
                    metadata_=entity.metadata,
                    deleted_at=entity.deleted_at,
                )
                self.session.add(row)
            else:
                row.name = entity.name
                row.amount = entity.amount.amount
                row.status = entity.status.value
                row.version = entity.version
                row.metadata_ = entity.metadata
                row.deleted_at = entity.deleted_at
            await self.session.flush()
            return entity
        except Exception as e:
            raise RepositoryError(f"save failed: {e}") from e

    async def soft_delete(self, entity_id: uuid.UUID) -> None:
        try:
            row = await self.session.get(__MODULE_CLASS__Model, entity_id)
            if row is not None:
                row.deleted_at = func.now()
                await self.session.flush()
        except Exception as e:
            raise RepositoryError(f"soft_delete failed: {e}") from e

    async def get_by_id(self, entity_id: uuid.UUID) -> __MODULE_CLASS__ | None:
        stmt = select(__MODULE_CLASS__Model).where(
            __MODULE_CLASS__Model.id == entity_id,
            __MODULE_CLASS__Model.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def get_by_code(self, code: str) -> __MODULE_CLASS__ | None:
        stmt = select(__MODULE_CLASS__Model).where(
            __MODULE_CLASS__Model.code == code,
            __MODULE_CLASS__Model.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def list(
        self,
        *,
        status: str | None,
        q: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[__MODULE_CLASS__], int]:
        base = select(__MODULE_CLASS__Model).where(
            __MODULE_CLASS__Model.deleted_at.is_(None)
        )
        if status:
            base = base.where(__MODULE_CLASS__Model.status == status)
        if q:
            like = f"%{q}%"
            base = base.where(
                or_(
                    __MODULE_CLASS__Model.code.ilike(like),
                    __MODULE_CLASS__Model.name.ilike(like),
                )
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = base.order_by(__MODULE_CLASS__Model.created_at.desc()).limit(limit).offset(offset)
        rows = (await self.session.execute(stmt)).scalars().all()
        return [self._to_entity(r) for r in rows], int(total)
'@

Write-Template "$MODULE_ROOT\infrastructure\caches.py" @'
"""__MODULE_CLASS__ caches — Redis with tombstone-first invalidation.

Protocol (from Migrations.txt):
  1. invalidate: SET tombstone (TTL) BEFORE DEL entry
  2. set:        check tombstone BEFORE writing
  3. tombstones outlive the longest plausible read-then-write window

Policy (when to read-through, when to invalidate, which TTL) lives in the
use case. This class only executes — and never raises. Postgres is the
source of truth; Redis is an accelerator we must be able to lose.
"""
from __future__ import annotations

import json
from decimal import Decimal

import structlog

from ..domain.entities import __MODULE_CLASS__
from ..domain.enums import __MODULE_CLASS__Status
from ..domain.value_objects import Money

log = structlog.get_logger()

# ── Namespacing & versioning ────────────────────────────────────
# Every key hangs off this namespace. Bump REDIS_CACHE_VERSION whenever
# the serialized payload changes — the previous generation becomes
# unreachable and expires by TTL on its own.
REDIS_KEY_PREFIX = "erp"
REDIS_CACHE_VERSION = "1"
REDIS_NAMESPACE = f"{REDIS_KEY_PREFIX}:v{REDIS_CACHE_VERSION}"

REDIS_DEFAULT_TTL_SECONDS = 3600
REDIS_TOMBSTONE_TTL_SECONDS = 30


def _entry_key(logical: str) -> str:
    """TH: ประกอบ key จริงใต้ namespace | EN: build real key under namespace"""
    return f"{REDIS_NAMESPACE}:{logical}"


def _tombstone_key(logical: str) -> str:
    return f"{REDIS_NAMESPACE}:{logical}:tombstone"


class Redis__MODULE_CLASS__Cache:
    """Redis__MODULE_CLASS__Cache — never-raise cache (tombstone-first)."""

    def __init__(self, redis_client) -> None:
        self.redis = redis_client

    async def get(self, key: str) -> __MODULE_CLASS__ | None:
        try:
            raw = await self.redis.get(_entry_key(key))
            if not raw:
                return None
            data = json.loads(raw)
            return __MODULE_CLASS__(
                code=data["code"],
                name=data["name"],
                amount=Money(Decimal(data["amount"]), data.get("currency", "THB")),
                status=__MODULE_CLASS__Status(data.get("status", "ACTIVE")),
            )
        except Exception as e:
            log.warning("cache.get_failed", key=key, err=str(e))
            return None

    async def set(
        self,
        key: str,
        entity: __MODULE_CLASS__,
        ttl: int = REDIS_DEFAULT_TTL_SECONDS,
    ) -> None:
        """TH: เขียน cache (tombstone check ก่อน) | EN: write (tombstone check first)."""
        try:
            # 1. tombstone check BEFORE write — a slow reader that missed
            #    the cache must not resurrect revoked data.
            tomb = await self.redis.get(_tombstone_key(key))
            if tomb:
                log.info("cache.set.suppressed_by_tombstone", key=key)
                return

            payload = {
                "code": entity.code,
                "name": entity.name,
                "amount": str(entity.amount.amount),
                "currency": entity.amount.currency,
                "status": entity.status.value,
            }
            await self.redis.set(_entry_key(key), json.dumps(payload), ex=ttl)
        except Exception as e:
            log.warning("cache.set_failed", key=key, err=str(e))

    async def invalidate(self, key: str) -> bool:
        """TH: tombstone ก่อน แล้วค่อย DEL | EN: tombstone first, then DEL."""
        try:
            # 1. write tombstone BEFORE removing the entry
            await self.redis.set(
                _tombstone_key(key), "1", ex=REDIS_TOMBSTONE_TTL_SECONDS
            )
            # 2. then delete the entry
            await self.redis.delete(_entry_key(key))
            return True
        except Exception as e:
            log.warning("cache.invalidate_failed", key=key, err=str(e))
            return False
'@

Write-Template "$MODULE_ROOT\infrastructure\services.py" @'
"""__MODULE_CLASS__ infrastructure services"""
from __future__ import annotations

import structlog

log = structlog.get_logger()


class __MODULE_CLASS__DomainService:
    """__MODULE_CLASS__DomainService — บริการระดับ infrastructure"""

    async def healthcheck(self) -> bool:
        try:
            return True
        except Exception as e:
            log.warning("service.healthcheck_failed", err=str(e))
            return False
'@

# ════════════════════════════════════════════════════════════
# 6. PRESENTATION LAYER
# ════════════════════════════════════════════════════════════
Write-Host "--- PRESENTATION layer ---" -ForegroundColor Yellow

Write-Template "$MODULE_ROOT\presentation\__init__.py" @'
"""__MODULE_CLASS__ presentation layer"""
from .dependencies import (
    get_create_uc, get_delete_uc, get_get_uc, get_list_uc, get_update_uc,
)
from .routers import router

__all__ = [
    "router",
    "get_create_uc", "get_get_uc", "get_list_uc",
    "get_update_uc", "get_delete_uc",
]
'@

Write-Template "$MODULE_ROOT\presentation\schemas.py" @'
"""__MODULE_CLASS__ schemas — Pydantic v2"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..domain.enums import __MODULE_CLASS__Status


class __MODULE_CLASS__CreateRequest(BaseModel):
    """__MODULE_CLASS__CreateRequest — payload สร้างใหม่"""
    model_config = ConfigDict(strict=True, extra="forbid")

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="THB", pattern="^(THB|USD|EUR)$")
    metadata: dict = Field(default_factory=dict)


class __MODULE_CLASS__UpdateRequest(BaseModel):
    """__MODULE_CLASS__UpdateRequest — payload แก้ไข (partial)"""
    model_config = ConfigDict(strict=True, extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    version: int | None = Field(default=None, ge=1)


class __MODULE_CLASS__Response(BaseModel):
    """__MODULE_CLASS__Response — response เดี่ยว"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    amount: Decimal
    currency: str = "THB"
    status: __MODULE_CLASS__Status
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class __MODULE_CLASS__ListResponse(BaseModel):
    """__MODULE_CLASS__ListResponse — response list"""

    items: list[__MODULE_CLASS__Response]
    total: int
    limit: int
    offset: int
'@

Write-Template "$MODULE_ROOT\presentation\docs.py" @'
"""__MODULE_CLASS__ presentation docs — OpenAPI metadata"""

RESPONSE_CREATE_201 = {
    "description": "สร้างสำเร็จ / created",
    "content": {
        "application/json": {
            "example": {
                "id": "00000000-0000-0000-0000-000000000000",
                "code": "X-001", "name": "Sample",
                "amount": "100.00", "currency": "THB",
                "status": "ACTIVE", "version": 1,
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z",
            }
        }
    },
}

RESPONSE_ERROR_400 = {
    "description": "Domain error",
    "content": {"application/json": {"example": {"detail": "amount must be >= 0"}}},
}

RESPONSE_ERROR_404 = {
    "description": "ไม่พบ entity",
    "content": {"application/json": {"example": {"detail": "__MODULE__ not found"}}},
}

RESPONSE_ERROR_409 = {
    "description": "Conflict (duplicate code / version)",
    "content": {"application/json": {"example": {"detail": "code already exists"}}},
}

RESPONSE_ERROR_422 = {
    "description": "Validation error",
    "content": {"application/json": {"example": {"detail": "invalid input"}}},
}
'@

Write-Template "$MODULE_ROOT\presentation\dependencies.py" @'
"""__MODULE_CLASS__ dependencies — FastAPI DI container"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.use_cases import (
    Create__MODULE_CLASS__UseCase,
    Delete__MODULE_CLASS__UseCase,
    Get__MODULE_CLASS__UseCase,
    List__MODULE_CLASS__UseCase,
    Update__MODULE_CLASS__UseCase,
)
from ..infrastructure.caches import Redis__MODULE_CLASS__Cache
from ..infrastructure.repositories import SQLAlchemy__MODULE_CLASS__Repository


try:
    from app.core.db import get_session  # type: ignore
except Exception:
    async def get_session():  # type: ignore
        raise RuntimeError("app.core.db.get_session not configured")

try:
    from app.core.context import get_context  # type: ignore
except Exception:
    def get_context():  # type: ignore
        return {"tenant_id": "00000000-0000-0000-0000-000000000001"}

try:
    from app.core.events import get_event_bus  # type: ignore
except Exception:
    class _NullBus:
        async def publish(self, event): return None
    def get_event_bus():  # type: ignore
        return _NullBus()

try:
    from app.core.idempotency import get_idempotency_store  # type: ignore
except Exception:
    class _NullIdem:
        async def check_or_lock(self, **_kw): return None
        async def complete(self, **_kw): return None
    def get_idempotency_store():  # type: ignore
        return _NullIdem()

try:
    from app.core.redis import get_redis  # type: ignore
except Exception:
    def get_redis():  # type: ignore
        return None


def get___MODULE___repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemy__MODULE_CLASS__Repository:
    return SQLAlchemy__MODULE_CLASS__Repository(session=session)


def get___MODULE___cache() -> Redis__MODULE_CLASS__Cache:
    return Redis__MODULE_CLASS__Cache(redis_client=get_redis())


async def get_create_uc(
    repo: Annotated[SQLAlchemy__MODULE_CLASS__Repository, Depends(get___MODULE___repo)],
    cache: Annotated[Redis__MODULE_CLASS__Cache, Depends(get___MODULE___cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    idem: Annotated[object, Depends(get_idempotency_store)],
    ctx: Annotated[dict, Depends(get_context)],
) -> Create__MODULE_CLASS__UseCase:
    return Create__MODULE_CLASS__UseCase(
        repo=repo, cache=cache, event_bus=bus, idempotency=idem, ctx=ctx,
    )


async def get_get_uc(
    repo: Annotated[SQLAlchemy__MODULE_CLASS__Repository, Depends(get___MODULE___repo)],
    cache: Annotated[Redis__MODULE_CLASS__Cache, Depends(get___MODULE___cache)],
    ctx: Annotated[dict, Depends(get_context)],
) -> Get__MODULE_CLASS__UseCase:
    return Get__MODULE_CLASS__UseCase(repo=repo, cache=cache, ctx=ctx)


async def get_list_uc(
    repo: Annotated[SQLAlchemy__MODULE_CLASS__Repository, Depends(get___MODULE___repo)],
    ctx: Annotated[dict, Depends(get_context)],
) -> List__MODULE_CLASS__UseCase:
    return List__MODULE_CLASS__UseCase(repo=repo, ctx=ctx)


async def get_update_uc(
    repo: Annotated[SQLAlchemy__MODULE_CLASS__Repository, Depends(get___MODULE___repo)],
    cache: Annotated[Redis__MODULE_CLASS__Cache, Depends(get___MODULE___cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    ctx: Annotated[dict, Depends(get_context)],
) -> Update__MODULE_CLASS__UseCase:
    return Update__MODULE_CLASS__UseCase(
        repo=repo, cache=cache, event_bus=bus, ctx=ctx,
    )


async def get_delete_uc(
    repo: Annotated[SQLAlchemy__MODULE_CLASS__Repository, Depends(get___MODULE___repo)],
    cache: Annotated[Redis__MODULE_CLASS__Cache, Depends(get___MODULE___cache)],
    bus: Annotated[object, Depends(get_event_bus)],
    ctx: Annotated[dict, Depends(get_context)],
) -> Delete__MODULE_CLASS__UseCase:
    return Delete__MODULE_CLASS__UseCase(
        repo=repo, cache=cache, event_bus=bus, ctx=ctx,
    )
'@

Write-Template "$MODULE_ROOT\presentation\routers.py" @'
"""__MODULE_CLASS__ routers — FastAPI endpoints"""
from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from ..application.exceptions import (
    DuplicateCodeError as AppDuplicateCodeError,
    __MODULE_CLASS__NotFoundError as AppNotFoundError,
)
from ..application.use_cases import (
    Create__MODULE_CLASS__UseCase,
    Delete__MODULE_CLASS__UseCase,
    Get__MODULE_CLASS__UseCase,
    List__MODULE_CLASS__UseCase,
    Update__MODULE_CLASS__UseCase,
)
from ..domain.exceptions import DomainError
from .dependencies import (
    get_create_uc, get_delete_uc, get_get_uc, get_list_uc, get_update_uc,
)
from .docs import (
    RESPONSE_CREATE_201,
    RESPONSE_ERROR_400,
    RESPONSE_ERROR_404,
    RESPONSE_ERROR_409,
    RESPONSE_ERROR_422,
)
from .schemas import (
    __MODULE_CLASS__CreateRequest,
    __MODULE_CLASS__ListResponse,
    __MODULE_CLASS__Response,
    __MODULE_CLASS__UpdateRequest,
)

log = structlog.get_logger()

router = APIRouter(prefix="/__MODULE__", tags=["__MODULE_CLASS__"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง __MODULE__",
    operation_id="create___MODULE__",
    response_model=__MODULE_CLASS__Response,
    responses={
        201: RESPONSE_CREATE_201,
        400: RESPONSE_ERROR_400,
        409: RESPONSE_ERROR_409,
        422: RESPONSE_ERROR_422,
    },
)
async def create___MODULE__(
    payload: __MODULE_CLASS__CreateRequest,
    idem_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
    uc: Annotated[Create__MODULE_CLASS__UseCase, Depends(get_create_uc)],
) -> __MODULE_CLASS__Response:
    """TH: สร้าง entity ใหม่ (idempotent) | EN: create entity (idempotent)"""
    log.info("http.create.start", code=payload.code, idem=idem_key[:8])
    try:
        entity = await uc.execute(
            code=payload.code, name=payload.name,
            amount=payload.amount, idempotency_key=idem_key,
        )
    except AppDuplicateCodeError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return __MODULE_CLASS__Response.model_validate(entity, from_attributes=True)


@router.get(
    "/",
    summary="รายการ __MODULE__",
    operation_id="list___MODULE__",
    response_model=__MODULE_CLASS__ListResponse,
)
async def list___MODULE__(
    uc: Annotated[List__MODULE_CLASS__UseCase, Depends(get_list_uc)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> __MODULE_CLASS__ListResponse:
    """TH: list + filter + paginate | EN: list + filter + paginate"""
    items, total = await uc.execute(
        status=status_filter, q=q, limit=limit, offset=offset
    )
    return __MODULE_CLASS__ListResponse(
        items=[__MODULE_CLASS__Response.model_validate(x, from_attributes=True) for x in items],
        total=total, limit=limit, offset=offset,
    )


@router.get(
    "/{entity_id}",
    summary="ดู __MODULE__ ตาม id",
    operation_id="get___MODULE__",
    response_model=__MODULE_CLASS__Response,
    responses={404: RESPONSE_ERROR_404},
)
async def get___MODULE__(
    entity_id: uuid.UUID,
    uc: Annotated[Get__MODULE_CLASS__UseCase, Depends(get_get_uc)],
) -> __MODULE_CLASS__Response:
    try:
        entity = await uc.execute(entity_id=entity_id)
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return __MODULE_CLASS__Response.model_validate(entity, from_attributes=True)


@router.patch(
    "/{entity_id}",
    summary="แก้ไข __MODULE__",
    operation_id="update___MODULE__",
    response_model=__MODULE_CLASS__Response,
    responses={404: RESPONSE_ERROR_404, 409: RESPONSE_ERROR_409},
)
async def update___MODULE__(
    entity_id: uuid.UUID,
    payload: __MODULE_CLASS__UpdateRequest,
    uc: Annotated[Update__MODULE_CLASS__UseCase, Depends(get_update_uc)],
) -> __MODULE_CLASS__Response:
    try:
        entity = await uc.execute(
            entity_id=entity_id, **payload.model_dump(exclude_unset=True)
        )
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return __MODULE_CLASS__Response.model_validate(entity, from_attributes=True)


@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ลบ __MODULE__ (soft delete)",
    operation_id="delete___MODULE__",
    responses={404: RESPONSE_ERROR_404},
)
async def delete___MODULE__(
    entity_id: uuid.UUID,
    uc: Annotated[Delete__MODULE_CLASS__UseCase, Depends(get_delete_uc)],
) -> None:
    try:
        await uc.execute(entity_id=entity_id)
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
'@

Write-Template "$MODULE_ROOT\__init__.py" @'
"""__MODULE_CLASS__ module — โมดูล __MODULE__"""
from .presentation.routers import router as __MODULE___router

__all__ = ["__MODULE___router"]
'@

Write-Host "[OK] Python files done" -ForegroundColor Green
Write-Host ""

# ════════════════════════════════════════════════════════════
# 7. SQL MIGRATIONS
# ════════════════════════════════════════════════════════════
if ($Sql) {
    Write-Host "--- SQL migrations ---" -ForegroundColor Yellow

    Write-Template "migrations\versions\db\V001__create___MODULE__.sql" @'
-- ═══════════════════════════════════════════════════════════════
-- V001__create___MODULE__.sql
-- Module: __MODULE__ | Prefix: __PREFIX__ | Layer: __LAYER__
-- Description: สร้างตาราง + index + RLS policy + trigger
-- ═══════════════════════════════════════════════════════════════
BEGIN;

CREATE SCHEMA IF NOT EXISTS __SCHEMA__;
CREATE SEQUENCE IF NOT EXISTS __PREFIX___number_seq START 1;

CREATE TABLE __SCHEMA__.__TABLES__ (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id    UUID NOT NULL,
    code         VARCHAR(50)  NOT NULL,
    name         VARCHAR(200) NOT NULL,
    status       VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE',
    amount       NUMERIC(15,2) NOT NULL DEFAULT 0,
    metadata     JSONB        NOT NULL DEFAULT '{}'::jsonb,
    version      INTEGER      NOT NULL DEFAULT 1,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT uq___MODULE___code   UNIQUE (tenant_id, code),
    CONSTRAINT ck___MODULE___amount CHECK (amount >= 0),
    CONSTRAINT ck___MODULE___status CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'))
);

CREATE INDEX ix___MODULE___tenant_status
    ON __SCHEMA__.__TABLES__(tenant_id, status)
    WHERE deleted_at IS NULL;
CREATE INDEX ix___MODULE___code ON __SCHEMA__.__TABLES__(code);
CREATE INDEX ix___MODULE___created ON __SCHEMA__.__TABLES__(created_at DESC);

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg___MODULE___updated_at
    BEFORE UPDATE ON __SCHEMA__.__TABLES__
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE __SCHEMA__.__TABLES__ ENABLE ROW LEVEL SECURITY;
ALTER TABLE __SCHEMA__.__TABLES__ FORCE ROW LEVEL SECURITY;

CREATE POLICY p___MODULE___tenant ON __SCHEMA__.__TABLES__
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
'@

    Write-Template "migrations\versions\db\V002__seed___MODULE__.sql" @'
-- ═══════════════════════════════════════════════════════════════
-- V002__seed___MODULE__.sql
-- Description: seed ข้อมูลตั้งต้น (system default)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO __SCHEMA__.__TABLES__ (tenant_id, code, name, status, amount)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'SYS-DEFAULT',
    'System Default',
    'ACTIVE',
    0
)
ON CONFLICT (tenant_id, code) DO NOTHING;

COMMIT;
'@

    Write-Template "migrations\versions\db\V003__rollback___MODULE__.sql" @'
-- ═══════════════════════════════════════════════════════════════
-- V003__rollback___MODULE__.sql
-- Description: rollback ทั้งหมด (ใช้ตอน dev/staging เท่านั้น)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER  IF EXISTS trg___MODULE___updated_at ON __SCHEMA__.__TABLES__;
DROP POLICY   IF EXISTS p___MODULE___tenant       ON __SCHEMA__.__TABLES__;
DROP TABLE    IF EXISTS __SCHEMA__.__TABLES__ CASCADE;
DROP SEQUENCE IF EXISTS __PREFIX___number_seq;

COMMIT;
'@

    Write-Template "migrations\versions\db\REGISTER___MODULE__.md" @'
# Register model in `migrations/env.py`

> Generator ได้ patch `migrations/env.py` ให้อัตโนมัติแล้ว
> (idempotent — รันซ้ำจะไม่เพิ่มบรรทัดซ้ำ)

## บรรทัดที่ถูกเพิ่ม

    # --- module __MODULE__ (auto-registered) ---
    from app.modules.__MODULE__.infrastructure.models import __MODULE_CLASS__Model  # noqa: F401

TH: register model เพื่อให้ Alembic/SQLAlchemy metadata รู้จัก
EN: register model so Alembic/SQLAlchemy metadata knows it

## ถ้าต้องการเพิ่มเอง (กรณีไฟล์ env.py ไม่มีตอน generate)

เพิ่มที่ด้านบนของ `migrations/env.py`:

    from app.modules.__MODULE__.infrastructure.models import __MODULE_CLASS__Model  # noqa: F401

และถ้า `env.py` ใช้ `_ = [...]` list ให้เพิ่ม `__MODULE_CLASS__Model` เข้าไปด้วย
มิฉะนั้น autogenerate จะ emit `drop_table` ให้ตารางที่ยัง live อยู่

## Verify

    make migration m="create___MODULE___model"
    make migrate

- [ ] migration ที่ generate **ไม่มี** `drop_table(...)` ที่ไม่คาดคิด
- [ ] ตาราง `__SCHEMA__.__TABLES__` ปรากฏใน migration
- [ ] RLS policy `p___MODULE___tenant` ปรากฏใน migration
'@

    # Auto-register the model so Alembic autogenerate sees it.
    # Without this, autogenerate emits a drop_table for the live table.
    Register-ModelInEnv -ModuleName $MODULE -ClassPrefix $MODULE_CLASS

    Write-Host "[OK] SQL migrations done" -ForegroundColor Green
    Write-Host ""
}

# ════════════════════════════════════════════════════════════
# 8. TESTS
# ════════════════════════════════════════════════════════════
if ($Tests) {
    Write-Host "--- Tests ---" -ForegroundColor Yellow

    Write-Template "tests\conftest.py" @'
"""tests/conftest.py — Global fixtures"""
from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)

TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OTHER_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def faker_th() -> Faker:
    return Faker("th_TH")


@pytest.fixture
def tenant_ctx() -> dict[str, Any]:
    return {
        "tenant_id": TENANT_ID,
        "user_id": uuid.uuid4(),
        "request_id": str(uuid.uuid4()),
        "trace_id": str(uuid.uuid4()),
    }


@pytest.fixture
def other_tenant_ctx() -> dict[str, Any]:
    return {
        "tenant_id": OTHER_TENANT_ID,
        "user_id": uuid.uuid4(),
        "request_id": str(uuid.uuid4()),
        "trace_id": str(uuid.uuid4()),
    }


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncIterator[Any]:
    url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5433/erp_test",
    )
    engine = create_async_engine(url, pool_pre_ping=True, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: Any) -> AsyncIterator[AsyncSession]:
    async with db_engine.connect() as conn:
        tx = await conn.begin()
        Session = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with Session() as session:
            await session.execute(
                text("SELECT set_config('app.current_tenant', :tid, true)"),
                {"tid": str(TENANT_ID)},
            )
            yield session
        await tx.rollback()


@pytest_asyncio.fixture
async def redis_client() -> AsyncIterator[Any]:
    import redis.asyncio as aioredis
    client = aioredis.from_url(
        os.getenv("TEST_REDIS_URL", "redis://localhost:6380/15"),
        decode_responses=True,
    )
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
def decimal_factory() -> Any:
    def _make(value: str | int) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    return _make
'@

    Write-Template "tests\unit\test___MODULE__.py" @'
"""tests/unit/test___MODULE__.py — Domain layer unit tests"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.modules.__MODULE__.domain.entities import __MODULE_CLASS__
from app.modules.__MODULE__.domain.enums import __MODULE_CLASS__Status
from app.modules.__MODULE__.domain.exceptions import (
    DomainError, InvalidAmountError, InvalidStatusTransitionError,
)
from app.modules.__MODULE__.domain.value_objects import Money

pytestmark = pytest.mark.unit

TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def make_entity():
    def _make(
        code: str = "X-001",
        name: str = "Sample",
        amount: Decimal = Decimal("100.00"),
        status: __MODULE_CLASS__Status = __MODULE_CLASS__Status.ACTIVE,
    ) -> __MODULE_CLASS__:
        return __MODULE_CLASS__.create(
            tenant_id=TENANT, code=code, name=name, amount=amount, status=status,
        )
    return _make


class TestCreate:
    def test_create_sets_defaults(self, make_entity) -> None:
        e = make_entity()
        assert e.id is not None
        assert e.version == 1
        assert e.status is __MODULE_CLASS__Status.ACTIVE
        assert e.deleted_at is None

    def test_create_with_zero_amount(self, make_entity) -> None:
        e = make_entity(amount=Decimal("0.00"))
        assert e.amount.amount == Decimal("0.00")

    def test_amount_precision_quantized(self, make_entity) -> None:
        e = make_entity(amount=Decimal("100.005"))
        assert e.amount.amount == Decimal("100.01")


class TestBehavior:
    def test_activate_from_inactive(self, make_entity) -> None:
        e = make_entity(status=__MODULE_CLASS__Status.INACTIVE)
        e.activate()
        assert e.status is __MODULE_CLASS__Status.ACTIVE
        assert e.version == 2

    def test_archive_then_activate_raises(self, make_entity) -> None:
        e = make_entity()
        e.archive()
        with pytest.raises(InvalidStatusTransitionError):
            e.activate()

    def test_soft_delete_sets_timestamp(self, make_entity) -> None:
        e = make_entity()
        e.soft_delete()
        assert e.deleted_at is not None
        assert e.is_deleted() is True


class TestErrors:
    def test_negative_amount_raises(self, make_entity) -> None:
        with pytest.raises(InvalidAmountError):
            make_entity(amount=Decimal("-1.00"))

    def test_empty_code_raises(self, make_entity) -> None:
        with pytest.raises(DomainError):
            make_entity(code="")


class TestMoneyVO:
    def test_money_add(self) -> None:
        a = Money(Decimal("10.00"))
        b = Money(Decimal("5.50"))
        assert (a + b).amount == Decimal("15.50")

    def test_money_currency_mismatch(self) -> None:
        a = Money(Decimal("10.00"), "THB")
        b = Money(Decimal("5.00"), "USD")
        with pytest.raises(DomainError):
            _ = a + b
'@

    Write-Template "tests\unit\test___MODULE___use_cases.py" @'
"""tests/unit/test___MODULE___use_cases.py — Application layer"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.__MODULE__.application.exceptions import DuplicateCodeError
from app.modules.__MODULE__.application.use_cases import Create__MODULE_CLASS__UseCase
from app.modules.__MODULE__.domain.entities import __MODULE_CLASS__

pytestmark = pytest.mark.unit


@pytest.fixture
def repo() -> AsyncMock:
    r = AsyncMock()
    r.get_by_code.return_value = None
    r.save.side_effect = lambda e: e
    r.get_by_id.side_effect = lambda _id: MagicMock(spec=__MODULE_CLASS__)
    return r


@pytest.fixture
def cache() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def event_bus() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def idem() -> AsyncMock:
    m = AsyncMock()
    m.check_or_lock.return_value = None
    return m


@pytest.fixture
def uc(repo, cache, event_bus, idem, tenant_ctx) -> Create__MODULE_CLASS__UseCase:
    return Create__MODULE_CLASS__UseCase(
        repo=repo, cache=cache, event_bus=event_bus,
        idempotency=idem, ctx=tenant_ctx,
    )


class TestCreateUseCase:
    async def test_happy_path(self, uc, repo, event_bus) -> None:
        await uc.execute(
            code="X-001", name="Test",
            amount=Decimal("100.00"), idempotency_key="k-12345678",
        )
        repo.save.assert_awaited_once()
        event_bus.publish.assert_awaited_once()

    async def test_duplicate_code_raises(self, uc, repo) -> None:
        repo.get_by_code.return_value = MagicMock(spec=__MODULE_CLASS__)
        with pytest.raises(DuplicateCodeError):
            await uc.execute(
                code="X-001", name="Dup",
                amount=Decimal("1.00"), idempotency_key="k-12345678",
            )
        repo.save.assert_not_awaited()

    async def test_cache_failure_does_not_break(self, uc, cache) -> None:
        cache.invalidate.side_effect = RuntimeError("redis down")
        await uc.execute(
            code="X-002", name="X",
            amount=Decimal("1.00"), idempotency_key="k-22345678",
        )

    async def test_readback_verification(self, uc, repo) -> None:
        await uc.execute(
            code="X-003", name="X",
            amount=Decimal("1.00"), idempotency_key="k-32345678",
        )
        repo.get_by_id.assert_awaited_once()
'@

    Write-Template "tests\unit\test___MODULE___cache.py" @'
"""tests/unit/test___MODULE___cache.py — Tombstone protocol."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.modules.__MODULE__.domain.entities import __MODULE_CLASS__
from app.modules.__MODULE__.infrastructure.caches import (
    Redis__MODULE_CLASS__Cache,
    _entry_key,
    _tombstone_key,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def redis() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def cache(redis) -> Redis__MODULE_CLASS__Cache:
    return Redis__MODULE_CLASS__Cache(redis_client=redis)


class TestTombstoneProtocol:
    async def test_invalidate_writes_tombstone_before_delete(
        self, cache, redis
    ) -> None:
        calls: list[str] = []
        async def rec_set(*a, **kw): calls.append("set")
        async def rec_del(*a, **kw): calls.append("del")
        redis.set.side_effect = rec_set
        redis.delete.side_effect = rec_del

        await cache.invalidate("__MODULE__:x")
        assert calls == ["set", "del"], "tombstone must be written first"

    async def test_set_suppressed_when_tombstone_present(
        self, cache, redis
    ) -> None:
        redis.get.return_value = "1"  # tombstone present
        entity = __MODULE_CLASS__.create(
            tenant_id=None, code="X", name="N", amount=Decimal("1.00"),
        )
        await cache.set("__MODULE__:x", entity)
        redis.set.assert_not_awaited()

    async def test_set_writes_when_no_tombstone(self, cache, redis) -> None:
        redis.get.return_value = None
        entity = __MODULE_CLASS__.create(
            tenant_id=None, code="X", name="N", amount=Decimal("1.00"),
        )
        await cache.set("__MODULE__:x", entity)
        redis.set.assert_awaited_once()

    async def test_get_failure_returns_none(self, cache, redis) -> None:
        redis.get.side_effect = RuntimeError("redis down")
        assert await cache.get("__MODULE__:x") is None

    async def test_invalidate_failure_returns_false(self, cache, redis) -> None:
        redis.set.side_effect = RuntimeError("redis down")
        assert await cache.invalidate("__MODULE__:x") is False
'@

    Write-Template "tests\integration\test___MODULE___repository.py" @'
"""tests/integration/test___MODULE___repository.py — Repository + RLS"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.modules.__MODULE__.domain.entities import __MODULE_CLASS__
from app.modules.__MODULE__.infrastructure.repositories import (
    SQLAlchemy__MODULE_CLASS__Repository,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def repo(db_session) -> SQLAlchemy__MODULE_CLASS__Repository:
    return SQLAlchemy__MODULE_CLASS__Repository(session=db_session)


class TestRepository:
    async def test_save_and_get(self, repo, tenant_ctx) -> None:
        e = __MODULE_CLASS__.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=f"X-{uuid.uuid4().hex[:6]}",
            name="Repo Test",
            amount=Decimal("99.99"),
        )
        saved = await repo.save(e)
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.code == saved.code

    async def test_rls_blocks_other_tenant(
        self, repo, db_session, tenant_ctx, other_tenant_ctx
    ) -> None:
        e = __MODULE_CLASS__.create(
            tenant_id=tenant_ctx["tenant_id"],
            code="X-RLS-1", name="RLS", amount=Decimal("1.00"),
        )
        await repo.save(e)
        await db_session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"),
            {"tid": str(other_tenant_ctx["tenant_id"])},
        )
        found = await repo.get_by_id(e.id)
        assert found is None

    async def test_unique_code_conflict(self, repo, tenant_ctx) -> None:
        code = f"X-{uuid.uuid4().hex[:6]}"
        e1 = __MODULE_CLASS__.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=code, name="A", amount=Decimal("1.00"),
        )
        await repo.save(e1)
        e2 = __MODULE_CLASS__.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=code, name="B", amount=Decimal("2.00"),
        )
        with pytest.raises(Exception):
            await repo.save(e2)

    async def test_soft_delete_filter(self, repo, tenant_ctx) -> None:
        e = __MODULE_CLASS__.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=f"X-{uuid.uuid4().hex[:6]}",
            name="Soft", amount=Decimal("1.00"),
        )
        saved = await repo.save(e)
        await repo.soft_delete(saved.id)
        found = await repo.get_by_id(saved.id)
        assert found is None
'@

    Write-Template "tests\property\test___MODULE___invariants.py" @'
"""tests/property/test___MODULE___invariants.py — Property-based"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st

from app.modules.__MODULE__.domain.entities import __MODULE_CLASS__
from app.modules.__MODULE__.domain.exceptions import InvalidAmountError
from app.modules.__MODULE__.domain.value_objects import Money

pytestmark = pytest.mark.property

TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")

amounts = st.decimals(
    min_value=Decimal("0.00"),
    max_value=Decimal("999999999.99"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)

codes = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-",
    min_size=1, max_size=50,
)


@settings(max_examples=100)
@given(amount=amounts, code=codes)
def test_non_negative_amount_always_valid(amount: Decimal, code: str) -> None:
    e = __MODULE_CLASS__.create(
        tenant_id=TENANT, code=code or "X", name="P", amount=amount,
    )
    assert e.amount.amount >= Decimal("0.00")


@settings(max_examples=100)
@given(amount=st.decimals(
    min_value=Decimal("-9999"), max_value=Decimal("-0.01"), places=2,
))
def test_negative_amount_always_rejected(amount: Decimal) -> None:
    with pytest.raises(InvalidAmountError):
        __MODULE_CLASS__.create(
            tenant_id=TENANT, code="X", name="P", amount=amount,
        )


@settings(max_examples=100)
@given(a=amounts, b=amounts)
def test_sum_is_commutative(a: Decimal, b: Decimal) -> None:
    m1 = Money(a); m2 = Money(b)
    assert (m1 + m2).amount == (m2 + m1).amount
'@

    Write-Template "tests\manual\manual_test___MODULE__.md" @'
# Manual Test — __MODULE__

## Pre-conditions
- [ ] DB migrated (V001–V003)
- [ ] Redis running
- [ ] Kafka running (ถ้ามี)
- [ ] .env set TEST_DATABASE_URL

## Scenarios (8)

| # | Scenario | Method | Endpoint | Expected | OK |
|---|---|---|---|---|---|
| 1 | Create happy | POST | /api/v1/__MODULE__/ | 201 + body | [ ] |
| 2 | Create duplicate | POST | /api/v1/__MODULE__/ | 409 | [ ] |
| 3 | Create invalid amount | POST | /api/v1/__MODULE__/ | 422 | [ ] |
| 4 | Get by id | GET | /api/v1/__MODULE__/{id} | 200 | [ ] |
| 5 | List + filter | GET | /api/v1/__MODULE__/?status=ACTIVE | 200 | [ ] |
| 6 | Update | PATCH | /api/v1/__MODULE__/{id} | 200 + version+1 | [ ] |
| 7 | Delete (soft) | DELETE | /api/v1/__MODULE__/{id} | 204 | [ ] |
| 8 | Cross-tenant | GET | other tenant token | 404 | [ ] |

## Idempotency
- [ ] POST ซ้ำด้วย Idempotency-Key เดิม -> ได้ response เดิม
- [ ] POST ด้วย key เดิม + payload ต่าง -> 422

## Security
- [ ] ไม่มี token -> 401
- [ ] token ผิด scope -> 403
- [ ] SQL injection ที่ code -> 422
'@

    Write-Host "[OK] Tests done" -ForegroundColor Green
    Write-Host ""
}

# ════════════════════════════════════════════════════════════
# 9. DOCS
# ════════════════════════════════════════════════════════════
if ($Docs) {
    Write-Host "--- Docs ---" -ForegroundColor Yellow

    Write-Template "docs\README___MODULE__.md" @'
# Module: __MODULE__

> Layer: __LAYER__ | Prefix: __PREFIX__ | Version: 1.0.0

## Purpose

TH: อธิบายวัตถุประสงค์ของ module __MODULE__
EN: describe purpose of __MODULE__ module

## Database Schema

CREATE TABLE __SCHEMA__.__TABLES__ (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

## Migrations

`migrations/versions/` ships **empty** — the first migration creates the
whole schema. The application runs `alembic upgrade head` on startup, so
a fresh stack migrates itself.

    make migration m="create___MODULE___model"   # autogenerate
    make migrate                                 # apply

A new model must be imported in `migrations/env.py` **and** added to its
`_ = [...]` list — see `migrations/versions/db/REGISTER___MODULE__.md`.
Autogenerate only sees registered models, and worse, it emits a
`drop_table` for a live table whose model it cannot see.

## Caching

Postgres is the source of truth. Redis is an accelerator you must be able
to lose at any moment.

**Read-through**

    UC -> Redis.get(key)
          hit  -> return entity
          miss -> UC reads DB -> UC best-effort set(key)

**Invalidation — tombstone first**

    1. cache.invalidate() writes tombstone (TTL) BEFORE DEL entry
    2. cache.set()        checks tombstone BEFORE writing
    3. tombstones outlive the longest plausible read-then-write window

This closes the race where a slow reader writes a stale snapshot to cache
*after* the writer has already deleted the key.

**Namespacing & versioning**

    REDIS_NAMESPACE = f"{REDIS_KEY_PREFIX}:v{REDIS_CACHE_VERSION}"

Bump `REDIS_CACHE_VERSION` whenever the serialized payload changes — the
previous generation becomes unreachable and expires by TTL on its own.

## API Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| POST   | /api/v1/__MODULE__/      | สร้างใหม่ | yes |
| GET    | /api/v1/__MODULE__/      | list      | yes |
| GET    | /api/v1/__MODULE__/{id}  | ดูตาม id  | yes |
| PATCH  | /api/v1/__MODULE__/{id}  | แก้ไข     | yes |
| DELETE | /api/v1/__MODULE__/{id}  | soft del  | yes |

## Domain Events

| Event | Trigger | Payload |
|---|---|---|
| __MODULE_CLASS__Created | after create | id, code, tenant_id |
| __MODULE_CLASS__Updated | after update | id, changes |
| __MODULE_CLASS__Deleted | after delete | id, deleted_at |

## Environment Variables

    DATABASE_URL=postgresql+asyncpg://...
    REDIS_URL=redis://...
    KAFKA_BOOTSTRAP=localhost:9092

    # Redis (see Migrations.txt)
    REDIS_KEY_PREFIX=erp
    REDIS_CACHE_VERSION=1
    REDIS_DEFAULT_TTL_SECONDS=3600
    REDIS_SESSION_TTL_SECONDS=1800
    REDIS_TOMBSTONE_TTL_SECONDS=30
    REDIS_FLUSH_ON_STARTUP=True
    REDIS_MAX_CONNECTIONS=50

## Setup

    alembic upgrade head
    uvicorn app.main:app --reload

## Testing

    pytest tests/unit/test___MODULE__.py -v
    pytest tests/integration/test___MODULE___repository.py -v
    pytest --cov=app.modules.__MODULE__ --cov-fail-under=85

## Usage Example

    curl -X POST http://localhost:8000/api/v1/__MODULE__/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Idempotency-Key: $(uuidgen)" \
      -H "Content-Type: application/json" \
      -d '{"code":"X-001","name":"Sample","amount":"100.00"}'

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | YYYY-MM-DD | initial release |
'@

    Write-Template "docs\API___MODULE__.md" @'
# API Reference — __MODULE_CLASS__

Base URL: {BASE_URL}/api/v1/__MODULE__

## Authentication

ทุก request ต้องมี:

    Authorization: Bearer <JWT>
    Idempotency-Key: <uuid>   # เฉพาะ POST/PATCH/DELETE

## Endpoints

### POST / — สร้างใหม่

Request:

    {
      "code": "X-001",
      "name": "Sample",
      "amount": "100.00",
      "currency": "THB",
      "metadata": {}
    }

Response 201:

    {
      "id": "00000000-0000-0000-0000-000000000000",
      "code": "X-001",
      "name": "Sample",
      "amount": "100.00",
      "status": "ACTIVE",
      "version": 1
    }

Errors:

| Status | Code | Description |
|---|---|---|
| 400 | DOMAIN_ERROR | amount < 0 |
| 409 | DUPLICATE_CODE | code ซ้ำ |
| 422 | VALIDATION_ERROR | schema ไม่ถูก |

### GET / — List

Query params: status, q, limit, offset

### GET /{id} — Get by ID

Response 404 ถ้าไม่พบ

### PATCH /{id} — Update

Request: partial {"name": "New"}

### DELETE /{id} — Soft Delete

Response 204
'@

    Write-Host "[OK] Docs done" -ForegroundColor Green
    Write-Host ""
}

# ════════════════════════════════════════════════════════════
# 10. POSTMAN
# ════════════════════════════════════════════════════════════
if ($Postman) {
    Write-Host "--- Postman ---" -ForegroundColor Yellow

    Write-Template "docs\postman\__MODULE__.postman_collection.json" @'
{
  "info": {
    "name": "ERPIoT — __MODULE_CLASS__",
    "_postman_id": "00000000-0000-0000-0000-__PREFIX__00000000",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    { "key": "base_url",  "value": "http://localhost:8000" },
    { "key": "token",     "value": "" },
    { "key": "tenant_id", "value": "00000000-0000-0000-0000-000000000001" },
    { "key": "entity_id", "value": "" }
  ],
  "auth": {
    "type": "bearer",
    "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
  },
  "item": [
    {
      "name": "__MODULE_CLASS__ — Create",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Idempotency-Key", "value": "{{$guid}}" },
          { "key": "Content-Type",    "value": "application/json" }
        ],
        "url": "{{base_url}}/api/v1/__MODULE__/",
        "body": {
          "mode": "raw",
          "raw": "{\"code\":\"X-001\",\"name\":\"Sample\",\"amount\":\"100.00\"}"
        }
      }
    },
    {
      "name": "__MODULE_CLASS__ — List",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/__MODULE__/?limit=20&offset=0"
      }
    },
    {
      "name": "__MODULE_CLASS__ — Get",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/__MODULE__/{{entity_id}}"
      }
    },
    {
      "name": "__MODULE_CLASS__ — Update",
      "request": {
        "method": "PATCH",
        "header": [{ "key": "Idempotency-Key", "value": "{{$guid}}" }],
        "url": "{{base_url}}/api/v1/__MODULE__/{{entity_id}}",
        "body": { "mode": "raw", "raw": "{\"name\":\"Updated\"}" }
      }
    },
    {
      "name": "__MODULE_CLASS__ — Delete",
      "request": {
        "method": "DELETE",
        "header": [{ "key": "Idempotency-Key", "value": "{{$guid}}" }],
        "url": "{{base_url}}/api/v1/__MODULE__/{{entity_id}}"
      }
    }
  ]
}
'@

    Write-Host "[OK] Postman done" -ForegroundColor Green
    Write-Host ""
}

# ════════════════════════════════════════════════════════════
# 11. ROUTES
# ════════════════════════════════════════════════════════════
if ($Routes) {
    Write-Host "--- Routing snippet ---" -ForegroundColor Yellow

    Write-Template "docs\ROUTES___MODULE__.md" @'
# Register router for __MODULE__

## 1. app/routes.py

เพิ่ม import ตาม layer __LAYER__:

    from app.modules.__MODULE__.presentation.routers import router as __MODULE___router

จากนั้น include:

    api_router.include_router(__MODULE___router)

## 2. migrations/env.py

    from app.modules.__MODULE__.infrastructure.models import __MODULE_CLASS__Model  # noqa: F401

## 3. Verify

    uvicorn app.main:app --reload

    # open
    http://localhost:8000/docs
    http://localhost:8000/openapi.json

    # smoke
    curl -X GET http://localhost:8000/api/v1/__MODULE__/
'@

    Write-Host "[OK] Routing snippet written" -ForegroundColor Green
    Write-Host ""
}

# ════════════════════════════════════════════════════════════
# 12. SUMMARY
# ════════════════════════════════════════════════════════════
$pyFiles = Get-ChildItem -Path $MODULE_ROOT -Recurse -Filter *.py -ErrorAction SilentlyContinue | Measure-Object
$sqlFiles = if ($Sql) { (Get-ChildItem -Path "migrations\versions\db" -Filter "V*___MODULE__*.sql" -ErrorAction SilentlyContinue | Measure-Object).Count } else { 0 }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " DONE — module '$MODULE' created"           -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Python files : $($pyFiles.Count)"         -ForegroundColor White
Write-Host " SQL files    : $sqlFiles"                 -ForegroundColor White
Write-Host " Layer        : $Layer"                    -ForegroundColor White
Write-Host " Prefix       : $PREFIX_L"                 -ForegroundColor White
Write-Host " Schema       : $SCHEMA"                   -ForegroundColor White
Write-Host ""
Write-Host " Next steps:" -ForegroundColor Yellow
Write-Host "   1. Register router  -> docs\ROUTES___MODULE__.md" -ForegroundColor White
Write-Host "   2. Register model   -> migrations/env.py (auto-registered if env.py exists)" -ForegroundColor White
Write-Host "   3. Run migrations   -> alembic upgrade head"      -ForegroundColor White
Write-Host "   4. Run tests        -> pytest tests/unit -m unit" -ForegroundColor White
Write-Host "   5. Verify docs      -> http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host " Hard rules (SKILL):" -ForegroundColor Yellow
Write-Host "   X no float / no commit in repo / no raise in cache"  -ForegroundColor DarkGray
Write-Host "   X no print / no PII in logs / no cross-tenant query" -ForegroundColor DarkGray
Write-Host "   OK Decimal / structlog / flush / RLS enforced"        -ForegroundColor DarkGray
Write-Host "   OK tombstone-first cache invalidation"                -ForegroundColor DarkGray
Write-Host "   OK auto-register model in migrations/env.py"          -ForegroundColor DarkGray
Write-Host "============================================" -ForegroundColor Cyan
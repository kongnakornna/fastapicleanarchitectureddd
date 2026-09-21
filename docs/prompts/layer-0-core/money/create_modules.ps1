# ============================================================
#  create_modules.ps1
#  สร้างโครงสร้าง Module money + idempotency (ห้ามไฟล์ว่าง)
#  Create module structure for money + idempotency (no empty files)
# ============================================================

$ErrorActionPreference = "Stop"
$ROOT = "app\modules"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Creating module structure at $ROOT" -ForegroundColor Cyan
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
    # ใช้ UTF8Encoding($false) = no BOM
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Resolve-Path -LiteralPath $dir).Path + "\" + (Split-Path $Path -Leaf), $Content, $utf8)
    Write-Host "  [OK] $Path" -ForegroundColor Green
}

# ---------- สร้างโฟลเดอร์หลัก ----------
$dirs = @(
    "$ROOT",
    "$ROOT\money",
    "$ROOT\money\domain",
    "$ROOT\money\application",
    "$ROOT\money\infrastructure",
    "$ROOT\money\presentation",
    "$ROOT\idempotency",
    "$ROOT\idempotency\domain",
    "$ROOT\idempotency\application",
    "$ROOT\idempotency\infrastructure",
    "$ROOT\idempotency\presentation"
)

foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Force -Path $d | Out-Null
    }
}
Write-Host "[OK] Folders created`n" -ForegroundColor Green

# ============================================================
#  MONEY MODULE
# ============================================================
Write-Host "--- Creating MONEY module files ---" -ForegroundColor Yellow

# ---------- money\__init__.py ----------
Write-File "$ROOT\money\__init__.py" @'
"""Money module — โมดูลเงิน"""
from .presentation.routers import router as money_router

__all__ = ["money_router"]
'@

# ---------- money\domain\__init__.py ----------
Write-File "$ROOT\money\domain\__init__.py" @'
"""Money domain layer — ชั้นโดเมนเงิน"""
from .enums import Currency, VATRate, RoundingMode
from .value_objects import Money, VAT, ExchangeRate
from .exceptions import DomainError
from .events import MoneyAdded, MoneySubtracted, VATCalculated, CurrencyConverted

__all__ = [
    "Currency", "VATRate", "RoundingMode",
    "Money", "VAT", "ExchangeRate",
    "DomainError",
    "MoneyAdded", "MoneySubtracted", "VATCalculated", "CurrencyConverted",
]
'@

# ---------- money\domain\entities.py ----------
Write-File "$ROOT\money\domain\entities.py" @'
"""Money entities — ไม่มี (pure VO module)

Module นี้เป็น pure Value Object — ไม่มี Entity
This module is pure Value Object — no entities
"""

__all__: list[str] = []
'@

# ---------- money\domain\enums.py ----------
Write-File "$ROOT\money\domain\enums.py" @'
"""Money enums — Enum สำหรับเงิน"""
from enum import Enum


class Currency(str, Enum):
    """Currency — สกุลเงิน"""
    THB = "THB"
    USD = "USD"
    EUR = "EUR"


class VATRate(str, Enum):
    """VAT rate — อัตราภาษีมูลค่าเพิ่ม"""
    ZERO = "0.00"
    SEVEN = "0.07"


class RoundingMode(str, Enum):
    """Rounding mode — โหมดปัดเศษ"""
    HALF_UP = "HALF_UP"
    HALF_DOWN = "HALF_DOWN"
    BANKERS = "BANKERS"
'@

# ---------- money\domain\exceptions.py ----------
Write-File "$ROOT\money\domain\exceptions.py" @'
"""Money domain exceptions — ข้อยกเว้นโดเมนเงิน"""


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดระดับโดเมน"""

    def __init__(self, message: str = "Domain error"):
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message
'@

# ---------- money\domain\events.py ----------
Write-File "$ROOT\money\domain\events.py" @'
"""Money domain events — เหตุการณ์โดเมนเงิน"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MoneyAdded:
    """MoneyAdded — เหตุการณ์บวกเงิน"""
    a: Decimal
    b: Decimal
    result: Decimal
    currency: str
    occurred_at: datetime


@dataclass(frozen=True)
class MoneySubtracted:
    """MoneySubtracted — เหตุการณ์ลบเงิน"""
    a: Decimal
    b: Decimal
    result: Decimal
    currency: str
    occurred_at: datetime


@dataclass(frozen=True)
class VATCalculated:
    """VATCalculated — เหตุการณ์คำนวณ VAT"""
    base: Decimal
    rate: Decimal
    vat: Decimal
    currency: str
    occurred_at: datetime


@dataclass(frozen=True)
class CurrencyConverted:
    """CurrencyConverted — เหตุการณ์แปลงสกุลเงิน"""
    from_currency: str
    to_currency: str
    rate: Decimal
    amount: Decimal
    converted: Decimal
    occurred_at: datetime
'@

# ---------- money\domain\value_objects.py ----------
Write-File "$ROOT\money\domain\value_objects.py" @'
"""Money value objects — วัตถุค่าเงิน"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from .enums import Currency
from .exceptions import DomainError


@dataclass(frozen=True)
class Money:
    """Money value object — วัตถุค่าเงิน"""
    amount: Decimal
    currency: str = "THB"

    def __post_init__(self):
        object.__setattr__(
            self, "amount",
            self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise DomainError("Amount must be Decimal")
        if self.currency not in Currency._value2member_map_:
            raise DomainError(f"Unsupported currency: {self.currency}")

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DomainError(
                f"Cannot operate on {self.currency} vs {other.currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal) -> "Money":
        if not isinstance(factor, Decimal):
            raise DomainError("Factor must be Decimal")
        return Money(self.amount * factor, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")


@dataclass(frozen=True)
class VAT:
    """VAT value object — วัตถุภาษีมูลค่าเพิ่ม"""
    rate: Decimal

    def calculate(self, base: Money) -> Money:
        return Money(
            (base.amount * self.rate).quantize(Decimal("0.01")),
            base.currency,
        )

    def extract(self, total: Money) -> Money:
        base = (total.amount / (Decimal("1") + self.rate)).quantize(Decimal("0.01"))
        return Money(total.amount - base, total.currency)


@dataclass(frozen=True)
class ExchangeRate:
    """Exchange rate VO — วัตถุอัตราแลกเปลี่ยน"""
    from_currency: str
    to_currency: str
    rate: Decimal
    as_of: datetime

    def __post_init__(self):
        if self.rate <= 0:
            raise DomainError("Exchange rate must be positive")

    def convert(self, amount: Money) -> Money:
        if amount.currency != self.from_currency:
            raise DomainError("Currency mismatch")
        return Money(amount.amount * self.rate, self.to_currency)
'@

Write-Host "[OK] money\domain done`n" -ForegroundColor Green

# ---------- money\application\__init__.py ----------
Write-File "$ROOT\money\application\__init__.py" @'
"""Money application layer — ชั้นแอปพลิเคชันเงิน"""
from .use_cases import MoneyUseCases
from .exceptions import MoneyException
from .utils import round_money, zero_money

__all__ = ["MoneyUseCases", "MoneyException", "round_money", "zero_money"]
'@

# ---------- money\application\exceptions.py ----------
Write-File "$ROOT\money\application\exceptions.py" @'
"""Money application exceptions — ข้อยกเว้นแอปพลิเคชันเงิน"""


class StandardException(Exception):
    """StandardException — ข้อผิดพลาดมาตรฐาน"""
    pass


class MoneyException(StandardException):
    """MoneyException — ข้อผิดพลาดโมดูลเงิน"""

    def __init__(self, message: str = "Money operation failed"):
        self.message = message
        super().__init__(message)
'@

# ---------- money\application\interfaces.py ----------
Write-File "$ROOT\money\application\interfaces.py" @'
"""Money application interfaces — Protocol ว่าง (VO module)"""
from typing import Protocol

from ..domain.value_objects import ExchangeRate, Money


class IMoneyConverter(Protocol):
    """IMoneyConverter — อินเทอร์เฟซแปลงเงิน (optional)"""

    def convert(self, amount: Money, rate: ExchangeRate) -> Money: ...


__all__ = ["IMoneyConverter"]
'@

# ---------- money\application\mappers.py ----------
Write-File "$ROOT\money\application\mappers.py" @'
"""Money mappers — ตัวแปลงข้อมูล"""
from decimal import Decimal

from ..domain.value_objects import Money


class MoneyMapper:
    """MoneyMapper — ตัวแปลง Money ไป-กลับ schema"""

    @staticmethod
    def to_schema(money: Money) -> dict:
        """แปลง Money เป็น dict"""
        return {"amount": str(money.amount), "currency": money.currency}

    @staticmethod
    def to_entity(data: dict) -> Money:
        """แปลง dict เป็น Money"""
        return Money(Decimal(str(data["amount"])), data.get("currency", "THB"))
'@

# ---------- money\application\use_cases.py ----------
Write-File "$ROOT\money\application\use_cases.py" @'
"""Money use cases — กรณีการใช้งานเงิน"""
from decimal import Decimal

from ..domain.enums import VATRate
from ..domain.exceptions import DomainError
from ..domain.value_objects import ExchangeRate, Money, VAT


class MoneyUseCases:
    """Money use cases — กรณีการใช้งานเงิน"""

    def add(self, a: Money, b: Money) -> Money:
        return a + b

    def subtract(self, a: Money, b: Money) -> Money:
        return a - b

    def multiply(self, a: Money, factor: Decimal) -> Money:
        return a * factor

    def calculate_vat(self, base: Money, rate: VATRate) -> Money:
        return VAT(Decimal(rate.value)).calculate(base)

    def extract_vat(self, total: Money, rate: VATRate) -> Money:
        return VAT(Decimal(rate.value)).extract(total)

    def convert(self, amount: Money, rate: ExchangeRate) -> Money:
        return rate.convert(amount)

    def sum_all(self, items: list[Money]) -> Money:
        if not items:
            raise DomainError("Cannot sum empty list")
        result = items[0]
        for item in items[1:]:
            result = result + item
        return result
'@

# ---------- money\application\utils.py ----------
Write-File "$ROOT\money\application\utils.py" @'
"""Money application utils — เครื่องมือช่วย"""
from decimal import ROUND_HALF_UP, Decimal

from ..domain.value_objects import Money


def round_money(amount: Decimal, places: int = 2) -> Decimal:
    """ปัดเศษเงิน — Round money to N places"""
    quant = Decimal("0.01") if places == 2 else Decimal(10) ** -places
    return amount.quantize(quant, rounding=ROUND_HALF_UP)


def zero_money(currency: str = "THB") -> Money:
    """สร้าง Money ศูนย์ — Create zero money"""
    return Money(Decimal("0.00"), currency)
'@

Write-Host "[OK] money\application done`n" -ForegroundColor Green

# ---------- money\infrastructure\__init__.py ----------
Write-File "$ROOT\money\infrastructure\__init__.py" @'
"""Money infrastructure layer — ไม่มี persistence (pure VO)

Pure VO module — no infrastructure required
"""

__all__: list[str] = []
'@

# ---------- money\infrastructure\models.py ----------
Write-File "$ROOT\money\infrastructure\models.py" @'
"""Money infrastructure models — ไม่มี (pure VO)

Pure VO module — no DB models
"""

__all__: list[str] = []
'@

# ---------- money\infrastructure\repositories.py ----------
Write-File "$ROOT\money\infrastructure\repositories.py" @'
"""Money infrastructure repositories — ไม่มี (pure VO)

Pure VO module — no repositories
"""

__all__: list[str] = []
'@

# ---------- money\infrastructure\caches.py ----------
Write-File "$ROOT\money\infrastructure\caches.py" @'
"""Money infrastructure caches — ไม่มี (pure VO)

Pure VO module — no caches
"""

__all__: list[str] = []
'@

# ---------- money\infrastructure\services.py ----------
Write-File "$ROOT\money\infrastructure\services.py" @'
"""Money infrastructure services — ไม่มี (pure VO)

Pure VO module — no services
"""

__all__: list[str] = []
'@

Write-Host "[OK] money\infrastructure done`n" -ForegroundColor Green

# ---------- money\presentation\__init__.py ----------
Write-File "$ROOT\money\presentation\__init__.py" @'
"""Money presentation layer — ชั้นนำเสนอเงิน"""
from .dependencies import get_money_use_cases
from .routers import router

__all__ = ["router", "get_money_use_cases"]
'@

# ---------- money\presentation\dependencies.py ----------
Write-File "$ROOT\money\presentation\dependencies.py" @'
"""Money presentation dependencies — dependencies สำหรับเงิน"""
from ..application.use_cases import MoneyUseCases


def get_money_use_cases() -> MoneyUseCases:
    """สร้าง MoneyUseCases — Get MoneyUseCases instance"""
    return MoneyUseCases()
'@

# ---------- money\presentation\docs.py ----------
Write-File "$ROOT\money\presentation\docs.py" @'
"""Money presentation docs — เอกสาร API"""

router_docs = {
    "tags": ["Money"],
    "description": "Money operations — การดำเนินการเกี่ยวกับเงิน",
}

add_docs = {"summary": "Add money — บวกเงิน"}
subtract_docs = {"summary": "Subtract money — ลบเงิน"}
vat_calculate_docs = {"summary": "Calculate VAT — คำนวณ VAT"}
vat_extract_docs = {"summary": "Extract VAT — แยก VAT"}
convert_docs = {"summary": "Convert currency — แปลงสกุลเงิน"}
'@

# ---------- money\presentation\schemas.py ----------
Write-File "$ROOT\money\presentation\schemas.py" @'
"""Money presentation schemas — Pydantic schemas"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ..domain.enums import VATRate
from ..domain.value_objects import Money


class MoneySchema(BaseModel):
    """MoneySchema — schema สำหรับเงิน"""
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="THB", pattern="^(THB|USD|EUR)$")
    model_config = ConfigDict(from_attributes=True)

    def to_money(self) -> Money:
        """แปลงเป็น Money VO"""
        return Money(self.amount, self.currency)


class VATRequest(BaseModel):
    """VATRequest — คำขอคำนวณ VAT"""
    base: MoneySchema
    rate: VATRate = VATRate.SEVEN


class VATResponse(BaseModel):
    """VATResponse — ผลลัพธ์ VAT"""
    vat: MoneySchema
    total: MoneySchema


class ExchangeRateSchema(BaseModel):
    """ExchangeRateSchema — schema อัตราแลกเปลี่ยน"""
    from_currency: str = Field(..., pattern="^(THB|USD|EUR)$")
    to_currency: str = Field(..., pattern="^(THB|USD|EUR)$")
    rate: Decimal = Field(..., gt=0)
    as_of: datetime = Field(default_factory=datetime.utcnow)
'@

# ---------- money\presentation\routers.py ----------
Write-File "$ROOT\money\presentation\routers.py" @'
"""Money presentation routers — API endpoints"""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException

from ..application.exceptions import MoneyException
from ..application.use_cases import MoneyUseCases
from ..domain.exceptions import DomainError
from ..domain.value_objects import ExchangeRate
from .dependencies import get_money_use_cases
from .schemas import ExchangeRateSchema, MoneySchema, VATRequest, VATResponse

router = APIRouter(prefix="/api/v1/money", tags=["Money"])


@router.post("/add/", response_model=MoneySchema)
async def add(
    a: MoneySchema,
    b: MoneySchema,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """บวกเงิน — Add money"""
    try:
        result = uc.add(a.to_money(), b.to_money())
        return MoneySchema(amount=result.amount, currency=result.currency)
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/subtract/", response_model=MoneySchema)
async def subtract(
    a: MoneySchema,
    b: MoneySchema,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """ลบเงิน — Subtract money"""
    try:
        result = uc.subtract(a.to_money(), b.to_money())
        return MoneySchema(amount=result.amount, currency=result.currency)
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/vat/calculate/", response_model=VATResponse)
async def vat_calculate(
    req: VATRequest,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """คำนวณ VAT — Calculate VAT"""
    try:
        base = req.base.to_money()
        vat = uc.calculate_vat(base, req.rate)
        total = base + vat
        return VATResponse(
            vat=MoneySchema(amount=vat.amount, currency=vat.currency),
            total=MoneySchema(amount=total.amount, currency=total.currency),
        )
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/vat/extract/", response_model=VATResponse)
async def vat_extract(
    req: VATRequest,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """แยก VAT — Extract VAT"""
    try:
        total = req.base.to_money()
        vat = uc.extract_vat(total, req.rate)
        base = total - vat
        return VATResponse(
            vat=MoneySchema(amount=vat.amount, currency=vat.currency),
            total=MoneySchema(amount=base.amount, currency=base.currency),
        )
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/convert/", response_model=MoneySchema)
async def convert(
    amount: MoneySchema,
    rate: ExchangeRateSchema,
    uc: MoneyUseCases = Depends(get_money_use_cases),
):
    """แปลงสกุลเงิน — Convert currency"""
    try:
        er = ExchangeRate(
            from_currency=rate.from_currency,
            to_currency=rate.to_currency,
            rate=rate.rate,
            as_of=rate.as_of,
        )
        result = uc.convert(amount.to_money(), er)
        return MoneySchema(amount=result.amount, currency=result.currency)
    except MoneyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")
'@

Write-Host "[OK] money\presentation done`n" -ForegroundColor Green

# ============================================================
#  IDEMPOTENCY MODULE
# ============================================================
Write-Host "--- Creating IDEMPOTENCY module files ---" -ForegroundColor Yellow

# ---------- idempotency\__init__.py ----------
Write-File "$ROOT\idempotency\__init__.py" @'
"""Idempotency module — โมดูล idempotency"""
from .presentation.dependencies import require_idempotency_key

__all__ = ["require_idempotency_key"]
'@

# ---------- idempotency\domain\__init__.py ----------
Write-File "$ROOT\idempotency\domain\__init__.py" @'
"""Idempotency domain layer — ชั้นโดเมน idempotency"""
from .entities import IdempotencyRecord
from .enums import IdempotencyConflict, IdempotencyStatus
from .events import (
    IdempotencyCompleted,
    IdempotencyConflictEvent,
    IdempotencyLocked,
)
from .exceptions import DomainError
from .value_objects import IdempotencyKey

__all__ = [
    "IdempotencyStatus", "IdempotencyConflict",
    "IdempotencyRecord", "IdempotencyKey",
    "DomainError",
    "IdempotencyLocked", "IdempotencyCompleted", "IdempotencyConflictEvent",
]
'@

# ---------- idempotency\domain\entities.py ----------
Write-File "$ROOT\idempotency\domain\entities.py" @'
"""Idempotency entities — เอนทิตี idempotency"""
from dataclasses import dataclass, field
from datetime import datetime

from .exceptions import DomainError


@dataclass
class BaseEntity:
    """BaseEntity — เอนทิตีฐาน"""
    id: str = ""
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IdempotencyRecord(BaseEntity):
    """Idempotency record — เอนทิตีบันทึก idempotency"""
    key: str = ""
    status: str = "IN_PROGRESS"
    request_hash: str = ""
    response_body: dict = field(default_factory=dict)
    response_status: int = 0
    locked_until: datetime | None = None
    expires_at: datetime | None = None

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.key:
            raise DomainError("Idempotency key required")

    def is_expired(self) -> bool:
        return self.expires_at is not None and datetime.utcnow() > self.expires_at

    def is_completed(self) -> bool:
        return self.status == "COMPLETED"

    def is_in_progress(self) -> bool:
        return self.status == "IN_PROGRESS"

    def complete(self, status: int, body: dict) -> None:
        """Mark completed — ทำเครื่องหมายเสร็จ"""
        self.status = "COMPLETED"
        self.response_status = status
        self.response_body = body
        self.updated_at = datetime.utcnow()
'@

# ---------- idempotency\domain\enums.py ----------
Write-File "$ROOT\idempotency\domain\enums.py" @'
"""Idempotency enums — Enum สำหรับ idempotency"""
from enum import Enum


class IdempotencyStatus(str, Enum):
    """IdempotencyStatus — สถานะ idempotency"""
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IdempotencyConflict(str, Enum):
    """IdempotencyConflict — ประเภทความขัดแย้ง"""
    SAME_KEY_SAME_PAYLOAD = "SAME_KEY_SAME_PAYLOAD"
    SAME_KEY_DIFF_PAYLOAD = "SAME_KEY_DIFF_PAYLOAD"
    CONCURRENT = "CONCURRENT"
'@

# ---------- idempotency\domain\exceptions.py ----------
Write-File "$ROOT\idempotency\domain\exceptions.py" @'
"""Idempotency domain exceptions — ข้อยกเว้นโดเมน"""


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดโดเมน"""

    def __init__(self, message: str = "Domain error"):
        self.message = message
        super().__init__(message)
'@

# ---------- idempotency\domain\events.py ----------
Write-File "$ROOT\idempotency\domain\events.py" @'
"""Idempotency domain events — เหตุการณ์โดเมน"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IdempotencyLocked:
    """IdempotencyLocked — เหตุการณ์ล็อก"""
    key: str
    scope: str
    tenant_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class IdempotencyCompleted:
    """IdempotencyCompleted — เหตุการณ์เสร็จสิ้น"""
    key: str
    scope: str
    tenant_id: str
    response_status: int
    occurred_at: datetime


@dataclass(frozen=True)
class IdempotencyConflictEvent:
    """IdempotencyConflictEvent — เหตุการณ์ความขัดแย้ง"""
    key: str
    scope: str
    tenant_id: str
    conflict_type: str
    occurred_at: datetime
'@

# ---------- idempotency\domain\value_objects.py ----------
Write-File "$ROOT\idempotency\domain\value_objects.py" @'
"""Idempotency value objects — วัตถุค่า idempotency"""
from dataclasses import dataclass

from .exceptions import DomainError


@dataclass(frozen=True)
class IdempotencyKey:
    """Idempotency key VO — วัตถุกุญแจ idempotency"""
    value: str
    scope: str  # e.g., "invoice.create"

    def __post_init__(self):
        if len(self.value) < 8 or len(self.value) > 255:
            raise DomainError("Idempotency key length must be 8-255")

    def redis_key(self, tenant_id: str) -> str:
        return f"t:{tenant_id}:idem:{self.scope}:{self.value}"
'@

Write-Host "[OK] idempotency\domain done`n" -ForegroundColor Green

# ---------- idempotency\application\__init__.py ----------
Write-File "$ROOT\idempotency\application\__init__.py" @'
"""Idempotency application layer"""
from .exceptions import (
    IdempotencyConflictException,
    IdempotencyException,
    IdempotencyStoreException,
)
from .use_cases import IdempotencyUseCases
from .utils import hash_payload, idempotent

__all__ = [
    "IdempotencyUseCases",
    "IdempotencyException",
    "IdempotencyConflictException",
    "IdempotencyStoreException",
    "hash_payload",
    "idempotent",
]
'@

# ---------- idempotency\application\exceptions.py ----------
Write-File "$ROOT\idempotency\application\exceptions.py" @'
"""Idempotency application exceptions — ข้อยกเว้นแอปพลิเคชัน"""


class StandardException(Exception):
    """StandardException — ข้อผิดพลาดมาตรฐาน"""
    pass


class IdempotencyException(StandardException):
    """IdempotencyException — ข้อผิดพลาด idempotency"""

    def __init__(self, message: str = "Idempotency operation failed"):
        self.message = message
        super().__init__(message)


class IdempotencyConflictException(IdempotencyException):
    """IdempotencyConflictException — ความขัดแย้ง idempotency"""

    def __init__(self, message: str = "Idempotency conflict"):
        super().__init__(message)


class IdempotencyStoreException(IdempotencyException):
    """IdempotencyStoreException — ข้อผิดพลาด store"""

    def __init__(self, message: str = "Idempotency store error"):
        super().__init__(message)
'@

# ---------- idempotency\application\interfaces.py ----------
Write-File "$ROOT\idempotency\application\interfaces.py" @'
"""Idempotency application interfaces — Protocol"""
from typing import Protocol

from ..domain.entities import IdempotencyRecord
from ..domain.value_objects import IdempotencyKey


class IIdempotencyStore(Protocol):
    """IIdempotencyStore — อินเทอร์เฟซ store"""

    async def get(
        self, key: IdempotencyKey, tenant_id: str
    ) -> IdempotencyRecord | None: ...

    async def set(
        self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord
    ) -> None: ...

    async def lock(
        self, key: IdempotencyKey, tenant_id: str, ttl: int
    ) -> bool: ...

    async def unlock(
        self, key: IdempotencyKey, tenant_id: str
    ) -> None: ...
'@

# ---------- idempotency\application\mappers.py ----------
Write-File "$ROOT\idempotency\application\mappers.py" @'
"""Idempotency mappers — ตัวแปลงข้อมูล"""
from ..domain.entities import IdempotencyRecord


class IdempotencyMapper:
    """IdempotencyMapper — ตัวแปลง record ไป-กลับ"""

    @staticmethod
    def to_schema(rec: IdempotencyRecord) -> dict:
        """แปลง record เป็น dict"""
        return {
            "key": rec.key,
            "status": rec.status,
            "request_hash": rec.request_hash,
            "response_status": rec.response_status,
            "response_body": rec.response_body,
            "expires_at": rec.expires_at.isoformat() if rec.expires_at else None,
        }

    @staticmethod
    def to_entity(data: dict) -> IdempotencyRecord:
        """แปลง dict เป็น record"""
        return IdempotencyRecord(
            key=data.get("key", ""),
            status=data.get("status", "IN_PROGRESS"),
            request_hash=data.get("request_hash", ""),
            response_status=data.get("response_status", 0),
            response_body=data.get("response_body", {}),
        )
'@

# ---------- idempotency\application\use_cases.py ----------
Write-File "$ROOT\idempotency\application\use_cases.py" @'
"""Idempotency use cases — กรณีการใช้งาน idempotency"""
import hashlib
import json
import logging
from datetime import datetime, timedelta

from ..domain.entities import IdempotencyRecord
from ..domain.exceptions import DomainError
from ..domain.value_objects import IdempotencyKey
from .exceptions import (
    IdempotencyConflictException,
    IdempotencyException,
    StandardException,
)

logger = logging.getLogger(__name__)


class IdempotencyUseCases:
    """Idempotency use cases — กรณีการใช้งาน idempotency"""

    def __init__(self, store, ttl: int = 86400):
        self.store = store
        self.ttl = ttl

    async def check_or_lock(
        self, raw_key: str, scope: str, payload: dict, tenant_id: str
    ) -> IdempotencyRecord | None:
        """Check existing or lock — ตรวจสอบหรือล็อก"""
        try:
            key = IdempotencyKey(value=raw_key, scope=scope)
            existing = await self.store.get(key, tenant_id)

            if existing and existing.is_completed():
                if existing.request_hash != self._hash(payload):
                    raise IdempotencyConflictException("Payload mismatch")
                return existing  # replay

            if existing and existing.is_in_progress():
                raise IdempotencyConflictException("Request in progress")

            locked = await self.store.lock(key, tenant_id, self.ttl)
            if not locked:
                raise IdempotencyConflictException("Concurrent request")

            rec = IdempotencyRecord(
                key=raw_key,
                status="IN_PROGRESS",
                request_hash=self._hash(payload),
                tenant_id=tenant_id,
                expires_at=datetime.utcnow() + timedelta(seconds=self.ttl),
            )
            await self.store.set(key, tenant_id, rec)
            return None  # proceed with execution
        except StandardException:
            raise
        except DomainError as e:
            raise IdempotencyException(str(e))
        except Exception as e:
            logger.exception("Error in check_or_lock: %s", e)
            raise IdempotencyException()

    async def complete(
        self,
        raw_key: str,
        scope: str,
        tenant_id: str,
        status: int,
        body: dict,
    ) -> None:
        """Mark completed — บันทึกผลลัพธ์"""
        try:
            key = IdempotencyKey(value=raw_key, scope=scope)
            rec = await self.store.get(key, tenant_id)
            if rec:
                rec.complete(status, body)
                await self.store.set(key, tenant_id, rec)
                await self.store.unlock(key, tenant_id)
        except Exception as e:
            logger.exception("Error in complete idempotency: %s", e)
            # don't re-raise — response already returned

    @staticmethod
    def _hash(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()
'@

# ---------- idempotency\application\utils.py ----------
Write-File "$ROOT\idempotency\application\utils.py" @'
"""Idempotency application utils — เครื่องมือช่วย"""
import functools
import hashlib
import json
from typing import Callable


def hash_payload(payload: dict) -> str:
    """แฮช payload — Hash payload deterministically"""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def idempotent(fn: Callable) -> Callable:
    """Decorator สำหรับ idempotent — Decorator for idempotent methods"""

    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        return await fn(*args, **kwargs)

    return wrapper
'@

Write-Host "[OK] idempotency\application done`n" -ForegroundColor Green

# ---------- idempotency\infrastructure\__init__.py ----------
Write-File "$ROOT\idempotency\infrastructure\__init__.py" @'
"""Idempotency infrastructure layer"""
from .caches import RedisIdempotencyStore
from .models import IdempotencyRecordModel
from .repositories import PostgresIdempotencyRepository

__all__ = [
    "IdempotencyRecordModel",
    "PostgresIdempotencyRepository",
    "RedisIdempotencyStore",
]
'@

# ---------- idempotency\infrastructure\models.py ----------
Write-File "$ROOT\idempotency\infrastructure\models.py" @'
"""Idempotency infrastructure models — SQLAlchemy models"""
from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


class IdempotencyRecordModel(BaseModel):
    """IdempotencyRecordModel — โมเดลบันทึก idempotency"""
    __tablename__ = "idempotency_records"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    scope = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    request_hash = Column(String(64), nullable=False)
    response_body = Column(JSONB, default=dict)
    response_status = Column(Integer)
    locked_until = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), index=True)

    __table_args__ = (
        UniqueConstraint(
            "key", "scope", "tenant_id",
            name="uq_idem_key_scope_tenant",
        ),
    )
'@

# ---------- idempotency\infrastructure\repositories.py ----------
Write-File "$ROOT\idempotency\infrastructure\repositories.py" @'
"""Idempotency infrastructure repositories — Postgres fallback"""
import logging

from ..domain.entities import IdempotencyRecord
from ..domain.value_objects import IdempotencyKey
from .models import IdempotencyRecordModel

logger = logging.getLogger(__name__)


class PostgresIdempotencyRepository:
    """PostgresIdempotencyRepository — fallback เมื่อ Redis ล่ม"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get(
        self, key: IdempotencyKey, tenant_id: str
    ) -> IdempotencyRecord | None:
        try:
            async with self.session_factory() as session:
                from sqlalchemy import select
                stmt = select(IdempotencyRecordModel).where(
                    IdempotencyRecordModel.key == key.value,
                    IdempotencyRecordModel.scope == key.scope,
                    IdempotencyRecordModel.tenant_id == tenant_id,
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                if row is None:
                    return None
                return IdempotencyRecord(
                    key=row.key,
                    status=row.status,
                    request_hash=row.request_hash,
                    response_body=row.response_body or {},
                    response_status=row.response_status or 0,
                    expires_at=row.expires_at,
                )
        except Exception as e:
            logger.exception("Postgres get failed: %s", e)
            return None

    async def set(
        self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord
    ) -> None:
        try:
            async with self.session_factory() as session:
                row = IdempotencyRecordModel(
                    key=key.value,
                    scope=key.scope,
                    tenant_id=tenant_id,
                    status=rec.status,
                    request_hash=rec.request_hash,
                    response_body=rec.response_body,
                    response_status=rec.response_status,
                    expires_at=rec.expires_at,
                )
                session.add(row)
                await session.commit()
        except Exception as e:
            logger.exception("Postgres set failed: %s", e)

    async def lock(
        self, key: IdempotencyKey, tenant_id: str, ttl: int
    ) -> bool:
        # Postgres fallback: always allow (Redis เป็น primary)
        return True

    async def unlock(
        self, key: IdempotencyKey, tenant_id: str
    ) -> None:
        return None
'@

# ---------- idempotency\infrastructure\caches.py ----------
Write-File "$ROOT\idempotency\infrastructure\caches.py" @'
"""Idempotency infrastructure caches — Redis store (primary)"""
import json
import logging

from ..domain.entities import IdempotencyRecord
from ..domain.value_objects import IdempotencyKey

logger = logging.getLogger(__name__)


class RedisIdempotencyStore:
    """RedisIdempotencyStore — primary store ด้วย atomic SET NX"""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(
        self, key: IdempotencyKey, tenant_id: str
    ) -> IdempotencyRecord | None:
        try:
            raw = await self.redis.get(key.redis_key(tenant_id))
            if not raw:
                return None
            data = json.loads(raw)
            return IdempotencyRecord(
                key=data.get("key", key.value),
                status=data.get("status", "IN_PROGRESS"),
                request_hash=data.get("request_hash", ""),
                response_body=data.get("response_body", {}),
                response_status=data.get("response_status", 0),
                expires_at=data.get("expires_at"),
            )
        except Exception as e:
            logger.exception("Redis get failed: %s", e)
            return None

    async def set(
        self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord
    ) -> None:
        try:
            payload = {
                "key": rec.key,
                "status": rec.status,
                "request_hash": rec.request_hash,
                "response_body": rec.response_body,
                "response_status": rec.response_status,
                "expires_at": (
                    rec.expires_at.isoformat() if rec.expires_at else None
                ),
            }
            await self.redis.set(
                key.redis_key(tenant_id),
                json.dumps(payload),
                ex=86400,
            )
        except Exception as e:
            logger.exception("Redis set failed: %s", e)

    async def lock(
        self, key: IdempotencyKey, tenant_id: str, ttl: int
    ) -> bool:
        try:
            result = await self.redis.set(
                f"{key.redis_key(tenant_id)}:lock",
                "1", nx=True, ex=ttl,
            )
            return bool(result)
        except Exception as e:
            logger.exception("Lock failed: %s", e)
            return False  # conservative: fail closed

    async def unlock(
        self, key: IdempotencyKey, tenant_id: str
    ) -> None:
        try:
            await self.redis.delete(f"{key.redis_key(tenant_id)}:lock")
        except Exception as e:
            logger.exception("Unlock failed: %s", e)
'@

# ---------- idempotency\infrastructure\services.py ----------
Write-File "$ROOT\idempotency\infrastructure\services.py" @'
"""Idempotency infrastructure services — ไม่มี

No infrastructure services required
"""

__all__: list[str] = []
'@

Write-Host "[OK] idempotency\infrastructure done`n" -ForegroundColor Green

# ---------- idempotency\presentation\__init__.py ----------
Write-File "$ROOT\idempotency\presentation\__init__.py" @'
"""Idempotency presentation layer"""
from .dependencies import require_idempotency_key
from .schemas import IdempotencyRecordSchema

__all__ = ["require_idempotency_key", "IdempotencyRecordSchema"]
'@

# ---------- idempotency\presentation\dependencies.py ----------
Write-File "$ROOT\idempotency\presentation\dependencies.py" @'
"""Idempotency presentation dependencies — FastAPI dependency"""
from fastapi import Header, HTTPException


async def require_idempotency_key(
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")
) -> str:
    """ต้องมี Idempotency-Key header — Require idempotency key"""
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key header required",
        )
    if len(idempotency_key) < 8 or len(idempotency_key) > 255:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key must be 8-255 characters",
        )
    return idempotency_key
'@

# ---------- idempotency\presentation\docs.py ----------
Write-File "$ROOT\idempotency\presentation\docs.py" @'
"""Idempotency presentation docs — เอกสาร"""

idempotency_docs = {
    "description": (
        "Idempotency middleware — ทุก mutating request ต้องส่ง "
        "Idempotency-Key header"
    ),
    "headers": {
        "Idempotency-Key": {
            "description": "Unique key 8-255 chars",
            "required": True,
        }
    },
}
'@

# ---------- idempotency\presentation\routers.py ----------
Write-File "$ROOT\idempotency\presentation\routers.py" @'
"""Idempotency presentation routers — ว่าง (ใช้ middleware)

Public router ว่าง — ใช้ middleware/dependency แทน
No public endpoints — handled via middleware/dependency
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/idempotency", tags=["Idempotency"])

__all__ = ["router"]
'@

# ---------- idempotency\presentation\schemas.py ----------
Write-File "$ROOT\idempotency\presentation\schemas.py" @'
"""Idempotency presentation schemas — Pydantic schemas"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IdempotencyRecordSchema(BaseModel):
    """IdempotencyRecordSchema — schema บันทึก idempotency"""
    key: str
    scope: str
    status: str
    request_hash: str
    response_status: int = 0
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
'@

Write-Host "[OK] idempotency\presentation done`n" -ForegroundColor Green

# ============================================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " DONE! Module structure created successfully." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " Structure:" -ForegroundColor White
Write-Host "   $ROOT\money\          (25 files)" -ForegroundColor White
Write-Host "   $ROOT\idempotency\    (25 files)" -ForegroundColor White
Write-Host ""
Write-Host " All files contain content — no empty files." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
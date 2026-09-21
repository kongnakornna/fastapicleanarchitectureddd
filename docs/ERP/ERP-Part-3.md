# 📕 PART 3 — Core Infrastructure Modules

> **Layer 0: Cross-cutting** — 6 modules ที่ทุก module อื่นต้องพึ่ง
> `money` · `audit` · `idempotency` · `config` · `events` · `tenant_context`

---

## 3.0 ภาพรวม Layer 0

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 0: CORE INFRASTRUCTURE                            │
│                                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                     │
│   │    money     │  │    audit     │  │ idempotency  │                     │
│   │  (Decimal +  │  │ (append-only │  │  (retry-safe │                     │
│   │   VAT calc)  │  │   log)       │  │   writes)    │                     │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                     │
│          │                 │                 │                             │
│   ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐                     │
│   │    config    │  │    events    │  │tenant_context│                     │
│   │ (VAT/waste/  │  │ (domain bus  │  │ (multi-      │                     │
│   │  pricing)    │  │  + outbox)   │  │  company)    │                     │
│   └──────────────┘  └──────────────┘  └──────────────┘                     │
│                                                                              │
│   ทุก module ใช้ 6 ตัวนี้ — ห้าม bypass                                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

**ทำไมต้องแยก Layer 0?**
- เป็น **shared kernel** ที่ทุก module ใช้
- ต้อง **stable** — เปลี่ยนทีกระทบทั้งระบบ
- ไม่มี business logic เฉพาะทาง — เป็น primitive เท่านั้น
- ต้อง **test หนัก** เพราะ bug ที่นี่ลามทั้งระบบ

---

# 🧩 Module 3.1 — `money`

## 3.1.1 Purpose & Scope

**Purpose:** ให้ primitive สำหรับคำนวณเงินที่แม่นยำระดับสตางค์ รองรับ VAT ไทย และ multi-currency

**Scope:**
- ✅ Money value object (amount + currency)
- ✅ Thai VAT calculator (7%, 0%, exempt)
- ✅ Rounding rules (ROUND_HALF_UP)
- ✅ Currency conversion (optional)
- ❌ ไม่เก็บ state — pure functions/objects
- ❌ ไม่แตะ DB
- ❌ ไม่มี business rule เฉพาะบริษัท (อยู่ใน `config`)

## 3.1.2 Domain Model

```python
# app/core/money/domain/value_objects.py

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Self


class Currency(str, Enum):
    THB = "THB"
    USD = "USD"
    EUR = "EUR"


QUANTUM = Decimal("0.01")  # สตางค์


@dataclass(frozen=True, slots=True)
class Money:
    """
    Immutable money value object.

    Invariants:
    - amount quantize เป็น 2 ตำแหน่งเสมอ (สตางค์)
    - currency ต้องเป็น Currency enum
    - ห้ามใช้ float เด็ดขาด
    - การบวก/ลบต้อง currency เดียวกัน
    """
    amount: Decimal
    currency: Currency = Currency.THB

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError(
                f"Money.amount must be Decimal, got {type(self.amount).__name__}. "
                "ใช้ Decimal('...') หรือ Decimal(str(x)) — ห้าม float"
            )
        object.__setattr__(
            self, "amount",
            self.amount.quantize(QUANTUM, rounding=ROUND_HALF_UP),
        )

    # ---------- Arithmetic ----------

    def __add__(self, other: Self) -> Self:
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Self) -> Self:
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: Decimal | int) -> Self:
        if isinstance(factor, float):
            raise TypeError("Money * float ห้ามใช้ — ใช้ Decimal")
        return Money(self.amount * Decimal(factor), self.currency)

    def __truediv__(self, divisor: Decimal | int) -> Self:
        if isinstance(divisor, float):
            raise TypeError("Money / float ห้ามใช้ — ใช้ Decimal")
        if divisor == 0:
            raise ZeroDivisionError("Money / 0")
        return Money(self.amount / Decimal(divisor), self.currency)

    def __neg__(self) -> Self:
        return Money(-self.amount, self.currency)

    # ---------- Comparison ----------

    def __lt__(self, other: Self) -> bool:
        self._assert_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Self) -> bool:
        self._assert_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: Self) -> bool:
        self._assert_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Self) -> bool:
        self._assert_same_currency(other)
        return self.amount >= other.amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    # ---------- Helpers ----------

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_positive(self) -> bool:
        return self.amount > Decimal("0.00")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")

    @classmethod
    def zero(cls, currency: Currency = Currency.THB) -> Self:
        return cls(Decimal("0.00"), currency)

    def _assert_same_currency(self, other: Self) -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch: {self.currency.value} vs {other.currency.value}"
            )

    def __repr__(self) -> str:
        return f"Money({self.amount}, {self.currency.value})"

    def __str__(self) -> str:
        return f"{self.amount:,.2f} {self.currency.value}"
```

```python
# app/core/money/domain/vat.py

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from app.core.money.domain.value_objects import Money, Currency


class VatMode(str, Enum):
    """โหมดการคิด VAT"""
    EXCLUSIVE = "exclusive"   # ราคาไม่รวม VAT → บวกเพิ่ม
    INCLUSIVE = "inclusive"   # ราคารวม VAT แล้ว → แยกออก
    ZERO_RATED = "zero"       # 0% (ส่งออก)
    EXEMPT = "exempt"         # ยกเว้น VAT (เช่น อาหารสดบางประเภท)


@dataclass(frozen=True, slots=True)
class VatRate:
    """อัตรา VAT + โหมด"""
    rate: Decimal
    mode: VatMode

    def __post_init__(self) -> None:
        if self.rate < 0 or self.rate > 1:
            raise ValueError(f"VAT rate ต้องอยู่ระหว่าง 0-1, got {self.rate}")

    @classmethod
    def thai_standard(cls) -> "VatRate":
        return cls(rate=Decimal("0.07"), mode=VatMode.EXCLUSIVE)

    @classmethod
    def thai_inclusive(cls) -> "VatRate":
        return cls(rate=Decimal("0.07"), mode=VatMode.INCLUSIVE)

    @classmethod
    def zero_rated(cls) -> "VatRate":
        return cls(rate=Decimal("0.00"), mode=VatMode.ZERO_RATED)

    @classmethod
    def exempt(cls) -> "VatRate":
        return cls(rate=Decimal("0.00"), mode=VatMode.EXEMPT)


@dataclass(frozen=True, slots=True)
class VatBreakdown:
    """ผลการคำนวณ VAT — แยก base + vat + total ชัดเจน"""
    base: Money
    vat: Money
    total: Money

    @property
    def rate(self) -> Decimal:
        if self.base.is_zero():
            return Decimal("0")
        return (self.vat.amount / self.base.amount).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )


class VatCalculator:
    """
    คำนวณ VAT ตามโหมด
    - EXCLUSIVE: total = base + vat
    - INCLUSIVE: base = total / (1 + rate), vat = total - base
    - ZERO_RATED / EXEMPT: vat = 0, total = base
    """

    @staticmethod
    def calculate(base: Money, rate: VatRate) -> VatBreakdown:
        if rate.mode in (VatMode.ZERO_RATED, VatMode.EXEMPT):
            return VatBreakdown(
                base=base,
                vat=Money.zero(base.currency),
                total=base,
            )

        if rate.mode == VatMode.EXCLUSIVE:
            vat_amount = (base.amount * rate.rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            vat = Money(vat_amount, base.currency)
            total = base + vat
            return VatBreakdown(base=base, vat=vat, total=total)

        if rate.mode == VatMode.INCLUSIVE:
            divisor = Decimal("1") + rate.rate
            base_amount = (base.amount / divisor).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            base_ex = Money(base_amount, base.currency)
            vat = base - base_ex
            return VatBreakdown(base=base_ex, vat=vat, total=base)

        raise ValueError(f"Unknown VatMode: {rate.mode}")

    @staticmethod
    def calculate_inclusive_total(total: Money, rate: VatRate) -> VatBreakdown:
        """คำนวณจากยอดรวม VAT (ใช้กับ receipt ที่พิมพ์ total ไว้แล้ว)"""
        return VatCalculator.calculate(total, rate)
```

## 3.1.3 Domain Errors

```python
# app/core/money/domain/errors.py

class MoneyError(Exception):
    """Base error สำหรับ money"""

class CurrencyMismatchError(MoneyError):
    """Currency ไม่ตรงกัน"""

class InvalidAmountError(MoneyError):
    """Amount ผิดรูปแบบ (เช่น float)"""

class InvalidVatRateError(MoneyError):
    """VAT rate นอกช่วง 0-1"""
```

## 3.1.4 Folder Structure

```text
app/core/money/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── value_objects.py       # Money, Currency
│   ├── vat.py                 # VatRate, VatMode, VatBreakdown, VatCalculator
│   └── errors.py              # MoneyError hierarchy
├── application/
│   ├── __init__.py
│   └── utils.py               # helpers เช่น parse_money, format_money
└── tests/
    ├── test_value_objects.py
    ├── test_vat.py
    └── test_property_based.py  # hypothesis tests
```

## 3.1.5 Tests

```python
# app/core/money/tests/test_value_objects.py

import pytest
from decimal import Decimal
from app.core.money.domain.value_objects import Money, Currency


class TestMoneyConstruction:
    def test_creates_with_decimal(self):
        m = Money(Decimal("100.50"), Currency.THB)
        assert m.amount == Decimal("100.50")

    def test_rejects_float(self):
        with pytest.raises(TypeError, match="must be Decimal"):
            Money(100.50, Currency.THB)  # type: ignore

    def test_quantizes_to_2_decimals(self):
        m = Money(Decimal("100.555"), Currency.THB)
        assert m.amount == Decimal("100.56")  # ROUND_HALF_UP

    def test_immutable(self):
        m = Money(Decimal("100"), Currency.THB)
        with pytest.raises(Exception):
            m.amount = Decimal("200")  # type: ignore


class TestMoneyArithmetic:
    def test_add_same_currency(self):
        a = Money(Decimal("100"), Currency.THB)
        b = Money(Decimal("50"), Currency.THB)
        assert (a + b).amount == Decimal("150.00")

    def test_add_different_currency_raises(self):
        a = Money(Decimal("100"), Currency.THB)
        b = Money(Decimal("50"), Currency.USD)
        with pytest.raises(ValueError, match="Currency mismatch"):
            a + b

    def test_multiply_by_decimal(self):
        m = Money(Decimal("100"), Currency.THB)
        assert (m * Decimal("1.07")).amount == Decimal("107.00")

    def test_multiply_by_float_raises(self):
        m = Money(Decimal("100"), Currency.THB)
        with pytest.raises(TypeError):
            m * 1.07  # type: ignore


# app/core/money/tests/test_property_based.py

from hypothesis import given, strategies as st
from decimal import Decimal
from app.core.money.domain.value_objects import Money, Currency
from app.core.money.domain.vat import VatCalculator, VatRate


decimals = st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999999.99"),
                       places=2, allow_nan=False, allow_infinity=False)


@given(a=decimals, b=decimals, c=decimals)
def test_addition_associative(a, b, c):
    """(a + b) + c == a + (b + c)"""
    A = Money(a); B = Money(b); C = Money(c)
    assert (A + B) + C == A + (B + C)


@given(a=decimals, b=decimals)
def test_addition_commutative(a, b):
    A = Money(a); B = Money(b)
    assert A + B == B + A


@given(a=decimals)
def test_additive_identity(a):
    A = Money(a)
    assert A + Money.zero() == A


@given(base=decimals)
def test_vat_exclusive_math(base):
    """total == base + vat เสมอ"""
    rate = VatRate.thai_standard()
    bd = VatCalculator.calculate(Money(base), rate)
    assert bd.total == bd.base + bd.vat


@given(total=decimals)
def test_vat_inclusive_math(total):
    """base + vat == total เสมอ (inclusive)"""
    rate = VatRate.thai_inclusive()
    bd = VatCalculator.calculate(Money(total), rate)
    assert bd.base + bd.vat == bd.total
```

## 3.1.6 Dependencies & Consumers

```text
money ถูกใช้โดย:
├── invoice          (คำนวณยอด, VAT)
├── ledger           (post entry)
├── payment          (รับชำระ)
├── pricing          (ราคา)
├── order            (ยอดสั่ง)
├── pos              (ขายหน้าร้าน)
├── reporting        (aggregate)
├── kpi              (ยอดขาย KPI)
└── reconciliation   (เทียบยอด)

money ไม่พึ่ง module ใดเลย — เป็น pure primitive
```

## 3.1.7 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (Week 1) |
| **DoD** | ✅ Money VO ผ่าน property-based test<br>✅ VatCalculator ผ่าน test 4 โหมด<br>✅ ห้าม float (lint rule)<br>✅ ทุก module ใช้ Money แทน float/Decimal ตรง ๆ |

---

# 🧩 Module 3.2 — `audit`

## 3.2.1 Purpose & Scope

**Purpose:** บันทึกทุก action ที่แตะเงิน/สต็อก/ข้อมูลสำคัญ แบบ **append-only** (INSERT เท่านั้น) เพื่อให้ตรวจสอบย้อนหลังได้

**Scope:**
- ✅ Append-only audit log
- ✅ ก่อน/หลัง state (JSONB diff)
- ✅ Actor, action, entity, timestamp
- ✅ Query API สำหรับ auditor
- ✅ Retention policy
- ❌ ไม่ให้ UPDATE/DELETE (บังคับด้วย DB trigger)
- ❌ ไม่เก็บ sensitive data แบบ plaintext (mask)

## 3.2.2 Domain Model

```python
# app/core/audit/domain/entities.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """
    Audit entry — append-only, immutable.

    Invariants:
    - id ไม่ซ้ำ
    - occurred_at เป็น UTC
    - ต้องมี actor (user/system/service)
    - before_state/after_state เป็น dict (JSONB)
    - action ต้องมาจาก AuditAction enum
    """
    id: UUID
    company_id: UUID
    actor_id: UUID | None          # None = system
    actor_type: ActorType
    action: AuditAction
    entity_type: str               # "invoice", "ledger_entry", ...
    entity_id: UUID
    before_state: dict[str, Any] | None
    after_state: dict[str, Any] | None
    metadata: dict[str, Any]       # request_id, ip, user_agent, ...
    occurred_at: datetime

    @classmethod
    def create(
        cls,
        *,
        company_id: UUID,
        actor_id: UUID | None,
        actor_type: "ActorType",
        action: "AuditAction",
        entity_type: str,
        entity_id: UUID,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> "AuditEntry":
        return cls(
            id=uuid4(),
            company_id=company_id,
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state,
            metadata=metadata or {},
            occurred_at=occurred_at or datetime.utcnow(),
        )


from enum import Enum


class ActorType(str, Enum):
    USER = "user"
    SYSTEM = "system"
    SERVICE = "service"      # internal worker
    EXTERNAL = "external"    # webhook, API client
    AI_AGENT = "ai_agent"    # Claude Code, Codex


class AuditAction(str, Enum):
    # Money
    INVOICE_ISSUED = "invoice.issued"
    INVOICE_CANCELLED = "invoice.cancelled"
    INVOICE_AMENDED = "invoice.amended"
    LEDGER_POSTED = "ledger.posted"
    LEDGER_REVERSED = "ledger.reversed"
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_REFUNDED = "payment.refunded"

    # Goods
    STOCK_RECEIVED = "stock.received"
    STOCK_ISSUED = "stock.issued"
    STOCK_ADJUSTED = "stock.adjusted"
    STOCK_TRANSFERRED = "stock.transferred"
    LOT_CREATED = "lot.created"
    LOT_EXPIRED = "lot.expired"

    # Production
    BATCH_STARTED = "batch.started"
    BATCH_COMPLETED = "batch.completed"
    BATCH_ABORTED = "batch.aborted"
    WASTE_RECORDED = "waste.recorded"

    # Transport
    SHIPMENT_DISPATCHED = "shipment.dispatched"
    SHIPMENT_DELIVERED = "shipment.delivered"
    SHIPMENT_RETURNED = "shipment.returned"

    # Retail
    SHIFT_OPENED = "shift.opened"
    SHIFT_CLOSED = "shift.closed"
    SALE_COMPLETED = "sale.completed"
    SALE_VOIDED = "sale.voided"
    SALE_REFUNDED = "sale.refunded"

    # Config
    CONFIG_CHANGED = "config.changed"
    VAT_RATE_CHANGED = "vat_rate.changed"

    # Auth
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"
    USER_DISABLED = "user.disabled"
    PERMISSION_CHANGED = "permission.changed"
```

## 3.2.3 Application — Interfaces & Use Cases

```python
# app/core/audit/application/interfaces.py

from typing import Protocol
from uuid import UUID
from datetime import datetime

from app.core.audit.domain.entities import AuditEntry


class IAuditRepository(Protocol):
    async def append(self, entry: AuditEntry) -> None:
        """INSERT เท่านั้น — ไม่มี update/delete"""
        ...

    async def query(
        self,
        *,
        company_id: UUID,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        actor_id: UUID | None = None,
        action: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]: ...


# app/core/audit/application/use_cases.py

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.core.audit.application.interfaces import IAuditRepository
from app.core.audit.domain.entities import AuditEntry, ActorType, AuditAction


@dataclass
class RecordAuditCommand:
    company_id: UUID
    actor_id: UUID | None
    actor_type: ActorType
    action: AuditAction
    entity_type: str
    entity_id: UUID
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class RecordAuditUseCase:
    """
    ใช้โดยทุก module ที่ต้อง audit
    ควรเรียกภายใน transaction เดียวกับ business operation
    """

    def __init__(self, repo: IAuditRepository) -> None:
        self.repo = repo

    async def execute(self, cmd: RecordAuditCommand) -> AuditEntry:
        entry = AuditEntry.create(
            company_id=cmd.company_id,
            actor_id=cmd.actor_id,
            actor_type=cmd.actor_type,
            action=cmd.action,
            entity_type=cmd.entity_type,
            entity_id=cmd.entity_id,
            before_state=self._mask_sensitive(cmd.before_state),
            after_state=self._mask_sensitive(cmd.after_state),
            metadata=cmd.metadata,
        )
        await self.repo.append(entry)
        return entry

    @staticmethod
    def _mask_sensitive(state: dict[str, Any] | None) -> dict[str, Any] | None:
        if state is None:
            return None
        masked = dict(state)
        sensitive_keys = {"password", "password_hash", "token", "secret", "api_key"}
        for key in masked:
            if key.lower() in sensitive_keys:
                masked[key] = "***MASKED***"
        return masked
```

## 3.2.4 Infrastructure — Model & Repository

```python
# app/core/audit/infrastructure/models.py

from sqlalchemy import (
    Column, DateTime, Enum as SAEnum, ForeignKey, Index, String, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import Base


class AuditLogModel(Base):
    """
    Audit log — append-only
    บังคับ append-only ด้วย PostgreSQL trigger (ดู migration)
    """
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("ix_audit_company_occurred", "company_id", "occurred_at"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_actor", "actor_id", "occurred_at"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    before_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    occurred_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
```

```python
# app/core/audit/infrastructure/repositories.py

from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit.domain.entities import AuditEntry
from app.core.audit.infrastructure.models import AuditLogModel


class PostgresAuditRepository:
    """Append-only repository"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def append(self, entry: AuditEntry) -> None:
        model = AuditLogModel(
            id=entry.id,
            company_id=entry.company_id,
            actor_id=entry.actor_id,
            actor_type=entry.actor_type.value,
            action=entry.action.value,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            before_state=entry.before_state,
            after_state=entry.after_state,
            metadata_=entry.metadata,
            occurred_at=entry.occurred_at,
        )
        self.session.add(model)
        # ไม่ commit — ให้ use case เป็นคน commit ใน transaction

    async def query(
        self,
        *,
        company_id: UUID,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        actor_id: UUID | None = None,
        action: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        stmt = select(AuditLogModel).where(AuditLogModel.company_id == company_id)

        if entity_type:
            stmt = stmt.where(AuditLogModel.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(AuditLogModel.entity_id == entity_id)
        if actor_id:
            stmt = stmt.where(AuditLogModel.actor_id == actor_id)
        if action:
            stmt = stmt.where(AuditLogModel.action == action)
        if from_date:
            stmt = stmt.where(AuditLogModel.occurred_at >= from_date)
        if to_date:
            stmt = stmt.where(AuditLogModel.occurred_at <= to_date)

        stmt = stmt.order_by(AuditLogModel.occurred_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars()]

    @staticmethod
    def _to_entity(m: AuditLogModel) -> AuditEntry:
        return AuditEntry(
            id=m.id,
            company_id=m.company_id,
            actor_id=m.actor_id,
            actor_type=m.actor_type,
            action=m.action,
            entity_type=m.entity_type,
            entity_id=m.entity_id,
            before_state=m.before_state,
            after_state=m.after_state,
            metadata=m.metadata_,
            occurred_at=m.occurred_at,
        )
```

## 3.2.5 Database Schema (DDL)

```sql
-- migrations/versions/XXXX_create_audit_log.py (upgrade)

CREATE TABLE audit_log (
    id            UUID PRIMARY KEY,
    company_id    UUID NOT NULL,
    actor_id      UUID,
    actor_type    VARCHAR(20) NOT NULL,
    action        VARCHAR(50) NOT NULL,
    entity_type   VARCHAR(50) NOT NULL,
    entity_id     UUID NOT NULL,
    before_state  JSONB,
    after_state   JSONB,
    metadata      JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_audit_company_occurred ON audit_log (company_id, occurred_at DESC);
CREATE INDEX ix_audit_entity ON audit_log (entity_type, entity_id);
CREATE INDEX ix_audit_actor ON audit_log (actor_id, occurred_at DESC);
CREATE INDEX ix_audit_action ON audit_log (action, occurred_at DESC);

-- 🛡️ บังคับ append-only
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log is append-only: % ไม่ได้รับอนุญาต', TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_no_update
BEFORE UPDATE ON audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

CREATE TRIGGER trg_audit_no_delete
BEFORE DELETE ON audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

-- Retention: 7 ปี (ตามกฎหมายบัญชีไทย)
-- ใช้ partition by occurred_at (year) + pg_partman
```

## 3.2.6 Presentation — API

```python
# app/core/audit/presentation/routers.py

from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


@router.get("/entries")
async def query_audit(
    entity_type: str | None = Query(None),
    entity_id: UUID | None = Query(None),
    actor_id: UUID | None = Query(None),
    action: str | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    use_case = Depends(get_query_audit_use_case),
    current_user = Depends(authenticate_manager),
):
    """ค้นหา audit log — เฉพาะ MANAGER ขึ้นไป"""
    return await use_case.execute(...)
```

**Endpoints:**

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/audit/entries` | MANAGER | ค้นหา audit |
| GET | `/api/v1/audit/entries/{id}` | MANAGER | ดูรายละเอียด |
| GET | `/api/v1/audit/timeline/{entity_type}/{entity_id}` | USER | timeline ของ entity |

## 3.2.7 Middleware Integration

```python
# app/core/audit/middleware.py

class AuditContextMiddleware:
    """
    เก็บ request_id, ip, user_agent ลง ContextVar
    เพื่อให้ audit use case ดึงไปใส่ metadata ได้
    """
    async def __call__(self, request, call_next):
        token = audit_ctx.set({
            "request_id": request.headers.get("X-Request-ID", str(uuid4())),
            "ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
            "path": request.url.path,
            "method": request.method,
        })
        try:
            return await call_next(request)
        finally:
            audit_ctx.reset(token)
```

## 3.2.8 Folder Structure

```text
app/core/audit/
├── __init__.py
├── domain/
│   ├── entities.py            # AuditEntry, ActorType, AuditAction
│   └── errors.py
├── application/
│   ├── interfaces.py          # IAuditRepository
│   └── use_cases.py           # RecordAudit, QueryAudit
├── infrastructure/
│   ├── models.py              # AuditLogModel
│   └── repositories.py        # PostgresAuditRepository
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
├── middleware.py              # AuditContextMiddleware
└── tests/
    ├── test_entities.py
    ├── test_use_cases.py
    ├── test_repository.py
    └── test_append_only.py    # ทดสอบว่า UPDATE/DELETE ไม่ได้
```

## 3.2.9 Pattern การใช้ใน Module อื่น

```python
# ตัวอย่าง: invoice use case
class IssueInvoiceUseCase:
    def __init__(self, invoice_repo, audit: RecordAuditUseCase, uow):
        ...

    async def execute(self, cmd: IssueInvoiceCommand) -> Invoice:
        async with self.uow.transaction():
            invoice = Invoice.create(...)
            await self.invoice_repo.save(invoice)

            await self.audit.execute(RecordAuditCommand(
                company_id=cmd.company_id,
                actor_id=cmd.actor_id,
                actor_type=ActorType.USER,
                action=AuditAction.INVOICE_ISSUED,
                entity_type="invoice",
                entity_id=invoice.id,
                before_state=None,
                after_state=invoice.to_dict(),
            ))
            # commit รวมใน transaction เดียว
        return invoice
```

## 3.2.10 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (Week 1) |
| **DoD** | ✅ append-only trigger ทำงาน<br>✅ mask sensitive data<br>✅ ทุก money/goods use case เรียก RecordAudit<br>✅ query API สำหรับ auditor<br>✅ partition by year |

---

# 🧩 Module 3.3 — `idempotency`

## 3.3.1 Purpose & Scope

**Purpose:** ทำให้ endpoint ที่แตะเงิน/สต็อก **retry-safe** — ยิงซ้ำได้ผลเดียวกัน

**Scope:**
- ✅ Idempotency-Key header processing
- ✅ Store request hash + response snapshot
- ✅ Redis (fast) + PostgreSQL (permanent)
- ✅ TTL policy แยกตาม action
- ✅ Conflict detection (same key, different request)
- ❌ ไม่ทำ retry — ทำ dedup เท่านั้น

## 3.3.2 Domain Model

```python
# app/core/idempotency/domain/entities.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID


class IdempotencyStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class IdempotencyScope(str, Enum):
    """อายุของ key ตามประเภท action"""
    SHORT = "short"      # 24 ชั่วโมง — query, preview
    MEDIUM = "medium"    # 7 วัน — general writes
    LONG = "long"        # 90 วัน — stock adjustment
    PERMANENT = "perm"   # ตลอด — invoice issuance, payment


SCOPE_TTL: dict[IdempotencyScope, timedelta | None] = {
    IdempotencyScope.SHORT: timedelta(hours=24),
    IdempotencyScope.MEDIUM: timedelta(days=7),
    IdempotencyScope.LONG: timedelta(days=90),
    IdempotencyScope.PERMANENT: None,
}


@dataclass
class IdempotencyRecord:
    """
    บันทึก idempotency key

    Invariants:
    - (company_id, key, endpoint) unique
    - request_hash ต้องตรงกัน ถ้า key ซ้ำแต่ body ต่าง → conflict
    - response_snapshot เก็บไว้ replay
    """
    id: UUID
    company_id: UUID
    key: str
    endpoint: str
    method: str
    request_hash: str
    status: IdempotencyStatus
    response_status: int | None
    response_body: dict | None
    scope: IdempotencyScope
    created_at: datetime
    completed_at: datetime | None
    expires_at: datetime | None


class IdempotencyConflictError(Exception):
    """Key ซ้ำ แต่ request ต่าง"""

class IdempotencyInProgressError(Exception):
    """Key กำลังประมวลผลอยู่ — ให้ client retry"""
```

## 3.3.3 Application — Use Case

```python
# app/core/idempotency/application/use_cases.py

import hashlib
import json
from dataclasses import dataclass
from typing import Callable, Awaitable, Any
from uuid import UUID

from app.core.idempotency.domain.entities import (
    IdempotencyRecord, IdempotencyStatus, IdempotencyScope,
    SCOPE_TTL, IdempotencyConflictError, IdempotencyInProgressError,
)
from app.core.idempotency.application.interfaces import IIdempotencyRepository


def compute_request_hash(body: Any) -> str:
    """canonical JSON hash"""
    canonical = json.dumps(body, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class IdempotentResult:
    replayed: bool
    status: int
    body: dict


class IdempotencyGuard:
    """
    ใช้ wrap use case ที่ต้อง idempotent

    Usage:
        guard = IdempotencyGuard(repo)
        result = await guard.execute(
            key=header_key,
            company_id=cid,
            endpoint="/api/v1/invoices",
            method="POST",
            body=request_body,
            scope=IdempotencyScope.PERMANENT,
            action=lambda: issue_invoice_use_case.execute(cmd),
        )
    """

    def __init__(self, repo: IIdempotencyRepository) -> None:
        self.repo = repo

    async def execute(
        self,
        *,
        key: str,
        company_id: UUID,
        endpoint: str,
        method: str,
        body: dict,
        scope: IdempotencyScope,
        action: Callable[[], Awaitable[tuple[int, dict]]],
    ) -> IdempotentResult:
        request_hash = compute_request_hash(body)

        # 1. ลอง acquire
        existing = await self.repo.get(company_id, key, endpoint)
        if existing:
            if existing.request_hash != request_hash:
                raise IdempotencyConflictError(
                    f"Key {key} ถูกใช้กับ request อื่น"
                )
            if existing.status == IdempotencyStatus.COMPLETED:
                return IdempotentResult(
                    replayed=True,
                    status=existing.response_status,
                    body=existing.response_body,
                )
            if existing.status == IdempotencyStatus.IN_PROGRESS:
                raise IdempotencyInProgressError(f"Key {key} กำลังประมวลผล")

        # 2. สร้าง record IN_PROGRESS
        record = await self.repo.acquire(
            company_id=company_id,
            key=key,
            endpoint=endpoint,
            method=method,
            request_hash=request_hash,
            scope=scope,
        )

        # 3. รัน action
        try:
            status, response_body = await action()
            await self.repo.complete(record.id, status, response_body)
            return IdempotentResult(replayed=False, status=status, body=response_body)
        except Exception as e:
            await self.repo.fail(record.id, str(e))
            raise
```

## 3.3.4 Infrastructure — Redis + PostgreSQL

```python
# app/core/idempotency/infrastructure/repositories.py

import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.idempotency.domain.entities import (
    IdempotencyRecord, IdempotencyStatus, IdempotencyScope, SCOPE_TTL,
)


class HybridIdempotencyRepository:
    """
    - Redis: fast path + lock สำหรับ IN_PROGRESS
    - PostgreSQL: permanent record (โดยเฉพาะ PERMANENT scope)
    """

    def __init__(self, redis: Redis, session: AsyncSession) -> None:
        self.redis = redis
        self.session = session

    def _redis_key(self, company_id: UUID, key: str, endpoint: str) -> str:
        return f"idem:{company_id}:{endpoint}:{key}"

    async def get(
        self, company_id: UUID, key: str, endpoint: str,
    ) -> IdempotencyRecord | None:
        rkey = self._redis_key(company_id, key, endpoint)
        cached = await self.redis.get(rkey)
        if cached:
            return self._from_json(json.loads(cached))
        # fallback DB (สำหรับ permanent scope)
        return await self._from_db(company_id, key, endpoint)

    async def acquire(
        self, *, company_id: UUID, key: str, endpoint: str, method: str,
        request_hash: str, scope: IdempotencyScope,
    ) -> IdempotencyRecord:
        record = IdempotencyRecord(
            id=uuid4(),
            company_id=company_id,
            key=key,
            endpoint=endpoint,
            method=method,
            request_hash=request_hash,
            status=IdempotencyStatus.IN_PROGRESS,
            response_status=None,
            response_body=None,
            scope=scope,
            created_at=datetime.now(timezone.utc),
            completed_at=None,
            expires_at=self._compute_expiry(scope),
        )

        rkey = self._redis_key(company_id, key, endpoint)
        ttl = SCOPE_TTL[scope]
        await self.redis.set(
            rkey,
            json.dumps(self._to_json(record)),
            ex=int(ttl.total_seconds()) if ttl else None,
            nx=True,
        )

        # permanent → เก็บใน DB ด้วย
        if scope == IdempotencyScope.PERMANENT:
            await self._persist_db(record)

        return record

    async def complete(
        self, record_id: UUID, status: int, body: dict,
    ) -> None:
        # update Redis + DB
        ...

    async def fail(self, record_id: UUID, error: str) -> None:
        ...

    @staticmethod
    def _compute_expiry(scope: IdempotencyScope) -> datetime | None:
        ttl = SCOPE_TTL[scope]
        if ttl is None:
            return None
        return datetime.now(timezone.utc) + ttl
```

## 3.3.5 Database Schema

```sql
CREATE TABLE idempotency_records (
    id              UUID PRIMARY KEY,
    company_id      UUID NOT NULL,
    key             VARCHAR(255) NOT NULL,
    endpoint        VARCHAR(255) NOT NULL,
    method          VARCHAR(10) NOT NULL,
    request_hash    VARCHAR(64) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    response_status INT,
    response_body   JSONB,
    scope           VARCHAR(20) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    completed_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    UNIQUE (company_id, key, endpoint)
);

CREATE INDEX ix_idem_expires ON idempotency_records (expires_at)
    WHERE expires_at IS NOT NULL;
```

## 3.3.6 Presentation — Middleware / Dependency

```python
# app/core/idempotency/presentation/dependencies.py

from fastapi import Header, HTTPException, Request

async def require_idempotency_key(
    request: Request,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> str:
    """ใช้กับ endpoint ที่ต้อง idempotent (POST/PATCH/PUT ที่แตะเงิน)"""
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="ต้องส่ง Idempotency-Key header สำหรับ endpoint นี้",
        )
    if len(idempotency_key) > 255:
        raise HTTPException(400, "Idempotency-Key ยาวเกิน 255 ตัวอักษร")
    return idempotency_key
```

**Flow Diagram:**

```text
Client                     API                       Redis/DB
  │                         │                          │
  │ POST /invoices          │                          │
  │ Idempotency-Key: abc    │                          │
  ├────────────────────────►│                          │
  │                         │  GET idem:abc            │
  │                         ├─────────────────────────►│
  │                         │◄──── not found ──────────┤
  │                         │                          │
  │                         │  SET idem:abc NX         │
  │                         ├─────────────────────────►│
  │                         │◄──── OK ─────────────────┤
  │                         │                          │
  │                         │  run use case            │
  │                         │  (issue invoice)         │
  │                         │                          │
  │                         │  SET idem:abc = result   │
  │                         ├─────────────────────────►│
  │◄──── 201 Created ───────┤                          │
  │                         │                          │
  │ POST /invoices (retry)  │                          │
  │ Idempotency-Key: abc    │                          │
  ├────────────────────────►│                          │
  │                         │  GET idem:abc            │
  │                         ├─────────────────────────►│
  │                         │◄──── cached result ──────┤
  │◄──── 201 (replayed) ────┤                          │
  │                         │                          │
  │ POST /invoices (diff)   │                          │
  │ Idempotency-Key: abc    │                          │
  ├────────────────────────►│                          │
  │                         │  GET idem:abc → hash ≠   │
  │◄──── 409 Conflict ──────┤                          │
```

## 3.3.7 Folder Structure

```text
app/core/idempotency/
├── __init__.py
├── domain/
│   ├── entities.py            # IdempotencyRecord, Status, Scope
│   └── errors.py
├── application/
│   ├── interfaces.py          # IIdempotencyRepository
│   └── use_cases.py           # IdempotencyGuard
├── infrastructure/
│   ├── models.py              # IdempotencyModel
│   └── repositories.py        # HybridIdempotencyRepository
├── presentation/
│   └── dependencies.py        # require_idempotency_key
└── tests/
    ├── test_guard.py
    ├── test_conflict.py
    └── test_replay.py
```

## 3.3.8 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (Week 1) |
| **DoD** | ✅ endpoint แตะเงินทุกตัวมี Idempotency-Key<br>✅ retry 100 ครั้ง → ได้ 1 record<br>✅ conflict detection ทำงาน<br>✅ permanent scope เก็บใน DB |

---

# 🧩 Module 3.4 — `config`

## 3.4.1 Purpose & Scope

**Purpose:** รวม configuration ทางธุรกิจที่ **เปลี่ยนได้โดยไม่ต้อง deploy** — VAT, waste%, pricing rules, numbering, เงื่อนไขการชำระ

**Scope:**
- ✅ Business config per company (VAT rate, waste%, terms)
- ✅ Versioned config (เปลี่ยนแล้ว trace ได้)
- ✅ Cache + invalidation
- ✅ Type-safe (schema validation)
- ❌ ไม่เก็บ secret (อยู่ใน .env)
- ❌ ไม่เก็บ user preference (อยู่ใน user module)

## 3.4.2 Domain Model

```python
# app/core/config/domain/entities.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ConfigEntry:
    """
    Business config — versioned

    Invariants:
    - (company_id, key, effective_from) unique
    - เมื่อเปลี่ยน config → create version ใหม่ (ห้าม update)
    - effective_from ต้องไม่ย้อนหลังเกิน 1 วัน
    """
    id: UUID
    company_id: UUID
    key: str                  # "vat.standard_rate", "production.waste_pct"
    value: Any                # JSONB
    value_type: str           # "decimal", "int", "string", "json"
    version: int
    effective_from: datetime
    effective_to: datetime | None
    changed_by: UUID
    changed_at: datetime
    reason: str | None


class ConfigKey:
    """Constants ของ key มาตรฐาน"""
    # Tax
    VAT_STANDARD_RATE = "tax.vat_standard_rate"
    VAT_INCLUSIVE_DEFAULT = "tax.vat_inclusive_default"
    WHT_RATE_DEFAULT = "tax.wht_default_rate"

    # Production
    WASTE_PCT_DEFAULT = "production.waste_pct_default"
    YIELD_TOLERANCE_PCT = "production.yield_tolerance_pct"

    # Pricing
    PRICING_TIER_B2B = "pricing.tier_b2b"
    PRICING_TIER_B2C = "pricing.tier_b2c"
    PRICING_ROUNDING = "pricing.rounding_rule"

    # Invoice
    INVOICE_NUMBER_FORMAT = "invoice.number_format"     # "INV-{YYYY}-{NNNNN}"
    INVOICE_DUE_DAYS_DEFAULT = "invoice.due_days_default"
    INVOICE_TAX_ID_REQUIRED = "invoice.tax_id_required"

    # Inventory
    STOCK_VALUATION_METHOD = "inventory.valuation_method"  # "FIFO" | "FEFO" | "AVG"
    STOCK_LOW_THRESHOLD_PCT = "inventory.low_threshold_pct"
    EXPIRY_ALERT_DAYS = "inventory.expiry_alert_days"

    # Delivery
    DELIVERY_FREE_MIN_AMOUNT = "delivery.free_min_amount"
    DELIVERY_FEE_DEFAULT = "delivery.fee_default"

    # Retail
    POS_CASH_ROUNDING = "pos.cash_rounding"              # "none" | "nearest_0.25" | "nearest_1"
    POS_RECEIPT_FOOTER = "pos.receipt_footer"
```

## 3.4.3 Application — Use Cases + Cache

```python
# app/core/config/application/use_cases.py

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.core.config.application.interfaces import IConfigRepository
from app.core.config.domain.entities import ConfigEntry
from app.core.audit.application.use_cases import RecordAuditUseCase, RecordAuditCommand
from app.core.audit.domain.entities import ActorType, AuditAction


class GetConfigUseCase:
    """อ่าน config ปัจจุบัน (with cache)"""

    def __init__(self, repo: IConfigRepository, cache):
        self.repo = repo
        self.cache = cache

    async def execute(self, company_id: UUID, key: str, default: Any = None) -> Any:
        cached = await self.cache.get(company_id, key)
        if cached is not None:
            return cached

        entry = await self.repo.get_current(company_id, key)
        value = entry.value if entry else default

        if entry:
            await self.cache.set(company_id, key, value)
        return value

    async def get_decimal(self, company_id: UUID, key: str, default: Decimal) -> Decimal:
        raw = await self.execute(company_id, key, str(default))
        return Decimal(str(raw))


@dataclass
class ChangeConfigCommand:
    company_id: UUID
    key: str
    value: Any
    value_type: str
    changed_by: UUID
    effective_from: datetime
    reason: str


class ChangeConfigUseCase:
    """
    เปลี่ยน config → สร้าง version ใหม่ + audit + invalidate cache
    """

    def __init__(
        self,
        repo: IConfigRepository,
        cache,
        audit: RecordAuditUseCase,
    ):
        self.repo = repo
        self.cache = cache
        self.audit = audit

    async def execute(self, cmd: ChangeConfigCommand) -> ConfigEntry:
        current = await self.repo.get_current(cmd.company_id, cmd.key)

        # ปิด version เก่า
        if current:
            await self.repo.close_version(current.id, cmd.effective_from)

        new_entry = await self.repo.create_version(
            company_id=cmd.company_id,
            key=cmd.key,
            value=cmd.value,
            value_type=cmd.value_type,
            effective_from=cmd.effective_from,
            changed_by=cmd.changed_by,
            reason=cmd.reason,
        )

        await self.audit.execute(RecordAuditCommand(
            company_id=cmd.company_id,
            actor_id=cmd.changed_by,
            actor_type=ActorType.USER,
            action=AuditAction.CONFIG_CHANGED,
            entity_type="config",
            entity_id=new_entry.id,
            before_state={"value": current.value} if current else None,
            after_state={"value": cmd.value, "key": cmd.key},
            metadata={"reason": cmd.reason},
        ))

        await self.cache.invalidate(cmd.company_id, cmd.key)
        return new_entry
```

## 3.4.4 Infrastructure

```python
# app/core/config/infrastructure/models.py

from sqlalchemy import Column, DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import Base


class ConfigEntryModel(Base):
    __tablename__ = "config_entries"
    __table_args__ = (
        Index("ix_config_company_key_effective",
              "company_id", "key", "effective_from", unique=True),
        Index("ix_config_current",
              "company_id", "key",
              postgresql_where="effective_to IS NULL"),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    value_type: Mapped[str] = mapped_column(String(20), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    effective_from: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    changed_by: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    changed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

## 3.4.5 Config Schema Validation

```python
# app/core/config/domain/schemas.py

from decimal import Decimal
from typing import Any, Callable

# Registry ของ validator ต่อ key
CONFIG_VALIDATORS: dict[str, Callable[[Any], None]] = {
    "tax.vat_standard_rate": lambda v: (
        Decimal(str(v)) >= 0 and Decimal(str(v)) <= 1
        or (_ for _ in ()).throw(ValueError("VAT rate ต้องอยู่ 0-1"))
    ),
    "production.waste_pct_default": lambda v: (
        Decimal(str(v)) >= 0 and Decimal(str(v)) <= 1
        or (_ for _ in ()).throw(ValueError("waste% ต้องอยู่ 0-1"))
    ),
    "inventory.valuation_method": lambda v: (
        v in ("FIFO", "FEFO", "AVG")
        or (_ for _ in ()).throw(ValueError("valuation ต้องเป็น FIFO/FEFO/AVG"))
    ),
    "pos.cash_rounding": lambda v: (
        v in ("none", "nearest_0.25", "nearest_1")
        or (_ for _ in ()).throw(ValueError("cash_rounding ไม่ถูกต้อง"))
    ),
}


def validate_config(key: str, value: Any) -> None:
    validator = CONFIG_VALIDATORS.get(key)
    if validator:
        validator(value)
```

## 3.4.6 Presentation

```python
# app/core/config/presentation/routers.py

router = APIRouter(prefix="/api/v1/config", tags=["Config"])


@router.get("/{key}")
async def get_config(key: str, company_id: UUID, ...):
    """อ่าน config ปัจจุบัน"""
    return await get_config_uc.execute(company_id, key)


@router.get("/")
async def list_config(company_id: UUID, ...):
    """ดู config ทั้งหมดของบริษัท"""
    ...


@router.post("/{key}")
async def change_config(
    key: str,
    body: ChangeConfigRequest,
    company_id: UUID,
    current_user = Depends(authenticate_admin),
    ...
):
    """เปลี่ยน config — ADMIN เท่านั้น + audit"""
    return await change_config_uc.execute(ChangeConfigCommand(...))


@router.get("/{key}/history")
async def config_history(key: str, company_id: UUID, ...):
    """ดูประวัติการเปลี่ยน config"""
    ...
```

## 3.4.7 ตัวอย่าง Config ที่ใช้จริง

```json
{
  "tax.vat_standard_rate": 0.07,
  "tax.vat_inclusive_default": false,
  "production.waste_pct_default": 0.05,
  "production.yield_tolerance_pct": 0.02,
  "pricing.tier_b2b": {"margin": 0.15, "min_qty": 10},
  "pricing.tier_b2c": {"margin": 0.35, "min_qty": 1},
  "invoice.number_format": "INV-{YYYY}-{NNNNN}",
  "invoice.due_days_default": 30,
  "inventory.valuation_method": "FEFO",
  "inventory.expiry_alert_days": 7,
  "pos.cash_rounding": "nearest_0.25",
  "delivery.free_min_amount": 2000
}
```

## 3.4.8 Folder Structure

```text
app/core/config/
├── __init__.py
├── domain/
│   ├── entities.py            # ConfigEntry, ConfigKey
│   ├── schemas.py             # validators
│   └── errors.py
├── application/
│   ├── interfaces.py          # IConfigRepository, IConfigCache
│   └── use_cases.py           # GetConfig, ChangeConfig
├── infrastructure/
│   ├── models.py
│   ├── repositories.py
│   └── cache.py               # RedisConfigCache
├── presentation/
│   ├── routers.py
│   ├── schemas.py
│   └── dependencies.py
└── tests/
    ├── test_use_cases.py
    ├── test_validation.py
    ├── test_versioning.py
    └── test_cache_invalidation.py
```

## 3.4.9 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (Week 1) |
| **DoD** | ✅ ทุก config เป็น versioned<br>✅ validator ทำงาน<br>✅ cache invalidate ถูกต้อง<br>✅ change config → audit<br>✅ ไม่มี hardcode VAT/waste% ในโค้ด |

---

# 🧩 Module 3.5 — `events`

## 3.5.1 Purpose & Scope

**Purpose:** Domain event bus + Outbox pattern — ให้ module ต่าง ๆ สื่อสารกันแบบ loose coupling และ sync กับ external ได้อย่าง retry-safe

**Scope:**
- ✅ Domain event definition
- ✅ In-process event bus (สำหรับ module ใน process เดียวกัน)
- ✅ Outbox pattern (transactional outbox)
- ✅ Kafka publisher (สำหรับ stream)
- ✅ Event replay
- ❌ ไม่ทำ orchestration (อยู่ใน use case)
- ❌ ไม่เป็น message queue แทน Kafka

## 3.5.2 Domain Model

```python
# app/core/events/domain/entities.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """
    Base domain event

    Invariants:
    - event_id ไม่ซ้ำ
    - aggregate_id ต้องอ้างถึง aggregate root
    - occurred_at เป็น UTC
    """
    event_id: UUID
    event_type: str          # "invoice.issued"
    aggregate_type: str      # "invoice"
    aggregate_id: UUID
    company_id: UUID
    payload: dict[str, Any]
    occurred_at: datetime
    actor_id: UUID | None = None
    correlation_id: UUID | None = None    # request_id
    causation_id: UUID | None = None      # event ที่ทำให้เกิด


# Concrete events

@dataclass(frozen=True, slots=True)
class InvoiceIssued(DomainEvent):
    @classmethod
    def create(
        cls, *, invoice_id: UUID, company_id: UUID, payload: dict,
        actor_id: UUID | None = None, correlation_id: UUID | None = None,
    ) -> "InvoiceIssued":
        return cls(
            event_id=uuid4(),
            event_type="invoice.issued",
            aggregate_type="invoice",
            aggregate_id=invoice_id,
            company_id=company_id,
            payload=payload,
            occurred_at=datetime.utcnow(),
            actor_id=actor_id,
            correlation_id=correlation_id,
        )


@dataclass(frozen=True, slots=True)
class InvoiceCancelled(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class LedgerPosted(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class LedgerReversed(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class StockPosted(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class StockLow(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class BatchCompleted(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class ShipmentDelivered(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class TempAlert(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class ShiftClosed(DomainEvent): ...
@dataclass(frozen=True, slots=True)
class KpiUpdated(DomainEvent): ...
```

## 3.5.3 Outbox Pattern

```python
# app/core/events/domain/outbox.py

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class OutboxStatus(str, Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class OutboxEntry:
    """
    Outbox entry — เขียนใน transaction เดียวกับ business op
    Worker จะอ่านไป publish ทีหลัง

    Invariants:
    - event_id unique (ไม่ publish ซ้ำ)
    - retry_count >= 0
    - published_at != None → status = PUBLISHED
    """
    id: UUID
    event_id: UUID
    event_type: str
    company_id: UUID
    payload: dict
    status: OutboxStatus
    retry_count: int
    max_retries: int
    last_error: str | None
    created_at: datetime
    published_at: datetime | None
    next_retry_at: datetime | None
```

## 3.5.4 Application — Event Bus + Outbox

```python
# app/core/events/application/event_bus.py

from typing import Callable, Awaitable, Type
from collections import defaultdict
from app.core.events.domain.entities import DomainEvent


Handler = Callable[[DomainEvent], Awaitable[None]]


class InProcessEventBus:
    """
    Event bus สำหรับ handler ใน process เดียวกัน
    (เช่น ledger handler ฟัง invoice.issued)

    หมายเหตุ: ใช้สำหรับ side-effect ที่ไม่ critical
    ถ้าต้องการ reliability → ใช้ Outbox + Worker
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                # log + dead letter
                ...
```

```python
# app/core/events/application/use_cases.py

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime, timedelta

from app.core.events.domain.entities import DomainEvent
from app.core.events.domain.outbox import OutboxEntry, OutboxStatus
from app.core.events.application.interfaces import (
    IOutboxRepository, IEventPublisher, IEventBus,
)


class PublishEventUseCase:
    """
    ใช้ภายใน transaction เดียวกับ business op
    เขียนลง outbox (ยังไม่ publish)
    """

    def __init__(self, outbox: IOutboxRepository, bus: IEventBus) -> None:
        self.outbox = outbox
        self.bus = bus

    async def execute(self, event: DomainEvent) -> None:
        await self.outbox.append(OutboxEntry(
            id=event.event_id,
            event_id=event.event_id,
            event_type=event.event_type,
            company_id=event.company_id,
            payload={
                "event_id": str(event.event_id),
                "event_type": event.event_type,
                "aggregate_type": event.aggregate_type,
                "aggregate_id": str(event.aggregate_id),
                "company_id": str(event.company_id),
                "actor_id": str(event.actor_id) if event.actor_id else None,
                "correlation_id": str(event.correlation_id) if event.correlation_id else None,
                "causation_id": str(event.causation_id) if event.causation_id else None,
                "payload": event.payload,
                "occurred_at": event.occurred_at.isoformat(),
            },
            status=OutboxStatus.PENDING,
            retry_count=0,
            max_retries=5,
            last_error=None,
            created_at=event.occurred_at,
            published_at=None,
            next_retry_at=event.occurred_at,
        ))

        # in-process bus (best-effort, ไม่ blocking)
        await self.bus.publish(event)


class OutboxPublisherWorker:
    """
    Worker — poll outbox → publish → mark published
    ใช้ exponential backoff สำหรับ retry
    """

    def __init__(
        self,
        outbox: IOutboxRepository,
        publisher: IEventPublisher,
        batch_size: int = 100,
    ):
        self.outbox = outbox
        self.publisher = publisher
        self.batch_size = batch_size

    async def run_once(self) -> int:
        entries = await self.outbox.fetch_pending(
            limit=self.batch_size,
            now=datetime.utcnow(),
        )
        published = 0
        for entry in entries:
            try:
                await self.publisher.publish(entry.event_type, entry.payload)
                await self.outbox.mark_published(entry.id)
                published += 1
            except Exception as e:
                await self.outbox.mark_failed(
                    entry.id,
                    error=str(e),
                    next_retry_at=self._backoff(entry.retry_count),
                )
        return published

    @staticmethod
    def _backoff(retry_count: int) -> datetime:
        """2^retry seconds, cap 1 hour"""
        seconds = min(2 ** retry_count, 3600)
        return datetime.utcnow() + timedelta(seconds=seconds)
```

## 3.5.5 Infrastructure

```python
# app/core/events/infrastructure/models.py

class OutboxModel(Base):
    __tablename__ = "outbox_events"
    __table_args__ = (
        Index("ix_outbox_status_retry", "status", "next_retry_at"),
        Index("ix_outbox_event", "event_id", unique=True),
    )

    id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    event_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    company_id: Mapped[str] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=5)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    next_retry_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
```

```python
# app/core/events/infrastructure/publishers.py

class KafkaEventPublisher:
    """Publish ไป Kafka"""

    def __init__(self, producer):
        self.producer = producer

    async def publish(self, event_type: str, payload: dict) -> None:
        topic = f"erp.{event_type.split('.')[0]}"   # erp.invoice, erp.stock
        await self.producer.send_and_wait(
            topic,
            value=json.dumps(payload).encode(),
            key=str(payload["aggregate_id"]).encode(),  # partition by aggregate
        )
```

## 3.5.6 Database Schema

```sql
CREATE TABLE outbox_events (
    id             UUID PRIMARY KEY,
    event_id       UUID NOT NULL UNIQUE,
    event_type     VARCHAR(50) NOT NULL,
    company_id     UUID NOT NULL,
    payload        JSONB NOT NULL,
    status         VARCHAR(20) NOT NULL,
    retry_count    INT NOT NULL DEFAULT 0,
    max_retries    INT NOT NULL DEFAULT 5,
    last_error     TEXT,
    created_at     TIMESTAMPTZ NOT NULL,
    published_at   TIMESTAMPTZ,
    next_retry_at  TIMESTAMPTZ
);

CREATE INDEX ix_outbox_status_retry ON outbox_events (status, next_retry_at);
CREATE INDEX ix_outbox_company_created ON outbox_events (company_id, created_at DESC);
```

## 3.5.7 Flow

```text
Use Case (ใน transaction)
    │
    │ 1. save aggregate
    │ 2. publish_event.execute(event)
    │    └─ INSERT outbox_events
    │    └─ bus.publish (in-process, best-effort)
    │
    ▼
COMMIT (transaction เดียว — atomic)
    │
    ▼
OutboxPublisherWorker (every 5s)
    │
    │ 1. SELECT * FROM outbox_events
    │    WHERE status='pending' AND next_retry_at <= now()
    │    FOR UPDATE SKIP LOCKED
    │
    │ 2. publish ไป Kafka
    │
    │ 3. UPDATE status='published'
    │
    ▼
Kafka Topics
    ├── erp.invoice  → ledger consumer, BI consumer
    ├── erp.stock    → analytics consumer
    └── erp.production → forecast consumer
```

## 3.5.8 Folder Structure

```text
app/core/events/
├── __init__.py
├── domain/
│   ├── entities.py            # DomainEvent + concrete events
│   └── outbox.py              # OutboxEntry
├── application/
│   ├── interfaces.py          # IEventBus, IOutboxRepository, IEventPublisher
│   ├── event_bus.py           # InProcessEventBus
│   └── use_cases.py           # PublishEvent, OutboxPublisherWorker
├── infrastructure/
│   ├── models.py              # OutboxModel
│   ├── repositories.py        # PostgresOutboxRepository
│   ├── publishers.py          # KafkaEventPublisher, NoopPublisher
│   └── worker.py              # Worker loop
└── tests/
    ├── test_outbox.py
    ├── test_retry.py
    ├── test_idempotent_publish.py
    └── test_replay.py
```

## 3.5.9 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (ออกแบบ) / 2 (implement Worker) |
| **DoD** | ✅ domain event ครบ<br>✅ outbox เขียนใน transaction เดียวกับ aggregate<br>✅ worker retry ได้<br>✅ event ไม่ publish ซ้ำ (event_id unique)<br>✅ Kafka topic per aggregate |

---

# 🧩 Module 3.6 — `tenant_context`

## 3.6.1 Purpose & Scope

**Purpose:** จัดการ multi-company — resolve company จาก request, ตั้ง schema, บังคับ isolation

**Scope:**
- ✅ Resolve company จาก JWT / header / subdomain
- ✅ ContextVar เก็บ current company
- ✅ PostgreSQL schema routing
- ✅ Cross-tenant guard (ห้าม query ข้ามบริษัท)
- ✅ Provision schema ใหม่
- ❌ ไม่เก็บ company data (อยู่ใน `tenancy`)

## 3.6.2 Domain Model

```python
# app/core/tenant_context/domain/context.py

from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TenantContext:
    company_id: UUID
    schema_name: str          # "company_a"
    user_id: UUID | None = None
    request_id: str | None = None


_ctx: ContextVar[TenantContext | None] = ContextVar("tenant_ctx", default=None)


def set_tenant(ctx: TenantContext) -> None:
    _ctx.set(ctx)


def get_tenant() -> TenantContext:
    ctx = _ctx.get()
    if ctx is None:
        raise RuntimeError(
            "ไม่พบ tenant context — request ไม่ได้ bind กับบริษัท "
            "ตรวจสอบว่ามี TenantResolverMiddleware"
        )
    return ctx


def get_company_id() -> UUID:
    return get_tenant().company_id


def get_schema_name() -> str:
    return get_tenant().schema_name


def try_get_tenant() -> TenantContext | None:
    return _ctx.get()
```

## 3.6.3 Schema Routing

```python
# app/core/tenant_context/infrastructure/schema_router.py

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant_context.domain.context import try_get_tenant


def install_schema_router(session_factory) -> None:
    """
    ติดตั้ง event listener ให้ SQLAlchemy ตั้ง search_path
    ตาม tenant ปัจจุบันก่อนทุก query
    """

    @event.listens_for(session_factory, "after_begin")
    def set_search_path(session, transaction, connection):
        ctx = try_get_tenant()
        if ctx is None:
            return
        # ตั้ง schema ของบริษัท + public (สำหรับ shared tables)
        connection.exec_driver_sql(
            f'SET LOCAL search_path TO "{ctx.schema_name}", public'
        )
```

## 3.6.4 Middleware

```python
# app/core/tenant_context/middleware.py

from fastapi import Request, HTTPException
from app.core.tenant_context.domain.context import TenantContext, set_tenant


class TenantResolverMiddleware:
    """
    Resolve company จาก (ตามลำดับ):
    1. X-Company-Id header (ถ้า user เป็น multi-company admin)
    2. subdomain (company_a.erp.example.com,mycompany.com,gmail.com)
    3. JWT claim "company_id" (default)
    """

    async def __call__(self, request: Request, call_next):
        # skip สำหรับ public endpoints
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        company_id = await self._resolve_company(request)
        if company_id is None:
            raise HTTPException(400, "ไม่พบ company context")

        # ดึง schema_name จาก cache/db
        schema_name = await self._get_schema(company_id)

        set_tenant(TenantContext(
            company_id=company_id,
            schema_name=schema_name,
            request_id=request.headers.get("X-Request-ID"),
        ))

        return await call_next(request)

    async def _resolve_company(self, request: Request):
        # 1. Header
        header = request.headers.get("X-Company-Id")
        if header:
            return UUID(header)

        # 2. Subdomain
        host = request.headers.get("host", "")
        if "." in host:
            sub = host.split(".")[0]
            # lookup sub → company_id
            ...

        # 3. JWT (จาก auth middleware)
        user = getattr(request.state, "user", None)
        if user and user.company_id:
            return user.company_id

        return None
```

## 3.6.5 Provisioning

```python
# app/core/tenant_context/application/use_cases.py

from dataclasses import dataclass
from uuid import UUID

from app.core.tenant_context.application.interfaces import ISchemaProvisioner


@dataclass
class ProvisionTenantCommand:
    company_id: UUID
    schema_name: str     # "company_a"


class ProvisionTenantUseCase:
    """
    ตอนสร้างบริษัทใหม่ — provision schema + run migrations + seed
    """

    def __init__(self, provisioner: ISchemaProvisioner) -> None:
        self.provisioner = provisioner

    async def execute(self, cmd: ProvisionTenantCommand) -> None:
        await self.provisioner.create_schema(cmd.schema_name)
        await self.provisioner.run_migrations(cmd.schema_name)
        await self.provisioner.seed_chart_of_accounts(cmd.schema_name)
        await self.provisioner.seed_default_config(cmd.schema_name)
```

```python
# app/core/tenant_context/infrastructure/provisioner.py

class PostgresSchemaProvisioner:
    """
    1. CREATE SCHEMA company_a
    2. SET search_path = company_a
    3. run alembic upgrade head (per-schema)
    4. seed COA, config, admin user
    """

    async def create_schema(self, schema_name: str) -> None:
        async with self.engine.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

    async def run_migrations(self, schema_name: str) -> None:
        # รัน alembic ใน schema นั้น
        # ใช้ env var ALEMBIC_SCHEMA=company_a
        ...

    async def seed_chart_of_accounts(self, schema_name: str) -> None:
        # seed ผังบัญชีมาตรฐานไทย
        ...
```

## 3.6.6 Cross-Tenant Guard

```python
# app/core/tenant_context/guard.py

class CrossTenantGuard:
    """
    ดักจับ query ที่พยายามข้ามบริษัท
    - inject company_id filter อัตโนมัติ (ถ้าใช้ ORM)
    - log + alert ถ้าพบ attempt
    """

    @staticmethod
    def assert_company(entity_company_id, current_company_id) -> None:
        if entity_company_id != current_company_id:
            # log security event
            logger.error(
                "cross_tenant_attempt",
                entity_company=str(entity_company_id),
                current=str(current_company_id),
            )
            raise PermissionError("ห้ามเข้าถึงข้อมูลบริษัทอื่น")
```

## 3.6.7 Database Schema (public)

```sql
-- เก็บใน public schema (shared)
CREATE TABLE companies (
    id             UUID PRIMARY KEY,
    code           VARCHAR(20) UNIQUE NOT NULL,  -- "FOODCO"
    name           VARCHAR(255) NOT NULL,
    tax_id         VARCHAR(13) NOT NULL,
    schema_name    VARCHAR(63) UNIQUE NOT NULL,  -- "company_foodco"
    is_active      BOOLEAN NOT NULL DEFAULT true,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 3.6.8 Folder Structure

```text
app/core/tenant_context/
├── __init__.py
├── domain/
│   ├── context.py             # TenantContext + ContextVar
│   └── errors.py
├── application/
│   ├── interfaces.py          # ISchemaProvisioner, ICompanyResolver
│   └── use_cases.py           # ProvisionTenant
├── infrastructure/
│   ├── schema_router.py       # SQLAlchemy event
│   ├── provisioner.py         # PostgresSchemaProvisioner
│   └── resolver.py
├── middleware.py              # TenantResolverMiddleware
├── guard.py                   # CrossTenantGuard
└── tests/
    ├── test_context.py
    ├── test_isolation.py      # company A อ่านข้อมูล company B ไม่ได้
    └── test_provisioning.py
```

## 3.6.9 Phase & DoD

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Phase** | 1 (ออกแบบ) / 6 (rollout) |
| **DoD** | ✅ contextvar ตั้งถูกทุก request<br>✅ search_path routing ถูก<br>✅ cross-tenant guard ทำงาน<br>✅ provision schema ใหม่ได้<br>✅ isolation test ผ่าน |

---

# 📊 PART 3 — สรุป

## Dependency Graph

```text
                    ┌──────────────────┐
                    │   tenant_context │  ← ทุก module ใช้
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌────────────┐  ┌────────────┐  ┌────────────┐
      │   money    │  │   audit    │  │   config   │
      └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
            │               │               │
            └───────────────┼───────────────┘
                            │
                    ┌───────┴───────┐
                    │  idempotency  │
                    └───────┬───────┘
                            │
                    ┌───────┴───────┐
                    │    events     │
                    └───────────────┘
                            │
                            ▼
              ทุก module ใน Layer 1-7 ใช้ทั้งหมด
```

## ลำดับการ Implement

```text
Week 1:
  Day 1-2: money + tests
  Day 3:   audit + trigger
  Day 4:   idempotency (Redis + DB)
  Day 5:   config + validators
  Day 6-7: events (outbox) + worker
  Day 8:   tenant_context (contextvar + middleware)
  Day 9-10: integration tests + ทดลองใช้ใน invoice module
```

## Checklist รวม

```text
┌─────────────────────────────────────────────────────────────────┐
│  CORE INFRASTRUCTURE — FINAL CHECKLIST                          │
├─────────────────────────────────────────────────────────────────┤
│  money                                                          │
│   □ Money VO ผ่าน property-based test                          │
│   □ VatCalculator 4 โหมดผ่าน test                              │
│   □ ห้าม float — lint rule + code review                       │
│   □ ทุก module ใช้ Money แทน float/Decimal ตรง ๆ               │
├─────────────────────────────────────────────────────────────────┤
│  audit                                                          │
│   □ trigger prevent UPDATE/DELETE                              │
│   □ mask sensitive data                                        │
│   □ ทุก money/goods use case เรียก RecordAudit                 │
│   □ query API สำหรับ auditor (MANAGER+)                        │
│   □ partition by year + retention 7 ปี                         │
├─────────────────────────────────────────────────────────────────┤
│  idempotency                                                    │
│   □ endpoint แตะเงินทุกตัว require header                      │
│   □ retry 100 ครั้ง → 1 record                                 │
│   □ conflict detection ทำงาน                                   │
│   □ permanent scope เก็บ DB                                    │
├─────────────────────────────────────────────────────────────────┤
│  config                                                         │
│   □ versioned + effective_from/to                              │
│   □ validator ต่อ key                                          │
│   □ cache invalidate ถูกต้อง                                   │
│   □ change → audit                                             │
│   □ ไม่มี hardcode VAT/waste%                                  │
├─────────────────────────────────────────────────────────────────┤
│  events                                                         │
│   □ domain events ครบทุก aggregate                             │
│   □ outbox เขียนใน transaction เดียวกับ aggregate               │
│   □ worker retry + backoff                                     │
│   □ event_id unique (no double publish)                        │
│   □ Kafka topic per aggregate                                  │
├─────────────────────────────────────────────────────────────────┤
│  tenant_context                                                 │
│   □ contextvar ตั้งทุก request                                 │
│   □ search_path routing ถูก                                    │
│   □ cross-tenant guard                                         │
│   □ provision schema ใหม่ได้                                   │
│   □ isolation test ผ่าน                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔜 Part 4 (ตอนถัดไป) — Foundation Layer

จะลงรายละเอียด:
- **Tenancy** — Company, Branch, Provisioning, Company settings
- **Authentication** — JWT (JWS+JWE), API Key, session (ตาม template)
- **User** — User, Role, Permission, RBAC (ตาม template)

พร้อม folder structure, domain model, use case, infrastructure, presentation, tests และ dependencies ครบเหมือน Part 3

---

 
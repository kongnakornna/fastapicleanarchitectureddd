# 📁 โครงสร้างไฟล์ AI Prompt Template สำหรับ ERP + CRM + IoT

---

## 📂 โครงสร้างโฟลเดอร์ docs/

```
docs/
├── template_modules.md                    # 📘 Master template (ไฟล์หลัก)
├── prompts/
│   ├── README.md                          # 📑 Index ของ prompts ทั้งหมด
│   │
│   ├── layer-0-core/
│   │   ├── money.md
│   │   ├── tenant_context.md
│   │   ├── audit.md
│   │   ├── idempotency.md
│   │   ├── config.md
│   │   └── events.md
│   │
│   ├── layer-1-foundation/
│   │   ├── tenancy.md
│   │   ├── authentication.md
│   │   ├── user.md
│   │   ├── employee.md
│   │   ├── customer.md
│   │   ├── supplier.md
│   │   ├── product.md
│   │   └── pricing.md
│   │
│   ├── layer-2-money-path/
│   │   ├── order.md
│   │   ├── invoice.md
│   │   ├── ledger.md
│   │   ├── payment.md
│   │   ├── accounting_gateway.md
│   │   ├── tax.md
│   │   └── reconciliation.md
│   │
│   ├── layer-3-goods-path/
│   │   ├── inventory.md
│   │   ├── warehouse.md
│   │   ├── lot.md
│   │   ├── production.md
│   │   ├── recipe.md
│   │   ├── quality.md
│   │   ├── waste.md
│   │   ├── procurement.md
│   │   ├── traceability.md
│   │   ├── agriculture.md
│   │   ├── crop.md
│   │   ├── soil.md
│   │   └── irrigation.md
│   │
│   ├── layer-4-operations/
│   │   ├── transport.md
│   │   ├── delivery.md
│   │   ├── route.md
│   │   ├── gps.md
│   │   ├── retail.md
│   │   ├── pos.md
│   │   ├── shift.md
│   │   ├── line_channel.md
│   │   ├── promotion.md
│   │   ├── loyalty.md
│   │   ├── crm.md
│   │   ├── campaign.md
│   │   └── support.md
│   │
│   ├── layer-5-intelligence/
│   │   ├── reporting.md
│   │   ├── analytics.md
│   │   ├── forecast.md
│   │   ├── kpi.md
│   │   ├── satisfaction.md
│   │   ├── recommendation.md
│   │   └── oee.md
│   │
│   ├── layer-6-monitoring/
│   │   ├── iot.md
│   │   ├── cctv.md
│   │   ├── monitoring.md
│   │   ├── backup.md
│   │   ├── alerting.md
│   │   ├── audit_viewer.md
│   │   ├── maintenance.md
│   │   └── energy.md
│   │
│   └── layer-7-templates/
│       ├── health.md
│       ├── example.md
│       └── blank.md
```

---

## 📘 ไฟล์ 1: `docs/template_modules.md` (Master Template)

```markdown
# AI Prompt Template — สร้าง Module ใหม่ใน ERP + CRM + IoT

> **เวอร์ชัน:** 2.0.0
> **ขอบเขตการใช้งาน:** SME ทุกประเภท (เกษตร · การผลิต · การขนส่ง · โรงงาน · ERP · CRM)
> **Stack:** Python 3.14+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · PostgreSQL 17 · Redis 8 · Kafka

---

## 📋 ข้อมูล Module (Metadata)

| หัวข้อ | รายละเอียด | ตัวอย่าง |
|---|---|---|
| **ชื่อ Module** | `{module_name}` | `agriculture` |
| **Layer** | `{layer_number}` (0-7) | `3` |
| **Priority** | `{priority}` (🔴/🟠/🟡/🟢) | `🟠` |
| **Phase** | `{phase}` (0-6) | `4` |
| **มิติธุรกิจ** | `{agriculture/production/logistics/factory/erp/crm}` | `agriculture` |
| **Dependencies** | `{list_of_modules}` | `crop, soil, iot, forecast` |
| **Domain Concepts** | `{entities}, {value_objects}, {enums}` | `Farm, Plot, CropCycle` |

---

## 🎯 Prompt Template (Master)

### สร้าง Module `{module_name}`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- PostgreSQL 17 (schema-per-tenant), Redis 8, Kafka
- รองรับ 4 มิติ: เกษตร, การผลิต, การขนส่ง, โรงงาน
- ทุก action แตะเงิน/สต็อก → audit log
- Money Path + Goods Path ต้อง idempotent

**ข้อกำหนด:**

#### 1. Domain Layer (`domain/`)
- `entities.py`: Dataclasses extending `BaseEntity`
- `value_objects.py`: Plain classes with `_normalize → _validate → __str__ → __eq__`
- `enums.py`: All enums as `(str, Enum)`
- **ห้าม import framework ใดๆ**

```python
# ตัวอย่าง: domain/entities.py
from dataclasses import dataclass, field
from app.modules.shared.domain.entities import BaseEntity

@dataclass
class Farm(BaseEntity):
    """Farm entity — เอนทิตีฟาร์ม"""
    code: str = ""
    name: str = ""
    location: str = ""
    area: float = 0.0
    plots: list = field(default_factory=list)
    owner_id: str = ""
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self) -> None:
        """Validate farm data — ตรวจสอบข้อมูลฟาร์ม"""
        if not self.code:
            raise DomainError("Farm code is required")
        if self.area <= 0:
            raise DomainError("Farm area must be positive")
```

#### 2. Application Layer (`application/`)
- `interfaces.py`: Protocol contracts
- `use_cases.py`: One `{Module}UseCases` class with business rules
- `mappers.py`: `# ENTITY/DTOS`, `# ENTITY/MODELS`, `# ENTITY/CACHE`
- `exceptions.py`: `{Module}Exception` + one per business rule
- `utils.py`: Module-local helpers

#### 3. Infrastructure Layer (`infrastructure/`)
- `models.py`: SQLAlchemy extending `BaseModel`
- `repositories.py`: `Postgres{Entity}Repository` — `flush()` never `commit()`
- `caches.py`: `Redis{Entity}Cache` — namespaced, tombstoned, never raises
- `services.py`: External systems behind Protocol

#### 4. Presentation Layer (`presentation/`)
- `routers.py`: `payload → mapper → use case → mapper → return`
- `schemas.py`: Pydantic v2 with full `Field` + `ConfigDict`
- `docs.py`: `router_docs` + one `{action}_docs` per endpoint
- `dependencies.py`: `Depends` factories returning Protocol type

#### 5. Error Handling (3 shapes)

```python
# 3-branch: Use cases + router handlers
try:
    ...
except StandardException:
    raise                          # ต้องมาก่อนเสมอ
except DomainError as e:
    raise DomainException(e)
except Exception as e:
    logger.opt(exception=e).error("Error in {module} endpoint.")
    raise {Module}Exception()

# 2-branch: Repositories + services
try:
    ...
except StandardException:
    raise
except Exception as e:
    logger.opt(exception=e).error("Error in {module} repository.")
    raise {Module}Exception()

# Never-raise: Caches
try:
    ...
except Exception as e:
    logger.opt(exception=e).error("Cache error. Falling back to DB.")
    return None
```

#### 6. Invariants ที่ต้องรักษา
- `{module_specific_invariants}`

#### 7. Domain Events
- `{Module}Created`, `{Module}Updated`, `{Module}Deleted`
- `{module_specific_events}`

#### 8. Tests
- Unit test สำหรับ use cases (in-memory fakes)
- Integration test สำหรับ repository
- Property-based test สำหรับ invariants

**Output:**
- ไฟล์ครบ 16 ไฟล์ (4 layers × 4 ไฟล์)
- Comment 2 ภาษา (ไทย + English)
- พร้อมรันด้วย `uvicorn app.app:app --reload`

---

## 📐 โครงสร้างไฟล์ Output (16 ไฟล์)

```
app/modules/{module_name}/
├── domain/
│   ├── entities.py
│   ├── value_objects.py
│   └── enums.py
├── application/
│   ├── interfaces.py
│   ├── use_cases.py
│   ├── mappers.py
│   ├── exceptions.py
│   └── utils.py
├── infrastructure/
│   ├── models.py
│   ├── repositories.py
│   ├── caches.py
│   └── services.py
└── presentation/
    ├── routers.py
    ├── schemas.py
    ├── docs.py
    └── dependencies.py
```

---

## ✅ Checklist ก่อนส่ง

- [ ] Domain layer ไม่ import framework
- [ ] ใช้ `flush()` ไม่ใช่ `commit()` ใน repository
- [ ] Cache never raises
- [ ] Error handling ถูก shape (3/2/never)
- [ ] Idempotency ครบ (money/goods path)
- [ ] Audit log ครบ
- [ ] Read-back verification ครบ
- [ ] Tests ครบ 3 ประเภท
- [ ] Comment 2 ภาษา
- [ ] พร้อมรัน
```

---

## 📑 ไฟล์ 2: `docs/prompts/README.md` (Index)

```markdown
# 📑 Module Prompts Index

รายการ AI Prompt สำหรับสร้าง Module ทั้งหมด **65 modules** แบ่งตาม Layer

---

## Layer 0: CORE (cross-cutting)

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 1 | `money` | 🔴 | 1 | [money.md](layer-0-core/money.md) |
| 2 | `tenant_context` | 🔴 | 1 | [tenant_context.md](layer-0-core/tenant_context.md) |
| 3 | `audit` | 🔴 | 1 | [audit.md](layer-0-core/audit.md) |
| 4 | `idempotency` | 🔴 | 1 | [idempotency.md](layer-0-core/idempotency.md) |
| 5 | `config` | 🔴 | 1 | [config.md](layer-0-core/config.md) |
| 6 | `events` | 🔴 | 1 | [events.md](layer-0-core/events.md) |

## Layer 1: FOUNDATION

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 7 | `tenancy` | 🔴 | 1 | [tenancy.md](layer-1-foundation/tenancy.md) |
| 8 | `authentication` | 🔴 | 1 | [authentication.md](layer-1-foundation/authentication.md) |
| 9 | `user` | 🔴 | 1 | [user.md](layer-1-foundation/user.md) |
| 10 | `employee` | 🟠 | 1 | [employee.md](layer-1-foundation/employee.md) |
| 11 | `customer` | 🔴 | 1 | [customer.md](layer-1-foundation/customer.md) |
| 12 | `supplier` | 🟠 | 1 | [supplier.md](layer-1-foundation/supplier.md) |
| 13 | `product` | 🔴 | 1 | [product.md](layer-1-foundation/product.md) |
| 14 | `pricing` | 🔴 | 1 | [pricing.md](layer-1-foundation/pricing.md) |

## Layer 2: MONEY PATH (ERP)

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 15 | `order` | 🔴 | 1 | [order.md](layer-2-money-path/order.md) |
| 16 | `invoice` | 🔴 | 1 | [invoice.md](layer-2-money-path/invoice.md) |
| 17 | `ledger` | 🔴 | 1 | [ledger.md](layer-2-money-path/ledger.md) |
| 18 | `payment` | 🔴 | 2 | [payment.md](layer-2-money-path/payment.md) |
| 19 | `accounting_gateway` | 🔴 | 2 | [accounting_gateway.md](layer-2-money-path/accounting_gateway.md) |
| 20 | `tax` | 🔴 | 2 | [tax.md](layer-2-money-path/tax.md) |
| 21 | `reconciliation` | 🔴 | 1 | [reconciliation.md](layer-2-money-path/reconciliation.md) |

## Layer 3: GOODS PATH (Production + Agriculture)

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 22 | `inventory` | 🔴 | 1 | [inventory.md](layer-3-goods-path/inventory.md) |
| 23 | `warehouse` | 🔴 | 1 | [warehouse.md](layer-3-goods-path/warehouse.md) |
| 24 | `lot` | 🔴 | 1 | [lot.md](layer-3-goods-path/lot.md) |
| 25 | `production` | 🔴 | 1 | [production.md](layer-3-goods-path/production.md) |
| 26 | `recipe` | 🟠 | 1 | [recipe.md](layer-3-goods-path/recipe.md) |
| 27 | `quality` | 🟠 | 1 | [quality.md](layer-3-goods-path/quality.md) |
| 28 | `waste` | 🟠 | 1 | [waste.md](layer-3-goods-path/waste.md) |
| 29 | `procurement` | 🟠 | 1 | [procurement.md](layer-3-goods-path/procurement.md) |
| 30 | `traceability` | 🔴 | 2 | [traceability.md](layer-3-goods-path/traceability.md) |
| 31 | `agriculture` | 🟠 | 4 | [agriculture.md](layer-3-goods-path/agriculture.md) |
| 32 | `crop` | 🟠 | 4 | [crop.md](layer-3-goods-path/crop.md) |
| 33 | `soil` | 🟠 | 4 | [soil.md](layer-3-goods-path/soil.md) |
| 34 | `irrigation` | 🟠 | 4 | [irrigation.md](layer-3-goods-path/irrigation.md) |

## Layer 4: OPERATIONS

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 35 | `transport` | 🟠 | 4 | [transport.md](layer-4-operations/transport.md) |
| 36 | `delivery` | 🟠 | 4 | [delivery.md](layer-4-operations/delivery.md) |
| 37 | `route` | 🟠 | 4 | [route.md](layer-4-operations/route.md) |
| 38 | `gps` | 🟠 | 4 | [gps.md](layer-4-operations/gps.md) |
| 39 | `retail` | 🟠 | 4 | [retail.md](layer-4-operations/retail.md) |
| 40 | `pos` | 🟠 | 4 | [pos.md](layer-4-operations/pos.md) |
| 41 | `shift` | 🟠 | 4 | [shift.md](layer-4-operations/shift.md) |
| 42 | `line_channel` | 🟠 | 4 | [line_channel.md](layer-4-operations/line_channel.md) |
| 43 | `promotion` | 🟡 | 4 | [promotion.md](layer-4-operations/promotion.md) |
| 44 | `loyalty` | 🟡 | 4 | [loyalty.md](layer-4-operations/loyalty.md) |
| 45 | `crm` | 🟠 | 5 | [crm.md](layer-4-operations/crm.md) |
| 46 | `campaign` | 🟡 | 5 | [campaign.md](layer-4-operations/campaign.md) |
| 47 | `support` | 🟡 | 5 | [support.md](layer-4-operations/support.md) |

## Layer 5: INTELLIGENCE

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 48 | `reporting` | 🔴 | 5 | [reporting.md](layer-5-intelligence/reporting.md) |
| 49 | `analytics` | 🟠 | 5 | [analytics.md](layer-5-intelligence/analytics.md) |
| 50 | `forecast` | 🟠 | 5 | [forecast.md](layer-5-intelligence/forecast.md) |
| 51 | `kpi` | 🟠 | 5 | [kpi.md](layer-5-intelligence/kpi.md) |
| 52 | `satisfaction` | 🟡 | 5 | [satisfaction.md](layer-5-intelligence/satisfaction.md) |
| 53 | `recommendation` | 🟡 | 5 | [recommendation.md](layer-5-intelligence/recommendation.md) |
| 54 | `oee` | 🟠 | 5 | [oee.md](layer-5-intelligence/oee.md) |

## Layer 6: MONITORING & SENSING

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 55 | `iot` | 🟠 | 4 | [iot.md](layer-6-monitoring/iot.md) |
| 56 | `cctv` | 🟡 | 4 | [cctv.md](layer-6-monitoring/cctv.md) |
| 57 | `monitoring` | 🔴 | 1 | [monitoring.md](layer-6-monitoring/monitoring.md) |
| 58 | `backup` | 🔴 | 1 | [backup.md](layer-6-monitoring/backup.md) |
| 59 | `alerting` | 🟠 | 1 | [alerting.md](layer-6-monitoring/alerting.md) |
| 60 | `audit_viewer` | 🟠 | 2 | [audit_viewer.md](layer-6-monitoring/audit_viewer.md) |
| 61 | `maintenance` | 🟠 | 5 | [maintenance.md](layer-6-monitoring/maintenance.md) |
| 62 | `energy` | 🟡 | 5 | [energy.md](layer-6-monitoring/energy.md) |

## Layer 7: TEMPLATES

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 63 | `health` | 🔴 | 1 | [health.md](layer-7-templates/health.md) |
| 64 | `example` | 🟢 | 1 | [example.md](layer-7-templates/example.md) |
| 65 | `blank` | 🟢 | 1 | [blank.md](layer-7-templates/blank.md) |

---

## 🚀 วิธีใช้

1. เปิดไฟล์ prompt ที่ต้องการ เช่น `docs/prompts/layer-3-goods-path/agriculture.md`
2. Copy prompt ไปวางใน AI (ChatGPT, Claude, Gemini)
3. AI จะสร้าง 16 ไฟล์ตาม template
4. ตรวจสอบ checklist ก่อน merge

## 📐 ลำดับการสร้างที่แนะนำ

```
Phase 1:  Layer 0 (Core) → Layer 1 (Foundation) → Layer 2 (Money) → Layer 3 (Goods)
Phase 2:  Layer 4 (Operations) → Layer 5 (Intelligence)
Phase 3:  Layer 6 (Monitoring) → Layer 7 (Templates)
```
```

---

## 📄 ไฟล์ 3: ตัวอย่าง `docs/prompts/layer-0-core/money.md`

```markdown
# AI Prompt — Module `money`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `money` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | Core (cross-cutting) |
| **Dependencies** | ไม่มี (primitive module) |
| **Domain Concepts** | `Money` (VO), `Currency` (enum), `VAT` (VO) |

---

## 🎯 Prompt

### สร้าง Module `money`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- Module นี้เป็น **primitive module** — ไม่มี persistence, ไม่มี cache
- ใช้ Decimal เท่านั้น (ห้ามใช้ float)
- Money is Domain Invariant — ต้องแม่นยำ 100%

**ข้อกำหนด:**

#### 1. Domain Layer

**`domain/value_objects.py` — Money (VO)**
```python
from decimal import Decimal
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    """Money value object — วัตถุค่าเงิน"""
    amount: Decimal
    currency: str = "THB"
    
    def __post_init__(self):
        # Normalize: quantize to 2 decimal places
        # ทำให้เป็นมาตรฐาน: ปัดทศนิยม 2 ตำแหน่ง
        object.__setattr__(self, "amount", self.amount.quantize(Decimal("0.01")))
        self._validate()
    
    def _validate(self) -> None:
        """Validate money — ตรวจสอบเงิน"""
        if not isinstance(self.amount, Decimal):
            raise DomainError("Amount must be Decimal")
        if self.currency not in ("THB", "USD", "EUR"):
            raise DomainError(f"Unsupported currency: {self.currency}")
    
    def __add__(self, other: "Money") -> "Money":
        """Add two money — บวกเงิน"""
        if self.currency != other.currency:
            raise DomainError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: "Money") -> "Money":
        """Subtract money — ลบเงิน"""
        if self.currency != other.currency:
            raise DomainError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, factor: Decimal) -> "Money":
        """Multiply money — คูณเงิน"""
        return Money(self.amount * factor, self.currency)
    
    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
```

**`domain/value_objects.py` — VAT (VO)**
```python
@dataclass(frozen=True)
class VAT:
    """VAT value object — วัตถุค่าภาษีมูลค่าเพิ่ม"""
    rate: Decimal  # e.g., 0.07 for 7%
    
    def calculate(self, base: Money) -> Money:
        """Calculate VAT — คำนวณภาษี"""
        return Money(base.amount * self.rate, base.currency)
    
    def extract(self, total: Money) -> Money:
        """Extract VAT from total — แยกภาษีจากยอดรวม"""
        base = total.amount / (Decimal("1") + self.rate)
        return Money(total.amount - base, total.currency)
```

**`domain/enums.py`**
```python
from enum import Enum

class Currency(str, Enum):
    THB = "THB"
    USD = "USD"
    EUR = "EUR"

class VATRate(str, Enum):
    ZERO = "0.00"
    SEVEN = "0.07"
```

#### 2. Application Layer

**`application/use_cases.py`**
```python
class MoneyUseCases:
    """Money use cases — กรณีการใช้งานเงิน"""
    
    def add(self, a: Money, b: Money) -> Money:
        """Add two money — บวกเงิน"""
        return a + b
    
    def subtract(self, a: Money, b: Money) -> Money:
        """Subtract money — ลบเงิน"""
        return a - b
    
    def calculate_vat(self, base: Money, rate: VATRate) -> Money:
        """Calculate VAT — คำนวณภาษี"""
        vat = VAT(Decimal(rate.value))
        return vat.calculate(base)
    
    def extract_vat(self, total: Money, rate: VATRate) -> Money:
        """Extract VAT from total — แยกภาษีจากยอดรวม"""
        vat = VAT(Decimal(rate.value))
        return vat.extract(total)
```

#### 3. Infrastructure Layer
- **ไม่มี** `models.py` (pure VO)
- **ไม่มี** `repositories.py` (pure computation)
- **ไม่มี** `caches.py` (pure computation)
- **ไม่มี** `services.py`

#### 4. Presentation Layer

**`presentation/schemas.py`**
```python
from pydantic import BaseModel, Field
from decimal import Decimal

class MoneySchema(BaseModel):
    """Money schema — สคีมาเงิน"""
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="THB", pattern="^(THB|USD|EUR)$")
    
    model_config = ConfigDict(from_attributes=True)
```

#### 5. Error Handling
- Use cases: 3-branch
- ไม่มี repository/cache

#### 6. Invariants
- `Decimal` precision (2 decimal places)
- `a + b == b + a` (commutative)
- `(a + b) + c == a + (b + c)` (associative)
- `a + Money(0) == a` (identity)
- `sum(debit) == sum(credit)` (in ledger context)

#### 7. Domain Events
- `MoneyAdded`, `MoneySubtracted`

#### 8. Tests

```python
# tests/unit/test_money.py
import pytest
from decimal import Decimal
from app.modules.money.domain.value_objects import Money, VAT

def test_money_addition():
    """Test money addition — ทดสอบการบวกเงิน"""
    a = Money(Decimal("100.00"))
    b = Money(Decimal("50.00"))
    assert a + b == Money(Decimal("150.00"))

def test_money_commutative():
    """Test commutative property — ทดสอบสมบัติการสลับที่"""
    a = Money(Decimal("100.00"))
    b = Money(Decimal("50.00"))
    assert a + b == b + a

def test_money_associative():
    """Test associative property — ทดสอบสมบัติการจัดกลุ่ม"""
    a = Money(Decimal("100.00"))
    b = Money(Decimal("50.00"))
    c = Money(Decimal("25.00"))
    assert (a + b) + c == a + (b + c)

def test_money_identity():
    """Test identity — ทดสอบเอกลักษณ์"""
    a = Money(Decimal("100.00"))
    assert a + Money(Decimal("0.00")) == a

def test_vat_calculation():
    """Test VAT 7% for 100.00 = 7.00 — ทดสอบภาษี 7%"""
    base = Money(Decimal("100.00"))
    vat = VAT(Decimal("0.07"))
    assert vat.calculate(base) == Money(Decimal("7.00"))

def test_vat_extract():
    """Test VAT extract from total — ทดสอบการแยกภาษี"""
    total = Money(Decimal("107.00"))
    vat = VAT(Decimal("0.07"))
    assert vat.extract(total) == Money(Decimal("7.00"))

def test_money_different_currency():
    """Test different currency error — ทดสอบ error สกุลต่าง"""
    a = Money(Decimal("100.00"), "THB")
    b = Money(Decimal("50.00"), "USD")
    with pytest.raises(DomainError):
        a + b
```

**Output:**
- ไฟล์ ~8 ไฟล์ (module เล็ก)
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 4: ตัวอย่าง `docs/prompts/layer-2-money-path/invoice.md`

```markdown
# AI Prompt — Module `invoice`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `invoice` |
| **Layer** | `2` (Money Path) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **มิติธุรกิจ** | ERP |
| **Dependencies** | `money`, `order`, `tax`, `ledger`, `audit`, `idempotency` |
| **Domain Concepts** | `Invoice` (entity), `InvoiceLine` (VO), `InvoiceStatus` (enum) |

---

## 🎯 Prompt

### สร้าง Module `invoice`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Module นี้เป็น **Money Path** — ต้อง idempotent, audit, read-back
- **Invariants:** `total = sum(lines) + VAT`, `invoice_number unique`

**ข้อกำหนด:**

#### 1. Domain Layer

**`domain/entities.py`**
```python
from dataclasses import dataclass, field
from datetime import datetime
from app.modules.shared.domain.entities import BaseEntity, DomainError

@dataclass
class Invoice(BaseEntity):
    """Invoice entity — เอนทิตีใบกำกับภาษี"""
    invoice_number: str = ""
    customer_id: str = ""
    lines: list = field(default_factory=list)
    subtotal: Decimal = Decimal("0.00")
    vat: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    status: str = "DRAFT"
    issued_at: datetime | None = None
    
    def __post_init__(self):
        self._validate()
        self._recalculate()
    
    def _validate(self) -> None:
        if not self.customer_id:
            raise DomainError("Customer ID is required")
        if not self.lines:
            raise DomainError("Invoice must have at least one line")
    
    def _recalculate(self) -> None:
        """Recalculate totals — คำนวณยอดใหม่"""
        self.subtotal = sum(line.amount for line in self.lines)
        self.vat = self.subtotal * Decimal("0.07")
        self.total = self.subtotal + self.vat
    
    def add_line(self, line: "InvoiceLine") -> None:
        """Add line — เพิ่มรายการ"""
        if self.status != "DRAFT":
            raise DomainError("Cannot add line to non-draft invoice")
        self.lines.append(line)
        self._recalculate()
    
    def issue(self) -> None:
        """Issue invoice — ออกใบกำกับ"""
        if self.status != "DRAFT":
            raise DomainError(f"Cannot issue invoice with status {self.status}")
        self.status = "ISSUED"
        self.issued_at = datetime.utcnow()
    
    def pay(self) -> None:
        """Pay invoice — ชำระเงิน"""
        if self.status != "ISSUED":
            raise DomainError(f"Cannot pay invoice with status {self.status}")
        self.status = "PAID"
    
    def void(self, reason: str) -> None:
        """Void invoice — ยกเลิก"""
        if self.status == "PAID":
            raise DomainError("Cannot void paid invoice")
        self.status = "VOIDED"
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class InvoiceLine:
    """Invoice line — รายการในใบกำกับ"""
    product_id: str
    qty: Decimal
    unit_price: Decimal
    
    @property
    def amount(self) -> Decimal:
        return self.qty * self.unit_price
    
    def __post_init__(self):
        if self.qty <= 0:
            raise DomainError("Quantity must be positive")
        if self.unit_price < 0:
            raise DomainError("Unit price cannot be negative")

@dataclass(frozen=True)
class InvoiceNumber:
    """Invoice number VO — วัตถุเลขที่ใบกำกับ"""
    value: str
    
    PATTERN = r"^INV-\d{6}-\d{4}$"  # INV-YYYYMM-XXXX
    
    def __post_init__(self):
        import re
        if not re.match(self.PATTERN, self.value):
            raise DomainError(f"Invalid invoice number: {self.value}")
```

**`domain/enums.py`**
```python
class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    VOIDED = "VOIDED"
    OVERDUE = "OVERDUE"
```

#### 2. Application Layer

**`application/interfaces.py`**
```python
from typing import Protocol
from app.modules.invoice.domain.entities import Invoice

class IInvoiceRepository(Protocol):
    async def save(self, invoice: Invoice) -> Invoice: ...
    async def get_by_id(self, id: str) -> Invoice | None: ...
    async def get_by_number(self, number: str) -> Invoice | None: ...
    async def list(self, page: int, limit: int) -> tuple[list[Invoice], int]: ...

class IInvoiceCache(Protocol):
    async def get(self, id: str) -> Invoice | None: ...
    async def insert(self, id: str, invoice: Invoice) -> None: ...
    async def delete(self, id: str) -> None: ...

class IInvoiceService(Protocol):
    async def generate_number(self) -> str: ...
```

**`application/use_cases.py`**
```python
class InvoiceUseCases:
    """Invoice use cases — กรณีการใช้งานใบกำกับ"""
    
    def __init__(
        self,
        repo: IInvoiceRepository,
        cache: IInvoiceCache,
        service: IInvoiceService,
        idempotency: IIdempotencyService,
        audit: IAuditService,
        events: IEventBus,
    ):
        self.repo = repo
        self.cache = cache
        self.service = service
        self.idempotency = idempotency
        self.audit = audit
        self.events = events
    
    async def create_invoice(self, payload: dict, idem_key: str) -> Invoice:
        """Create invoice — สร้างใบกำกับ"""
        try:
            # Check idempotency — ตรวจสอบ idempotency
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing
            
            # Create entity — สร้างเอนทิตี
            invoice = Invoice(**payload)
            
            # Generate number — สร้างเลขที่
            invoice.invoice_number = await self.service.generate_number()
            
            # Save — บันทึก
            invoice = await self.repo.save(invoice)
            
            # Read-back verification — ตรวจสอบการอ่านกลับ
            verified = await self.repo.get_by_id(invoice.id)
            if not verified or verified.total != invoice.total:
                raise InvoiceException("Read-back verification failed")
            
            # Audit — บันทึก audit
            await self.audit.log("invoice.created", invoice.id)
            
            # Idempotency — เก็บ idempotency
            await self.idempotency.set(idem_key, invoice)
            
            # Event — ส่ง event
            await self.events.publish("InvoiceIssued", invoice)
            
            return invoice
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_invoice")
            raise InvoiceException()
```

#### 3. Infrastructure Layer

**`infrastructure/models.py`**
```python
from sqlalchemy import Column, String, Numeric, DateTime, Index, UniqueConstraint
from app.modules.shared.infrastructure.models import BaseModel

class InvoiceModel(BaseModel):
    """Invoice SQLAlchemy model — โมเดล SQLAlchemy"""
    __tablename__ = "invoices"
    
    invoice_number = Column(String(50), nullable=False, unique=True)
    customer_id = Column(String(36), nullable=False, index=True)
    subtotal = Column(Numeric(15, 2), nullable=False)
    vat = Column(Numeric(15, 2), nullable=False)
    total = Column(Numeric(15, 2), nullable=False)
    status = Column(String(20), nullable=False, index=True)
    issued_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        UniqueConstraint("invoice_number", name="uq_invoices_invoice_number"),
        Index("ix_invoices_customer_id", "customer_id"),
        Index("ix_invoices_status", "status"),
    )
```

**`infrastructure/repositories.py`**
```python
class PostgresInvoiceRepository:
    """Postgres invoice repository — รีโพซิทอรีใบกำกับ"""
    
    def __init__(self, session):
        self.session = session
    
    async def save(self, invoice: Invoice) -> Invoice:
        """Save invoice — บันทึกใบกำกับ"""
        try:
            model = InvoiceMapper.to_model(invoice)
            self.session.add(model)
            await self.session.flush()  # flush, never commit
            return InvoiceMapper.to_entity(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in save invoice")
            raise InvoiceException()
    
    async def generate_number(self) -> str:
        """Generate invoice number — สร้างเลขที่"""
        # SELECT FOR UPDATE to prevent race
        result = await self.session.execute(
            text("SELECT nextval('invoice_number_seq')")
        )
        seq = result.scalar()
        return f"INV-{datetime.utcnow():%Y%m}-{seq:04d}"
```

**`infrastructure/caches.py`**
```python
class RedisInvoiceCache:
    """Redis invoice cache — แคชใบกำกับ"""
    
    def __init__(self, redis):
        self.redis = redis
        self.namespace = settings.REDIS_NAMESPACE
    
    async def get(self, id: str) -> Invoice | None:
        try:
            data = await self.redis.get(f"{self.namespace}:invoice:{id}")
            return InvoiceMapper.from_cache(data) if data else None
        except Exception as e:
            logger.opt(exception=e).error("Cache get failed. Falling back.")
            return None  # Never raise
    
    async def delete(self, id: str) -> None:
        try:
            # Write tombstone BEFORE delete
            await self.redis.setex(
                f"{self.namespace}:tombstone:invoice:{id}",
                settings.REDIS_TOMBSTONE_TTL_SECONDS,
                "1"
            )
            await self.redis.delete(f"{self.namespace}:invoice:{id}")
        except Exception as e:
            logger.opt(exception=e).error("Cache delete failed.")
```

#### 4. Presentation Layer

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/invoice", tags=["Invoice"])

@router.post("/", status_code=201)
async def create_invoice(
    payload: InvoiceCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    use_cases: InvoiceUseCases = Depends(get_invoice_use_cases),
    auth: Authentication = Depends(authenticate_user),
):
    """Create invoice — สร้างใบกำกับ"""
    entity = InvoiceMapper.to_entity(payload)
    result = await use_cases.create_invoice(entity, idem_key)
    return InvoiceMapper.to_response(result)

@router.patch("/{id}/issue/")
async def issue_invoice(id: str, ...): ...

@router.patch("/{id}/pay/")
async def pay_invoice(id: str, ...): ...

@router.delete("/{id}/")
async def void_invoice(id: str, ...): ...
```

#### 5. Tests

```python
# tests/unit/test_invoice.py
async def test_create_invoice_valid():
    """Test create invoice — ทดสอบสร้างใบกำกับ"""
    use_cases = InvoiceUseCases(fake_repo, fake_cache, ...)
    invoice = await use_cases.create_invoice({...}, "idem-001")
    assert invoice.status == "DRAFT"
    assert invoice.total == invoice.subtotal + invoice.vat

async def test_invoice_total_invariant():
    """Property-based: total = sum(lines) + VAT — ทดสอบ invariant"""
    for _ in range(100):
        lines = [random_line() for _ in range(random.randint(1, 10))]
        invoice = Invoice(customer_id="c1", lines=lines)
        assert invoice.total == invoice.subtotal + invoice.vat

async def test_concurrent_number_generation():
    """Test concurrent invoice number — ทดสอบเลขที่พร้อมกัน"""
    # Spawn 100 concurrent create_invoice
    # Verify all numbers unique
```

**Output:**
- 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 5: ตัวอย่าง `docs/prompts/layer-3-goods-path/agriculture.md`

```markdown
# AI Prompt — Module `agriculture`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `agriculture` |
| **Layer** | `3` (Goods Path) |
| **Priority** | 🟠 |
| **Phase** | 4 |
| **มิติธุรกิจ** | 🌾 เกษตร |
| **Dependencies** | `crop`, `soil`, `irrigation`, `iot`, `forecast`, `inventory`, `traceability` |
| **Domain Concepts** | `Farm` (entity), `Plot` (VO), `CropCycle` (VO), `Harvest` (VO) |

---

## 🎯 Prompt

### สร้าง Module `agriculture`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- มิติ: 🌾 เกษตร
- **Invariants:** `Harvest yield ≥ expected`, `Plot area > 0`
- **Events:** `FarmCreated`, `PlotPlanted`, `CropHarvested`, `YieldRecorded`

**ข้อกำหนด:**

#### 1. Domain Layer

**`domain/entities.py` — Farm**
```python
from dataclasses import dataclass, field
from app.modules.shared.domain.entities import BaseEntity, DomainError

@dataclass
class Farm(BaseEntity):
    """Farm entity — เอนทิตีฟาร์ม"""
    code: str = ""
    name: str = ""
    location: str = ""
    area: float = 0.0
    plots: list = field(default_factory=list)
    owner_id: str = ""
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self) -> None:
        """Validate farm data — ตรวจสอบข้อมูลฟาร์ม"""
        if not self.code:
            raise DomainError("Farm code is required")
        if self.area <= 0:
            raise DomainError("Farm area must be positive")
    
    def add_plot(self, plot: "Plot") -> None:
        """Add plot — เพิ่มแปลง"""
        if any(p.code == plot.code for p in self.plots):
            raise DomainError(f"Plot {plot.code} already exists")
        self.plots.append(plot)
    
    def remove_plot(self, plot_code: str) -> None:
        """Remove plot — ลบแปลง"""
        self.plots = [p for p in self.plots if p.code != plot_code]
    
    def get_total_area(self) -> float:
        """Get total plot area — พื้นที่รวม"""
        return sum(p.area for p in self.plots)
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Plot:
    """Plot VO — แปลงปลูก"""
    code: str
    area: float
    crop_id: str | None = None
    planted_at: datetime | None = None
    expected_yield: float = 0.0
    
    def __post_init__(self):
        if self.area <= 0:
            raise DomainError("Plot area must be positive")

@dataclass(frozen=True)
class CropCycle:
    """Crop cycle VO — รอบปลูก"""
    crop_id: str
    start: datetime
    end: datetime | None
    yield_amount: float = 0.0
    status: str = "PLANTED"
    
    def __post_init__(self):
        if self.end and self.end < self.start:
            raise DomainError("End date must be after start date")

@dataclass(frozen=True)
class Harvest:
    """Harvest VO — ผลผลิต"""
    plot_id: str
    qty: float
    quality: str
    harvested_at: datetime
    
    def __post_init__(self):
        if self.qty < 0:
            raise DomainError("Harvest quantity cannot be negative")
        if self.quality not in ("A", "B", "C", "REJECT"):
            raise DomainError(f"Invalid quality: {self.quality}")
```

**`domain/enums.py`**
```python
class PlotStatus(str, Enum):
    IDLE = "IDLE"
    PLANTED = "PLANTED"
    GROWING = "GROWING"
    HARVESTED = "HARVESTED"
    FALLOW = "FALLOW"

class CropType(str, Enum):
    RICE = "RICE"
    VEGETABLE = "VEGETABLE"
    FRUIT = "FRUIT"
    MUSHROOM = "MUSHROOM"
    HERB = "HERB"

class Quality(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    REJECT = "REJECT"
```

#### 2. Application Layer

**`application/interfaces.py`**
```python
class IFarmRepository(Protocol):
    async def save(self, farm: Farm) -> Farm: ...
    async def get_by_id(self, id: str) -> Farm | None: ...
    async def list(self, page: int, limit: int) -> tuple[list[Farm], int]: ...

class IFarmCache(Protocol):
    async def get(self, id: str) -> Farm | None: ...
    async def insert(self, id: str, farm: Farm) -> None: ...
    async def delete(self, id: str) -> None: ...

class IAgricultureService(Protocol):
    async def get_weather(self, location: str) -> dict: ...
    async def get_satellite_image(self, plot_id: str) -> bytes: ...
    async def detect_disease(self, image: bytes) -> dict: ...
```

**`application/use_cases.py`**
```python
class AgricultureUseCases:
    """Agriculture use cases — กรณีการใช้งานเกษตร"""
    
    def __init__(
        self,
        repo: IFarmRepository,
        cache: IFarmCache,
        service: IAgricultureService,
        inventory: IInventoryService,
        idempotency: IIdempotencyService,
        audit: IAuditService,
        events: IEventBus,
    ):
        ...
    
    async def create_farm(self, payload: dict, idem_key: str) -> Farm:
        """Create farm — สร้างฟาร์ม"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing
            
            farm = Farm(**payload)
            farm = await self.repo.save(farm)
            
            # Read-back verification
            verified = await self.repo.get_by_id(farm.id)
            if not verified or verified.code != farm.code:
                raise AgricultureException("Read-back failed")
            
            await self.audit.log("farm.created", farm.id)
            await self.idempotency.set(idem_key, farm)
            await self.events.publish("FarmCreated", farm)
            
            return farm
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_farm")
            raise AgricultureException()
    
    async def add_plot(self, farm_id: str, payload: dict) -> Farm:
        """Add plot to farm — เพิ่มแปลงในฟาร์ม"""
        try:
            farm = await self.repo.get_by_id(farm_id)
            if not farm:
                raise FarmNotFoundException()
            
            plot = Plot(**payload)
            farm.add_plot(plot)
            farm = await self.repo.save(farm)
            
            await self.cache.delete(farm_id)
            await self.audit.log("plot.added", farm_id)
            
            return farm
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in add_plot")
            raise AgricultureException()
    
    async def plant_crop(self, plot_id: str, crop_id: str) -> Farm:
        """Plant crop in plot — ปลูกพืชในแปลง"""
        try:
            farm = await self.repo.get_by_plot(plot_id)
            if not farm:
                raise FarmNotFoundException()
            
            plot = next((p for p in farm.plots if p.code == plot_id), None)
            if not plot:
                raise PlotNotFoundException()
            
            # Update plot with crop
            new_plot = Plot(
                code=plot.code,
                area=plot.area,
                crop_id=crop_id,
                planted_at=datetime.utcnow(),
            )
            farm.remove_plot(plot.code)
            farm.add_plot(new_plot)
            
            farm = await self.repo.save(farm)
            await self.cache.delete(farm.id)
            await self.audit.log("plot.planted", plot_id)
            await self.events.publish("PlotPlanted", {"farm_id": farm.id, "plot_id": plot_id})
            
            return farm
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in plant_crop")
            raise AgricultureException()
    
    async def harvest(self, plot_id: str, qty: float, quality: str, idem_key: str) -> Harvest:
        """Harvest crop — เก็บเกี่ยว"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing
            
            # Validate
            harvest = Harvest(
                plot_id=plot_id,
                qty=qty,
                quality=quality,
                harvested_at=datetime.utcnow(),
            )
            
            # Update inventory
            await self.inventory.post_movement({
                "product_id": plot_id,
                "type": "IN",
                "qty": qty,
                "reference": f"HARVEST-{idem_key}",
            })
            
            await self.audit.log("crop.harvested", plot_id)
            await self.idempotency.set(idem_key, harvest)
            await self.events.publish("CropHarvested", harvest)
            await self.events.publish("YieldRecorded", {"plot_id": plot_id, "qty": qty})
            
            return harvest
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in harvest")
            raise AgricultureException()
    
    async def get_yield(self, plot_id: str) -> dict:
        """Get yield — ดูผลผลิต"""
        try:
            # Aggregate from harvest records
            ...
        except Exception as e:
            logger.opt(exception=e).error("Error in get_yield")
            raise AgricultureException()
    
    async def detect_disease(self, plot_id: str, image: bytes) -> dict:
        """Detect disease from image — ตรวจจับโรคจากภาพ"""
        try:
            result = await self.service.detect_disease(image)
            if result["confidence"] > 0.9:
                await self.events.publish("DiseaseDetected", {
                    "plot_id": plot_id,
                    "disease": result["disease"],
                })
            return result
        except Exception as e:
            logger.opt(exception=e).error("Error in detect_disease")
            raise AgricultureException()
```

#### 3. Infrastructure Layer

**`infrastructure/models.py`**
```python
class FarmModel(BaseModel):
    __tablename__ = "farms"
    
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(500))
    area = Column(Numeric(10, 2), nullable=False)
    owner_id = Column(String(36), index=True)
    
    plots = relationship("PlotModel", back_populates="farm", cascade="all, delete-orphan")

class PlotModel(BaseModel):
    __tablename__ = "plots"
    
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    area = Column(Numeric(10, 2), nullable=False)
    crop_id = Column(String(36), nullable=True)
    planted_at = Column(DateTime, nullable=True)
    expected_yield = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="IDLE")
    
    farm = relationship("FarmModel", back_populates="plots")
    
    __table_args__ = (
        UniqueConstraint("farm_id", "code", name="uq_plots_farm_code"),
    )
```

**`infrastructure/services.py`**
```python
class SatelliteService:
    """Satellite service — บริการดาวเทียม"""
    async def get_image(self, plot_id: str) -> bytes:
        ...

class WeatherService:
    """Weather service — บริการพยากรณ์อากาศ"""
    async def get_forecast(self, location: str, days: int) -> list[dict]:
        ...

class DiseaseDetectionService:
    """Disease detection service — บริการตรวจจับโรค"""
    async def detect(self, image: bytes) -> dict:
        # Use YOLOv8 model
        ...
```

#### 4. Presentation Layer

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/agriculture", tags=["Agriculture"])

@router.post("/farm/", status_code=201)
async def create_farm(
    payload: FarmCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    use_cases: AgricultureUseCases = Depends(get_agriculture_use_cases),
    auth: Authentication = Depends(authenticate_user),
): ...

@router.post("/farm/{id}/plot/")
async def add_plot(id: str, payload: PlotCreate, ...): ...

@router.patch("/plot/{id}/plant/")
async def plant_crop(id: str, payload: PlantRequest, ...): ...

@router.patch("/plot/{id}/harvest/")
async def harvest(id: str, payload: HarvestRequest, ...): ...

@router.get("/plot/{id}/yield/")
async def get_yield(id: str, ...): ...

@router.post("/plot/{id}/detect-disease/")
async def detect_disease(id: str, image: UploadFile, ...): ...
```

#### 5. Tests

```python
async def test_create_farm_valid():
    """Test create farm — ทดสอบสร้างฟาร์ม"""
    use_cases = AgricultureUseCases(fakes...)
    farm = await use_cases.create_farm({...}, "idem-001")
    assert farm.code == "FARM001"
    assert farm.area > 0

async def test_plant_crop_valid():
    """Test plant crop — ทดสอบปลูกพืช"""
    ...

async def test_harvest_updates_inventory():
    """Test harvest → inventory — ทดสอบเก็บเกี่ยว → สต็อก"""
    ...

async def test_harvest_yield_invariant():
    """Property-based: yield >= 0 — ทดสอบ invariant"""
    for _ in range(100):
        qty = random.uniform(0, 10000)
        harvest = Harvest(plot_id="p1", qty=qty, quality="A", harvested_at=now)
        assert harvest.qty >= 0

async def test_plot_area_invariant():
    """Property-based: plot area > 0 — ทดสอบ invariant"""
    with pytest.raises(DomainError):
        Plot(code="p1", area=-1)
```

**Output:**
- 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 6: ตัวอย่าง `docs/prompts/layer-4-operations/crm.md`

```markdown
# AI Prompt — Module `crm`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `crm` |
| **Layer** | `4` (Operations) |
| **Priority** | 🟠 |
| **Phase** | 5 |
| **มิติธุรกิจ** | 📞 CRM |
| **Dependencies** | `customer`, `line_channel`, `notification`, `campaign`, `invoice` |
| **Domain Concepts** | `Lead` (entity), `Deal` (entity), `Pipeline` (VO), `Activity` (VO) |

---

## 🎯 Prompt

### สร้าง Module `crm`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- มิติ: 📞 CRM (Lead → Customer → Loyalty → Satisfaction)
- **Invariants:** `Deal value >= 0`, `Pipeline stage sequential`
- **Events:** `LeadCreated`, `LeadConverted`, `DealCreated`, `DealWon`, `DealLost`

**ข้อกำหนด:**

#### 1. Domain Layer

**`domain/entities.py`**
```python
@dataclass
class Lead(BaseEntity):
    """Lead entity — เอนทิตีลีด"""
    name: str = ""
    contact: str = ""
    source: str = ""
    status: str = "NEW"
    assigned_to: str = ""
    
    def convert(self, customer_data: dict) -> "Customer":
        """Convert lead to customer — เปลี่ยนลีดเป็นลูกค้า"""
        if self.status == "CONVERTED":
            raise DomainError("Lead already converted")
        self.status = "CONVERTED"
        return Customer(**customer_data)

@dataclass
class Deal(BaseEntity):
    """Deal entity — เอนทิตีดีล"""
    customer_id: str = ""
    value: Decimal = Decimal("0.00")
    stage: str = "PROSPECTING"
    probability: int = 0
    expected_close: datetime | None = None
    
    def __post_init__(self):
        if self.value < 0:
            raise DomainError("Deal value cannot be negative")
        if not 0 <= self.probability <= 100:
            raise DomainError("Probability must be 0-100")
    
    def advance_stage(self, new_stage: str) -> None:
        """Advance deal stage — เลื่อนขั้นดีล"""
        stages = ["PROSPECTING", "QUALIFICATION", "PROPOSAL", "NEGOTIATION", "CLOSED_WON", "CLOSED_LOST"]
        current_idx = stages.index(self.stage)
        new_idx = stages.index(new_stage)
        if new_idx < current_idx:
            raise DomainError("Cannot move deal backward")
        self.stage = new_stage
```

**`domain/enums.py`**
```python
class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"

class DealStage(str, Enum):
    PROSPECTING = "PROSPECTING"
    QUALIFICATION = "QUALIFICATION"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"

class ActivityType(str, Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    LINE = "LINE"
    NOTE = "NOTE"
```

#### 2. Application Layer

**`application/use_cases.py`**
```python
class CRMUseCases:
    """CRM use cases — กรณีการใช้งาน CRM"""
    
    async def create_lead(self, payload: dict, idem_key: str) -> Lead:
        """Create lead — สร้างลีด"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing
            
            lead = Lead(**payload)
            lead = await self.repo.save_lead(lead)
            
            await self.audit.log("lead.created", lead.id)
            await self.idempotency.set(idem_key, lead)
            await self.events.publish("LeadCreated", lead)
            
            return lead
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in create_lead")
            raise CRMException()
    
    async def convert_lead(self, id: str, customer_data: dict) -> "Customer":
        """Convert lead to customer — เปลี่ยนลีดเป็นลูกค้า"""
        try:
            lead = await self.repo.get_lead(id)
            if not lead:
                raise LeadNotFoundException()
            
            customer = lead.convert(customer_data)
            customer = await self.customer_repo.save(customer)
            await self.repo.save_lead(lead)  # save updated status
            
            await self.audit.log("lead.converted", lead.id)
            await self.events.publish("LeadConverted", {"lead_id": lead.id, "customer_id": customer.id})
            
            return customer
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in convert_lead")
            raise CRMException()
    
    async def create_deal(self, payload: dict, idem_key: str) -> Deal:
        """Create deal — สร้างดีล"""
        ...
    
    async def update_deal_stage(self, id: str, stage: str) -> Deal:
        """Update deal stage — อัปเดตขั้นดีล"""
        ...
    
    async def get_pipeline(self, assigned_to: str) -> dict:
        """Get pipeline — ดู pipeline"""
        ...
```

#### 3. Tests

```python
async def test_create_lead():
    """Test create lead — ทดสอบสร้างลีด"""
    ...

async def test_convert_lead():
    """Test convert lead — ทดสอบเปลี่ยนลีด"""
    ...

async def test_deal_stage_forward_only():
    """Property-based: deal stage forward only — ทดสอบ invariant"""
    deal = Deal(customer_id="c1", value=Decimal("1000"), stage="PROPOSAL")
    with pytest.raises(DomainError):
        deal.advance_stage("PROSPECTING")  # backward

async def test_deal_value_positive():
    """Property-based: deal value >= 0 — ทดสอบ invariant"""
    with pytest.raises(DomainError):
        Deal(customer_id="c1", value=Decimal("-100"))
```

**Output:**
- 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 7: ตัวอย่าง `docs/prompts/layer-5-intelligence/forecast.md`

```markdown
# AI Prompt — Module `forecast`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `forecast` |
| **Layer** | `5` (Intelligence) |
| **Priority** | 🟠 |
| **Phase** | 5 |
| **มิติธุรกิจ** | BI |
| **Dependencies** | `analytics`, `reporting`, `production`, `inventory`, `agriculture` |
| **Domain Concepts** | `Forecast` (entity), `ForecastResult` (VO), `ForecastMethod` (enum) |

---

## 🎯 Prompt

### สร้าง Module `forecast`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- **Invariants:** `MAPE < 20%`, `Forecast non-negative`
- **Events:** `ForecastGenerated`, `ForecastUpdated`, `ForecastAccuracyDropped`

**ข้อกำหนด:**

#### 1. Domain Layer

**`domain/entities.py`**
```python
@dataclass
class Forecast(BaseEntity):
    """Forecast entity — เอนทิตีพยากรณ์"""
    product_id: str = ""
    branch_id: str = ""
    forecast_date: date | None = None
    predicted_qty: Decimal = Decimal("0.00")
    actual_qty: Decimal | None = None
    method: str = "LSTM"
    mape: Decimal | None = None
    
    def __post_init__(self):
        if self.predicted_qty < 0:
            raise DomainError("Predicted qty cannot be negative")
    
    def update_actual(self, actual_qty: Decimal) -> None:
        """Update actual and calculate MAPE — อัปเดตค่าจริงและคำนวณ MAPE"""
        if actual_qty < 0:
            raise DomainError("Actual qty cannot be negative")
        self.actual_qty = actual_qty
        if actual_qty > 0:
            self.mape = abs(self.predicted_qty - actual_qty) / actual_qty * 100
    
    def is_accurate(self) -> bool:
        """Check if forecast is accurate (MAPE < 20%) — ตรวจสอบความแม่นยำ"""
        return self.mape is not None and self.mape < 20
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class ForecastResult:
    """Forecast result VO — ผลลัพธ์พยากรณ์"""
    predicted: Decimal
    actual: Decimal | None
    error: Decimal | None
    mape: Decimal | None
```

**`domain/enums.py`**
```python
class ForecastMethod(str, Enum):
    LSTM = "LSTM"
    PROPHET = "PROPHET"
    XGBOOST = "XGBOOST"
    ARIMA = "ARIMA"
    ENSEMBLE = "ENSEMBLE"

class ForecastType(str, Enum):
    DEMAND = "DEMAND"
    PRODUCTION = "PRODUCTION"
    YIELD = "YIELD"
    PRICE = "PRICE"
```

#### 2. Application Layer

**`application/use_cases.py`**
```python
class ForecastUseCases:
    """Forecast use cases — กรณีการใช้งานพยากรณ์"""
    
    async def generate_forecast(
        self,
        product_id: str,
        branch_id: str,
        days: int,
    ) -> list[Forecast]:
        """Generate forecast — สร้างพยากรณ์"""
        try:
            # Load historical data
            data = await self.analytics_repo.get_history(product_id, branch_id)
            
            # Train/predict
            predictions = await self.ml_service.predict(data, days)
            
            # Save
            forecasts = []
            for pred in predictions:
                forecast = Forecast(
                    product_id=product_id,
                    branch_id=branch_id,
                    forecast_date=pred["date"],
                    predicted_qty=pred["qty"],
                    method="LSTM",
                )
                forecast = await self.repo.save(forecast)
                forecasts.append(forecast)
            
            await self.audit.log("forecast.generated", product_id)
            await self.events.publish("ForecastGenerated", {
                "product_id": product_id,
                "branch_id": branch_id,
                "count": len(forecasts),
            })
            
            return forecasts
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in generate_forecast")
            raise ForecastException()
    
    async def update_actual(self, forecast_id: str, actual_qty: Decimal) -> Forecast:
        """Update actual — อัปเดตค่าจริง"""
        ...
    
    async def backtest(self, product_id: str, days: int) -> dict:
        """Backtest — ทดสอบย้อนหลัง"""
        ...
```

#### 3. Tests

```python
async def test_generate_forecast_non_negative():
    """Property-based: forecast >= 0 — ทดสอบ invariant"""
    ...

async def test_mape_calculation():
    """Test MAPE — ทดสอบ MAPE"""
    forecast = Forecast(predicted_qty=Decimal("100"))
    forecast.update_actual(Decimal("110"))
    assert forecast.mape == Decimal("9.09")  # (|100-110|/110)*100

async def test_forecast_accurate():
    """Test accurate — ทดสอบความแม่นยำ"""
    forecast = Forecast(predicted_qty=Decimal("100"))
    forecast.update_actual(Decimal("105"))
    assert forecast.is_accurate()  # MAPE < 20%
```

**Output:**
- 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📄 ไฟล์ 8: ตัวอย่าง `docs/prompts/layer-6-monitoring/iot.md`

```markdown
# AI Prompt — Module `iot`

## 📋 Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `iot` |
| **Layer** | `6` (Monitoring & Sensing) |
| **Priority** | 🟠 |
| **Phase** | 4 |
| **มิติธุรกิจ** | IoT |
| **Dependencies** | `monitoring`, `alerting`, `events` |
| **Domain Concepts** | `SensorReading` (entity), `Threshold` (VO), `SensorType` (enum) |

---

## 🎯 Prompt

### สร้าง Module `iot`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME
- Clean Architecture + DDD (4 layers)
- **Invariants:** `Reading within valid range`, `Alert when threshold exceeded`
- **Events:** `SensorReadingReceived`, `ThresholdExceeded`, `SensorOffline`

**ข้อกำหนด:**

#### 1. Domain Layer

**`domain/entities.py`**
```python
@dataclass
class SensorReading(BaseEntity):
    """Sensor reading entity — เอนทิตีค่าอ่านเซ็นเซอร์"""
    sensor_id: str = ""
    sensor_type: str = ""
    value: Decimal = Decimal("0.00")
    unit: str = ""
    timestamp: datetime | None = None
    location: str = ""
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self) -> None:
        """Validate reading — ตรวจสอบค่าอ่าน"""
        if not self.sensor_id:
            raise DomainError("Sensor ID is required")
        
        ranges = {
            "TEMPERATURE": (-50, 100),
            "HUMIDITY": (0, 100),
            "CO2": (0, 10000),
            "LIGHT": (0, 200000),
            "PH": (0, 14),
            "EC": (0, 100),
        }
        
        if self.sensor_type in ranges:
            min_val, max_val = ranges[self.sensor_type]
            if not min_val <= self.value <= max_val:
                raise DomainError(f"{self.sensor_type} out of range: {self.value}")
    
    def is_out_of_range(self, threshold: "Threshold") -> bool:
        """Check if out of range — ตรวจสอบว่านอกช่วง"""
        return self.value < threshold.min or self.value > threshold.max
```

**`domain/value_objects.py`**
```python
@dataclass(frozen=True)
class Threshold:
    """Threshold VO — ค่าเกณฑ์"""
    min: Decimal
    max: Decimal
    unit: str
    
    def __post_init__(self):
        if self.min >= self.max:
            raise DomainError("Min must be less than max")
```

**`domain/enums.py`**
```python
class SensorType(str, Enum):
    TEMPERATURE = "TEMPERATURE"
    HUMIDITY = "HUMIDITY"
    CO2 = "CO2"
    LIGHT = "LIGHT"
    PH = "PH"
    EC = "EC"
    FLOW = "FLOW"
    PRESSURE = "PRESSURE"
```

#### 2. Application Layer

**`application/use_cases.py`**
```python
class IoTUseCases:
    """IoT use cases — กรณีการใช้งาน IoT"""
    
    async def ingest_reading(self, payload: dict, idem_key: str) -> SensorReading:
        """Ingest sensor reading — รับค่าจากเซ็นเซอร์"""
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing
            
            reading = SensorReading(**payload)
            reading = await self.repo.save(reading)
            
            # Check threshold
            threshold = await self.get_threshold(reading.sensor_id)
            if threshold and reading.is_out_of_range(threshold):
                await self.alerting.send(
                    f"Sensor {reading.sensor_id} out of range: {reading.value}"
                )
                await self.events.publish("ThresholdExceeded", {
                    "sensor_id": reading.sensor_id,
                    "value": str(reading.value),
                })
            
            await self.idempotency.set(idem_key, reading)
            await self.events.publish("SensorReadingReceived", reading)
            
            return reading
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in ingest_reading")
            raise IoTException()
    
    async def get_latest(self, sensor_id: str) -> SensorReading | None:
        """Get latest reading — ดูค่าล่าสุด"""
        # Try cache first
        cached = await self.cache.get(sensor_id)
        if cached:
            return cached
        
        # Fallback to DB
        reading = await self.repo.get_latest(sensor_id)
        if reading:
            await self.cache.insert(sensor_id, reading)
        return reading
    
    async def get_range(self, sensor_id: str, from_dt: datetime, to_dt: datetime) -> list[SensorReading]:
        """Get readings in range — ดูค่าช่วงเวลา"""
        ...
```

#### 3. Infrastructure Layer

**`infrastructure/services.py`**
```python
class MQTTService:
    """MQTT service — บริการ MQTT"""
    
    def __init__(self, broker: str, client_id: str):
        self.broker = broker
        self.client_id = client_id
        self.client: mqtt.Client | None = None
    
    async def connect(self) -> None:
        """Connect to MQTT broker — เชื่อมต่อ MQTT"""
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.connect(self.broker, 1883, 60)
        self.client.loop_start()
    
    async def subscribe(self, topic: str, handler: callable) -> None:
        """Subscribe to topic — สมัคร topic"""
        self.client.subscribe(topic, qos=1)
        self.client.on_message = handler
    
    async def publish(self, topic: str, payload: dict) -> None:
        """Publish message — ส่งข้อความ"""
        self.client.publish(topic, json.dumps(payload), qos=1)

class InfluxDBService:
    """InfluxDB service — บริการ InfluxDB"""
    
    async def write(self, reading: SensorReading) -> None:
        """Write to InfluxDB — เขียน InfluxDB"""
        ...
    
    async def query_range(self, sensor_id: str, from_dt, to_dt) -> list:
        """Query range — ค้นช่วง"""
        ...
```

#### 4. Presentation Layer

**`presentation/routers.py`**
```python
router = APIRouter(prefix="/api/v1/iot", tags=["IoT"])

@router.post("/reading/", status_code=201)
async def ingest_reading(
    payload: SensorReadingCreate,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    use_cases: IoTUseCases = Depends(get_iot_use_cases),
): ...

@router.get("/{sensor_id}/latest/")
async def get_latest(sensor_id: str, ...): ...

@router.get("/{sensor_id}/range/")
async def get_range(sensor_id: str, from_dt: datetime, to_dt: datetime, ...): ...

@router.get("/sensors/")
async def list_sensors(...): ...
```

#### 5. Tests

```python
async def test_ingest_valid_reading():
    """Test ingest valid — ทดสอบรับค่าถูกต้อง"""
    ...

async def test_ingest_out_of_range():
    """Test out of range → alert — ทดสอบนอกช่วง → แจ้งเตือน"""
    ...

async def test_temperature_invariant():
    """Property-based: temperature in range — ทดสอบ invariant"""
    with pytest.raises(DomainError):
        SensorReading(sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("200"))
```

**Output:**
- 16 ไฟล์
- Comment 2 ภาษา
- พร้อมรัน
```

---

## 📊 สรุปโครงสร้างไฟล์ที่สร้าง

| ลำดับ | ไฟล์ | คำอธิบาย | สถานะ |
|---|---|---|---|
| 1 | `docs/template_modules.md` | Master template | ✅ |
| 2 | `docs/prompts/README.md` | Index ของ prompts ทั้งหมด | ✅ |
| 3 | `docs/prompts/layer-0-core/money.md` | ตัวอย่าง Layer 0 | ✅ |
| 4 | `docs/prompts/layer-2-money-path/invoice.md` | ตัวอย่าง Layer 2 | ✅ |
| 5 | `docs/prompts/layer-3-goods-path/agriculture.md` | ตัวอย่าง Layer 3 (เกษตร) | ✅ |
| 6 | `docs/prompts/layer-4-operations/crm.md` | ตัวอย่าง Layer 4 (CRM) | ✅ |
| 7 | `docs/prompts/layer-5-intelligence/forecast.md` | ตัวอย่าง Layer 5 | ✅ |
| 8 | `docs/prompts/layer-6-monitoring/iot.md` | ตัวอย่าง Layer 6 | ✅ |
| ... | ... | ... | (อีก ~57 ไฟล์) |

---

## 🚀 วิธีใช้

### 1. สร้างโฟลเดอร์

```bash
mkdir -p docs/prompts/{layer-0-core,layer-1-foundation,layer-2-money-path,layer-3-goods-path,layer-4-operations,layer-5-intelligence,layer-6-monitoring,layer-7-templates}
```

### 2. คัดลอกไฟล์

- คัดลอก `docs/template_modules.md` ไปวาง
- คัดลอก `docs/prompts/README.md` ไปวาง
- คัดลอกแต่ละ prompt ไปวางตาม layer

### 3. ใช้งาน

```bash
# เปิด prompt ที่ต้องการ
cat docs/prompts/layer-3-goods-path/agriculture.md

# Copy prompt ไปวางใน AI
# AI จะสร้าง 16 ไฟล์ใน app/modules/agriculture/
```

### 4. ตรวจสอบ

```bash
# ตรวจสอบ checklist
grep -r "\[ \]" docs/prompts/

# รัน test
uv run pytest tests/unit/test_agriculture.py -v
```

---

## 📋 รายการ Prompts ที่ต้องสร้างเพิ่ม (ที่เหลือ)

| Layer | Modules | จำนวน |
|---|---|---|
| Layer 0 | tenant_context, audit, idempotency, config, events | 5 |
| Layer 1 | tenancy, authentication, user, employee, customer, supplier, product, pricing | 8 |
| Layer 2 | order, ledger, payment, accounting_gateway, tax, reconciliation | 6 |
| Layer 3 | inventory, warehouse, lot, production, recipe, quality, waste, procurement, traceability, crop, soil, irrigation | 12 |
| Layer 4 | transport, delivery, route, gps, retail, pos, shift, line_channel, promotion, loyalty, campaign, support | 12 |
| Layer 5 | reporting, analytics, kpi, satisfaction, recommendation, oee | 6 |
| Layer 6 | cctv, monitoring, backup, alerting, audit_viewer, maintenance, energy | 7 |
| Layer 7 | health, example, blank | 3 |
| **รวม** | | **59** |

---

## 📌 สรุปสุดท้าย

โครงสร้างไฟล์ AI Prompt Template สำหรับ **ERP + CRM + IoT** ประกอบด้วย:

1. **`docs/template_modules.md`** — Master template
2. **`docs/prompts/README.md`** — Index 65 modules
3. **`docs/prompts/{layer}/`** — 65 prompt files

**รูปแบบ prompt มาตรฐาน:**
- 📋 Metadata (ชื่อ, layer, priority, phase, มิติ, dependencies)
- 🎯 Prompt (บริบท + ข้อกำหนด 8 ข้อ)
- 📐 โครงสร้าง 16 ไฟล์
- ✅ Checklist

**วิธีใช้:**
1. เปิด prompt ที่ต้องการ
2. Copy ไปวางใน AI
3. AI สร้าง 16 ไฟล์ตาม template
4. ตรวจสอบ checklist ก่อน merge

---

> **ผู้แต่ง:** Kongnakorn Jantakun  
> **Email:** kongnakornjantakun@gmail.com  
> **อัปเดต:** 2026-09-17  
> **เวอร์ชัน:** 2.0.0  
> **สถานะ:** ✅ พร้อมใช้งาน — พร้อมสร้าง Module ใหม่ได้ทันที
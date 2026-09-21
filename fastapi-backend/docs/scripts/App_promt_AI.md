# 📦 AI Prompt Template System — เรียบเรียงใหม่ตามลำดับ

> **เวอร์ชัน:** 3.4.0 · **Stack:** Python 3.14+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · PostgreSQL 17 · Redis 8 · Kafka
> **ขอบเขต:** ERP + CRM + IoT สำหรับ SME (Multi-company) — 65 modules / 8 layers

---

# 📑 สารบัญ (Table of Contents)

| ส่วน | หัวข้อ | คำอธิบาย |
|---|---|---|
| **1** | [ภาพรวมระบบ](#1-ภาพรวมระบบ) | สถาปัตยกรรม, Layers, Modules |
| **2** | [โครงสร้างโฟลเดอร์](#2-โครงสร้างโฟลเดอร์) | docs/, app/, scripts/, tests/ |
| **3** | [Master Template](#3-master-template) | `docs/template_modules.md` |
| **4** | [Prompts Index](#4-prompts-index) | `docs/prompts/README.md` — 65 modules |
| **5** | [Layer 0: Core](#5-layer-0-core-6-modules) | 6 modules (prompts เต็ม) |
| **6** | [Layer 1–7: ตัวอย่าง](#6-layer-17-ตัวอย่าง-prompts) | ตัวอย่าง representative prompts |
| **7** | [Python Script — v3.4](#7-python-script--v34) | 18 features, 40+ CLI flags |
| **8** | [ภาคผนวก](#8-ภาคผนวก) | Use cases, CI/CD, Dependencies |

---

# 1. ภาพรวมระบบ

## 1.1 Layers & Modules (65 modules / 8 layers)

| Layer | ชื่อ | Modules | จำนวน |
|---|---|---|---|
| **0** | Core (cross-cutting) | `money`, `tenant_context`, `audit`, `idempotency`, `config`, `events` | 6 |
| **1** | Foundation | `tenancy`, `authentication`, `user`, `employee`, `customer`, `supplier`, `product`, `pricing` | 8 |
| **2** | Money Path | `order`, `invoice`, `ledger`, `payment`, `accounting_gateway`, `tax`, `reconciliation` | 7 |
| **3** | Goods Path | `inventory`, `warehouse`, `lot`, `production`, `recipe`, `quality`, `waste`, `procurement`, `traceability`, `agriculture`, `crop`, `soil`, `irrigation` | 13 |
| **4** | Operations | `transport`, `delivery`, `route`, `gps`, `retail`, `pos`, `shift`, `line_channel`, `promotion`, `loyalty`, `crm`, `campaign`, `support` | 13 |
| **5** | Intelligence | `reporting`, `analytics`, `forecast`, `kpi`, `satisfaction`, `recommendation`, `oee` | 7 |
| **6** | Monitoring | `iot`, `cctv`, `monitoring`, `backup`, `alerting`, `audit_viewer`, `maintenance`, `energy` | 8 |
| **7** | Templates | `health`, `example`, `blank` | 3 |
| | **รวม** | | **65** |

## 1.2 หลักการสำคัญ (Design Principles)

| หลักการ | รายละเอียด |
|---|---|
| **Clean Architecture** | 4 layers: Domain → Application → Infrastructure → Presentation |
| **DDD** | Entities, Value Objects, Enums, Domain Events, Invariants |
| **Multi-tenancy** | Schema-per-tenant, Redis namespace, Kafka topic prefix |
| **Idempotency** | Money Path + Goods Path ต้อง idempotent 100% |
| **Audit** | ทุก action ที่แตะเงิน/สต็อก → audit log (append-only, 7 ปี) |
| **Error Handling** | 3-branch (use cases), 2-branch (repos), never-raise (caches) |
| **Type Safety** | Python 3.14+, Pydantic v2, `Decimal` เท่านั้น (ห้าม `float`) |

## 1.3 Output มาตรฐาน — 23 ไฟล์ต่อ Module

```
app/modules/{module}/
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

db/migrations/
├── V001__create_{module}.sql
├── V002__seed_{module}.sql
└── V003__rollback_{module}.sql

tests/
├── unit/test_{module}.py
├── integration/test_{module}_repository.py
├── property/test_{module}_invariants.py
└── manual/manual_test_{module}.md
```

---

# 2. โครงสร้างโฟลเดอร์

```
project-root/
├── docs/
│   ├── template_modules.md            # Master template
│   └── prompts/
│       ├── README.md                  # Index 65 modules
│       ├── layer-0-core/              # 6 prompts
│       ├── layer-1-foundation/        # 8 prompts
│       ├── layer-2-money-path/        # 7 prompts
│       ├── layer-3-goods-path/        # 13 prompts
│       ├── layer-4-operations/        # 13 prompts
│       ├── layer-5-intelligence/      # 7 prompts
│       ├── layer-6-monitoring/        # 8 prompts
│       └── layer-7-templates/         # 3 prompts
│
├── app/
│   └── modules/
│       └── {module}/                  # 16 ไฟล์ + tests + SQL
│
├── db/migrations/                     # 3 SQL files per module
├── tests/                             # 4 test files per module
└── scripts/
    └── generate_prompts.py            # v3.4 — 18 features
```

**คำสั่งสร้างโฟลเดอร์:**

```bash
mkdir -p docs/prompts/{layer-0-core,layer-1-foundation,layer-2-money-path,layer-3-goods-path,layer-4-operations,layer-5-intelligence,layer-6-monitoring,layer-7-templates}
```

---

# 3. Master Template

**ไฟล์:** `docs/template_modules.md`

## 3.1 Metadata (ข้อมูล Module)

| หัวข้อ | รายละเอียด | ตัวอย่าง |
|---|---|---|
| **ชื่อ Module** | `{module_name}` | `agriculture` |
| **Layer** | `{layer_number}` (0-7) | `3` |
| **Priority** | `{priority}` (🔴/🟠/🟡/🟢) | `🟠` |
| **Phase** | `{phase}` (0-6) | `4` |
| **มิติธุรกิจ** | `{agriculture/production/logistics/factory/erp/crm}` | `agriculture` |
| **Dependencies** | `{list_of_modules}` | `crop, soil, iot, forecast` |
| **Domain Concepts** | `{entities}, {value_objects}, {enums}` | `Farm, Plot, CropCycle` |

## 3.2 Prompt Template (Master)

### บริบท
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- PostgreSQL 17 (schema-per-tenant), Redis 8, Kafka
- รองรับ 4 มิติ: เกษตร, การผลิต, การขนส่ง, โรงงาน
- ทุก action แตะเงิน/สต็อก → audit log
- Money Path + Goods Path ต้อง idempotent

### ข้อกำหนด 8 ข้อ

| # | Layer/Section | รายละเอียด |
|---|---|---|
| 1 | **Domain Layer** | `entities.py`, `value_objects.py`, `enums.py` — ห้าม import framework |
| 2 | **Application Layer** | `interfaces.py`, `use_cases.py`, `mappers.py`, `exceptions.py`, `utils.py` |
| 3 | **Infrastructure Layer** | `models.py`, `repositories.py`, `caches.py`, `services.py` |
| 4 | **Presentation Layer** | `routers.py`, `schemas.py`, `docs.py`, `dependencies.py` |
| 5 | **Error Handling** | 3 shapes: 3-branch / 2-branch / never-raise |
| 6 | **Invariants** | Domain-specific business rules |
| 7 | **Domain Events** | `{Module}Created`, `{Module}Updated`, `{Module}Deleted` |
| 8 | **Tests** | Unit + Integration + Property-based |

## 3.3 Error Handling Patterns

```python
# ─── 3-branch: Use cases + router handlers ─────────────
try:
    ...
except StandardException:
    raise                          # ต้องมาก่อนเสมอ
except DomainError as e:
    raise DomainException(e)
except Exception as e:
    logger.opt(exception=e).error("Error in {module} endpoint.")
    raise {Module}Exception()

# ─── 2-branch: Repositories + services ─────────────────
try:
    ...
except StandardException:
    raise
except Exception as e:
    logger.opt(exception=e).error("Error in {module} repository.")
    raise {Module}Exception()

# ─── Never-raise: Caches ───────────────────────────────
try:
    ...
except Exception as e:
    logger.opt(exception=e).error("Cache error. Falling back to DB.")
    return None
```

## 3.4 Checklist ก่อนส่ง

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

---

# 4. Prompts Index

**ไฟล์:** `docs/prompts/README.md`

## 4.1 ตาราง Index ทั้ง 65 Modules

### Layer 0: CORE

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 1 | `money` | 🔴 | 1 | [money.md](layer-0-core/money.md) |
| 2 | `tenant_context` | 🔴 | 1 | [tenant_context.md](layer-0-core/tenant_context.md) |
| 3 | `audit` | 🔴 | 1 | [audit.md](layer-0-core/audit.md) |
| 4 | `idempotency` | 🔴 | 1 | [idempotency.md](layer-0-core/idempotency.md) |
| 5 | `config` | 🔴 | 1 | [config.md](layer-0-core/config.md) |
| 6 | `events` | 🔴 | 1 | [events.md](layer-0-core/events.md) |

### Layer 1: FOUNDATION

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

### Layer 2: MONEY PATH

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 15 | `order` | 🔴 | 1 | [order.md](layer-2-money-path/order.md) |
| 16 | `invoice` | 🔴 | 1 | [invoice.md](layer-2-money-path/invoice.md) |
| 17 | `ledger` | 🔴 | 1 | [ledger.md](layer-2-money-path/ledger.md) |
| 18 | `payment` | 🔴 | 2 | [payment.md](layer-2-money-path/payment.md) |
| 19 | `accounting_gateway` | 🔴 | 2 | [accounting_gateway.md](layer-2-money-path/accounting_gateway.md) |
| 20 | `tax` | 🔴 | 2 | [tax.md](layer-2-money-path/tax.md) |
| 21 | `reconciliation` | 🔴 | 1 | [reconciliation.md](layer-2-money-path/reconciliation.md) |

### Layer 3: GOODS PATH

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

### Layer 4: OPERATIONS

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

### Layer 5: INTELLIGENCE

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 48 | `reporting` | 🔴 | 5 | [reporting.md](layer-5-intelligence/reporting.md) |
| 49 | `analytics` | 🟠 | 5 | [analytics.md](layer-5-intelligence/analytics.md) |
| 50 | `forecast` | 🟠 | 5 | [forecast.md](layer-5-intelligence/forecast.md) |
| 51 | `kpi` | 🟠 | 5 | [kpi.md](layer-5-intelligence/kpi.md) |
| 52 | `satisfaction` | 🟡 | 5 | [satisfaction.md](layer-5-intelligence/satisfaction.md) |
| 53 | `recommendation` | 🟡 | 5 | [recommendation.md](layer-5-intelligence/recommendation.md) |
| 54 | `oee` | 🟠 | 5 | [oee.md](layer-5-intelligence/oee.md) |

### Layer 6: MONITORING & SENSING

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

### Layer 7: TEMPLATES

| # | Module | Priority | Phase | ไฟล์ |
|---|---|---|---|---|
| 63 | `health` | 🔴 | 1 | [health.md](layer-7-templates/health.md) |
| 64 | `example` | 🟢 | 1 | [example.md](layer-7-templates/example.md) |
| 65 | `blank` | 🟢 | 1 | [blank.md](layer-7-templates/blank.md) |

## 4.2 ลำดับการสร้างที่แนะนำ

```
Phase 1:  Layer 0 (Core) → Layer 1 (Foundation) → Layer 2 (Money) → Layer 3 (Goods)
Phase 2:  Layer 4 (Operations) → Layer 5 (Intelligence)
Phase 3:  Layer 6 (Monitoring) → Layer 7 (Templates)
```

## 4.3 วิธีใช้

1. เปิดไฟล์ prompt ที่ต้องการ เช่น `docs/prompts/layer-3-goods-path/agriculture.md`
2. Copy prompt ไปวางใน AI (ChatGPT, Claude, Gemini)
3. AI จะสร้าง 23 ไฟล์ตาม template
4. ตรวจสอบ checklist ก่อน merge

---

# 5. Layer 0: Core (6 modules)

> Module ทั้ง 6 นี้เป็น **primitive modules** — ไม่มี persistence หรือมีน้อย, ใช้ `Decimal` เท่านั้น

---

## 5.1 Module `money`

**ไฟล์:** `docs/prompts/layer-0-core/money.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `money` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | ไม่มี (primitive module) |
| **Domain Concepts** | `Money` (VO), `Currency` (enum), `VAT` (VO), `ExchangeRate` (VO) |

### Domain Layer

**`domain/value_objects.py` — Money**

```python
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Money value object — วัตถุค่าเงิน"""

    amount: Decimal
    currency: str = "THB"

    def __post_init__(self):
        object.__setattr__(
            self,
            "amount",
            self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        )
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise DomainError("Amount must be Decimal")
        if self.currency not in Currency._value2member_map_:
            raise DomainError(f"Unsupported currency: {self.currency}")

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DomainError(f"Cannot operate on {self.currency} vs {other.currency}")

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
```

**`domain/value_objects.py` — VAT**

```python
@dataclass(frozen=True)
class VAT:
    """VAT value object — วัตถุภาษีมูลค่าเพิ่ม"""

    rate: Decimal  # e.g., 0.07

    def calculate(self, base: Money) -> Money:
        return Money((base.amount * self.rate).quantize(Decimal("0.01")), base.currency)

    def extract(self, total: Money) -> Money:
        base = (total.amount / (Decimal("1") + self.rate)).quantize(Decimal("0.01"))
        return Money(total.amount - base, total.currency)
```

**`domain/value_objects.py` — ExchangeRate**

```python
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


class RoundingMode(str, Enum):
    HALF_UP = "HALF_UP"
    HALF_DOWN = "HALF_DOWN"
    BANKERS = "BANKERS"
```

### Application Layer

**`application/use_cases.py`**

```python
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
```

### Infrastructure Layer
- **ไม่มี** `models.py`, `repositories.py`, `caches.py`, `services.py` (pure VO)

### Presentation Layer

**`presentation/schemas.py`**

```python
class MoneySchema(BaseModel):
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="THB", pattern="^(THB|USD|EUR)$")
    model_config = ConfigDict(from_attributes=True)


class VATRequest(BaseModel):
    base: MoneySchema
    rate: VATRate = VATRate.SEVEN


class VATResponse(BaseModel):
    vat: MoneySchema
    total: MoneySchema
```

**`presentation/routers.py`**

```python
router = APIRouter(prefix="/api/v1/money", tags=["Money"])


@router.post("/add/")
async def add(a: MoneySchema, b: MoneySchema): ...


@router.post("/subtract/")
async def subtract(a: MoneySchema, b: MoneySchema): ...


@router.post("/vat/calculate/")
async def vat_calculate(req: VATRequest): ...


@router.post("/vat/extract/")
async def vat_extract(req: VATRequest): ...


@router.post("/convert/")
async def convert(amount: MoneySchema, rate: ExchangeRateSchema): ...
```

### Invariants

- `Decimal` quantize 2 ตำแหน่ง (ROUND_HALF_UP)
- `a + b == b + a` (commutative)
- `(a + b) + c == a + (b + c)` (associative)
- `a + Money(0) == a` (identity)
- `a - a == Money(0)` (inverse)
- `VAT.calculate(base) + base == VAT.extract(total)` consistency

### Domain Events
- `MoneyAdded`, `MoneySubtracted`, `VATCalculated`, `CurrencyConverted`

### Tests

```python
def test_commutative():
    assert a + b == b + a


def test_associative():
    assert (a + b) + c == a + (b + c)


def test_identity():
    assert a + Money(Decimal("0")) == a


def test_currency_mismatch():
    pytest.raises(DomainError)


def test_vat_7_percent():
    assert VAT(Decimal("0.07")).calculate(Money(Decimal("100"))) == Money(
        Decimal("7.00")
    )


def test_vat_extract_roundtrip(): ...
def test_exchange_rate_convert(): ...
def test_negative_money():
    assert Money(Decimal("-10")).is_negative()


def test_zero_money():
    assert Money(Decimal("0")).is_zero()
```

---

## 5.2 Module `tenant_context`

**ไฟล์:** `docs/prompts/layer-0-core/tenant_context.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `tenant_context` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | ไม่มี (primitive module) |
| **Domain Concepts** | `TenantContext` (VO), `TenantScope` (enum), `RequestContext` (VO) |

### Domain Layer

**`domain/value_objects.py` — TenantContext**

```python
from dataclasses import dataclass, field
from datetime import datetime
from contextvars import ContextVar


@dataclass(frozen=True)
class TenantContext:
    """Tenant context VO — วัตถุบริบทผู้เช่า"""

    tenant_id: str
    user_id: str | None = None
    correlation_id: str = ""
    request_id: str = ""
    locale: str = "th-TH"
    timezone: str = "Asia/Bangkok"

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.tenant_id:
            raise DomainError("Tenant ID is required")
        if not self.correlation_id:
            raise DomainError("Correlation ID is required")

    @property
    def schema_name(self) -> str:
        return f"tenant_{self.tenant_id}"

    def redis_namespace(self, key: str) -> str:
        return f"t:{self.tenant_id}:{key}"

    def kafka_topic(self, topic: str) -> str:
        return f"t.{self.tenant_id}.{topic}"


_context_var: ContextVar[TenantContext | None] = ContextVar(
    "tenant_context", default=None
)


def set_context(ctx: TenantContext) -> None:
    _context_var.set(ctx)


def get_context() -> TenantContext:
    ctx = _context_var.get()
    if ctx is None:
        raise DomainError("Tenant context not set")
    return ctx


def clear_context() -> None:
    _context_var.set(None)
```

**`domain/value_objects.py` — RequestContext**

```python
@dataclass(frozen=True)
class RequestContext:
    """Request context VO — วัตถุบริบทคำขอ"""

    method: str
    path: str
    ip_address: str
    user_agent: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
```

**`domain/enums.py`**

```python
class TenantScope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    USER = "USER"


class IsolationLevel(str, Enum):
    SCHEMA_PER_TENANT = "SCHEMA_PER_TENANT"
    DATABASE_PER_TENANT = "DATABASE_PER_TENANT"
    ROW_LEVEL = "ROW_LEVEL"
```

### Application Layer

**`application/interfaces.py`**

```python
class ITenantContextProvider(Protocol):
    def get(self) -> TenantContext: ...
    def set(self, ctx: TenantContext) -> None: ...
    def clear(self) -> None: ...


class ITenantResolver(Protocol):
    async def resolve(self, identifier: str) -> TenantContext | None: ...
```

**`application/use_cases.py`**

```python
class TenantContextUseCases:
    """Tenant context use cases — กรณีการใช้งานบริบทผู้เช่า"""

    def __init__(self, resolver: ITenantResolver):
        self.resolver = resolver

    async def establish(
        self, tenant_id: str, user_id: str | None, headers: dict
    ) -> TenantContext:
        try:
            ctx = TenantContext(
                tenant_id=tenant_id,
                user_id=user_id,
                correlation_id=headers.get("X-Correlation-ID") or str(uuid7()),
                request_id=headers.get("X-Request-ID") or str(uuid7()),
                locale=headers.get("Accept-Language", "th-TH"),
            )
            set_context(ctx)
            return ctx
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in establish tenant context")
            raise TenantContextException()

    def current(self) -> TenantContext:
        return get_context()

    def teardown(self) -> None:
        clear_context()
```

### Infrastructure Layer

**`infrastructure/repositories.py` — PostgresTenantResolver**

```python
class PostgresTenantResolver:
    """Resolve tenant from DB — ค้นหา tenant จาก DB"""

    def __init__(self, session):
        self.session = session

    async def resolve(self, identifier: str) -> TenantContext | None:
        try:
            result = await self.session.execute(
                text("SELECT id FROM public.tenants WHERE slug = :s AND active = true"),
                {"s": identifier},
            )
            row = result.first()
            if not row:
                return None
            return TenantContext(tenant_id=str(row.id), correlation_id=str(uuid7()))
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error resolving tenant")
            raise TenantContextException()
```

**`infrastructure/caches.py` — RedisTenantCache**

```python
class RedisTenantCache:
    """Cache tenant lookup — แคชข้อมูล tenant"""

    async def get(self, identifier: str) -> TenantContext | None:
        try:
            data = await self.redis.get(f"tenant:lookup:{identifier}")
            return TenantContext(**json.loads(data)) if data else None
        except Exception as e:
            logger.opt(exception=e).error("Cache get failed. Falling back.")
            return None  # never raise

    async def insert(self, identifier: str, ctx: TenantContext) -> None:
        try:
            await self.redis.setex(
                f"tenant:lookup:{identifier}", 300, json.dumps(asdict(ctx))
            )
        except Exception as e:
            logger.opt(exception=e).error("Cache insert failed.")
```

### Invariants
- ทุก request ต้องมี `tenant_id` + `correlation_id`
- Context ถูก propagate ผ่าน `contextvars` (async-safe)
- `schema_name == f"tenant_{tenant_id}"`
- Redis keys ขึ้นต้นด้วย `t:{tenant_id}:` เสมอ

### Domain Events- `TenantContextEstablished`, `TenantContextCleared`, `TenantSwitched`

---

## 5.3 Module `audit`

**ไฟล์:** `docs/prompts/layer-0-core/audit.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `audit` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `tenant_context` |
| **Domain Concepts** | `AuditLog` (entity), `AuditAction` (enum), `ChangeSet` (VO) |

### Domain Layer

**`domain/entities.py`**

```python
@dataclass
class AuditLog(BaseEntity):
    """Audit log entity — เอนทิตีบันทึก audit"""

    action: str = ""
    resource_type: str = ""
    resource_id: str = ""
    actor_id: str = ""
    before_state: dict = field(default_factory=dict)
    after_state: dict = field(default_factory=dict)
    changes: list = field(default_factory=list)
    ip_address: str = ""
    user_agent: str = ""
    correlation_id: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.action:
            raise DomainError("Action is required")
        if not self.resource_type or not self.resource_id:
            raise DomainError("Resource type/id required")

    def diff(self) -> list[dict]:
        """Compute diff — คำนวณส่วนต่าง"""
        keys = set(self.before_state) | set(self.after_state)
        return [
            {
                "field": k,
                "before": self.before_state.get(k),
                "after": self.after_state.get(k),
            }
            for k in keys
            if self.before_state.get(k) != self.after_state.get(k)
        ]
```

**`domain/value_objects.py`**

```python
@dataclass(frozen=True)
class ChangeSet:
    """Change set VO — วัตถุชุดการเปลี่ยนแปลง"""

    entity: str
    entity_id: str
    changes: tuple[tuple[str, any, any], ...]  # (field, before, after)

    def is_empty(self) -> bool:
        return len(self.changes) == 0
```

**`domain/enums.py`**

```python
class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    VOID = "VOID"
    PAYMENT = "PAYMENT"
    STOCK_MOVE = "STOCK_MOVE"


class AuditSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
```

### Application Layer

**`application/interfaces.py`**

```python
class IAuditRepository(Protocol):
    async def append(self, log: AuditLog) -> AuditLog: ...
    async def query(
        self, filters: dict, page: int, limit: int
    ) -> tuple[list[AuditLog], int]: ...


class IAuditCache(Protocol):
    async def get(self, id: str) -> AuditLog | None: ...
    async def insert(self, id: str, log: AuditLog) -> None: ...


class IAuditPublisher(Protocol):
    async def publish(self, log: AuditLog) -> None: ...
```

**`application/use_cases.py`**

```python
class AuditUseCases:
    """Audit use cases — กรณีการใช้งาน audit"""

    def __init__(self, repo, cache, publisher, events):
        self.repo = repo
        self.cache = cache
        self.publisher = publisher
        self.events = events

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        before: dict,
        after: dict,
    ) -> AuditLog:
        try:
            ctx = get_context()
            log = AuditLog(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                actor_id=ctx.user_id or "system",
                before_state=before,
                after_state=after,
                correlation_id=ctx.correlation_id,
            )
            log = await self.repo.append(log)

            # Read-back verification
            verified = await self.repo.get_by_id(log.id)
            if not verified:
                raise AuditException("Read-back failed")

            await self.publisher.publish(log)
            await self.events.publish("AuditLogged", log)

            return log
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in audit log")
            raise AuditException()

    async def query(self, filters: dict, page: int, limit: int) -> tuple[list, int]:
        return await self.repo.query(filters, page, limit)
```

### Infrastructure Layer

**`infrastructure/models.py`**

```python
class AuditLogModel(BaseModel):
    __tablename__ = "audit_logs"
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(36), nullable=False, index=True)
    actor_id = Column(String(36), nullable=False, index=True)
    before_state = Column(JSONB, default=dict)
    after_state = Column(JSONB, default=dict)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    correlation_id = Column(String(36), index=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_actor_time", "actor_id", "occurred_at"),
        # Append-only: REVOKE UPDATE/DELETE ใน migration
    )
```

### Invariants
- Audit log **immutable** — append-only
- ทุก log ต้องมี `actor_id`, `correlation_id`, `occurred_at`
- `diff()` ต้องตรงกับ `before`/`after`
- Retention 7 ปี — ห้ามลบก่อนกำหนด

### Domain Events
- `AuditLogged`, `AuditQueryExecuted`

---

## 5.4 Module `idempotency`

**ไฟล์:** `docs/prompts/layer-0-core/idempotency.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `idempotency` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `tenant_context`, `config` |
| **Domain Concepts** | `IdempotencyKey` (VO), `IdempotencyRecord` (entity), `IdempotencyStatus` (enum) |

### Domain Layer

**`domain/entities.py`**

```python
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
        self.status = "COMPLETED"
        self.response_status = status
        self.response_body = body
```

**`domain/value_objects.py`**

```python
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
```

**`domain/enums.py`**

```python
class IdempotencyStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IdempotencyConflict(str, Enum):
    SAME_KEY_SAME_PAYLOAD = "SAME_KEY_SAME_PAYLOAD"
    SAME_KEY_DIFF_PAYLOAD = "SAME_KEY_DIFF_PAYLOAD"
    CONCURRENT = "CONCURRENT"
```

### Application Layer

**`application/use_cases.py`**

```python
class IdempotencyUseCases:
    """Idempotency use cases — กรณีการใช้งาน idempotency"""

    def __init__(self, store, config):
        self.store = store
        self.ttl = config.IDEMPOTENCY_TTL_SECONDS

    async def check_or_lock(
        self, raw_key: str, scope: str, payload: dict
    ) -> IdempotencyRecord | None:
        """Check existing or lock — ตรวจสอบหรือล็อก"""
        try:
            ctx = get_context()
            key = IdempotencyKey(value=raw_key, scope=scope)
            existing = await self.store.get(key, ctx.tenant_id)

            if existing and existing.is_completed():
                if existing.request_hash != self._hash(payload):
                    raise IdempotencyConflictException("Payload mismatch")
                return existing  # replay

            if existing and existing.is_in_progress():
                raise IdempotencyConflictException("Request in progress")

            locked = await self.store.lock(key, ctx.tenant_id, self.ttl)
            if not locked:
                raise IdempotencyConflictException("Concurrent request")

            rec = IdempotencyRecord(
                key=raw_key,
                status="IN_PROGRESS",
                request_hash=self._hash(payload),
                expires_at=datetime.utcnow() + timedelta(seconds=self.ttl),
            )
            await self.store.set(key, ctx.tenant_id, rec)
            return None  # proceed with execution
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in check_or_lock")
            raise IdempotencyException()

    async def complete(self, raw_key: str, scope: str, status: int, body: dict) -> None:
        try:
            ctx = get_context()
            key = IdempotencyKey(value=raw_key, scope=scope)
            rec = await self.store.get(key, ctx.tenant_id)
            if rec:
                rec.complete(status, body)
                await self.store.set(key, ctx.tenant_id, rec)
                await self.store.unlock(key, ctx.tenant_id)
        except Exception as e:
            logger.opt(exception=e).error("Error in complete idempotency")
            # don't re-raise — response already returned

    @staticmethod
    def _hash(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()
```

### Infrastructure Layer

**`infrastructure/models.py`**

```python
class IdempotencyRecordModel(BaseModel):
    __tablename__ = "idempotency_records"
    key = Column(String(255), nullable=False, index=True)
    scope = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    request_hash = Column(String(64), nullable=False)
    response_body = Column(JSONB, default=dict)
    response_status = Column(Integer)
    locked_until = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), index=True)

    __table_args__ = (
        UniqueConstraint("key", "scope", "tenant_id", name="uq_idem_key_scope_tenant"),
    )
```

**`infrastructure/caches.py` — RedisIdempotencyStore**

```python
class RedisIdempotencyStore:
    async def lock(self, key: IdempotencyKey, tenant_id: str, ttl: int) -> bool:
        try:
            result = await self.redis.set(
                f"{key.redis_key(tenant_id)}:lock", "1", nx=True, ex=ttl
            )
            return bool(result)
        except Exception as e:
            logger.opt(exception=e).error("Lock failed")
            return False  # conservative: fail closed
```

### Invariants
- Key + Scope + Tenant = unique
- `COMPLETED` record ต้อง return response เดิมเสมอ
- Payload hash ต้องตรงกัน ไม่งั้น 422
- Concurrent requests → 1 success, rest 409

### Domain Events
- `IdempotencyLocked`, `IdempotencyCompleted`, `IdempotencyConflict`

---

## 5.5 Module `config`

**ไฟล์:** `docs/prompts/layer-0-core/config.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `config` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `tenant_context` |
| **Domain Concepts** | `ConfigEntry` (entity), `ConfigScope` (enum), `ConfigType` (enum) |

### Domain Layer

**`domain/entities.py`**

```python
@dataclass
class ConfigEntry(BaseEntity):
    """Config entry — เอนทิตีรายการตั้งค่า"""

    key: str = ""
    value: str = ""
    value_type: str = "string"
    scope: str = "TENANT"
    scope_id: str = ""
    is_secret: bool = False
    description: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.key:
            raise DomainError("Config key required")
        if not re.match(r"^[a-z][a-z0-9_.]*$", self.key):
            raise DomainError(f"Invalid key format: {self.key}")

    def typed_value(self):
        if self.value_type == "int":
            return int(self.value)
        if self.value_type == "decimal":
            return Decimal(self.value)
        if self.value_type == "bool":
            return self.value.lower() in ("1", "true", "yes")
        if self.value_type == "json":
            return json.loads(self.value)
        return self.value

    def mask(self) -> "ConfigEntry":
        """Mask secret value — ปิดบังค่า secret"""
        if self.is_secret:
            copy = replace(self, value="***")
            return copy
        return self
```

**`domain/value_objects.py`**

```python
@dataclass(frozen=True)
class ConfigKey:
    """Config key VO — วัตถุกุญแจ config"""

    value: str

    def __post_init__(self):
        if not re.match(r"^[a-z][a-z0-9_.]*$", self.value):
            raise DomainError(f"Invalid config key: {self.value}")

    def namespace(self) -> str:
        return self.value.split(".", 1)[0]
```

**`domain/enums.py`**

```python
class ConfigScope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"
    USER = "USER"


class ConfigType(str, Enum):
    STRING = "string"
    INT = "int"
    DECIMAL = "decimal"
    BOOL = "bool"
    JSON = "json"
    SECRET = "secret"
```

### Application Layer

**`application/use_cases.py`**

```python
class ConfigUseCases:
    """Config use cases — กรณีการใช้งาน config"""

    def __init__(self, repo, cache, cipher, events, config): ...

    async def get_effective(self, key: str, user_id: str | None = None) -> ConfigEntry:
        try:
            ctx = get_context()
            cache_key = f"{ctx.tenant_id}:{user_id or '-'}:{key}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            entry = await self.repo.get_effective(key, ctx.tenant_id, user_id)
            if entry is None:
                raise ConfigKeyNotFoundException(key)

            if entry.is_secret:
                plain = self.cipher.decrypt(entry.value)
                entry = replace(entry, value=plain)

            await self.cache.insert(cache_key, entry)
            return entry
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in get_effective config")
            raise ConfigException()

    async def set(
        self,
        key: str,
        value: str,
        value_type: str,
        scope: str,
        scope_id: str,
        is_secret: bool = False,
    ) -> ConfigEntry:
        try:
            if is_secret:
                value = self.cipher.encrypt(value)
            entry = ConfigEntry(
                key=key,
                value=value,
                value_type=value_type,
                scope=scope,
                scope_id=scope_id,
                is_secret=is_secret,
            )
            entry = await self.repo.save(entry)

            # Read-back
            verified = await self.repo.get(key, scope, scope_id)
            if not verified or verified.value != entry.value:
                raise ConfigException("Read-back failed")

            await self.cache.invalidate(f"{scope_id}:{key}")
            await self.events.publish("ConfigChanged", {"key": key, "scope": scope})
            return entry.mask()
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in set config")
            raise ConfigException()
```

### Infrastructure Layer

**`infrastructure/models.py`**

```python
class ConfigEntryModel(BaseModel):
    __tablename__ = "config_entries"
    key = Column(String(200), nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False, default="string")
    scope = Column(String(20), nullable=False, index=True)
    scope_id = Column(String(36), nullable=False, index=True)
    is_secret = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("key", "scope", "scope_id", name="uq_config_key_scope"),
    )
```

**`infrastructure/services.py`**

```python
class FernetCipher:
    """Fernet cipher — เข้ารหัส Fernet"""

    def __init__(self, key: bytes):
        self.fernet = Fernet(key)

    def encrypt(self, plain: str) -> str:
        return self.fernet.encrypt(plain.encode()).decode()

    def decrypt(self, cipher: str) -> str:
        return self.fernet.decrypt(cipher.encode()).decode()


class ConfigPubSub:
    """Config hot-reload via Redis Pub/Sub — โหลด config ใหม่ทันที"""

    async def subscribe(self, callback) -> None: ...
```

### Invariants
- 3-level override: `USER` > `TENANT` > `GLOBAL`
- Secret values **ไม่ return ผ่าน API** (mask)
- Config key format: `^[a-z][a-z0-9_.]*$`
- Cache invalidation ต้อง propagate ทันที

### Domain Events
- `ConfigChanged`, `ConfigDeleted`, `ConfigReloaded`

---

## 5.6 Module `events`

**ไฟล์:** `docs/prompts/layer-0-core/events.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `events` |
| **Layer** | `0` (Core) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `tenant_context`, `audit` |
| **Domain Concepts** | `DomainEvent` (VO), `EventEnvelope` (VO), `EventStatus` (enum) |

### Domain Layer

**`domain/value_objects.py` — DomainEvent**

```python
@dataclass(frozen=True)
class DomainEvent:
    """Domain event VO — วัตถุเหตุการณ์"""

    event_type: str
    aggregate_id: str
    payload: dict
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

    def __post_init__(self):
        if not self.event_type:
            raise DomainError("Event type required")
        if not self.aggregate_id:
            raise DomainError("Aggregate ID required")
        if self.version < 1:
            raise DomainError("Version must be >= 1")
```

**`domain/value_objects.py` — EventEnvelope**

```python
@dataclass(frozen=True)
class EventEnvelope:
    """Event envelope — วัตถุซองเหตุการณ์"""

    event_id: str
    event_type: str
    tenant_id: str
    correlation_id: str
    occurred_at: datetime
    version: int
    payload: dict
    retry_count: int = 0

    def to_kafka_topic(self) -> str:
        return f"t.{self.tenant_id}.{self.event_type.lower()}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EventEnvelope":
        return cls(**data)
```

**`domain/enums.py`**

```python
class EventStatus(str, Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    PROCESSING = "PROCESSING"
    CONSUMED = "CONSUMED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"


class EventPriority(str, Enum):
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class EventCategory(str, Enum):
    MONEY = "MONEY"
    GOODS = "GOODS"
    USER = "USER"
    SYSTEM = "SYSTEM"
    IoT = "IoT"
```

### Application Layer

**`application/use_cases.py`**

```python
class EventUseCases:
    """Event use cases — กรณีการใช้งานเหตุการณ์"""

    def __init__(self, bus, store, handlers, serializer):
        self.bus = bus
        self.store = store
        self.handlers = {h.event_type: h for h in handlers}
        self.serializer = serializer

    async def publish(self, event: DomainEvent) -> EventEnvelope:
        try:
            ctx = get_context()
            envelope = EventEnvelope(
                event_id=str(uuid7()),
                event_type=event.event_type,
                tenant_id=ctx.tenant_id,
                correlation_id=ctx.correlation_id,
                occurred_at=event.occurred_at,
                version=event.version,
                payload=event.payload,
            )
            await self.store.append(envelope)
            await self.bus.publish(event)
            return envelope
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in publish event")
            raise EventException()

    async def consume(self, raw: bytes) -> None:
        try:
            envelope = self.serializer.deserialize(raw)

            # Idempotency check — ตรวจสอบ idempotency
            existing = await self.store.get(envelope.event_id)
            if existing and existing.retry_count >= 0:
                logger.info(f"Duplicate event {envelope.event_id}, skipping")
                return

            handler = self.handlers.get(envelope.event_type)
            if not handler:
                logger.warning(f"No handler for {envelope.event_type}")
                return

            await handler.handle(envelope)
            await self.store.mark_consumed(envelope.event_id)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Error in consume event")
            # retry logic
            if envelope.retry_count < 5:
                await self._retry(envelope)
            else:
                await self._to_dlq(envelope)

    async def _retry(self, envelope: EventEnvelope) -> None:
        """Retry with exponential backoff — ลองใหม่แบบ exponential"""
        delay = 2**envelope.retry_count
        await asyncio.sleep(delay)
        envelope.retry_count += 1
        await self.bus.publish(envelope)  # republish

    async def _to_dlq(self, envelope: EventEnvelope) -> None:
        """Send to DLQ — ส่งไป DLQ"""
        await self.bus.publish_to_dlq(envelope)
```

### Infrastructure Layer

**`infrastructure/models.py`**

```python
class EventStoreModel(BaseModel):
    __tablename__ = "event_store"
    event_id = Column(String(36), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    correlation_id = Column(String(36), index=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    payload = Column(JSONB, nullable=False)
    status = Column(String(20), default="PENDING", index=True)
    retry_count = Column(Integer, default=0)
    consumed_at = Column(DateTime(timezone=True))
```

**`infrastructure/services.py`**

```python
class KafkaEventBus:
    """Kafka event bus — บัสเหตุการณ์ Kafka"""

    def __init__(self, bootstrap: str):
        self.producer = None
        self.bootstrap = bootstrap

    async def publish(self, event: DomainEvent) -> None:
        try:
            ctx = get_context()
            topic = f"t.{ctx.tenant_id}.{event.event_type.lower()}"
            await self.producer.send_and_wait(topic, json.dumps(asdict(event)).encode())
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("Kafka publish failed")
            raise EventException()

    async def publish_to_dlq(self, envelope: EventEnvelope) -> None:
        await self.producer.send_and_wait(
            "dlq.events", json.dumps(asdict(envelope)).encode()
        )


class JsonEventSerializer:
    """JSON serializer — ตัวแปลง JSON"""

    def serialize(self, envelope: EventEnvelope) -> bytes:
        return json.dumps(asdict(envelope), default=str).encode()

    def deserialize(self, data: bytes) -> EventEnvelope:
        return EventEnvelope.from_dict(json.loads(data))


class EventConsumerLoop:
    """Kafka consumer loop — วนลูปผู้บริโภค"""

    async def run(self, topics: list[str], handler) -> None: ...
```

### Invariants
- `event_id` unique (dedup)
- At-least-once delivery + consumer idempotent
- Retry: exponential backoff สูงสุด 5 ครั้ง → DLQ
- Event schema backward-compatible (versioned)
- ทุก event มี `tenant_id` + `correlation_id`

### Domain Events (Meta)
- `EventPublished`, `EventConsumed`, `EventFailed`, `EventDeadLettered`

---

# 6. Layer 1–7: ตัวอย่าง Prompts

> ต่อไปนี้เป็นตัวอย่าง representative prompts จาก Layer 2–6 ที่แสดง pattern การใช้งานจริง

---

## 6.1 Layer 2: Module `invoice` (Money Path)

**ไฟล์:** `docs/prompts/layer-2-money-path/invoice.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `invoice` |
| **Layer** | `2` (Money Path) |
| **Priority** | 🔴 |
| **Phase** | 1 |
| **Dependencies** | `money`, `order`, `tax`, `ledger`, `audit`, `idempotency` |
| **Domain Concepts** | `Invoice` (entity), `InvoiceLine` (VO), `InvoiceStatus` (enum) |

### Domain Layer

**`domain/entities.py`**

```python
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
        if self.status != "DRAFT":
            raise DomainError("Cannot add line to non-draft invoice")
        self.lines.append(line)
        self._recalculate()

    def issue(self) -> None:
        if self.status != "DRAFT":
            raise DomainError(f"Cannot issue invoice with status {self.status}")
        self.status = "ISSUED"
        self.issued_at = datetime.utcnow()

    def pay(self) -> None:
        if self.status != "ISSUED":
            raise DomainError(f"Cannot pay invoice with status {self.status}")
        self.status = "PAID"

    def void(self, reason: str) -> None:
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

### Application Layer

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

### Infrastructure Layer

**`infrastructure/models.py`**

```python
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
                "1",
            )
            await self.redis.delete(f"{self.namespace}:invoice:{id}")
        except Exception as e:
            logger.opt(exception=e).error("Cache delete failed.")
```

### Presentation Layer

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

### Tests

```python
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

---

## 6.2 Layer 3: Module `agriculture` (Goods Path — เกษตร)

**ไฟล์:** `docs/prompts/layer-3-goods-path/agriculture.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `agriculture` |
| **Layer** | `3` (Goods Path) |
| **Priority** | 🟠 |
| **Phase** | 4 |
| **มิติธุรกิจ** | 🌾 เกษตร |
| **Dependencies** | `crop`, `soil`, `irrigation`, `iot`, `forecast`, `inventory`, `traceability` |
| **Domain Concepts** | `Farm` (entity), `Plot` (VO), `CropCycle` (VO), `Harvest` (VO) |

### Domain Layer

**`domain/entities.py` — Farm**

```python
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
        if not self.code:
            raise DomainError("Farm code is required")
        if self.area <= 0:
            raise DomainError("Farm area must be positive")

    def add_plot(self, plot: "Plot") -> None:
        if any(p.code == plot.code for p in self.plots):
            raise DomainError(f"Plot {plot.code} already exists")
        self.plots.append(plot)

    def remove_plot(self, plot_code: str) -> None:
        self.plots = [p for p in self.plots if p.code != plot_code]

    def get_total_area(self) -> float:
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

### Application Layer

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
    ): ...

    async def create_farm(self, payload: dict, idem_key: str) -> Farm:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            farm = Farm(**payload)
            farm = await self.repo.save(farm)

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
        try:
            farm = await self.repo.get_by_plot(plot_id)
            if not farm:
                raise FarmNotFoundException()

            plot = next((p for p in farm.plots if p.code == plot_id), None)
            if not plot:
                raise PlotNotFoundException()

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
            await self.events.publish(
                "PlotPlanted", {"farm_id": farm.id, "plot_id": plot_id}
            )

            return farm
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in plant_crop")
            raise AgricultureException()

    async def harvest(
        self, plot_id: str, qty: float, quality: str, idem_key: str
    ) -> Harvest:
        try:
            existing = await self.idempotency.get(idem_key)
            if existing:
                return existing

            harvest = Harvest(
                plot_id=plot_id,
                qty=qty,
                quality=quality,
                harvested_at=datetime.utcnow(),
            )

            await self.inventory.post_movement(
                {
                    "product_id": plot_id,
                    "type": "IN",
                    "qty": qty,
                    "reference": f"HARVEST-{idem_key}",
                }
            )

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
        try:
            ...
        except Exception as e:
            logger.opt(exception=e).error("Error in get_yield")
            raise AgricultureException()

    async def detect_disease(self, plot_id: str, image: bytes) -> dict:
        try:
            result = await self.service.detect_disease(image)
            if result["confidence"] > 0.9:
                await self.events.publish(
                    "DiseaseDetected",
                    {
                        "plot_id": plot_id,
                        "disease": result["disease"],
                    },
                )
            return result
        except Exception as e:
            logger.opt(exception=e).error("Error in detect_disease")
            raise AgricultureException()
```

### Infrastructure Layer

**`infrastructure/models.py`**

```python
class FarmModel(BaseModel):
    __tablename__ = "farms"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(500))
    area = Column(Numeric(10, 2), nullable=False)
    owner_id = Column(String(36), index=True)

    plots = relationship(
        "PlotModel", back_populates="farm", cascade="all, delete-orphan"
    )


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

    __table_args__ = (UniqueConstraint("farm_id", "code", name="uq_plots_farm_code"),)
```

**`infrastructure/services.py`**

```python
class SatelliteService:
    """Satellite service — บริการดาวเทียม"""

    async def get_image(self, plot_id: str) -> bytes: ...


class WeatherService:
    """Weather service — บริการพยากรณ์อากาศ"""

    async def get_forecast(self, location: str, days: int) -> list[dict]: ...


class DiseaseDetectionService:
    """Disease detection service — บริการตรวจจับโรค"""

    async def detect(self, image: bytes) -> dict:
        # Use YOLOv8 model
        ...
```

### Presentation Layer

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

### Tests

```python
async def test_create_farm_valid():
    """Test create farm — ทดสอบสร้างฟาร์ม"""
    use_cases = AgricultureUseCases(fakes...)
    farm = await use_cases.create_farm({...}, "idem-001")
    assert farm.code == "FARM001"
    assert farm.area > 0

async def test_plant_crop_valid():
    ...

async def test_harvest_updates_inventory():
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

---

## 6.3 Layer 4: Module `crm` (Operations — CRM)

**ไฟล์:** `docs/prompts/layer-4-operations/crm.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `crm` |
| **Layer** | `4` (Operations) |
| **Priority** | 🟠 |
| **Phase** | 5 |
| **มิติธุรกิจ** | 📞 CRM |
| **Dependencies** | `customer`, `line_channel`, `notification`, `campaign`, `invoice` |
| **Domain Concepts** | `Lead` (entity), `Deal` (entity), `Pipeline` (VO), `Activity` (VO) |

### Domain Layer

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
        stages = [
            "PROSPECTING",
            "QUALIFICATION",
            "PROPOSAL",
            "NEGOTIATION",
            "CLOSED_WON",
            "CLOSED_LOST",
        ]
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

### Application Layer

**`application/use_cases.py`**

```python
class CRMUseCases:
    """CRM use cases — กรณีการใช้งาน CRM"""

    async def create_lead(self, payload: dict, idem_key: str) -> Lead:
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
        try:
            lead = await self.repo.get_lead(id)
            if not lead:
                raise LeadNotFoundException()

            customer = lead.convert(customer_data)
            customer = await self.customer_repo.save(customer)
            await self.repo.save_lead(lead)  # save updated status

            await self.audit.log("lead.converted", lead.id)
            await self.events.publish(
                "LeadConverted", {"lead_id": lead.id, "customer_id": customer.id}
            )

            return customer
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in convert_lead")
            raise CRMException()

    async def create_deal(self, payload: dict, idem_key: str) -> Deal: ...

    async def update_deal_stage(self, id: str, stage: str) -> Deal: ...

    async def get_pipeline(self, assigned_to: str) -> dict: ...
```

### Tests

```python
async def test_create_lead(): ...


async def test_convert_lead(): ...


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

---

## 6.4 Layer 5: Module `forecast` (Intelligence)

**ไฟล์:** `docs/prompts/layer-5-intelligence/forecast.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `forecast` |
| **Layer** | `5` (Intelligence) |
| **Priority** | 🟠 |
| **Phase** | 5 |
| **มิติธุรกิจ** | BI |
| **Dependencies** | `analytics`, `reporting`, `production`, `inventory`, `agriculture` |
| **Domain Concepts** | `Forecast` (entity), `ForecastResult` (VO), `ForecastMethod` (enum) |

### Domain Layer

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

### Application Layer

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
            await self.events.publish(
                "ForecastGenerated",
                {
                    "product_id": product_id,
                    "branch_id": branch_id,
                    "count": len(forecasts),
                },
            )

            return forecasts
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("Error in generate_forecast")
            raise ForecastException()

    async def update_actual(
        self, forecast_id: str, actual_qty: Decimal
    ) -> Forecast: ...

    async def backtest(self, product_id: str, days: int) -> dict: ...
```

### Tests

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

---

## 6.5 Layer 6: Module `iot` (Monitoring)

**ไฟล์:** `docs/prompts/layer-6-monitoring/iot.md`

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `iot` |
| **Layer** | `6` (Monitoring & Sensing) |
| **Priority** | 🟠 |
| **Phase** | 4 |
| **มิติธุรกิจ** | IoT |
| **Dependencies** | `monitoring`, `alerting`, `events` |
| **Domain Concepts** | `SensorReading` (entity), `Threshold` (VO), `SensorType` (enum) |

### Domain Layer

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
            "LIGHT": (0, 800000),
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

### Application Layer

**`application/use_cases.py`**

```python
class IoTUseCases:
    """IoT use cases — กรณีการใช้งาน IoT"""

    async def ingest_reading(self, payload: dict, idem_key: str) -> SensorReading:
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
                await self.events.publish(
                    "ThresholdExceeded",
                    {
                        "sensor_id": reading.sensor_id,
                        "value": str(reading.value),
                    },
                )

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
        # Try cache first
        cached = await self.cache.get(sensor_id)
        if cached:
            return cached

        # Fallback to DB
        reading = await self.repo.get_latest(sensor_id)
        if reading:
            await self.cache.insert(sensor_id, reading)
        return reading

    async def get_range(
        self, sensor_id: str, from_dt: datetime, to_dt: datetime
    ) -> list[SensorReading]: ...
```

### Infrastructure Layer

**`infrastructure/services.py`**

```python
class MQTTService:
    """MQTT service — บริการ MQTT"""

    def __init__(self, broker: str, client_id: str):
        self.broker = broker
        self.client_id = client_id
        self.client: mqtt.Client | None = None

    async def connect(self) -> None:
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.connect(self.broker, 1883, 60)
        self.client.loop_start()

    async def subscribe(self, topic: str, handler: callable) -> None:
        self.client.subscribe(topic, qos=1)
        self.client.on_message = handler

    async def publish(self, topic: str, payload: dict) -> None:
        self.client.publish(topic, json.dumps(payload), qos=1)


class InfluxDBService:
    """InfluxDB service — บริการ InfluxDB"""

    async def write(self, reading: SensorReading) -> None: ...

    async def query_range(self, sensor_id: str, from_dt, to_dt) -> list: ...
```

### Presentation Layer

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

### Tests

```python
async def test_ingest_valid_reading(): ...


async def test_ingest_out_of_range(): ...


async def test_temperature_invariant():
    """Property-based: temperature in range — ทดสอบ invariant"""
    with pytest.raises(DomainError):
        SensorReading(sensor_id="s1", sensor_type="TEMPERATURE", value=Decimal("200"))
```

---

# 7. Python Script — v3.4

**ไฟล์:** `scripts/generate_prompts.py`

## 7.1 Version History

| Version | Features | CLI Flags | Lines |
|---|---|---|---|
| v3.0 | 4 | 13 | ~1,100 |
| v3.1 | 4 | 13 | ~1,100 |
| v3.2 | 8 | 19 | ~1,750 |
| v3.3 | 13 | 29 | ~2,700 |
| **v3.4** | **18** | **40+** | **~3,500** |

## 7.2 Features ทั้ง 18

### Core (v3.0)

| # | Feature | CLI Flag | คำอธิบาย |
|---|---|---|---|
| 1 | **Generate** | `--output` `--layer` `--module` `--force` `--dry-run` | สร้าง prompt files |
| 2 | **Filter** | `--layer` `--module` | กรองตาม layer/module |
| 3 | **Quiet** | `--quiet` | ซ่อน per-file output |
| 4 | **All** | `--all` | รันทุก feature |

### v3.1

| # | Feature | CLI Flag | คำอธิบาย |
|---|---|---|---|
| 5 | **Bilingual** | `--lang {th,en}` | ภาษา prompt content |
| 6 | **Export JSON** | `--export-json PATH` | Metadata JSON |
| 7 | **Export YAML** | `--export-yaml PATH` | Metadata YAML (custom parser) |
| 8 | **Validate** | `--validate-deps` | ตรวจ dependency graph |
| 9 | **README** | `--generate-readme` | Index README |

### v3.2

| # | Feature | CLI Flag | คำอธิบาย |
|---|---|---|---|
| 10 | **Fix Deps** | `--fix-deps` `--strict-deps` | Auto-fix dependencies |
| 11 | **Graph Export** | `--export-graph` `--graph-format` `--graph-styles` | Mermaid/DOT |
| 12 | **Stats** | `--stats` `--stats-verbose` `--stats-json` | Statistics |
| 13 | **Merge** | `--merge-template` `--repo-root` | Merge prompt + code |

### v3.3

| # | Feature | CLI Flag | คำอธิบาย |
|---|---|---|---|
| 14 | **HTML Report** | `--html-report PATH` | Interactive dashboard |
| 15 | **Diff** | `--diff` `--diff-json` | Prompt vs code drift |
| 16 | **Mock Scaffold** | `--mock-scaffold` `--scaffold-force` | Stub generator |
| 17 | **Notify** | `--notify {slack,line}` | Webhook notification |
| 18 | **Sign** | `--sign` `--gpg-key` `--sign-method` | GPG/SHA-256 |

### v3.4

| # | Feature | CLI Flag | คำอธิบาย |
|---|---|---|---|
| 19 | **i18n** | `--i18n {en,th,jp}` | UI language |
| 20 | **Pipeline** | `--pipeline PATH.yaml` | Multi-step execution |
| 21 | **Trend** | `--trend` `--trend-json` `--trend-reset` `--trend-notes` | History + sparklines |
| 22 | **Plugin** | `--plugin DIR` | Custom plugins |
| 23 | **Template Packs** | `--template-pack {minimal,standard,enterprise}` | Template variants |

## 7.3 CLI Reference (ครบทุก flag)

| Flag | Feature | Version |
|---|---|---|
| `--output / -o` | Core | v3.0 |
| `--layer / -l` | Core | v3.0 |
| `--module / -m` | Core | v3.0 |
| `--lang {th,en}` | 🌏 Bilingual | v3.1 |
| `--force / -f` | Core | v3.0 |
| `--dry-run` | Core | v3.0 |
| `--quiet / -q` | Core | v3.0 |
| `--export-json PATH` | 📄 | v3.1 |
| `--export-yaml PATH` | 📄 | v3.1 |
| `--validate-deps` | 🔍 | v3.1 |
| `--generate-readme` | 📊 | v3.1 |
| `--fix-deps` | 🔧 | v3.2 |
| `--strict-deps` | 🔧 | v3.2 |
| `--export-graph PATH` | 🌐 | v3.2 |
| `--graph-format {mermaid,dot}` | 🌐 | v3.2 |
| `--graph-styles` | 🌐 | v3.2 |
| `--stats` | 📊 | v3.2 |
| `--stats-verbose` | 📊 | v3.2 |
| `--stats-json PATH` | 📊 | v3.2 |
| `--merge-template` | 🔄 | v3.2 |
| `--repo-root PATH` | 🔄 | v3.2 |
| `--html-report PATH` | 🎨 | v3.3 |
| `--diff` | 🔬 | v3.3 |
| `--diff-json PATH` | 🔬 | v3.3 |
| `--mock-scaffold` | 🧪 | v3.3 |
| `--scaffold-force` | 🧪 | v3.3 |
| `--notify {slack,line}` | 📡 | v3.3 |
| `--slack-webhook URL` | 📡 | v3.3 |
| `--line-token TOKEN` | 📡 | v3.3 |
| `--line-to ID` | 📡 | v3.3 |
| `--sign` | 🔐 | v3.3 |
| `--gpg-key ID` | 🔐 | v3.3 |
| `--sign-method {auto,gpg,sha256}` | 🔐 | v3.3 |
| `--sign-pattern GLOB` | 🔐 | v3.3 |
| **`--i18n {en,th,jp}`** | 🌍 | **v3.4** |
| **`--pipeline PATH.yaml`** | 🧬 | **v3.4** |
| **`--trend`** | 📈 | **v3.4** |
| **`--trend-json PATH`** | 📈 | **v3.4** |
| **`--trend-reset`** | 📈 | **v3.4** |
| **`--trend-notes TEXT`** | 📈 | **v3.4** |
| **`--plugin DIR`** | 🔌 | **v3.4** |
| **`--template-pack {minimal,standard,enterprise}`** | 🎭 | **v3.4** |
| `--all` | Core | v3.0 |

## 7.4 ตัวอย่างการใช้งาน

### Scenario 1: Full Regeneration

```bash
python scripts/generate_prompts.py --all --force
# → 65 prompts + validate + JSON + YAML + README + graph + stats + HTML
```

### Scenario 2: Health Check

```bash
# 1. Validate + fix deps
python scripts/generate_prompts.py --validate-deps --fix-deps

# 2. ดู stats
python scripts/generate_prompts.py --stats --stats-verbose

# 3. Export graph
python scripts/generate_prompts.py --export-graph architecture.mmd --graph-styles
```

### Scenario 3: Onboarding Module ใหม่

```bash
# 1. Generate prompt ใหม่
python scripts/generate_prompts.py --module new_module --force

# 2. Merge กับ code ที่ implement
python scripts/generate_prompts.py --module new_module --merge-template

# 3. Scaffold missing
python scripts/generate_prompts.py --mock-scaffold
```

### Scenario 4: CI/CD Pipeline

```yaml
# .github/workflows/prompts.yml
name: AI Prompts CI
on: [push]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate deps
        run: python scripts/generate_prompts.py --validate-deps

      - name: Generate + report
        run: |
          python scripts/generate_prompts.py --all --force \
            --html-report docs/prompts/_dashboard.html

      - name: Check drift
        run: python scripts/generate_prompts.py --diff --diff-json drift.json

      - name: Sign (release only)
        if: startsWith(github.ref, 'refs/tags/')
        run: |
          python scripts/generate_prompts.py --sign \
            --gpg-key ${{ secrets.GPG_KEY }}

      - name: Notify
        if: failure()
        run: |
          python scripts/generate_prompts.py --notify slack \
            --slack-webhook ${{ secrets.SLACK_WEBHOOK }}

      - uses: actions/upload-artifact@v4
        with:
          name: prompts-dashboard
          path: docs/prompts/_dashboard.html
```

### Scenario 5: Pipeline YAML

**`pipelines/full.yaml`:**

```yaml
pipeline:
  name: Full generation pipeline
  version: 1.0
  steps:
    - name: Validate deps
      action: validate
      on_error: stop

    - name: Generate all prompts
      action: generate
      args:
        output: docs/prompts
        lang: en
      on_error: stop

    - name: Statistics
      action: stats
      args:
        json: reports/stats.json
        verbose: true

    - name: HTML dashboard
      action: html
      args:
        path: reports/dashboard.html

    - name: Dependency graph
      action: graph
      args:
        path: reports/graph.mmd
        format: mermaid
        styles: true

    - name: Drift check
      action: diff
      args:
        repo_root: .
        json: reports/drift.json
      on_error: continue

    - name: Scaffold missing
      action: scaffold
      args:
        repo_root: .

    - name: Generate README
      action: readme

    - name: Notify Slack
      action: notify
      args:
        channel: slack
      on_error: continue
```

```bash
python scripts/generate_prompts.py --pipeline pipelines/full.yaml
```

### Scenario 6: Trend Analysis

```bash
# Take snapshot + view trend
python scripts/generate_prompts.py --trend --trend-notes "After adding 5 modules"

# Output:
# 📈 Trend Analysis
#    Metric                 Current   Previous  Δ
#    Modules                     57         57  ±0
#    Entities                   148        138  📈 +10.0 (+7.2%)
#    Events                     218        205  📈 +13.0 (+6.3%)
#
#    📊 Sparklines:
#    Entities     ▃█  [138..148]
#    Events       ▃█  [205..218]
```

### Scenario 7: Plugin Extension

**`plugins/watermark.py`:**

```python
"""Example plugin — adds a watermark to every prompt."""

from scripts.generate_prompts import PluginBase, PluginContext, ModuleMeta


class Plugin(PluginBase):
    name = "Watermark Plugin"
    version = "1.0.0"
    description = "Adds custom watermark to each prompt file"

    def on_load(self, ctx: PluginContext) -> None:
        print(f"   [plugin] {self.name} loaded (modules: {len(ctx.modules)})")

    def transform_prompt(
        self, ctx: PluginContext, meta: ModuleMeta, content: str
    ) -> str:
        return content + f"\n\n<!-- Generated by {self.name} v{self.version} -->"

    def on_complete(self, ctx: PluginContext) -> None:
        print(f"   [plugin] {self.name} done")
```

```bash
python scripts/generate_prompts.py --plugin plugins/ --all
```

## 7.5 Dependencies

**Zero external Python deps** — ใช้แค่ stdlib:

| Feature | stdlib ที่ใช้ |
|---|---|
| HTML report | `json` (Chart.js โหลดจาก CDN) |
| Diff | `re`, `hashlib` |
| Scaffold | `pathlib` |
| Notify | `urllib.request`, `json` |
| Sign | `subprocess`, `hashlib`, `shutil` |
| i18n | `dict` lookup |
| Pipeline | custom YAML parser (stdlib) |
| Trend | `json`, `datetime`, Unicode |
| Plugin | `importlib.util` |
| Template packs | pure string templates |

**External tools (optional):**
- `gpg` — สำหรับ GPG signing (fallback → SHA-256 อัตโนมัติ)
- `dot` (Graphviz) — สำหรับ render DOT graph
- `mmdc` (Mermaid CLI) — สำหรับ render Mermaid

## 7.6 สรุป v3.4

| Metric | Value |
|---|---|
| **Features** | 18 |
| **CLI flags** | 40+ |
| **Languages (UI)** | 3 (EN/TH/JP) |
| **Languages (content)** | 2 (TH/EN) |
| **Template packs** | 3 |
| **Plugin hooks** | 5 |
| **Pipeline actions** | 10 |
| **External deps** | 0 (Python) |

---

# 8. ภาคผนวก

## 8.1 ลำดับการทำงานที่แนะนำ

```
┌─────────────────────────────────────────────────────────────┐
│  1. ตรวจสุขภาพโปรเจกต์                                      │
│     --validate-deps --fix-deps --stats --export-graph      │
├─────────────────────────────────────────────────────────────┤
│  2. Generate prompts                                        │
│     --all --force                                           │
├─────────────────────────────────────────────────────────────┤
│  3. Implement code ตาม prompts                              │
│     (developer ทำงาน)                                       │
├─────────────────────────────────────────────────────────────┤
│  4. ตรวจ drift                                              │
│     --diff --mock-scaffold                                  │
├─────────────────────────────────────────────────────────────┤
│  5. Merge template                                          │
│     --merge-template                                        │
├─────────────────────────────────────────────────────────────┤
│  6. Report + Notify                                         │
│     --html-report --notify slack                            │
├─────────────────────────────────────────────────────────────┤
│  7. Track trend                                             │
│     --trend --trend-json                                    │
├─────────────────────────────────────────────────────────────┤
│  8. Release                                                 │
│     --sign --gpg-key $RELEASE_KEY                           │
└─────────────────────────────────────────────────────────────┘
```

## 8.2 Checklist ก่อน Merge

- [ ] Domain layer ไม่ import framework
- [ ] ใช้ `flush()` ไม่ใช่ `commit()` ใน repository
- [ ] Cache never raises
- [ ] Error handling ถูก shape (3/2/never)
- [ ] Idempotency ครบ (money/goods path)
- [ ] Audit log ครบ
- [ ] Read-back verification ครบ
- [ ] Tests ครบ 3 ประเภท (unit/integration/property)
- [ ] Manual test cases ครบ 8 scenarios
- [ ] SQL migrations ครบ 3 ไฟล์ (V001/V002/V003)
- [ ] RLS policy present
- [ ] Comment 2 ภาษา
- [ ] พร้อมรัน

## 8.3 ไฟล์อ้างอิง

| ไฟล์ | คำอธิบาย |
|---|---|
| `docs/template_modules.md` | Master template |
| `docs/prompts/README.md` | Index 65 modules |
| `docs/prompts/layer-{n}-{name}/{module}.md` | 65 prompt files |
| `scripts/generate_prompts.py` | Python generator v3.4 |
| `app/modules/{module}/` | Generated code |
| `db/migrations/` | SQL migrations |
| `tests/` | Test files |

## 8.4 สรุปสุดท้าย

| Component | Count |
|---|---|
| **Layers** | 8 (0-7) |
| **Modules** | 65 |
| **Files per Module** | 23 |
| **Total Files** | 1,495 |
| **Prompt Files** | 65 |
| **Script Features** | 18 |
| **CLI Flags** | 40+ |
| **External Deps** | 0 |

---

> **เวอร์ชัน:** 3.4.0 · **วันที่:** 2026-09-17
> **ผู้เขียน:** AI Prompt Template System
> **License:** Internal Use
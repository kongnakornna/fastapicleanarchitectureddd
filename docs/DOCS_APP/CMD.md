
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


 สร้าง  AI Prompt ตาม Template

 เรียง ตามนี้
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

1 module  = 1 file
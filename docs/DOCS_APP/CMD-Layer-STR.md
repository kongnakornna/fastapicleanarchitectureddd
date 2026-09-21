1. ✅ **สร้างไฟล์** (File Generation)
2. ✅ **ออกแบบ Database** → สร้างไฟล์ `prefix_ชื่อmodules.sql`
3. ✅ **ออกแบบ Unit Test + Manual Test**

ด้านล่างคือ **Template v3.0** ที่ปรับปรุงแล้วครับ

---

## 📂 โครงสร้างโฟลเดอร์ใหม่ (อัปเดต)

```
project-root/
├── docs/
│   ├── template_modules.md                    # 📘 Master template v3.0
│   └── prompts/
│       ├── README.md
│       ├── layer-0-core/ ... layer-7-templates/
│
├── app/modules/{module_name}/                 # 🐍 Python code (16 ไฟล์)
│   ├── domain/           (3 ไฟล์)
│   ├── application/      (5 ไฟล์)
│   ├── infrastructure/   (4 ไฟล์)
│   └── presentation/     (4 ไฟล์)
│
├── db/                                         # 🗄️ Database
│   └── migrations/
│       ├── V001__create_{module_name}.sql      # DDL
│       ├── V002__seed_{module_name}.sql        # Seed data
│       └── V003__rollback_{module_name}.sql    # Rollback
│
└── tests/                                      # 🧪 Tests
    ├── unit/
    │   └── test_{module_name}.py
    ├── integration/
    │   └── test_{module_name}_repository.py
    ├── property/
    │   └── test_{module_name}_invariants.py
    └── manual/
        └── manual_test_{module_name}.md        # 📋 Manual Test Cases
```

---

## 📘 ไฟล์ 1: `docs/template_modules.md` (Master Template v3.0)

```markdown
# AI Prompt Template — สร้าง Module ใหม่ใน ERP + CRM + IoT

> **เวอร์ชัน:** 3.0.0
> **Stack:** Python 3.14+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · PostgreSQL 17 · Redis 8 · Kafka
> **เพิ่มใหม่ v3.0:** SQL Migration · Unit Test · Manual Test

---

## 📋 ข้อมูล Module (Metadata)

| หัวข้อ | รายละเอียด | ตัวอย่าง |
|---|---|---|
| **ชื่อ Module** | `{module_name}` | `agriculture` |
| **Prefix** | `{prefix}` | `agr` |
| **Layer** | `{layer_number}` (0-7) | `3` |
| **Priority** | `{priority}` | `🟠` |
| **Phase** | `{phase}` | `4` |
| **มิติธุรกิจ** | `{agriculture/production/logistics/factory/erp/crm}` | `agriculture` |
| **Dependencies** | `{list_of_modules}` | `crop, soil, iot` |
| **Domain Concepts** | `{entities}, {value_objects}, {enums}` | `Farm, Plot` |

---

## 🎯 Prompt Template (Master v3.0)

### สร้าง Module `{module_name}`

**บริบท:**
- ERP + CRM + IoT สำหรับ SME (Multi-company)
- Clean Architecture + DDD (4 layers)
- Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0
- PostgreSQL 17 (schema-per-tenant), Redis 8, Kafka
- ทุก action แตะเงิน/สต็อก → audit log
- Money Path + Goods Path ต้อง idempotent

**ข้อกำหนด (10 ข้อ):**

#### 1. Domain Layer (`domain/`)
- `entities.py`: Dataclasses extending `BaseEntity`
- `value_objects.py`: Plain classes with `_normalize → _validate → __str__ → __eq__`
- `enums.py`: All enums as `(str, Enum)`
- **ห้าม import framework ใดๆ**

#### 2. Application Layer (`application/`)
- `interfaces.py`: Protocol contracts
- `use_cases.py`: One `{Module}UseCases` class
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

#### 5. 🆕 Database Layer (`db/migrations/`)

**ไฟล์:** `V001__create_{module_name}.sql`

```sql
-- Migration: V001__create_{module_name}.sql
-- Module: {module_name} | Layer: {layer} | Tenant-aware: YES
-- Author: {author} | Date: {date}

BEGIN;

-- Schema (per-tenant)
CREATE SCHEMA IF NOT EXISTS tenant_{prefix};

-- Main table
CREATE TABLE tenant_{prefix}.{module_name}s (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    code            VARCHAR(50) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    amount          NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    metadata        JSONB DEFAULT '{}'::jsonb,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT uq_{prefix}_code UNIQUE (tenant_id, code),
    CONSTRAINT ck_{prefix}_amount_positive CHECK (amount >= 0),
    CONSTRAINT ck_{prefix}_status_valid CHECK (status IN ('DRAFT','ISSUED','PAID','VOIDED'))
);

-- Child table
CREATE TABLE tenant_{prefix}.{module_name}_lines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    parent_id       UUID NOT NULL REFERENCES tenant_{prefix}.{module_name}s(id) ON DELETE CASCADE,
    product_id      UUID NOT NULL,
    qty             NUMERIC(15, 4) NOT NULL,
    unit_price      NUMERIC(15, 2) NOT NULL,
    amount          NUMERIC(15, 2) GENERATED ALWAYS AS (qty * unit_price) STORED,

    CONSTRAINT ck_{prefix}_line_qty_positive CHECK (qty > 0),
    CONSTRAINT ck_{prefix}_line_price_non_negative CHECK (unit_price >= 0)
);

-- Idempotency table (Money/Goods path only)
CREATE TABLE tenant_{prefix}.{module_name}_idempotency (
    idem_key        VARCHAR(255) PRIMARY KEY,
    tenant_id       UUID NOT NULL,
    response_hash   VARCHAR(64) NOT NULL,
    response_body   JSONB NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX ix_{prefix}_tenant_id      ON tenant_{prefix}.{module_name}s(tenant_id);
CREATE INDEX ix_{prefix}_status         ON tenant_{prefix}.{module_name}s(status) WHERE deleted_at IS NULL;
CREATE INDEX ix_{prefix}_created_at     ON tenant_{prefix}.{module_name}s(created_at DESC);
CREATE INDEX ix_{prefix}_metadata_gin   ON tenant_{prefix}.{module_name}s USING GIN(metadata);
CREATE INDEX ix_{prefix}_lines_parent   ON tenant_{prefix}.{module_name}_lines(parent_id);

-- Audit trigger
CREATE TRIGGER trg_{prefix}_updated_at
    BEFORE UPDATE ON tenant_{prefix}.{module_name}s
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Row-Level Security
ALTER TABLE tenant_{prefix}.{module_name}s ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_{prefix}_tenant_isolation ON tenant_{prefix}.{module_name}s
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**ไฟล์:** `V002__seed_{module_name}.sql` — seed data สำหรับ dev
**ไฟล์:** `V003__rollback_{module_name}.sql` — DROP ทั้งหมด

#### 6. 🆕 Unit Test (`tests/unit/test_{module_name}.py`)

```python
"""
Unit tests — {module_name}
ใช้ in-memory fakes, ไม่แตะ DB/Redis/Kafka
Coverage target: ≥ 90%
"""
import pytest
from decimal import Decimal
from app.modules.{module_name}.domain.entities import {Entity}
from app.modules.{module_name}.domain.value_objects import {VO}
from app.modules.{module_name}.application.use_cases import {Module}UseCases
from tests.fakes import Fake{Module}Repository, Fake{Module}Cache

# ─── Domain Tests ─────────────────────────────────
class Test{Entity}Domain:
    def test_create_valid(self): ...
    def test_create_invalid_code_raises(self): ...
    def test_status_transition_forward_only(self): ...

# ─── Use Case Tests ───────────────────────────────
class Test{Module}UseCases:
    @pytest.fixture
    def use_cases(self):
        return {Module}UseCases(
            repo=Fake{Module}Repository(),
            cache=Fake{Module}Cache(),
            idempotency=FakeIdempotency(),
            audit=FakeAudit(),
            events=FakeEventBus(),
        )

    async def test_create_success(self, use_cases): ...
    async def test_create_idempotent(self, use_cases): ...
    async def test_create_readback_verification(self, use_cases): ...

# ─── Property-Based Tests ─────────────────────────
from hypothesis import given, strategies as st

class TestInvariants:
    @given(st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1e9")))
    def test_amount_always_positive(self, amount): ...

    @given(st.lists(st.builds(Line), min_size=1, max_size=100))
    def test_total_equals_sum_of_lines(self, lines): ...
```

#### 7. 🆕 Integration Test (`tests/integration/test_{module_name}_repository.py`)

```python
"""
Integration tests — {module_name} repository
ใช้ testcontainers + PostgreSQL จริง
"""
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="module")
def postgres():
    with PostgresContainer("postgres:17") as pg:
        yield pg

class TestPostgres{Entity}Repository:
    async def test_save_and_get_by_id(self, postgres): ...
    async def test_flush_not_commit(self, postgres): ...
    async def test_unique_constraint_violation(self, postgres): ...
    async def test_tenant_isolation_rls(self, postgres): ...
    async def test_concurrent_number_generation(self, postgres): ...
```

#### 8. 🆕 Manual Test Cases (`tests/manual/manual_test_{module_name}.md`)

```markdown
# Manual Test Cases — Module `{module_name}`

> **Tester:** _____ **Date:** _____ **Build:** _____
> **Environment:** ☐ DEV ☐ UAT ☐ PROD

## 🎯 Pre-conditions
- [ ] DB migration รันแล้ว (`V001__create_{module_name}.sql`)
- [ ] Tenant context ถูกตั้งค่า
- [ ] User มี role `{required_role}`
- [ ] Redis + Kafka พร้อม

## 📋 Test Scenarios

### TC-01: สร้างข้อมูลใหม่ (Happy Path)
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | POST `/api/v1/{module_name}/` + Idempotency-Key | 201 + body | ☐ Pass ☐ Fail |
| 2 | ตรวจ DB table `{prefix}_{module_name}s` | 1 row, status=DRAFT | ☐ Pass ☐ Fail |
| 3 | ตรวจ audit log | มี `{module_name}.created` | ☐ Pass ☐ Fail |
| 4 | ตรวจ Kafka topic `{module_name}.events` | มี `{Module}Created` | ☐ Pass ☐ Fail |

### TC-02: Idempotency (ส่งซ้ำ)
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | POST เดิม + Idempotency-Key เดิม (2 ครั้ง) | 201 ครั้งเดียว, ครั้งที่ 2 ได้ response เดิม | ☐ Pass ☐ Fail |
| 2 | ตรวจ DB | มี 1 row เท่านั้น | ☐ Pass ☐ Fail |

### TC-03: Read-back Verification
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | สร้างข้อมูล → query DB ทันที | ค่าตรงกับ response | ☐ Pass ☐ Fail |

### TC-04: Validation Errors
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | POST ด้วย `amount = -100` | 422 Unprocessable | ☐ Pass ☐ Fail |
| 2 | POST โดยไม่มี Idempotency-Key | 422 | ☐ Pass ☐ Fail |
| 3 | POST ด้วย code ซ้ำ | 409 Conflict | ☐ Pass ☐ Fail |

### TC-05: Multi-tenant Isolation
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | Login tenant A → สร้างข้อมูล | OK | ☐ Pass ☐ Fail |
| 2 | Login tenant B → GET ข้อมูลของ A | 404 Not Found | ☐ Pass ☐ Fail |

### TC-06: Cache Fallback
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | ปิด Redis → GET | ยัง return 200 (fallback DB) | ☐ Pass ☐ Fail |
| 2 | เปิด Redis → GET | ใช้ cache (ตรวจ log) | ☐ Pass ☐ Fail |

### TC-07: Concurrency
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | ยิง 100 concurrent POSTs | code ไม่ซ้ำ, ไม่มี deadlock | ☐ Pass ☐ Fail |

### TC-08: Rollback Migration
| Step | Action | Expected | Result |
|---|---|---|---|
| 1 | รัน `V003__rollback_{module_name}.sql` | tables ถูก drop | ☐ Pass ☐ Fail |
| 2 | รัน `V001__create_{module_name}.sql` อีกครั้ง | สร้างใหม่ได้ | ☐ Pass ☐ Fail |

## 📊 Sign-off
| Role | Name | Date | Signature |
|---|---|---|---|
| Developer | | | |
| QA | | | |
| Tech Lead | | | |
```

#### 9. Error Handling (3 shapes)
- 3-branch: Use cases + router handlers
- 2-branch: Repositories + services
- Never-raise: Caches

#### 10. Checklist & Invariants
- Invariants: `{module_specific_invariants}`
- Domain Events: `{Module}Created/Updated/Deleted`
- Audit log ครบทุก action
- Idempotency ครบ (money/goods path)

**Output รวม:**
- 🐍 Python: **16 ไฟล์** (4 layers × 4)
- 🗄️ SQL: **3 ไฟล์** (create / seed / rollback)
- 🧪 Tests: **4 ไฟล์** (unit / integration / property / manual)
- **รวม: 23 ไฟล์**

---

## 📐 โครงสร้างไฟล์ Output (23 ไฟล์)

```
app/modules/{module_name}/                # 🐍 16 Python files
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

db/migrations/                            # 🗄️ 3 SQL files
├── V001__create_{module_name}.sql
├── V002__seed_{module_name}.sql
└── V003__rollback_{module_name}.sql

tests/                                    # 🧪 4 test files
├── unit/
│   └── test_{module_name}.py
├── integration/
│   └── test_{module_name}_repository.py
├── property/
│   └── test_{module_name}_invariants.py
└── manual/
    └── manual_test_{module_name}.md
```

---

## ✅ Checklist v3.0 ก่อนส่ง

### Code Quality
- [ ] Domain layer ไม่ import framework
- [ ] ใช้ `flush()` ไม่ใช่ `commit()` ใน repository
- [ ] Cache never raises
- [ ] Error handling ถูก shape (3/2/never)
- [ ] Comment 2 ภาษา
- [ ] พร้อมรัน `uvicorn app.app:app --reload`

### 🆕 Database
- [ ] มี `V001__create_{module_name}.sql`
- [ ] มี `V002__seed_{module_name}.sql`
- [ ] มี `V003__rollback_{module_name}.sql`
- [ ] ใช้ `tenant_{prefix}` schema
- [ ] มี RLS policy
- [ ] มี CHECK constraints ครบ
- [ ] มี GIN index สำหรับ JSONB (ถ้ามี)
- [ ] มี trigger `updated_at`

### 🆕 Testing
- [ ] Unit test coverage ≥ 90%
- [ ] Integration test ผ่าน (testcontainers)
- [ ] Property-based test ผ่าน (hypothesis)
- [ ] Manual test cases ครบ 8 scenarios
- [ ] `pytest --cov` ผ่าน threshold

### Business
- [ ] Idempotency ครบ (money/goods path)
- [ ] Audit log ครบ
- [ ] Read-back verification ครบ
- [ ] Multi-tenant isolation ทดสอบแล้ว
```

---

## 🚀 วิธีใช้ v3.0

```bash
# 1. สร้างโครงสร้างโฟลเดอร์
mkdir -p app/modules/{module_name}/{domain,application,infrastructure,presentation}
mkdir -p db/migrations
mkdir -p tests/{unit,integration,property,manual}

# 2. Copy prompt ไปวางใน AI
# AI จะสร้าง 23 ไฟล์ให้ครบ

# 3. รัน migration
psql -f db/migrations/V001__create_{module_name}.sql
psql -f db/migrations/V002__seed_{module_name}.sql

# 4. รัน tests
uv run pytest tests/unit/ -v --cov
uv run pytest tests/integration/ -v
uv run pytest tests/property/ -v

# 5. Manual test
# เปิด tests/manual/manual_test_{module_name}.md แล้วทำตาม TC-01 ถึง TC-08
```

---

## 📊 สรุปการเปลี่ยนแปลง v2.0 → v3.0

| หมวด | v2.0 | v3.0 | เพิ่ม |
|---|---|---|---|
| Python files | 16 | 16 | — |
| SQL files | 0 | **3** | +3 |
| Test files | 3 | **4** | +1 (manual) |
| **รวมต่อ module** | **19** | **23** | **+4** |
| **รวม 65 modules** | **1,235** | **1,495** | **+260** |

---

ต้องการให้ผม **generate ตัวอย่างเต็ม** สำหรับ module ใดก่อนไหมครับ? เช่น:

- 🟢 `agriculture` (เกษตร) — มี Farm, Plot, Harvest + SQL + tests
- 🔴 `invoice` (Money Path) — มี Idempotency + RLS + concurrency test
- 🟠 `iot` (Sensing) — มี Time-series + InfluxDB + threshold alert

 # 📚 Prompt Templates — 59 Modules ที่เหลือ (v3.0)

> **ใช้ร่วมกับ:** `docs/template_modules.md` (Master Template v3.0)
> **รูปแบบ:** แต่ละ module จะระบุเฉพาะ **Metadata + Domain Concepts + Invariants + Events + Special Rules**
> ที่เหลือ (16 Python files + 3 SQL + 4 tests) ใช้ boilerplate จาก Master Template

---

## 📑 Layer 0: CORE (5 modules)

### 1. `tenant_context` — Multi-tenant Context

| Field | Value |
|---|---|
| Layer / Priority / Phase | 0 / 🔴 / 1 |
| มิติ | Core (cross-cutting) |
| Prefix | `tctx` |
| Dependencies | `tenancy` |

**Domain Concepts:**
- Entity: `TenantContext`
- VO: `TenantId`, `SchemaName`
- Enum: `ContextSource` (HEADER, JWT, SUBDOMAIN)

**Invariants:**
- `tenant_id` ต้องถูกตั้งค่าก่อนทุก DB query
- `schema_name` ตรงกับ pattern `^tenant_[a-z0-9_]+$`

**Events:** `TenantContextSet`, `TenantContextCleared`

**Tables:** `tenant_{prefix}.tenant_contexts` (audit trail)

**Special Rules:**
- Middleware-level: ใช้ `ContextVar` (asyncio-safe)
- Set `app.current_tenant` GUC สำหรับ RLS
- ทุก repository ต้อง `Depends(get_current_tenant)`

---

### 2. `audit` — Audit Log

| Field | Value |
|---|---|
| Layer / Priority / Phase | 0 / 🔴 / 1 |
| มิติ | Core |
| Prefix | `aud` |
| Dependencies | `tenant_context`, `events` |

**Domain Concepts:**
- Entity: `AuditLog`
- VO: `AuditAction`, `AuditDiff`, `Actor`
- Enum: `AuditAction` (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, EXPORT)

**Invariants:**
- Audit log **immutable** (append-only, no UPDATE/DELETE)
- ทุก record ต้องมี `actor_id` + `tenant_id` + `timestamp`
- `before` + `after` ต้องเป็น valid JSON

**Events:** `AuditLogWritten`, `AuditLogExported`

**Tables:** `tenant_{prefix}.audit_logs` (BRIN index on timestamp)

**Special Rules:**
- Async write (fire-and-forget ผ่าน Kafka)
- Retention 7 ปี (compliance)
- PII masking ใน metadata

---

### 3. `idempotency` — Idempotency Keys

| Field | Value |
|---|---|
| Layer / Priority / Phase | 0 / 🔴 / 1 |
| มิติ | Core |
| Prefix | `idem` |
| Dependencies | `tenant_context` |

**Domain Concepts:**
- Entity: `IdempotencyRecord`
- VO: `IdempotencyKey`, `ResponseHash`
- Enum: `IdempotencyStatus` (PENDING, COMPLETED, FAILED)

**Invariants:**
- Key unique ต่อ `(tenant_id, key)` 
- Response hash ต้องตรงกันถ้าส่งซ้ำ
- TTL = 24 ชั่วโมง (Redis) + persistent (Postgres)

**Events:** `IdempotencyHit`, `IdempotencyMiss`, `IdempotencyConflict`

**Tables:** `tenant_{prefix}.idempotency_records`

**Special Rules:**
- ใช้ `SETNX` ใน Redis ก่อน → fallback Postgres
- Return cached response ถ้า key ซ้ำ + hash ตรง
- Return 409 Conflict ถ้า key ซ้ำ + hash ไม่ตรง

---

### 4. `config` — Configuration Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 0 / 🔴 / 1 |
| มิติ | Core |
| Prefix | `cfg` |
| Dependencies | `tenant_context`, `audit` |

**Domain Concepts:**
- Entity: `ConfigEntry`
- VO: `ConfigKey`, `ConfigValue`
- Enum: `ConfigScope` (GLOBAL, TENANT, USER, MODULE)

**Invariants:**
- Config key unique ต่อ `(scope, tenant_id, key)`
- Value type ตรงกับ schema ที่ลงทะเบียน
- Sensitive config ต้อง encrypted at rest

**Events:** `ConfigChanged`, `ConfigRollback`, `ConfigImported`

**Tables:** `tenant_{prefix}.configs`

**Special Rules:**
- Hierarchical override: GLOBAL < TENANT < USER
- Cache ใน Redis (namespace `cfg:{scope}:{tenant}:{key}`)
- Versioning + rollback support

---

### 5. `events` — Domain Event Bus

| Field | Value |
|---|---|
| Layer / Priority / Phase | 0 / 🔴 / 1 |
| มิติ | Core |
| Prefix | `evt` |
| Dependencies | `tenant_context` |

**Domain Concepts:**
- Entity: `EventLog`
- VO: `EventName`, `EventPayload`, `CorrelationId`
- Enum: `EventStatus` (PENDING, PUBLISHED, FAILED, DEAD_LETTER)

**Invariants:**
- Event name ตรง pattern `^[A-Z][a-zA-Z]+$` (PascalCase)
- Payload ต้อง serialize ได้ (JSON)
- `correlation_id` + `causation_id` ต้องมี

**Events:** `EventPublished`, `EventFailed`, `EventDeadLettered`

**Tables:** `tenant_{prefix}.event_logs` (outbox pattern)

**Special Rules:**
- Transactional outbox pattern
- Kafka topics: `{tenant}.{module}.events`
- Retry 3 ครั้ง → dead letter queue
- At-least-once delivery + consumer idempotency

---

## 📑 Layer 1: FOUNDATION (8 modules)

### 6. `tenancy` — Multi-tenancy

| Field | Value |
|---|---|
| Layer / Priority / Phase | 1 / 🔴 / 1 |
| มิติ | Foundation |
| Prefix | `ten` |
| Dependencies | `tenant_context`, `audit` |

**Domain Concepts:**
- Entity: `Tenant`, `TenantPlan`
- VO: `TenantSlug`, `SchemaName`, `ResourceQuota`
- Enum: `TenantStatus` (ACTIVE, SUSPENDED, TRIAL, CANCELLED)

**Invariants:**
- Slug unique + pattern `^[a-z][a-z0-9-]{2,30}$`
- Schema name = `tenant_{slug}`
- Quota ไม่ติดลบ

**Events:** `TenantCreated`, `TenantSuspended`, `TenantUpgraded`, `TenantDeleted`

**Tables:** `public.tenants`, `public.tenant_plans`

**Special Rules:**
- Provisioning schema อัตโนมัติ (CREATE SCHEMA + migrations)
- Soft delete (grace period 30 วัน)
- Billing integration (Stripe/Omise)

---

### 7. `authentication` — Authentication

| Field | Value |
|---|---|
| Layer / Priority / Phase | 1 / 🔴 / 1 |
| มิติ | Foundation |
| Prefix | `auth` |
| Dependencies | `tenancy`, `user`, `audit` |

**Domain Concepts:**
- Entity: `Session`, `RefreshToken`, `ApiKey`
- VO: `PasswordHash`, `JWTClaim`
- Enum: `AuthMethod` (PASSWORD, OAUTH, API_KEY, MFA)

**Invariants:**
- Password hash ใช้ Argon2id (ไม่ใช่ bcrypt)
- Refresh token single-use (rotation)
- API key hash เก็บแบบ SHA-256
- Max 5 login attempts → lock 15 นาที

**Events:** `UserLoggedIn`, `UserLoggedOut`, `LoginFailed`, `TokenRefreshed`, `MFARequired`

**Tables:** `tenant_{prefix}.sessions`, `tenant_{prefix}.refresh_tokens`, `tenant_{prefix}.api_keys`, `tenant_{prefix}.login_attempts`

**Special Rules:**
- JWT access token: 15 นาที
- Refresh token: 7 วัน (rotating)
- MFA: TOTP + backup codes
- Rate limit: 5 req/min ต่อ IP

---

### 8. `user` — User Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 1 / 🔴 / 1 |
| มิติ | Foundation |
| Prefix | `usr` |
| Dependencies | `tenancy`, `authentication`, `audit` |

**Domain Concepts:**
- Entity: `User`, `Role`, `Permission`
- VO: `Email`, `PhoneNumber`, `FullName`
- Enum: `UserStatus` (ACTIVE, INACTIVE, SUSPENDED, PENDING_VERIFICATION)

**Invariants:**
- Email unique ต่อ tenant
- User ต้องมี role อย่างน้อย 1
- Role name unique ต่อ tenant

**Events:** `UserCreated`, `UserUpdated`, `UserDeactivated`, `RoleAssigned`, `PermissionGranted`

**Tables:** `tenant_{prefix}.users`, `tenant_{prefix}.roles`, `tenant_{prefix}.permissions`, `tenant_{prefix}.user_roles`

**Special Rules:**
- Email verification required
- Soft delete (deleted_at)
- RBAC model (role → permissions)
- ไม่ให้ลบ user ที่มี audit log

---

### 9. `employee` — Employee Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 1 / 🟠 / 1 |
| มิติ | Foundation (HR) |
| Prefix | `emp` |
| Dependencies | `user`, `audit` |

**Domain Concepts:**
- Entity: `Employee`, `Department`, `Position`
- VO: `EmployeeCode`, `Salary`, `HireDate`
- Enum: `EmploymentType` (FULL_TIME, PART_TIME, CONTRACT, INTERN)

**Invariants:**
- Employee code unique ต่อ tenant
- Salary >= 0
- Hire date <= today
- User 1 คน = 1 employee

**Events:** `EmployeeHired`, `EmployeePromoted`, `EmployeeTerminated`, `DepartmentCreated`

**Tables:** `tenant_{prefix}.employees`, `tenant_{prefix}.departments`, `tenant_{prefix}.positions`

**Special Rules:**
- Link กับ user (1:1)
- Salary encrypted at rest
- Org chart relationship

---

### 10. `customer` — Customer Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 1 / 🔴 / 1 |
| มิติ | Foundation (CRM) |
| Prefix | `cust` |
| Dependencies | `tenancy`, `audit` |

**Domain Concepts:**
- Entity: `Customer`, `CustomerGroup`, `Address`
- VO: `TaxId`, `CreditLimit`, `CustomerTier`
- Enum: `CustomerType` (INDIVIDUAL, COMPANY, GOVERNMENT)

**Invariants:**
- Tax ID unique ต่อ tenant (ถ้ามี)
- Credit limit >= 0
- Email/phone format valid

**Events:** `CustomerCreated`, `CustomerUpdated`, `CustomerBlacklisted`, `CreditLimitChanged`

**Tables:** `tenant_{prefix}.customers`, `tenant_{prefix}.customer_groups`, `tenant_{prefix}.customer_addresses`

**Special Rules:**
- Soft delete (ลูกค้าที่มี invoice ห้ามลบ)
- PDPA compliance (consent tracking)
- Merge duplicate customers

---

### 11. `supplier` — Supplier Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 1 / 🟠 / 1 |
| มิติ | Foundation (Procurement) |
| Prefix | `sup` |
| Dependencies | `audit`, `product` |

**Domain Concepts:**
- Entity: `Supplier`, `SupplierContact`, `SupplierProduct`
- VO: `TaxId`, `PaymentTerms`, `LeadTime`
- Enum: `SupplierStatus` (ACTIVE, INACTIVE, BLACKLISTED, PENDING)

**Invariants:**
- Tax ID unique ต่อ tenant
- Payment terms >= 0 วัน
- Rating 0-5

**Events:** `SupplierCreated`, `SupplierApproved`, `SupplierBlacklisted`, `SupplierRated`

**Tables:** `tenant_{prefix}.suppliers`, `tenant_{prefix}.supplier_contacts`, `tenant_{prefix}.supplier_products`

**Special Rules:**
- Vendor rating system
- Approved vendor list (AVL)
- Link กับ product (many-to-many)

---

### 12. `product` — Product Catalog

| Field | Value |
|---|---|
| Layer / Priority / Phase | 1 / 🔴 / 1 |
| มิติ | Foundation |
| Prefix | `prod` |
| Dependencies | `audit`, `pricing` |

**Domain Concepts:**
- Entity: `Product`, `ProductVariant`, `Category`, `UOM`
- VO: `SKU`, `Barcode`, `ProductName`, `Weight`
- Enum: `ProductType` (GOODS, SERVICE, RAW_MATERIAL, BUNDLE)

**Invariants:**
- SKU unique ต่อ tenant
- Barcode unique (ถ้ามี)
- Weight >= 0

**Events:** `ProductCreated`, `ProductUpdated`, `ProductDiscontinued`, `PriceChanged`

**Tables:** `tenant_{prefix}.products`, `tenant_{prefix}.product_variants`, `tenant_{prefix}.categories`, `tenant_{prefix}.uoms`

**Special Rules:**
- Soft delete
- Multi-UOM (base + conversion)
- Image storage (S3/MinIO)
- Variant matrix (size × color)

---

### 13. `pricing` — Pricing & Discounts

| Field | Value |
|---|---|
| Layer / Priority / Phase | 1 / 🔴 / 1 |
| มิติ | Foundation |
| Prefix | `prc` |
| Dependencies | `product`, `customer`, `audit` |

**Domain Concepts:**
- Entity: `PriceList`, `PriceRule`, `Discount`
- VO: `Price`, `DiscountRate`, `EffectiveDate`
- Enum: `PriceType` (RETAIL, WHOLESALE, MEMBER, PROMOTION)

**Invariants:**
- Price >= 0
- Discount 0-100%
- Effective date range valid
- ไม่มี overlapping price list ที่ active

**Events:** `PriceListCreated`, `PriceChanged`, `DiscountApplied`, `PromotionStarted`

**Tables:** `tenant_{prefix}.price_lists`, `tenant_{prefix}.price_rules`, `tenant_{prefix}.discounts`

**Special Rules:**
- Hierarchical pricing (customer > group > default)
- Time-based pricing
- Volume discounts (tiered)

---

## 📑 Layer 2: MONEY PATH (6 modules)

### 14. `order` — Sales Order

| Field | Value |
|---|---|
| Layer / Priority / Phase | 2 / 🔴 / 1 |
| มิติ | ERP |
| Prefix | `ord` |
| Dependencies | `customer`, `product`, `pricing`, `tax`, `audit`, `idempotency` |

**Domain Concepts:**
- Entity: `SalesOrder`, `OrderLine`
- VO: `OrderNumber`, `OrderTotal`, `ShippingAddress`
- Enum: `OrderStatus` (DRAFT, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED)

**Invariants:**
- `total = subtotal - discount + VAT + shipping`
- `qty > 0` ทุก line
- Order number unique + pattern `SO-YYYYMM-XXXX`
- Status transition forward-only

**Events:** `OrderCreated`, `OrderConfirmed`, `OrderCancelled`, `OrderShipped`, `OrderDelivered`

**Tables:** `tenant_{prefix}.sales_orders`, `tenant_{prefix}.sales_order_lines`

**Special Rules:**
- Reserve inventory on confirm
- Release on cancel
- Link to invoice (1:N)

---

### 15. `ledger` — General Ledger

| Field | Value |
|---|---|
| Layer / Priority / Phase | 2 / 🔴 / 1 |
| มิติ | ERP (Accounting) |
| Prefix | `led` |
| Dependencies | `money`, `audit`, `idempotency` |

**Domain Concepts:**
- Entity: `JournalEntry`, `LedgerEntry`, `Account`
- VO: `AccountCode`, `DebitCredit`, `PostingDate`
- Enum: `AccountType` (ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE)

**Invariants:**
- **`sum(debit) == sum(credit)`** (double-entry)
- Journal entry posted = immutable
- Posting date <= today
- Account code unique

**Events:** `JournalEntryPosted`, `LedgerEntryCreated`, `AccountCreated`, `PeriodClosed`

**Tables:** `tenant_{prefix}.accounts`, `tenant_{prefix}.journal_entries`, `tenant_{prefix}.ledger_entries`, `tenant_{prefix}.accounting_periods`

**Special Rules:**
- Immutable after posting (reversal entries only)
- Fiscal period lock
- Trial balance report

---

### 16. `payment` — Payment Processing

| Field | Value |
|---|---|
| Layer / Priority / Phase | 2 / 🔴 / 2 |
| มิติ | ERP |
| Prefix | `pay` |
| Dependencies | `money`, `invoice`, `ledger`, `audit`, `idempotency` |

**Domain Concepts:**
- Entity: `Payment`, `PaymentAllocation`
- VO: `PaymentMethod`, `TransactionRef`, `PaymentAmount`
- Enum: `PaymentMethod` (CASH, TRANSFER, CARD, QR, CHEQUE), `PaymentStatus` (PENDING, COMPLETED, FAILED, REFUNDED)

**Invariants:**
- `sum(allocations) == payment.amount`
- Amount > 0
- Cannot allocate to voided invoice
- Transaction ref unique

**Events:** `PaymentReceived`, `PaymentAllocated`, `PaymentRefunded`, `PaymentFailed`

**Tables:** `tenant_{prefix}.payments`, `tenant_{prefix}.payment_allocations`

**Special Rules:**
- Gateway integration (Omise/Stripe/SCB)
- Partial payment support
- Reconciliation with bank statement

---

### 17. `accounting_gateway` — Accounting Integration

| Field | Value |
|---|---|
| Layer / Priority / Phase | 2 / 🔴 / 2 |
| มิติ | ERP |
| Prefix | `acg` |
| Dependencies | `ledger`, `invoice`, `payment`, `tax` |

**Domain Concepts:**
- Entity: `AccountingSync`, `MappingRule`
- VO: `ExternalAccountCode`, `SyncBatch`
- Enum: `AccountingProvider` (XERO, QUICKBOOKS, PEAK, FLOWACCOUNT)

**Invariants:**
- Mapping 1:1 (internal account ↔ external)
- Sync idempotent (same ref = skip)
- Batch ≤ 1000 entries

**Events:** `AccountingSynced`, `MappingCreated`, `SyncFailed`, `ReconciliationNeeded`

**Tables:** `tenant_{prefix}.accounting_syncs`, `tenant_{prefix}.mapping_rules`

**Special Rules:**
- OAuth2 to external providers
- Retry with exponential backoff
- Reconciliation report

---

### 18. `tax` — Tax Engine

| Field | Value |
|---|---|
| Layer / Priority / Phase | 2 / 🔴 / 2 |
| มิติ | ERP |
| Prefix | `tax` |
| Dependencies | `money`, `product`, `customer`, `audit` |

**Domain Concepts:**
- Entity: `TaxRate`, `TaxRule`, `TaxReport`
- VO: `TaxRatePercent`, `TaxBase`, `TaxAmount`
- Enum: `TaxType` (VAT, WHT, EXCISE, IMPORT_DUTY)

**Invariants:**
- VAT rate 0-100%
- WHT rate 0-100%
- Tax base >= 0
- Rule effective date range valid

**Events:** `TaxCalculated`, `TaxReportGenerated`, `TaxRuleUpdated`, `WHTIssued`

**Tables:** `tenant_{prefix}.tax_rates`, `tenant_{prefix}.tax_rules`, `tenant_{prefix}.tax_reports`

**Special Rules:**
- Thai VAT 7% default
- WHT 1%, 3%, 5% ตามประเภท
- ภ.พ.30 / ภ.ง.ด.53 reports
- Reverse charge for imports

---

### 19. `reconciliation` — Bank Reconciliation

| Field | Value |
|---|---|
| Layer / Priority / Phase | 2 / 🔴 / 1 |
| มิติ | ERP |
| Prefix | `rec` |
| Dependencies | `ledger`, `payment`, `audit` |

**Domain Concepts:**
- Entity: `BankStatement`, `Reconciliation`, `MatchRule`
- VO: `StatementLine`, `MatchScore`
- Enum: `MatchStatus` (MATCHED, UNMATCHED, DISPUTED)

**Invariants:**
- `sum(statement_lines) == statement.closing_balance`
- Match score 0-1
- Auto-match threshold ≥ 0.95

**Events:** `StatementImported`, `MatchFound`, `DiscrepancyFound`, `ReconciliationCompleted`

**Tables:** `tenant_{prefix}.bank_statements`, `tenant_{prefix}.reconciliations`, `tenant_{prefix}.match_rules`

**Special Rules:**
- CSV/MT940/OFX import
- Fuzzy matching (amount + date + ref)
- Manual override with reason

---

## 📑 Layer 3: GOODS PATH (12 modules)

### 20. `inventory` — Inventory Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🔴 / 1 |
| มิติ | Goods |
| Prefix | `invt` |
| Dependencies | `product`, `warehouse`, `lot`, `audit`, `idempotency` |

**Domain Concepts:**
- Entity: `InventoryItem`, `StockMovement`
- VO: `Quantity`, `ReservedQty`, `AvailableQty`
- Enum: `MovementType` (IN, OUT, TRANSFER, ADJUST, RESERVE, RELEASE)

**Invariants:**
- **`available = on_hand - reserved`**
- `available >= 0` (no negative stock)
- Movement qty ≠ 0
- Ledger sum = current stock

**Events:** `StockIn`, `StockOut`, `StockReserved`, `StockReleased`, `StockAdjusted`, `LowStockAlert`

**Tables:** `tenant_{prefix}.inventory_items`, `tenant_{prefix}.stock_movements`

**Special Rules:**
- FIFO/LIFO/Weighted-average costing
- Multi-warehouse
- Reservation timeout (15 min)
- Cycle count support

---

### 21. `warehouse` — Warehouse & Locations

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🔴 / 1 |
| มิติ | Goods |
| Prefix | `wh` |
| Dependencies | `audit` |

**Domain Concepts:**
- Entity: `Warehouse`, `Bin`, `Zone`, `Location`
- VO: `BinCode`, `Capacity`, `Coordinates`
- Enum: `WarehouseType` (MAIN, BRANCH, COLD_STORAGE, TRANSIT)

**Invariants:**
- Bin code unique ต่อ warehouse
- Capacity > 0
- Zone bin count ≤ capacity

**Events:** `WarehouseCreated`, `BinAssigned`, `BinCapacityExceeded`, `WarehouseDeactivated`

**Tables:** `tenant_{prefix}.warehouses`, `tenant_{prefix}.bins`, `tenant_{prefix}.zones`

**Special Rules:**
- Hierarchical: warehouse → zone → bin
- Pick-path optimization
- Temperature zone support

---

### 22. `lot` — Lot & Serial Tracking

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🔴 / 1 |
| มิติ | Goods |
| Prefix | `lot` |
| Dependencies | `product`, `inventory`, `traceability` |

**Domain Concepts:**
- Entity: `Lot`, `SerialNumber`
- VO: `LotNumber`, `ExpiryDate`, `ManufactureDate`
- Enum: `LotStatus` (ACTIVE, QUARANTINE, EXPIRED, RECALLED)

**Invariants:**
- Lot number unique ต่อ product
- Expiry > manufacture date
- FEFO enforcement

**Events:** `LotCreated`, `LotExpired`, `LotQuarantined`, `LotRecalled`

**Tables:** `tenant_{prefix}.lots`, `tenant_{prefix}.serial_numbers`

**Special Rules:**
- FEFO picking (First Expired First Out)
- Recall propagation
- Traceability 2-way (forward/backward)

---

### 23. `production` — Manufacturing

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🔴 / 1 |
| มิติ | Production |
| Prefix | `prodn` |
| Dependencies | `inventory`, `recipe`, `lot`, `quality`, `audit`, `idempotency` |

**Domain Concepts:**
- Entity: `ProductionOrder`, `WorkOrder`, `ProductionLine`
- VO: `BatchSize`, `YieldRate`, `CycleTime`
- Enum: `ProductionStatus` (PLANNED, RELEASED, IN_PROGRESS, COMPLETED, CANCELLED)

**Invariants:**
- `input_qty >= output_qty * recipe_ratio`
- Yield rate 0-100%
- Production order linked to lot

**Events:** `ProductionStarted`, `ProductionCompleted`, `YieldRecorded`, `ScrapRecorded`

**Tables:** `tenant_{prefix}.production_orders`, `tenant_{prefix}.work_orders`, `tenant_{prefix}.production_lines`

**Special Rules:**
- MRP (Material Requirements Planning)
- Backflush vs manual issue
- Backorder handling

---

### 24. `recipe` — BOM & Recipes

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🟠 / 1 |
| มิติ | Production |
| Prefix | `rcp` |
| Dependencies | `product`, `production` |

**Domain Concepts:**
- Entity: `Recipe`, `RecipeIngredient`, `BOM`
- VO: `IngredientQty`, `YieldRatio`, `Step`
- Enum: `RecipeType` (MANUFACTURING, ASSEMBLY, FOOD, CHEMICAL)

**Invariants:**
- Ingredient qty > 0
- Recipe total cost = sum(ingredient costs)
- Version immutable after use

**Events:** `RecipeCreated`, `RecipeUpdated`, `RecipeVersioned`, `BOMExploded`

**Tables:** `tenant_{prefix}.recipes`, `tenant_{prefix}.recipe_ingredients`, `tenant_{prefix}.bom_versions`

**Special Rules:**
- Versioning (immutable)
- Scaling (batch size)
- Sub-recipes (nested BOM)
- By-product + co-product

---

### 25. `quality` — Quality Control

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🟠 / 1 |
| มิติ | Production |
| Prefix | `qlty` |
| Dependencies | `production`, `lot`, `audit` |

**Domain Concepts:**
- Entity: `QualityCheck`, `Inspection`, `NonConformance`
- VO: `TestResult`, `AcceptanceCriteria`, `SampleSize`
- Enum: `QualityStatus` (PASS, FAIL, CONDITIONAL, PENDING)

**Invariants:**
- Pass rate 0-100%
- Sample size > 0
- Failed check → quarantine

**Events:** `QualityCheckStarted`, `QualityCheckPassed`, `QualityCheckFailed`, `NCRCreated`

**Tables:** `tenant_{prefix}.quality_checks`, `tenant_{prefix}.inspections`, `tenant_{prefix}.non_conformances`

**Special Rules:**
- AQL sampling (ISO 2859)
- SPC charts (control limits)
- CAPA workflow

---

### 26. `waste` — Waste Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🟠 / 1 |
| มิติ | Production |
| Prefix | `wst` |
| Dependencies | `inventory`, `production`, `audit` |

**Domain Concepts:**
- Entity: `WasteRecord`, `WasteType`, `DisposalMethod`
- VO: `WasteQty`, `DisposalCost`, `Reason`
- Enum: `WasteCategory` (SCRAP, EXPIRED, DAMAGED, BYPRODUCT)

**Invariants:**
- Waste qty > 0
- Waste qty ≤ input qty
- Disposal cost >= 0

**Events:** `WasteRecorded`, `WasteDisposed`, `WasteReductionTargetMissed`

**Tables:** `tenant_{prefix}.waste_records`, `tenant_{prefix}.waste_types`, `tenant_{prefix}.disposal_methods`

**Special Rules:**
- Environmental compliance
- Waste-to-value (byproduct)
- Cost allocation to production

---

### 27. `procurement` — Purchasing

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🟠 / 1 |
| มิติ | Goods |
| Prefix | `proc` |
| Dependencies | `supplier`, `product`, `inventory`, `audit`, `idempotency` |

**Domain Concepts:**
- Entity: `PurchaseOrder`, `POLine`, `GoodsReceipt`
- VO: `PONumber`, `POTotal`, `LeadTime`
- Enum: `POStatus` (DRAFT, APPROVED, SENT, PARTIAL, RECEIVED, CLOSED, CANCELLED)

**Invariants:**
- `sum(lines) == po.total`
- Received qty ≤ ordered qty
- Approval required ถ้า total > threshold

**Events:** `POCreated`, `POApproved`, `POReceived`, `POPartialReceived`, `POCancelled`

**Tables:** `tenant_{prefix}.purchase_orders`, `tenant_{prefix}.po_lines`, `tenant_{prefix}.goods_receipts`

**Special Rules:**
- 3-way match (PO ↔ GR ↔ Invoice)
- Approval workflow (multi-level)
- Blanket PO support

---

### 28. `traceability` — Traceability

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🔴 / 2 |
| มิติ | Goods |
| Prefix | `trc` |
| Dependencies | `lot`, `production`, `inventory` |

**Domain Concepts:**
- Entity: `TraceEvent`, `TraceLink`
- VO: `TraceCode`, `ChainNode`, `Genealogy`
- Enum: `TraceDirection` (FORWARD, BACKWARD)

**Invariants:**
- ทุก link ต้อง valid + immutable
- Forward trace: raw → finished
- Backward trace: finished → raw

**Events:** `TraceEventRecorded`, `TraceChainBuilt`, `RecallInitiated`, `RecallCompleted`

**Tables:** `tenant_{prefix}.trace_events`, `tenant_{prefix}.trace_links`

**Special Rules:**
- GS1 EPCIS compliance
- Graph traversal (recursive CTE)
- Recall within 4 ชั่วโมง

---

### 29. `agriculture` — Farm Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🟠 / 4 |
| มิติ | 🌾 เกษตร |
| Prefix | `agr` |
| Dependencies | `crop`, `soil`, `irrigation`, `iot`, `forecast`, `inventory`, `traceability` |

**Domain Concepts:**
- Entity: `Farm`, `Plot`, `Harvest`
- VO: `PlotArea`, `YieldRate`, `Season`
- Enum: `PlotStatus` (IDLE, PLANTED, GROWING, HARVESTED, FALLOW)

**Invariants:**
- Plot area > 0
- Yield ≥ 0
- Harvest qty ≤ expected_yield × 1.5

**Events:** `FarmCreated`, `PlotPlanted`, `CropHarvested`, `YieldRecorded`, `DiseaseDetected`

**Tables:** `tenant_{prefix}.farms`, `tenant_{prefix}.plots`, `tenant_{prefix}.harvests`

**Special Rules:**
- Weather integration
- Satellite imagery (NDVI)
- Yield prediction (ML)

---

### 30. `crop` — Crop Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🟠 / 4 |
| มิติ | 🌾 เกษตร |
| Prefix | `crp` |
| Dependencies | `agriculture`, `soil`, `iot` |

**Domain Concepts:**
- Entity: `Crop`, `CropCycle`, `Variety`
- VO: `GrowthStage`, `PlantingDate`, `ExpectedYield`
- Enum: `CropType` (RICE, VEGETABLE, FRUIT, HERB), `GrowthStage` (SEED, SPROUT, VEGETATIVE, FLOWERING, FRUITING, MATURITY)

**Invariants:**
- Growth stage sequential
- Planting date ≤ today
- Cycle duration > 0

**Events:** `CropPlanted`, `GrowthStageAdvanced`, `CropReadyForHarvest`

**Tables:** `tenant_{prefix}.crops`, `tenant_{prefix}.crop_cycles`, `tenant_{prefix}.varieties`

**Special Rules:**
- Growing Degree Days (GDD) tracking
- Phenology model
- Variety recommendation

---

### 31. `soil` — Soil Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🟠 / 4 |
| มิติ | 🌾 เกษตร |
| Prefix | `sol` |
| Dependencies | `agriculture`, `crop`, `iot` |

**Domain Concepts:**
- Entity: `SoilTest`, `SoilProfile`, `FertilizerPlan`
- VO: `NPK`, `pH`, `OrganicMatter`, `CEC`
- Enum: `SoilType` (SANDY, LOAMY, CLAY, SILT)

**Invariants:**
- pH 0-14
- NPK >= 0
- Test date recent (≤ 6 months for recommendation)

**Events:** `SoilTested`, `FertilizerRecommended`, `NutrientDeficiencyDetected`

**Tables:** `tenant_{prefix}.soil_tests`, `tenant_{prefix}.soil_profiles`, `tenant_{prefix}.fertilizer_plans`

**Special Rules:**
- Lab integration
- Nutrient balance calculation
- Organic certification tracking

---

### 32. `irrigation` — Irrigation Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 3 / 🟠 / 4 |
| มิติ | 🌾 เกษตร |
| Prefix | `irr` |
| Dependencies | `agriculture`, `iot`, `crop` |

**Domain Concepts:**
- Entity: `IrrigationSchedule`, `IrrigationEvent`, `Valve`
- VO: `FlowRate`, `Duration`, `WaterVolume`
- Enum: `IrrigationType` (DRIP, SPRINKLER, FLOOD, PIVOT)

**Invariants:**
- Flow rate > 0
- Duration > 0
- Water volume ≤ daily quota

**Events:** `IrrigationStarted`, `IrrigationCompleted`, `ValveOpened`, `WaterQuotaExceeded`

**Tables:** `tenant_{prefix}.irrigation_schedules`, `tenant_{prefix}.irrigation_events`, `tenant_{prefix}.valves`

**Special Rules:**
- Soil moisture sensor integration
- ET (evapotranspiration) calculation
- Auto-scheduling based on weather

---

## 📑 Layer 4: OPERATIONS (12 modules)

### 33. `transport` — Transportation

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 4 |
| มิติ | Logistics |
| Prefix | `trn` |
| Dependencies | `order`, `delivery`, `gps`, `audit` |

**Domain Concepts:**
- Entity: `TransportOrder`, `Vehicle`, `Driver`
- VO: `Route`, `Distance`, `FuelCost`
- Enum: `TransportStatus` (PLANNED, LOADING, IN_TRANSIT, DELIVERED, CANCELLED)

**Invariants:**
- Distance > 0
- Vehicle capacity ≥ load weight
- Driver license valid

**Events:** `TransportPlanned`, `VehicleDispatched`, `GoodsLoaded`, `TransportCompleted`

**Tables:** `tenant_{prefix}.transport_orders`, `tenant_{prefix}.vehicles`, `tenant_{prefix}.drivers`

**Special Rules:**
- Load optimization
- Multi-stop routing
- Fuel cost tracking

---

### 34. `delivery` — Delivery Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 4 |
| มิติ | Logistics |
| Prefix | `dlv` |
| Dependencies | `order`, `transport`, `customer`, `gps` |

**Domain Concepts:**
- Entity: `Delivery`, `DeliveryItem`, `ProofOfDelivery`
- VO: `TrackingNumber`, `DeliveryWindow`, `Signature`
- Enum: `DeliveryStatus` (PENDING, ASSIGNED, PICKED_UP, IN_TRANSIT, DELIVERED, FAILED)

**Invariants:**
- Tracking number unique
- Delivery window valid
- POD required for completed

**Events:** `DeliveryCreated`, `DeliveryAssigned`, `OutForDelivery`, `DeliveryCompleted`, `DeliveryFailed`

**Tables:** `tenant_{prefix}.deliveries`, `tenant_{prefix}.delivery_items`, `tenant_{prefix}.proofs_of_delivery`

**Special Rules:**
- Real-time tracking
- Customer notification (SMS/LINE)
- Failed delivery → retry

---

### 35. `route` — Route Optimization

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 4 |
| มิติ | Logistics |
| Prefix | `rte` |
| Dependencies | `transport`, `delivery`, `gps` |

**Domain Concepts:**
- Entity: `Route`, `RouteStop`, `RoutePlan`
- VO: `Waypoint`, `EstimatedTime`, `Sequence`
- Enum: `RouteOptimization` (SHORTEST, FASTEST, CHEAPEST)

**Invariants:**
- Stop sequence valid (no duplicate positions)
- Total distance ≥ direct distance
- Vehicle capacity respected

**Events:** `RoutePlanned`, `RouteOptimized`, `RouteDeviated`, `RouteCompleted`

**Tables:** `tenant_{prefix}.routes`, `tenant_{prefix}.route_stops`, `tenant_{prefix}.route_plans`

**Special Rules:**
- VRP solver (OR-Tools)
- Traffic integration
- Time window constraints

---

### 36. `gps` — GPS Tracking

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 4 |
| มิติ | IoT |
| Prefix | `gps` |
| Dependencies | `transport`, `iot`, `monitoring` |

**Domain Concepts:**
- Entity: `GpsTrack`, `Geofence`, `LocationPoint`
- VO: `Coordinates`, `Speed`, `Heading`
- Enum: `GeofenceEvent` (ENTER, EXIT, DWELL)

**Invariants:**
- Latitude -90..90, Longitude -180..180
- Speed ≥ 0
- Timestamp monotonic

**Events:** `LocationUpdated`, `GeofenceEntered`, `GeofenceExited`, `SpeedViolation`

**Tables:** `tenant_{prefix}.gps_tracks` (TimescaleDB hypertable), `tenant_{prefix}.geofences`

**Special Rules:**
- TimescaleDB / InfluxDB
- Downsampling (1s → 1min → 1hr)
- Retention 90 วัน

---

### 37. `retail` — Retail Operations

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 4 |
| มิติ | Retail |
| Prefix | `rtl` |
| Dependencies | `inventory`, `pos`, `pricing`, `customer` |

**Domain Concepts:**
- Entity: `Store`, `StoreInventory`, `Planogram`
- VO: `StoreCode`, `ShelfLocation`, `ShelfCapacity`
- Enum: `StoreType` (FLAGSHIP, STANDARD, KIOSK, POPUP)

**Invariants:**
- Store code unique
- Shelf capacity > 0
- Shelf stock ≤ capacity

**Events:** `StoreOpened`, `StockReplenished`, `PlanogramChanged`, `ShelfOutOfStock`

**Tables:** `tenant_{prefix}.stores`, `tenant_{prefix}.store_inventory`, `tenant_{prefix}.planograms`

**Special Rules:**
- Store-to-store transfer
- Replenishment from DC
- Shelf-life management

---

### 38. `pos` — Point of Sale

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 4 |
| มิติ | Retail |
| Prefix | `pos` |
| Dependencies | `retail`, `product`, `payment`, `inventory`, `shift`, `audit` |

**Domain Concepts:**
- Entity: `PosTransaction`, `PosLine`, `Receipt`
- VO: `ReceiptNumber`, `CashDrawer`, `Change`
- Enum: `PosStatus` (OPEN, SUSPENDED, COMPLETED, VOIDED, REFUNDED)

**Invariants:**
- `sum(lines) == transaction.total`
- Payment ≥ total
- Shift required for transaction

**Events:** `TransactionStarted`, `TransactionCompleted`, `ReceiptPrinted`, `TransactionVoided`

**Tables:** `tenant_{prefix}.pos_transactions`, `tenant_{prefix}.pos_lines`, `tenant_{prefix}.receipts`

**Special Rules:**
- Offline mode (sync when online)
- Multiple payment methods
- Loyalty integration

---

### 39. `shift` — Cashier Shifts

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 4 |
| มิติ | Retail |
| Prefix | `shf` |
| Dependencies | `pos`, `user`, `audit` |

**Domain Concepts:**
- Entity: `Shift`, `CashDrawer`, `ShiftSummary`
- VO: `OpeningFloat`, `ClosingCount`, `Variance`
- Enum: `ShiftStatus` (OPEN, CLOSED, DISCREPANCY)

**Invariants:**
- Opening float ≥ 0
- `closing = opening + sales - refunds`
- One open shift per cashier

**Events:** `ShiftOpened`, `ShiftClosed`, `DiscrepancyFound`, `CashDropRecorded`

**Tables:** `tenant_{prefix}.shifts`, `tenant_{prefix}.cash_drawers`, `tenant_{prefix}.shift_summaries`

**Special Rules:**
- Blind close option
- Cash drop tracking
- End-of-day report

---

### 40. `line_channel` — LINE Channel Integration

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 4 |
| มิติ | CRM |
| Prefix | `lnc` |
| Dependencies | `customer`, `crm`, `campaign` |

**Domain Concepts:**
- Entity: `LineChannel`, `LineUser`, `MessageTemplate`
- VO: `ChannelId`, `UserId`, `RichMenuId`
- Enum: `MessageType` (TEXT, IMAGE, FLEX, TEMPLATE, STICKER)

**Invariants:**
- Channel ID unique
- Line user 1:1 กับ customer (ถ้า link)
- Message ≤ 5000 chars

**Events:** `UserFollowed`, `UserUnfollowed`, `MessageReceived`, `MessageSent`

**Tables:** `tenant_{prefix}.line_channels`, `tenant_{prefix}.line_users`, `tenant_{prefix}.message_templates`

**Special Rules:**
- LINE Messaging API
- Webhook handling
- Rich menu management
- Broadcast rate limit

---

### 41. `promotion` — Promotion Engine

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟡 / 4 |
| มิติ | CRM |
| Prefix | `prm` |
| Dependencies | `pricing`, `product`, `customer`, `audit` |

**Domain Concepts:**
- Entity: `Promotion`, `PromotionRule`, `PromotionUsage`
- VO: `DiscountValue`, `Condition`, `UsageLimit`
- Enum: `PromotionType` (PERCENT, FIXED, BOGO, BUNDLE, FREE_SHIPPING)

**Invariants:**
- Discount ≤ product price
- Start date < end date
- Usage limit ≥ 0
- No conflicting promotions (same product + period)

**Events:** `PromotionCreated`, `PromotionApplied`, `PromotionExpired`, `UsageLimitReached`

**Tables:** `tenant_{prefix}.promotions`, `tenant_{prefix}.promotion_rules`, `tenant_{prefix}.promotion_usages`

**Special Rules:**
- Stackable vs exclusive
- Customer segment targeting
- Anti-abuse (max 1 per customer)

---

### 42. `loyalty` — Loyalty Program

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟡 / 4 |
| มิติ | CRM |
| Prefix | `loy` |
| Dependencies | `customer`, `pos`, `promotion` |

**Domain Concepts:**
- Entity: `LoyaltyAccount`, `PointsTransaction`, `Reward`, `Tier`
- VO: `Points`, `TierLevel`, `ExpiryDate`
- Enum: `PointsType` (EARN, REDEEM, EXPIRE, ADJUST)

**Invariants:**
- Points balance ≥ 0
- Redeem ≤ balance
- Tier upgrade based on cumulative points

**Events:** `AccountCreated`, `PointsEarned`, `PointsRedeemed`, `TierUpgraded`, `PointsExpired`

**Tables:** `tenant_{prefix}.loyalty_accounts`, `tenant_{prefix}.points_transactions`, `tenant_{prefix}.rewards`, `tenant_{prefix}.tiers`

**Special Rules:**
- Points expiry (12 เดือน)
- Tier benefits (discount, free shipping)
- Birthday bonus

---

### 43. `crm` — CRM

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟠 / 5 |
| มิติ | 📞 CRM |
| Prefix | `crm` |
| Dependencies | `customer`, `line_channel`, `campaign`, `invoice` |

**Domain Concepts:**
- Entity: `Lead`, `Deal`, `Activity`
- VO: `PipelineStage`, `DealValue`, `Probability`
- Enum: `LeadStatus` (NEW, CONTACTED, QUALIFIED, CONVERTED, LOST), `DealStage` (PROSPECTING, QUALIFICATION, PROPOSAL, NEGOTIATION, WON, LOST)

**Invariants:**
- Deal value ≥ 0
- Probability 0-100
- Deal stage forward-only
- Lead → Customer 1:1

**Events:** `LeadCreated`, `LeadConverted`, `DealCreated`, `DealWon`, `DealLost`

**Tables:** `tenant_{prefix}.leads`, `tenant_{prefix}.deals`, `tenant_{prefix}.activities`

**Special Rules:**
- Sales pipeline view
- Activity logging (call, email, meeting)
- Forecast by stage

---

### 44. `campaign` — Marketing Campaign

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟡 / 5 |
| มิติ | CRM |
| Prefix | `cmp` |
| Dependencies | `crm`, `line_channel`, `customer`, `promotion` |

**Domain Concepts:**
- Entity: `Campaign`, `CampaignSegment`, `CampaignMessage`
- VO: `Audience`, `Schedule`, `Budget`
- Enum: `CampaignStatus` (DRAFT, SCHEDULED, RUNNING, PAUSED, COMPLETED)

**Invariants:**
- Budget ≥ 0
- Start date < end date
- Audience size ≤ segment size

**Events:** `CampaignCreated`, `CampaignStarted`, `CampaignCompleted`, `CampaignPaused`

**Tables:** `tenant_{prefix}.campaigns`, `tenant_{prefix}.campaign_segments`, `tenant_{prefix}.campaign_messages`

**Special Rules:**
- A/B testing
- Multi-channel (LINE, SMS, Email)
- Conversion tracking
- ROI report

---

### 45. `support` — Customer Support

| Field | Value |
|---|---|
| Layer / Priority / Phase | 4 / 🟡 / 5 |
| มิติ | CRM |
| Prefix | `spt` |
| Dependencies | `customer`, `line_channel`, `user`, `audit` |

**Domain Concepts:**
- Entity: `Ticket`, `TicketMessage`, `Sla`
- VO: `TicketNumber`, `Priority`, `ResponseTime`
- Enum: `TicketStatus` (OPEN, IN_PROGRESS, WAITING, RESOLVED, CLOSED), `Priority` (LOW, MEDIUM, HIGH, URGENT)

**Invariants:**
- Ticket number unique
- SLA response time > 0
- Closed ticket immutable

**Events:** `TicketCreated`, `TicketAssigned`, `TicketResolved`, `SlaBreached`

**Tables:** `tenant_{prefix}.tickets`, `tenant_{prefix}.ticket_messages`, `tenant_{prefix}.slas`

**Special Rules:**
- Auto-assignment (round-robin)
- SLA escalation
- CSAT survey after resolve

---

## 📑 Layer 5: INTELLIGENCE (6 modules)

### 46. `reporting` — Reporting

| Field | Value |
|---|---|
| Layer / Priority / Phase | 5 / 🔴 / 5 |
| มิติ | BI |
| Prefix | `rpt` |
| Dependencies | `ledger`, `order`, `inventory`, `analytics` |

**Domain Concepts:**
- Entity: `Report`, `ReportTemplate`, `ReportExecution`
- VO: `ReportFormat`, `Parameters`, `Schedule`
- Enum: `ReportType` (FINANCIAL, SALES, INVENTORY, OPERATIONAL)

**Invariants:**
- Report template versioned
- Execution result immutable
- Schedule valid cron

**Events:** `ReportGenerated`, `ReportScheduled`, `ReportFailed`, `ReportShared`

**Tables:** `tenant_{prefix}.reports`, `tenant_{prefix}.report_templates`, `tenant_{prefix}.report_executions`

**Special Rules:**
- PDF/Excel/CSV export
- Scheduled delivery (email)
- Row-level security in reports

---

### 47. `analytics` — Business Analytics

| Field | Value |
|---|---|
| Layer / Priority / Phase | 5 / 🟠 / 5 |
| มิติ | BI |
| Prefix | `ana` |
| Dependencies | `reporting`, `order`, `customer`, `product` |

**Domain Concepts:**
- Entity: `Metric`, `Dimension`, `DataMart`
- VO: `Aggregation`, `TimeGrain`, `Filter`
- Enum: `MetricType` (COUNT, SUM, AVG, RATIO, PERCENTILE)

**Invariants:**
- Metric definition unique
- Aggregation consistent
- Data freshness ≤ 1 hour

**Events:** `DataMartBuilt`, `MetricCalculated`, `AnomalyDetected`

**Tables:** `tenant_{prefix}.metrics`, `tenant_{prefix}.dimensions`, `tenant_{prefix}.data_marts`

**Special Rules:**
- OLAP cube
- Drill-down support
- Materialized views

---

### 48. `forecast` — Forecasting

| Field | Value |
|---|---|
| Layer / Priority / Phase | 5 / 🟠 / 5 |
| มิติ | BI |
| Prefix | `fcs` |
| Dependencies | `analytics`, `production`, `inventory`, `agriculture` |

**Domain Concepts:**
- Entity: `Forecast`, `ForecastModel`
- VO: `Prediction`, `Confidence`, `MAPE`
- Enum: `ForecastMethod` (LSTM, PROPHET, XGBOOST, ARIMA, ENSEMBLE)

**Invariants:**
- MAPE < 20% (target)
- Prediction ≥ 0
- Confidence 0-1

**Events:** `ForecastGenerated`, `ForecastUpdated`, `ForecastAccuracyDropped`

**Tables:** `tenant_{prefix}.forecasts`, `tenant_{prefix}.forecast_models`

**Special Rules:**
- Model retraining weekly
- Backtesting before deploy
- Ensemble voting

---

### 49. `kpi` — KPI Tracking

| Field | Value |
|---|---|
| Layer / Priority / Phase | 5 / 🟠 / 5 |
| มิติ | BI |
| Prefix | `kpi` |
| Dependencies | `analytics`, `reporting`, `user` |

**Domain Concepts:**
- Entity: `Kpi`, `KpiTarget`, `KpiActual`
- VO: `TargetValue`, `ActualValue`, `AchievementRate`
- Enum: `KpiFrequency` (DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY)

**Invariants:**
- Target > 0
- Achievement rate = actual / target × 100
- Actual ≥ 0

**Events:** `KpiCreated`, `KpiTargetSet`, `KpiAchieved`, `KpiMissed`

**Tables:** `tenant_{prefix}.kpis`, `tenant_{prefix}.kpi_targets`, `tenant_{prefix}.kpi_actuals`

**Special Rules:**
- Cascading KPI (company → dept → individual)
- Balanced scorecard
- Alert on threshold breach

---

### 50. `satisfaction` — Customer Satisfaction

| Field | Value |
|---|---|
| Layer / Priority / Phase | 5 / 🟡 / 5 |
| มิติ | CRM |
| Prefix | `sat` |
| Dependencies | `customer`, `support`, `order` |

**Domain Concepts:**
- Entity: `Survey`, `Response`, `NpsScore`
- VO: `Rating`, `NpsScore`, `CsatScore`
- Enum: `SurveyType` (NPS, CSAT, CES), `Sentiment` (POSITIVE, NEUTRAL, NEGATIVE)

**Invariants:**
- Rating 1-5
- NPS -100..100
- Response rate 0-100%

**Events:** `SurveySent`, `ResponseReceived`, `NpsCalculated`, `DetractorDetected`

**Tables:** `tenant_{prefix}.surveys`, `tenant_{prefix}.responses`, `tenant_{prefix}.nps_scores`

**Special Rules:**
- Auto-trigger after delivery
- Detractor follow-up workflow
- Trend analysis

---

### 51. `recommendation` — Recommendation Engine

| Field | Value |
|---|---|
| Layer / Priority / Phase | 5 / 🟡 / 5 |
| มิติ | CRM |
| Prefix | `rcm` |
| Dependencies | `customer`, `order`, `product`, `analytics` |

**Domain Concepts:**
- Entity: `Recommendation`, `UserProfile`, `ItemSimilarity`
- VO: `Score`, `Rank`, `Context`
- Enum: `RecAlgorithm` (COLLABORATIVE, CONTENT_BASED, HYBRID)

**Invariants:**
- Score 0-1
- Top-N ≤ 100
- No out-of-stock recommendations

**Events:** `RecommendationGenerated`, `RecommendationClicked`, `RecommendationPurchased`

**Tables:** `tenant_{prefix}.recommendations`, `tenant_{prefix}.user_profiles`, `tenant_{prefix}.item_similarities`

**Special Rules:**
- Cold-start handling
- Real-time vs batch
- A/B testing framework

---

### 52. `oee` — Overall Equipment Effectiveness

| Field | Value |
|---|---|
| Layer / Priority / Phase | 5 / 🟠 / 5 |
| มิติ | Factory |
| Prefix | `oee` |
| Dependencies | `production`, `iot`, `maintenance`, `quality` |

**Domain Concepts:**
- Entity: `OeeRecord`, `Equipment`, `DowntimeEvent`
- VO: `Availability`, `Performance`, `Quality`, `OeeScore`
- Enum: `DowntimeReason` (BREAKDOWN, SETUP, MATERIAL, SCHEDULED)

**Invariants:**
- Availability 0-100%
- Performance 0-100%
- Quality 0-100%
- **OEE = A × P × Q**

**Events:** `OeeCalculated`, `DowntimeRecorded`, `OeeBelowTarget`, `EquipmentFailure`

**Tables:** `tenant_{prefix}.oee_records`, `tenant_{prefix}.equipment`, `tenant_{prefix}.downtime_events`

**Special Rules:**
- Real-time from IoT sensors
- World-class OEE ≥ 85%
- Six Big Losses analysis

---

## 📑 Layer 6: MONITORING (7 modules)

### 53. `iot` — IoT Platform

| Field | Value |
|---|---|
| Layer / Priority / Phase | 6 / 🟠 / 4 |
| มิติ | IoT |
| Prefix | `iot` |
| Dependencies | `monitoring`, `alerting`, `events` |

**Domain Concepts:**
- Entity: `SensorReading`, `Sensor`, `Threshold`
- VO: `Measurement`, `Unit`, `Timestamp`
- Enum: `SensorType` (TEMPERATURE, HUMIDITY, CO2, LIGHT, PH, EC)

**Invariants:**
- Reading in valid range ต่อ sensor type
- Threshold min < max
- Timestamp monotonic

**Events:** `SensorReadingReceived`, `ThresholdExceeded`, `SensorOffline`

**Tables:** `tenant_{prefix}.sensor_readings` (TimescaleDB), `tenant_{prefix}.sensors`, `tenant_{prefix}.thresholds`

**Special Rules:**
- MQTT ingestion
- TimescaleDB hypertable
- Downsampling + retention
- Edge computing support

---

### 54. `cctv` — CCTV Integration

| Field | Value |
|---|---|
| Layer / Priority / Phase | 6 / 🟡 / 4 |
| มิติ | IoT |
| Prefix | `cctv` |
| Dependencies | `monitoring`, `alerting`, `iot` |

**Domain Concepts:**
- Entity: `Camera`, `Recording`, `MotionEvent`
- VO: `StreamUrl`, `StoragePath`, `MotionScore`
- Enum: `CameraStatus` (ONLINE, OFFLINE, RECORDING, ERROR)

**Invariants:**
- Retention ≥ 30 วัน
- Recording size ≤ quota
- Stream URL valid RTSP/RTMP

**Events:** `MotionDetected`, `CameraOffline`, `RecordingStarted`, `RecordingArchived`

**Tables:** `tenant_{prefix}.cameras`, `tenant_{prefix}.recordings`, `tenant_{prefix}.motion_events`

**Special Rules:**
- RTSP → HLS transcoding
- Object detection (YOLO)
- Time-lapse generation
- S3 cold storage

---

### 55. `monitoring` — System Monitoring

| Field | Value |
|---|---|
| Layer / Priority / Phase | 6 / 🔴 / 1 |
| มิติ | Ops |
| Prefix | `mon` |
| Dependencies | `alerting`, `events` |

**Domain Concepts:**
- Entity: `HealthCheck`, `Metric`, `Incident`
- VO: `MetricValue`, `Threshold`, `Duration`
- Enum: `HealthStatus` (HEALTHY, DEGRADED, UNHEALTHY)

**Invariants:**
- Health check interval > 0
- Response time ≥ 0
- Incident duration ≥ 0

**Events:** `HealthCheckFailed`, `IncidentOpened`, `IncidentResolved`, `DegradedPerformance`

**Tables:** `tenant_{prefix}.health_checks`, `tenant_{prefix}.metrics`, `tenant_{prefix}.incidents`

**Special Rules:**
- Prometheus/Grafana integration
- 4 golden signals (latency, traffic, errors, saturation)
- SLO/SLI tracking

---

### 56. `backup` — Backup Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 6 / 🔴 / 1 |
| มิติ | Ops |
| Prefix | `bkp` |
| Dependencies | `monitoring`, `audit` |

**Domain Concepts:**
- Entity: `BackupJob`, `BackupSnapshot`, `RestoreRequest`
- VO: `BackupSize`, `Checksum`, `Retention`
- Enum: `BackupType` (FULL, INCREMENTAL, DIFFERENTIAL), `BackupStatus` (PENDING, RUNNING, SUCCESS, FAILED)

**Invariants:**
- Retention ≥ 30 วัน
- Checksum verified
- Test restore monthly

**Events:** `BackupStarted`, `BackupCompleted`, `BackupFailed`, `RestoreCompleted`

**Tables:** `tenant_{prefix}.backup_jobs`, `tenant_{prefix}.backup_snapshots`, `tenant_{prefix}.restore_requests`

**Special Rules:**
- S3/GCS storage
- Encryption at rest (KMS)
- Point-in-time recovery (PITR)
- Cross-region replication

---

### 57. `alerting` — Alerting

| Field | Value |
|---|---|
| Layer / Priority / Phase | 6 / 🟠 / 1 |
| มิติ | Ops |
| Prefix | `alr` |
| Dependencies | `monitoring`, `notification`, `events` |

**Domain Concepts:**
- Entity: `Alert`, `AlertRule`, `NotificationChannel`
- VO: `Severity`, `EscalationPolicy`, `Silence`
- Enum: `Severity` (INFO, WARNING, ERROR, CRITICAL), `AlertStatus` (FIRING, RESOLVED, SILENCED)

**Invariants:**
- Severity valid
- Escalation timeout > 0
- Silence duration valid

**Events:** `AlertFired`, `AlertResolved`, `AlertSilenced`, `EscalationTriggered`

**Tables:** `tenant_{prefix}.alerts`, `tenant_{prefix}.alert_rules`, `tenant_{prefix}.notification_channels`

**Special Rules:**
- Deduplication (5-min window)
- Escalation policy
- Multi-channel (Slack, Email, SMS, LINE)
- On-call rotation

---

### 58. `audit_viewer` — Audit Viewer

| Field | Value |
|---|---|
| Layer / Priority / Phase | 6 / 🟠 / 2 |
| มิติ | Compliance |
| Prefix | `auv` |
| Dependencies | `audit`, `user`, `tenant_context` |

**Domain Concepts:**
- Entity: `AuditView`, `SavedFilter`
- VO: `FilterCriteria`, `TimeRange`
- Enum: `AuditCategory` (SECURITY, FINANCIAL, DATA, SYSTEM)

**Invariants:**
- Read-only (no write operations)
- Filter criteria valid
- Export audit logged

**Events:** `AuditQueried`, `AuditExported`, `SuspiciousActivityDetected`

**Tables:** `tenant_{prefix}.audit_views`, `tenant_{prefix}.saved_filters`

**Special Rules:**
- Full-text search (Elasticsearch)
- Compliance reports (SOC2, ISO 27001)
- Immutable view (WORM storage)

---

### 59. `maintenance` — Maintenance Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 6 / 🟠 / 5 |
| มิติ | Factory |
| Prefix | `mnt` |
| Dependencies | `production`, `iot`, `oee`, `audit` |

**Domain Concepts:**
- Entity: `MaintenanceOrder`, `Asset`, `MaintenanceSchedule`
- VO: `MttrMttf`, `Downtime`, `Cost`
- Enum: `MaintenanceType` (PREVENTIVE, CORRECTIVE, PREDICTIVE, EMERGENCY)

**Invariants:**
- Asset unique
- MTTR ≥ 0, MTTF > 0
- Schedule interval > 0

**Events:** `MaintenanceScheduled`, `MaintenanceStarted`, `MaintenanceCompleted`, `AssetFailurePredicted`

**Tables:** `tenant_{prefix}.maintenance_orders`, `tenant_{prefix}.assets`, `tenant_{prefix}.maintenance_schedules`

**Special Rules:**
- CMMS integration
- Predictive (ML from IoT)
- Spare parts inventory
- MTTR/MTBF tracking

---

### 60. `energy` — Energy Management

| Field | Value |
|---|---|
| Layer / Priority / Phase | 6 / 🟡 / 5 |
| มิติ | Factory |
| Prefix | `eng` |
| Dependencies | `iot`, `production`, `oee`, `analytics` |

**Domain Concepts:**
- Entity: `EnergyReading`, `Meter`, `EnergyTarget`
- VO: `Kwh`, `PeakDemand`, `CarbonFootprint`
- Enum: `EnergySource` (GRID, SOLAR, GENERATOR, BATTERY)

**Invariants:**
- Energy ≥ 0
- Reading interval consistent
- Peak demand ≥ avg demand

**Events:** `EnergyMeasured`, `PeakDemandExceeded`, `EnergyTargetMissed`, `SolarGenerationStarted`

**Tables:** `tenant_{prefix}.energy_readings`, `tenant_{prefix}.meters`, `tenant_{prefix}.energy_targets`

**Special Rules:**
- Real-time monitoring
- Load balancing
- Carbon accounting (Scope 1/2/3)
- ISO 50001 compliance

---

## 📑 Layer 7: TEMPLATES (3 modules)

### 61. `health` — Health Check

| Field | Value |
|---|---|
| Layer / Priority / Phase | 7 / 🔴 / 1 |
| มิติ | Ops |
| Prefix | `hlt` |
| Dependencies | ไม่มี |

**Domain Concepts:**
- Entity: `HealthStatus`
- VO: `ComponentHealth`, `Version`
- Enum: `ComponentStatus` (UP, DOWN, DEGRADED)

**Invariants:**
- Response time < 1s
- Read-only endpoint

**Events:** `HealthChecked`, `ComponentDown`, `ComponentRecovered`

**Tables:** ไม่มี (stateless)

**Special Rules:**
- `/health`, `/ready`, `/live` endpoints
- Kubernetes probe compatible
- Check: DB, Redis, Kafka, external APIs

---

### 62. `example` — Reference Example

| Field | Value |
|---|---|
| Layer / Priority / Phase | 7 / 🟢 / 1 |
| มิติ | Reference |
| Prefix | `ex` |
| Dependencies | ทุกอย่าง (ใช้เป็นตัวอย่าง) |

**Domain Concepts:**
- Entity: `Example`
- VO: `ExampleValue`
- Enum: `ExampleStatus` (NEW, USED, ARCHIVED)

**Invariants:**
- ใช้แสดง pattern ครบทั้ง 4 layers

**Events:** `ExampleCreated`

**Tables:** `tenant_{prefix}.examples`

**Special Rules:**
- ใช้เป็น reference implementation
- มี comment 2 ภาษา
- Coverage 100%

---

### 63. `blank` — Blank Template

| Field | Value |
|---|---|
| Layer / Priority / Phase | 7 / 🟢 / 1 |
| มิติ | Template |
| Prefix | `blk` |
| Dependencies | ไม่มี |

**Domain Concepts:**
- Entity: `{Entity}` (placeholder)
- VO: `{VO}` (placeholder)
- Enum: `{Enum}` (placeholder)

**Invariants:**
- `{module_specific_invariants}`

**Events:** `{Module}Created`, `{Module}Updated`, `{Module}Deleted`

**Tables:** `tenant_{prefix}.{table_name}`

**Special Rules:**
- พร้อมให้ replace `{placeholders}` ทั้งหมด
- ทุกที่ที่มี `{module_name}` → replace
- ทุกที่ที่มี `{Entity}` → replace

---

## 📊 สรุปตารางรวมทั้งหมด 63 Modules

| Layer | Modules | Prefix |
|---|---|---|
| **0** | tenant_context, audit, idempotency, config, events | tctx, aud, idem, cfg, evt |
| **1** | tenancy, authentication, user, employee, customer, supplier, product, pricing | ten, auth, usr, emp, cust, sup, prod, prc |
| **2** | order, ledger, payment, accounting_gateway, tax, reconciliation | ord, led, pay, acg, tax, rec |
| **3** | inventory, warehouse, lot, production, recipe, quality, waste, procurement, traceability, agriculture, crop, soil, irrigation | invt, wh, lot, prodn, rcp, qlty, wst, proc, trc, agr, crp, sol, irr |
| **4** | transport, delivery, route, gps, retail, pos, shift, line_channel, promotion, loyalty, crm, campaign, support | trn, dlv, rte, gps, rtl, pos, shf, lnc, prm, loy, crm, cmp, spt |
| **5** | reporting, analytics, forecast, kpi, satisfaction, recommendation, oee | rpt, ana, fcs, kpi, sat, rcm, oee |
| **6** | iot, cctv, monitoring, backup, alerting, audit_viewer, maintenance, energy | iot, cctv, mon, bkp, alr, auv, mnt, eng |
| **7** | health, example, blank | hlt, ex, blk |

**รวม:** 63 modules × 23 ไฟล์ = **1,449 ไฟล์**

---

## 🚀 วิธีใช้

### 1. สร้าง prompt file ต่อ module

```bash
# ตัวอย่างสำหรับ module `ledger`
cat > docs/prompts/layer-2-money-path/ledger.md << 'EOF'
# AI Prompt — Module `ledger`

> **Master Template:** ดู `docs/template_modules.md` v3.0
> **ใช้ boilerplate 16 Python + 3 SQL + 4 Tests จาก master**

## 📋 Metadata
| Field | Value |
|---|---|
| Layer | 2 |
| Priority | 🔴 |
| Phase | 1 |
| Prefix | `led` |
| Dependencies | money, audit, idempotency |

## 🎯 Prompt

### สร้าง Module `ledger`

**Domain Concepts:**
- Entity: JournalEntry, LedgerEntry, Account
- VO: AccountCode, DebitCredit, PostingDate
- Enum: AccountType (ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE)

**Invariants:**
- `sum(debit) == sum(credit)` ← **CRITICAL**
- Journal entry posted = immutable
- Posting date <= today

**Events:** JournalEntryPosted, LedgerEntryCreated, AccountCreated, PeriodClosed

**Tables:** tenant_led.accounts, tenant_led.journal_entries, tenant_led.ledger_entries

**Special Rules:**
- Immutable after posting
- Fiscal period lock
- Trial balance report

**Output:** 23 ไฟล์ (ตาม Master Template v3.0)
EOF
```

### 2. Generate ครั้งเดียวทีละ layer

```bash
# Layer 0 ทั้งหมด
for m in tenant_context audit idempotency config events; do
  # copy prompt ไปวางใน AI
done

# Layer 3 (12 modules)
for m in inventory warehouse lot production recipe quality waste procurement traceability agriculture crop soil irrigation; do
  # ...
done
```

### 3. ตรวจสอบ

```bash
# ตรวจว่า prompt ครบ 63 ไฟล์
find docs/prompts -name "*.md" | wc -l
# Expected: 65 (README + 63 modules + blank template)

# รัน test ทุก module
uv run pytest tests/ -v --cov=app/modules --cov-report=html
```

---

## 📌 สรุปสุดท้าย

| รายการ | จำนวน |
|---|---|
| **Modules ทั้งหมด** | 63 |
| **Prompts ที่มีอยู่** | 6 (money, invoice, agriculture, crm, forecast, iot) |
| **Prompts ที่ generate เพิ่มในเอกสารนี้** | 57 |
| **ไฟล์ต่อ module** | 23 (16 Python + 3 SQL + 4 Tests) |
| **ไฟล์รวมทั้งหมด** | 1,449 ไฟล์ |

---

> **ผู้แต่ง:** Kongnakorn Jantakun  
> **Email:** kongnakornjantakun@gmail.com  
> **อัปเดต:** 2026-09-17  
> **เวอร์ชัน:** 3.0.0  
> **สถานะ:** ✅ พร้อมใช้งาน — ครอบคลุม 63 modules + 57 templates ใหม่

---

ต้องการให้ผม **generate prompt แบบเต็ม** (23 ไฟล์ output) สำหรับ module ใดเป็นพิเศษไหมครับ? เช่น:

- 🔴 `ledger` (Double-entry accounting — ซับซ้อนสุด)
- 🟠 `production` (Manufacturing — มี MRP + BOM)
- 🟠 `gps` (TimescaleDB + Geofence)
- 🟡 `promotion` (Rule engine)

 **เขียน Python script** ที่ auto-generate prompt files ทั้ง 57 ไฟล์จาก metadata ในตารางด้านบน 
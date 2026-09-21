# opencode_promt_python_ddd.md (v2.0 — เพิ่ม Testing + Debug)

> **Consolidated Master Prompt for Python DDD / Clean Architecture**
> รวมข้อมูลจาก `create_module.ps1`, `create_modules.bat`, `opencode_promt.md`, `readme_promt.md`, `RUN_GUIDE_opencode_promt.md`
> **Stack:** Python 3.14+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · PostgreSQL 17 · Redis 8 · Kafka
> **ขอบเขต:** ERP + CRM + IoT (Multi-company, 65 modules / 8 layers)
> **อัปเดต v2.0:** เพิ่ม **Testing Block (§9)** + **Debug Block (§10)**

---

# 📋 สารบัญ

| # | ส่วน | คำอธิบาย |
|---|---|---|
| **0** | Global Constraints | กฎบังคับทุก prompt |
| **1** | Master Structure | 23 ส่วนบังคับ |
| **2** | Task Templates A–G | 7 ประเภทงาน |
| **3** | SQL & Migration Block | V001 / V002 / V003 + RLS |
| **4** | Routing Block | Router + Model registration |
| **5** | Docs / Swagger / Postman | เอกสาร 4 ระบบ |
| **6** | Report Templates | Report A–D |
| **7** | Checklists | DoD + TDD + SQL + Docs |
| **8** | Scripts (Bat/PS1) | Template Generator |
| **9** | 🆕 Testing Block | Test Pyramid + Unit Test เต็มรูปแบบ |
| **10** | 🆕 Debug Block | Debug workflow + Tools + Recipes |
| **11** | Quick Command Cheatsheet | คำสั่งด่วน |
| **12** | Universal Header | Header กลางสำหรับทุก prompt |

---

# 0. Global Constraints

```markdown
[GLOBAL CONSTRAINTS]
- ห้ามทักทาย / ห้ามสรุป / ห้ามอธิบายซ้ำ
- ตอบเฉพาะไฟล์ใน "Output Scope"
- โค้ดเต็ม Production-ready ห้าม `...` หรือ `# code here`
- ห้ามแตะไฟล์นอก Scope (ถ้าจำเป็น → ประกาศ SIDE-EFFECT WARNING)
- คอมเมนต์ 2 ภาษา (ไทย + English) สั้น กระชับ
- Error handling:
  • Use Case   → 3-branch (StandardException → DomainError → Exception)
  • Repository → 2-branch (StandardException → Exception)
  • Cache      → never-raise (log + return None/False)
- Type hints ครบ / Pydantic v2 / SQLAlchemy 2.0 async
- ใช้ `Decimal` เท่านั้น (ห้าม float กับเงิน/สต็อก)
- ใช้ `flush()` ห้าม `commit()` ใน Repository
- SQL: V001 create + V002 seed + V003 rollback + RLS + Trigger
- Routing: register ที่ `app/routes.py` + `migrations/env.py`
- Docs: README + OpenAPI + Postman + AsyncAPI (ถ้ามี WS)
- Tests: unit ≥ 8 / integration / property / manual — coverage ≥ 85%
- Debug: ห้าม print() — ใช้ structlog เท่านั้น / ห้าม log PII
- Path: `app/modules/{module}/{layer}/{file}.py`
- ข้อมูลไม่พอ → ถาม 1 คำถาม ห้ามเดา
```

---

# 1. Master Structure — 23 ส่วนบังคับ

```markdown
## 01. รายละเอียด (Details)
## 02. หลักการทำงาน (Concept / Behavior Spec)
## 03. ข้อกำหนด (Requirements)
## 04. เป้าหมาย (Target)
## 05. ขอบเขต (Scope)
## 06. โครงสร้าง Folder + ไฟล์
## 07. Workflow การทำงาน
## 08. Affected Areas
## 09. รายการกระบวนการทำงาน
## 10. Performance Considerations
## 11. TDD Plan
## 12. ข้อห้าม (Prohibitions)
## 13. ข้อควรระวัง (Cautions)
## 14. ข้อดี (Pros)
## 15. ข้อเสีย (Cons)
## 16. Checklist การทดสอบ
## 17. SQL & Migration Plan
## 18. Routing Registration
## 19. Documentation Package
## 20. Swagger / OpenAPI Spec
## 21. Postman Collection
## 22. สรุป (Summary)
## 23. รายงานสรุปผลการดำเนินการ
```

---

# 2. Task Templates A–G

## 🎯 TEMPLATE A: สร้างใหม่ (CREATE_NEW)

### 01. รายละเอียด

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `CREATE_NEW` |
| **Module** | `[module]` |
| **Layer** | `[0-Core / 1-Foundation / 2-Money / 3-Goods / 4-Ops / 5-Intel / 6-Monitor / 7-Template]` |
| **Stack** | `[FastAPI / Django / Both]` |
| **Priority** | `🔴 / 🟠 / 🟡` |
| **Phase** | `[1-6]` |
| **Prefix** | `[3 chars]` |
| **Dependencies** | `[module list]` |
| **Tables** | `tenant_{tid}.[table]` |
| **Endpoints** | `/api/v1/[module]/` |
| **Events** | `[ModuleCreated, ModuleUpdated, ...]` |

### 06. โครงสร้าง Folder + ไฟล์ (40 ไฟล์)

```
app/modules/{module}/
├── domain/                (6 ไฟล์)
│   ├── __init__.py
│   ├── entities.py
│   ├── value_objects.py
│   ├── enums.py
│   ├── events.py
│   └── exceptions.py
├── application/           (6 ไฟล์)
│   ├── __init__.py
│   ├── interfaces.py
│   ├── use_cases.py
│   ├── mappers.py
│   ├── exceptions.py
│   └── utils.py
├── infrastructure/        (5 ไฟล์)
│   ├── __init__.py
│   ├── models.py
│   ├── repositories.py
│   ├── caches.py
│   └── services.py
├── presentation/          (5 ไฟล์)
│   ├── __init__.py
│   ├── routers.py
│   ├── schemas.py
│   ├── docs.py
│   └── dependencies.py
└── __init__.py            (1 ไฟล์)

db/migrations/             (3 ไฟล์)
├── V001__create_{module}.sql
├── V002__seed_{module}.sql
└── V003__rollback_{module}.sql

tests/                     (5 ไฟล์)  ← อัปเดต: เพิ่ม conftest
├── conftest.py
├── unit/test_{module}.py
├── integration/test_{module}_repository.py
├── property/test_{module}_invariants.py
└── manual/manual_test_{module}.md

docs/                      (2 ไฟล์)
├── README_{module}.md
└── API_{module}.md

app/routes.py              (แก้)
migrations/env.py          (แก้)
```

### 07. Workflow

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Router
    participant UC as UseCase
    participant ID as Idempotency
    participant RP as Repository
    participant DB as PostgreSQL
    participant CX as Redis
    participant EV as EventBus

    C->>R: POST + Idempotency-Key
    R->>R: Pydantic v2 validate
    R->>UC: create(payload, idem_key)
    UC->>UC: get_context() → tenant_id
    UC->>ID: check_or_lock(key, scope, payload)
    ID-->>UC: None | replay | 409 | 422
    UC->>RP: save(entity)
    RP->>DB: INSERT (flush, no commit)
    RP-->>UC: entity
    UC->>RP: get_by_id (read-back verify)
    RP->>DB: SELECT
    DB-->>RP: verified ✅
    UC->>CX: invalidate cache
    UC->>ID: complete(key, status, body)
    UC->>EV: publish(ModuleCreated)
    UC-->>R: entity
    R-->>C: 201 Created
```

### 12. ข้อห้าม

```markdown
❌ ห้าม import framework ใน domain/
❌ ห้าม commit() ใน Repository (ใช้ flush())
❌ ห้าม raise ใน Cache (never-raise)
❌ ห้าม float กับเงิน/สต็อก
❌ ห้าม hardcode secret
❌ ห้าม UPDATE/DELETE ใน audit/event store
❌ ห้าม query ข้าม tenant
❌ ห้ามลบ migration V001-V003 ที่ commit แล้ว
❌ ห้าม CREATE TABLE IF NOT EXISTS ใน migration หลัก
❌ ห้ามใช้ print() — ใช้ structlog เท่านั้น
❌ ห้าม mock สิ่งที่ตัวเองเป็นเจ้าของ (mock เฉพาะ port)
```

### 17. SQL & Migration Plan

> ใช้ `create_modules.bat sql {module} {prefix}` หรือดูกฎใน [ส่วนที่ 3](#3-sql--migration-block)

### 18. Routing Registration

> ใช้ `create_modules.bat routes {module}` หรือดูกฎใน [ส่วนที่ 4](#4-routing-block)

### 22. สรุป

| รายการ | จำนวน |
|---|---|
| Python files | 23 |
| SQL files | 3 |
| Test files | 5 |
| Docs files | 2 |
| Routing (แก้) | 2 |
| **รวม** | **35** |

### 23. รายงาน — Report A

---

## 🎯 TEMPLATE B: แก้ไขของเดิม (REFACTOR)

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `REFACTOR` |
| **Target Files** | `[list]` |
| **Breaking Change** | `Yes / No` |
| **Migration Impact** | `None / New migration needed` |

```mermaid
flowchart LR
    A[Read Existing] --> B[Analyze Coupling]
    B --> C[Plan Refactor]
    C --> D[Keep Public API]
    D --> E[Update Internal]
    E --> F[Run Tests]
    F --> G[Update Docs]
    G --> H{Pass?}
    H -->|No| E
    H -->|Yes| I[Done]
```

**ข้อห้าม:**
```markdown
❌ ห้ามเปลี่ยน public signature
❌ ห้ามแตะ layer อื่น
❌ ห้าม refactor นอกจุดที่ระบุ
❌ ห้ามเพิ่ม feature ใหม่
❌ ห้ามลบ tests เดิม
❌ ห้ามแก้ migration V001-V003 ที่ commit แล้ว
❌ ห้ามลด coverage
```

---

## 🎯 TEMPLATE C: เพิ่ม/แก้ไขจากเดิม (EXTEND)

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `EXTEND` |
| **Module** | `[module]` |
| **Feature** | `[feature ใหม่]` |
| **New Endpoints** | `[list]` |
| **New Migration** | `V00X__{action}.sql` |

**Diff Plan:**

| ไฟล์ | Action | รายละเอียด |
|---|---|---|
| `domain/entities.py` | `+method` | `bulk_create()` |
| `application/use_cases.py` | `+class` | `BulkCreateUseCase` |
| `presentation/routers.py` | `+endpoint` | `POST /bulk/` |
| `presentation/schemas.py` | `+schema` | `BulkCreateRequest` |
| `tests/unit/test_{module}.py` | `+test` | `test_bulk_create_*` |
| `db/migrations/V004__add_bulk.sql` | `new` | index + column |

---

## 🎯 TEMPLATE D: แก้ Bug (BUGFIX)

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `BUGFIX` |
| **Severity** | `🔴 / 🟡 / 🟢` |
| **Env** | `dev / staging / prod` |
| **Migration Impact** | `None / New migration` |

**Bug Report:**
```markdown
Symptom: [อาการ]
Steps: 1. ... 2. ...
Expected: [สิ่งที่ควรเกิด]
Actual: [สิ่งที่เกิด]
Stacktrace: [paste]
```

**Hypothesis (STEP 1 — รออนุมัติ):**
```markdown
1. Root Cause: [ไฟล์:บรรทัด + คำอธิบาย]
2. Fix Strategy: hotfix / proper fix / refactor
3. Migration needed? Yes/No
4. Regression Test: [ชื่อ test ที่จะเพิ่ม]
```

---

## 🎯 TEMPLATE E: ตรวจสอบความปลอดภัย (SECURITY AUDIT)

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `SECURITY_AUDIT` |
| **Standard** | `OWASP Top 10 / ASVS L2` |
| **Mode** | `Read-only / Audit+Fix` |

**Output — ตารางเท่านั้น:**

| # | Risk | Layer | File:Line | Severity | CWE | แนะนำแก้ | Auto-fix |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | 🔴 | CWE-XXX | ... | ✅ |

**Security Checklist:**
```markdown
#### A. Authentication & Authorization
- [ ] Nested JWT (JWS + JWE)
- [ ] Refresh token rotation
- [ ] RBAC ทุก endpoint

#### B. Input Validation
- [ ] Pydantic v2 strict
- [ ] SQL injection (ORM parameterized)
- [ ] Mass assignment

#### C. Data Protection
- [ ] Encryption at rest
- [ ] TLS in transit
- [ ] PII masking ใน logs

#### D. Multi-tenancy
- [ ] tenant_id ทุก query
- [ ] RLS policy ทุกตาราง
- [ ] Cross-tenant leakage test

#### E. API Security
- [ ] Rate limiting
- [ ] CORS policy
- [ ] CSRF (BFF)
- [ ] Idempotency key

#### F. SQL Security
- [ ] RLS enabled + forced
- [ ] FK ON DELETE ถูกต้อง
- [ ] Search_path ปลอดภัย
```

---

## 🎯 TEMPLATE F: ทดสอบประสิทธิภาพ (PERFORMANCE)

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `PERF_TEST` |
| **SLO** | `p95 < X ms, > Y rps` |
| **Tool** | `locust / k6 / pytest-benchmark` |

**Metrics:**

| Metric | Tool | Target | Before | After |
|---|---|---|---|---|
| p50 | pytest-benchmark | < 50ms | ? | ? |
| p95 | locust | < 200ms | ? | ? |
| RPS | locust | > 100 | ? | ? |
| DB queries/req | SQLAlchemy events | < 5 | ? | ? |
| Seq scans | EXPLAIN | 0 | ? | ? |

---

## 🎯 TEMPLATE G: ทำคู่มือ (DOCUMENTATION)

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `DOCUMENTATION` |
| **Doc Type** | `README / API / ARCH / RUNBOOK / ONBOARDING / ADR` |
| **Audience** | `Dev / DevOps / PM / End-user` |

**Doc Structure:**
```
docs/
├── README_{module}.md
├── API_{module}.md
├── ARCH_{module}.md
├── RUNBOOK_{module}.md
├── postman/{module}.postman_collection.json
└── adr/ADR-{nnn}-{title}.md
```

---

# 3. SQL & Migration Block

### 📄 `V001__create_{module}.sql`

```sql
-- ═══════════════════════════════════════════════════════════════
-- V001__create_{module}.sql
-- Module: {module} | Prefix: {prefix} | Layer: {layer}
-- Description: สร้างตาราง + index + RLS policy + trigger
-- ═══════════════════════════════════════════════════════════════
BEGIN;

CREATE SEQUENCE IF NOT EXISTS {prefix}_number_seq START 1;

CREATE TABLE tenant_{prefix}.{module}s (
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

    CONSTRAINT uq_{module}_code   UNIQUE (tenant_id, code),
    CONSTRAINT ck_{module}_amount CHECK (amount >= 0),
    CONSTRAINT ck_{module}_status CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'))
);

CREATE INDEX ix_{module}_tenant_status
    ON tenant_{prefix}.{module}s(tenant_id, status)
    WHERE deleted_at IS NULL;
CREATE INDEX ix_{module}_code    ON tenant_{prefix}.{module}s(code);
CREATE INDEX ix_{module}_created ON tenant_{prefix}.{module}s(created_at DESC);

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_{module}_updated_at
    BEFORE UPDATE ON tenant_{prefix}.{module}s
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE tenant_{prefix}.{module}s ENABLE ROW LEVEL SECURITY;

CREATE POLICY p_{module}_tenant ON tenant_{prefix}.{module}s
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
```

### 📄 `V002__seed_{module}.sql`

```sql
BEGIN;
INSERT INTO tenant_{prefix}.{module}s (tenant_id, code, name, status)
VALUES ('00000000-0000-0000-0000-000000000001', 'SYS-DEFAULT', 'System Default', 'ACTIVE')
ON CONFLICT (tenant_id, code) DO NOTHING;
COMMIT;
```

### 📄 `V003__rollback_{module}.sql`

```sql
BEGIN;
DROP TRIGGER  IF EXISTS trg_{module}_updated_at ON tenant_{prefix}.{module}s;
DROP POLICY   IF EXISTS p_{module}_tenant       ON tenant_{prefix}.{module}s;
DROP TABLE    IF EXISTS tenant_{prefix}.{module}s CASCADE;
DROP SEQUENCE IF EXISTS {prefix}_number_seq;
COMMIT;
```

### 📄 Update `migrations/env.py`

```python
from app.modules.{module}.infrastructure.models import {Module}Model
```

---

# 4. Routing Block

### 📄 `app/routes.py`

```python
from fastapi import APIRouter
from app.modules.{module}.presentation.routers import router as {module}_router

api_router = APIRouter(prefix="/api/v1")

# Layer 0
api_router.include_router(events_router)
api_router.include_router(audit_router)

# Layer N
api_router.include_router({module}_router)  # ← เพิ่ม

router = APIRouter()
router.include_router(api_router)
router.include_router(health_router)
```

### 📄 `presentation/routers.py`

```python
router = APIRouter(prefix="/{module}", tags=["{Module}"])
```

### ✅ Routing Checklist

```markdown
- [ ] import router ใน `app/routes.py`
- [ ] `include_router({module}_router)` อยู่ layer ถูก
- [ ] prefix ไม่ซ้ำกับ module อื่น
- [ ] tags ถูกต้อง (แสดงใน Swagger)
- [ ] เปิด `http://localhost:8000/docs` → เห็น endpoint ใหม่
- [ ] เปิด `http://localhost:8000/openapi.json` → เห็น schema
```

---

# 5. Docs / Swagger / Postman Block

### 📄 `docs/README_{module}.md`

```markdown
# Module: {module}
> Layer · Prefix · Version

## Purpose
## Architecture (Mermaid)
## Dependencies
## Database Schema
## API Endpoints
## Permissions
## Domain Events
## Environment Variables
## Setup
## Testing
## Usage Example
## Known Limitations
## Changelog
```

### 📄 Swagger Metadata

```python
router = APIRouter(prefix="/{module}", tags=["{Module}"])

@router.post(
    "/",
    status_code=201,
    summary="สร้าง {module}",
    operation_id="create_{module}",
    responses={
        201: RESPONSE_CREATE_201,
        400: RESPONSE_ERROR_400,
        409: {"description": "Conflict"},
        422: {"description": "Idempotency mismatch"},
    },
)
```

### 📄 Postman Collection

```json
{
  "info": { "name": "ERPIoT — {Module}" },
  "item": [
    { "name": "Auth" },
    { "name": "{Module} — Create" },
    { "name": "{Module} — List" },
    { "name": "{Module} — Get" },
    { "name": "{Module} — Update" },
    { "name": "{Module} — Delete" },
    { "name": "Health" }
  ]
}
```

---

# 6. Report Templates

## 📊 Report A: Task Completion

```markdown
# 📋 Task Report — {TaskType} / {Module}
## ✅ สรุปผล
| รายการ | สถานะ | หมายเหตุ |
|---|---|---|
| Domain | ✅ | 6 ไฟล์ |
| Application | ✅ | 6 ไฟล์ |
| Infrastructure | ✅ | 5 ไฟล์ |
| Presentation | ✅ | 5 ไฟล์ |
| SQL Migrations | ✅ | V001/V002/V003 |
| Routing | ✅ | routes.py + env.py |
| Docs | ✅ | README + API |
| Tests | ✅ | 5 ไฟล์ |
| Coverage | ✅ | ≥ 85% |
```

## 📊 Report B: Bug Fix

```markdown
# 🐛 Bug Fix Report — {bug_id}
## 🔍 Root Cause
## 🛠️ Fix
## 🧪 Regression Test
## 📊 Impact
## ✅ Verification
```

## 📊 Report C: Security Audit

```markdown
# 🔐 Security Audit Report
| # | Risk | Severity | CWE | Location | Fix |
```

## 📊 Report D: Performance

```markdown
# ⚡ Performance Report
| Metric | Before | After | Δ | Target | ผ่าน? |
```

---

# 7. Checklists

## ✅ DoD

```markdown
### Code
- [ ] Domain ไม่ import framework
- [ ] ใช้ Decimal
- [ ] flush() ไม่ commit()
- [ ] Cache never-raise
- [ ] Error handling 3/2/never
- [ ] Type hints ครบ

### SQL
- [ ] V001 create + index + RLS + trigger
- [ ] V002 seed
- [ ] V003 rollback
- [ ] env.py import models

### Routing
- [ ] register app/routes.py
- [ ] /docs เห็น tag ใหม่
- [ ] prefix ไม่ซ้ำ

### Tests
- [ ] Unit ≥ 8
- [ ] Integration ผ่าน
- [ ] Property 100 iter
- [ ] Manual 8 scenarios
- [ ] Coverage ≥ 85%

### Docs
- [ ] README อัปเดต
- [ ] Swagger metadata ครบ
- [ ] Postman collection อัปเดต
```

## ✅ SQL Migration

```markdown
- [ ] V001 (ไม่ IF NOT EXISTS)
- [ ] V002 (ON CONFLICT DO NOTHING)
- [ ] V003 (CASCADE)
- [ ] BEGIN/COMMIT ครบ
- [ ] id/tenant_id/version/created_at/updated_at/deleted_at
- [ ] CONSTRAINT (CHECK, UNIQUE, FK)
- [ ] Partial index
- [ ] ENABLE ROW LEVEL SECURITY
- [ ] CREATE POLICY
- [ ] BEFORE UPDATE trigger
```

## ✅ TDD Flow

```markdown
### Step 1: RED
- [ ] test fail ก่อน
- [ ] happy path
- [ ] edge cases
- [ ] error cases

### Step 2: GREEN
- [ ] minimal code
- [ ] test ผ่าน

### Step 3: REFACTOR
- [ ] behavior คงเดิม
- [ ] test ผ่าน
- [ ] Coverage ไม่ลด
```

## ✅ Pre-Flight

```markdown
- [ ] ใส่ Global Constraints
- [ ] Task Type (A-G)
- [ ] Module + Layer + Stack
- [ ] Output Scope (files)
- [ ] SQL needed? Yes/No
- [ ] Routing update? Yes/No
- [ ] Docs needed? Yes/No
- [ ] Postman needed? Yes/No
- [ ] Bug → stacktrace
- [ ] Security → Mode
- [ ] Perf → SLO
```

---

# 8. Scripts (Bat/PS1)

## 8.1 ตาราง Scripts

| Script | หน้าที่ | ตัวอย่าง |
|---|---|---|
| `create_modules.bat` | Wrapper เรียก PS1 | `create_modules.bat new inventory 3 inv --sql --tests --docs --routes` |
| `create_module.ps1` | Implementation หลัก | ดูรายละเอียดด้านล่าง |

## 8.2 Actions

| Action | คำอธิบาย |
|---|---|
| `new` | สร้าง module ใหม่ (4 layers + __init__) |
| `sql` | สร้าง V001/V002/V003 |
| `routes` | Register router + model |
| `test` | สร้าง unit/integration/property/manual + conftest |
| `docs` | สร้าง README + API |
| `all` | ทำทุกอย่าง |
| `template` | Generate OpenCode prompt ตาม Template A-G |
| `debug` | 🆕 Generate debug checklist + log config |
| `help` | แสดง help |

## 8.3 Layer Mapping

| Layer | ชื่อ | ตัวอย่าง |
|---|---|---|
| 0 | Core | audit, idempotency, events |
| 1 | Foundation | tenant, user, auth |
| 2 | Money | invoice, payment, gl |
| 3 | Goods | inventory, product, warehouse |
| 4 | Ops | sales, purchase, production |
| 5 | Intel | report, dashboard, analytics |
| 6 | Monitor | iot, alert, health |
| 7 | Template | report_template, email_template |

## 8.4 `create_modules.bat` — Full Code

```bat
@echo off
REM ═══════════════════════════════════════════════════════════════
REM  create_modules.bat
REM  Wrapper — เรียก PowerShell เพื่อสร้าง/แก้ไข module
REM  (Generic Module Generator for ERP+CRM+IoT)
REM
REM  USAGE:
REM    create_modules.bat <action> <module> [layer] [prefix] [options]
REM
REM  ACTIONS:
REM    new       สร้าง module ใหม่ (4 layers + __init__)
REM    sql       สร้าง SQL migrations V001/V002/V003
REM    routes    Register router + model
REM    test      สร้าง tests (unit/integration/property/manual + conftest)
REM    docs      สร้าง docs (README + API)
REM    template  Generate OpenCode prompt ตาม Template A-G
REM    debug     Generate debug checklist + log config
REM    all       ทำทุกอย่าง
REM    help      แสดง help
REM
REM  OPTIONS:
REM    --sql     สร้าง SQL
REM    --tests   สร้าง tests
REM    --docs    สร้าง docs
REM    --routes  register router + model
REM    --force   เขียนทับไฟล์เดิม
REM    --template=A|B|C|D|E|F|G
REM
REM  EXAMPLES:
REM    create_modules.bat new inventory 3 inv --sql --tests --docs --routes
REM    create_modules.bat template A inventory 3 inv
REM    create_modules.bat sql invoice inv
REM    create_modules.bat debug inventory
REM    create_modules.bat all sales 4 sal --force
REM    create_modules.bat help
REM ═══════════════════════════════════════════════════════════════

chcp 65001 >nul
setlocal EnableDelayedExpansion

where powershell >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PowerShell not found in PATH
    exit /b 1
)

set "PS_SCRIPT=%~dp0create_module.ps1"
if not exist "%PS_SCRIPT%" (
    echo [ERROR] create_module.ps1 not found at:
    echo        %PS_SCRIPT%
    exit /b 1
)

if "%~1"=="" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" -Action help
    goto :end
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*
set "EXITCODE=%ERRORLEVEL%"

:end
echo.
if not "%EXITCODE%"=="0" (
    echo [ERROR] Exit code %EXITCODE%
) else (
    echo [DONE] Completed successfully.
)
echo.
pause
endlocal
exit /b %EXITCODE%
```

## 8.5 `create_module.ps1` — Usage & Core Spec

```powershell
<#
.SYNOPSIS
    create_module.ps1 — Generic Module Generator v7.0
.DESCRIPTION
    สร้าง/แก้ไข module ตาม Clean Architecture + DDD (ERP+CRM+IoT)
    - 4 layers: domain / application / infrastructure / presentation
    - SQL: V001 create + V002 seed + V003 rollback + RLS
    - Routing: app/routes.py + migrations/env.py
    - Tests: unit / integration / property / manual + conftest
    - Docs: README + API
    - Debug: log config + debug checklist
    - Template: Generate OpenCode prompt (A-G)
.EXAMPLE
    .\create_module.ps1 new inventory 3 inv --sql --tests --docs --routes
.EXAMPLE
    .\create_module.ps1 template A inventory 3 inv
.EXAMPLE
    .\create_module.ps1 debug inventory
.EXAMPLE
    .\create_module.ps1 help
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("new","sql","routes","test","docs","template","debug","all","help")]
    [string]$Action = "help",

    [Parameter(Position = 1)]
    [string]$Module = "",

    [Parameter(Position = 2)]
    [string]$Layer = "0",

    [Parameter(Position = 3)]
    [string]$Prefix = "",

    [ValidateSet("A","B","C","D","E","F","G")]
    [string]$TemplateName = "A",

    [switch]$SQL,
    [switch]$Tests,
    [switch]$Docs,
    [switch]$Routes,
    [switch]$Force
)

# CONFIG
$ROOT        = "app\modules"
$ROUTES_F    = "app\routes.py"
$ENV_F       = "migrations\env.py"
$SQL_DIR     = "db\migrations"
$TESTS_DIR   = "tests"
$DOCS_DIR    = "docs"
$PROMPTS_DIR = "docs\prompts"
$DEBUG_DIR   = "docs\debug"
```

**Functions หลัก:**
- `Write-FileUtf8` — เขียนไฟล์ UTF-8 no BOM
- `Get-LayerName` — map layer 0-7
- `Get-Pascal` — แปลง snake_case → PascalCase
- `New-DomainLayer` — 6 ไฟล์
- `New-ApplicationLayer` — 6 ไฟล์
- `New-InfrastructureLayer` — 5 ไฟล์
- `New-PresentationLayer` — 5 ไฟล์
- `New-ModuleRoot` — `__init__.py`
- `New-SQLMigrations` — V001/V002/V003
- `New-Tests` — 5 ไฟล์ (incl. conftest.py) 🆕
- `New-Docs` — README + API
- `Add-RouterRegistration` — แก้ `app/routes.py`
- `Add-ModelRegistration` — แก้ `migrations/env.py`
- `New-OpenCodePrompt` — สร้าง prompt Template A-G
- `New-DebugKit` — 🆕 สร้าง `docs/debug/{module}_debug.md` + `log_config.py`

## 8.6 ตัวอย่างครบวงจร

```bat
REM 1. สร้าง module เปล่า
create_modules.bat new inventory 3 inv

REM 2. Full package
create_modules.bat new inventory 3 inv --sql --tests --docs --routes

REM 3. Generate OpenCode prompt
create_modules.bat template A inventory 3 inv

REM 4. เพิ่ม SQL ใหม่
create_modules.bat sql inventory inv

REM 5. Register router
create_modules.bat routes inventory

REM 6. Generate debug kit
create_modules.bat debug inventory

REM 7. ดู help
create_modules.bat help
```

---

# 9. 🆕 Testing Block

## 9.1 Test Pyramid

```mermaid
graph TD
    A["🔺 E2E / Manual (5%)<br/>8 scenarios"] --> B["🔷 Integration (25%)<br/>Repository + DB + Redis"]
    B --> C["🟩 Unit (70%)<br/>Domain / UseCase / Mapper"]
    C --> D["🟪 Property (bonus)<br/>Hypothesis invariants"]
```

| ระดับ | เป้าหมาย | เครื่องมือ | จำนวนขั้นต่ำ |
|---|---|---|---|
| Unit | Domain + Application logic | pytest + pytest-asyncio + unittest.mock | ≥ 8 ต่อ module |
| Integration | Repository + SQL + RLS | pytest + testcontainers + asyncpg | ≥ 4 |
| Property | Invariants | hypothesis | ≥ 3 |
| Manual | Smoke E2E | Postman / curl | 8 scenarios |

## 9.2 Dependencies (`pyproject.toml`)

```toml
[project.optional-dependencies]
test = [
    "pytest==8.3.*",
    "pytest-asyncio==0.24.*",
    "pytest-cov==6.0.*",
    "pytest-benchmark==5.1.*",
    "hypothesis==6.115.*",
    "testcontainers[postgres,redis]==4.8.*",
    "faker==30.*",
    "freezegun==1.5.*",
    "respx==0.21.*",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths   = ["tests"]
addopts = """
    -ra
    --strict-markers
    --strict-config
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=85
"""
markers = [
    "unit: Unit tests (fast, no IO)",
    "integration: Integration tests (DB/Redis)",
    "property: Property-based tests",
    "slow: Slow tests (> 1s)",
]

[tool.coverage.run]
branch = true
source = ["app"]
omit   = ["*/__init__.py", "*/migrations/*", "tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

## 9.3 `tests/conftest.py` — Fixtures กลาง

```python
"""
tests/conftest.py
Global fixtures — ใช้ร่วมทุก module
TH: Fixture กลางสำหรับ unit/integration test
EN: Shared fixtures for all test suites
"""
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
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ─── Tenant constants ─────────────────────────────────
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OTHER_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

# ─── Event loop ───────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """TH: event loop ระดับ session | EN: session-scoped loop"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# ─── Faker ────────────────────────────────────────────
@pytest.fixture
def faker_th() -> Faker:
    """TH: Faker locale ไทย | EN: Thai locale faker"""
    return Faker("th_TH")

# ─── Context ──────────────────────────────────────────
@pytest.fixture
def tenant_ctx() -> dict[str, Any]:
    """TH: request context มาตรฐาน | EN: standard request context"""
    return {
        "tenant_id": TENANT_ID,
        "user_id": uuid.uuid4(),
        "request_id": str(uuid.uuid4()),
        "trace_id": str(uuid.uuid4()),
    }

@pytest.fixture
def other_tenant_ctx() -> dict[str, Any]:
    """TH: context ของ tenant อื่น (ใช้ทดสอบ RLS) | EN: other tenant ctx"""
    return {
        "tenant_id": OTHER_TENANT_ID,
        "user_id": uuid.uuid4(),
        "request_id": str(uuid.uuid4()),
        "trace_id": str(uuid.uuid4()),
    }

# ─── DB (integration) ─────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncIterator[Any]:
    """
    TH: สร้าง engine จาก TEST_DATABASE_URL (testcontainers หรือ env)
    EN: Build engine from TEST_DATABASE_URL
    """
    url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5433/erp_test",
    )
    engine = create_async_engine(url, pool_pre_ping=True, echo=False)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine: Any) -> AsyncIterator[AsyncSession]:
    """
    TH: session ที่ rollback อัตโนมัติหลัง test
    EN: session with automatic rollback per test
    """
    async with db_engine.connect() as conn:
        tx = await conn.begin()
        Session = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with Session() as session:
            # ตั้ง tenant ปัจจุบันให้ RLS ทำงาน
            await session.execute(
                # TH: set_config สำหรับ RLS | EN: set_config for RLS
                __import__("sqlalchemy").text(
                    "SELECT set_config('app.current_tenant', :tid, true)"
                ),
                {"tid": str(TENANT_ID)},
            )
            yield session
        await tx.rollback()

# ─── Redis (integration) ──────────────────────────────
@pytest_asyncio.fixture
async def redis_client() -> AsyncIterator[Any]:
    """TH: Redis client สำหรับ test | EN: Redis test client"""
    import redis.asyncio as aioredis
    client = aioredis.from_url(
        os.getenv("TEST_REDIS_URL", "redis://localhost:6380/15"),
        decode_responses=True,
    )
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()

# ─── Mocks / Fakes ────────────────────────────────────
@pytest.fixture
def fake_clock() -> Any:
    """TH: เวลาคงที่สำหรับ deterministic test | EN: frozen clock"""
    from freezegun import freeze_time
    with freeze_time("2025-01-15 10:00:00+07:00") as frozen:
        yield frozen

@pytest.fixture
def decimal_factory() -> Any:
    """TH: factory สร้าง Decimal ปลอดภัย | EN: safe Decimal factory"""
    def _make(value: str | int) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    return _make
```

## 9.4 Unit Test Template — Domain

```python
"""
tests/unit/test_{module}.py — Domain Layer
TH: ทดสอบ entity + value object + domain rules
EN: Domain entity + VO + rule tests
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.domain.enums import {Module}Status
from app.modules.{module}.domain.exceptions import (
    InvalidAmountError,
    InvalidStatusTransitionError,
)
from app.modules.{module}.domain.value_objects import Money

pytestmark = pytest.mark.unit

# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════
@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")

@pytest.fixture
def make_{module}(tenant_id: uuid.UUID):
    """TH: factory สร้าง entity | EN: entity factory"""
    def _make(
        code: str = "INV-001",
        name: str = "Sample",
        amount: Decimal = Decimal("100.00"),
        status: {Module}Status = {Module}Status.ACTIVE,
    ) -> {Module}:
        return {Module}.create(
            tenant_id=tenant_id,
            code=code,
            name=name,
            amount=amount,
            status=status,
        )
    return _make

# ═══════════════════════════════════════════════════════════════
# Happy Path
# ═══════════════════════════════════════════════════════════════
class TestCreate:
    def test_create_sets_defaults(self, make_{module}) -> None:
        """TH: สร้างแล้วค่าตั้งต้นถูกต้อง | EN: defaults are set"""
        e = make_{module}()
        assert e.id is not None
        assert e.version == 1
        assert e.status is {Module}Status.ACTIVE
        assert e.deleted_at is None

    def test_create_with_zero_amount(self, make_{module}) -> None:
        """TH: ยอด 0 อนุญาต | EN: zero amount allowed"""
        e = make_{module}(amount=Decimal("0.00"))
        assert e.amount == Decimal("0.00")

# ═══════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════
class TestEdgeCases:
    def test_code_is_immutable(self, make_{module}) -> None:
        """TH: code แก้ไม่ได้หลังสร้าง | EN: code immutable"""
        e = make_{module}()
        with pytest.raises(AttributeError):
            e.code = "NEW"  # type: ignore[misc]

    def test_amount_precision_quantized(self, make_{module}) -> None:
        """TH: amount ถูก quantize 2 ตำแหน่ง | EN: amount quantized"""
        e = make_{module}(amount=Decimal("100.005"))
        assert e.amount == Decimal("100.01")  # ROUND_HALF_UP

# ═══════════════════════════════════════════════════════════════
# Error Cases
# ═══════════════════════════════════════════════════════════════
class TestErrors:
    def test_negative_amount_raises(self, make_{module}) -> None:
        """TH: ยอดติดลบต้อง error | EN: negative amount raises"""
        with pytest.raises(InvalidAmountError):
            make_{module}(amount=Decimal("-1.00"))

    def test_invalid_status_transition(self, make_{module}) -> None:
        """TH: ARCHIVED → ACTIVE ต้อง error | EN: invalid transition"""
        e = make_{module}(status={Module}Status.ARCHIVED)
        with pytest.raises(InvalidStatusTransitionError):
            e.activate()

    def test_empty_code_raises(self, make_{module}) -> None:
        """TH: code ว่างต้อง error | EN: empty code raises"""
        with pytest.raises(ValueError, match="code"):
            make_{module}(code="")

# ═══════════════════════════════════════════════════════════════
# Value Object
# ═══════════════════════════════════════════════════════════════
class TestMoneyVO:
    def test_money_add(self) -> None:
        a = Money(Decimal("10.00"))
        b = Money(Decimal("5.50"))
        assert (a + b).amount == Decimal("15.50")

    def test_money_currency_mismatch(self) -> None:
        a = Money(Decimal("10.00"), "THB")
        b = Money(Decimal("5.00"), "USD")
        with pytest.raises(ValueError, match="currency"):
            _ = a + b
```

## 9.5 Unit Test Template — Use Case (กับ Mock)

```python
"""
tests/unit/test_{module}_use_cases.py
TH: ทดสอบ use case ด้วย mock repository/cache/eventbus
EN: Use case tests with mocked ports
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.{module}.application.exceptions import DuplicateCodeError
from app.modules.{module}.application.use_cases import Create{Module}UseCase
from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.domain.events import {Module}Created

pytestmark = pytest.mark.unit

@pytest.fixture
def repo() -> AsyncMock:
    r = AsyncMock()
    r.get_by_code.return_value = None      # ไม่มีของซ้ำ
    r.save.side_effect = lambda e: e       # คืน entity เดิม
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
    m.check_or_lock.return_value = None    # ยังไม่เคยใช้ key
    return m

@pytest.fixture
def uc(repo, cache, event_bus, idem, tenant_ctx) -> Create{Module}UseCase:
    return Create{Module}UseCase(
        repo=repo, cache=cache, event_bus=event_bus, idempotency=idem,
        ctx=tenant_ctx,
    )

class TestCreateUseCase:
    async def test_happy_path(self, uc, repo, event_bus) -> None:
        """TH: สร้างสำเร็จ + publish event | EN: success + event emitted"""
        out = await uc.execute(
            code="INV-001", name="Test", amount=Decimal("100.00"),
            idempotency_key="k-1",
        )
        assert out.code == "INV-001"
        repo.save.assert_awaited_once()
        event_bus.publish.assert_awaited_once()
        evt = event_bus.publish.await_args.args[0]
        assert isinstance(evt, {Module}Created)

    async def test_duplicate_code_raises(self, uc, repo) -> None:
        """TH: code ซ้ำ → DuplicateCodeError | EN: duplicate raises"""
        repo.get_by_code.return_value = MagicMock(spec={Module})
        with pytest.raises(DuplicateCodeError):
            await uc.execute(
                code="INV-001", name="Dup", amount=Decimal("1.00"),
                idempotency_key="k-2",
            )
        repo.save.assert_not_awaited()

    async def test_cache_failure_does_not_break(
        self, uc, cache, event_bus
    ) -> None:
        """TH: cache พังไม่ทำให้ use case ล้ม | EN: cache never-raise"""
        cache.invalidate.side_effect = RuntimeError("redis down")
        # ต้องไม่ raise
        out = await uc.execute(
            code="INV-002", name="X", amount=Decimal("1.00"),
            idempotency_key="k-3",
        )
        assert out.code == "INV-002"
        event_bus.publish.assert_awaited_once()

    async def test_readback_verification(
        self, uc, repo
    ) -> None:
        """TH: ต้องเรียก get_by_id หลัง save | EN: read-back verify"""
        await uc.execute(
            code="INV-003", name="X", amount=Decimal("1.00"),
            idempotency_key="k-4",
        )
        repo.get_by_id.assert_awaited_once()
```

## 9.6 Integration Test — Repository + RLS

```python
"""
tests/integration/test_{module}_repository.py
TH: ทดสอบ repository กับ PostgreSQL จริง + RLS
EN: Repository test against real PostgreSQL + RLS
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.infrastructure.repositories import (
    SQLAlchemy{Module}Repository,
)

pytestmark = pytest.mark.integration

@pytest.fixture
def repo(db_session) -> SQLAlchemy{Module}Repository:
    return SQLAlchemy{Module}Repository(session=db_session)

class TestRepository:
    async def test_save_and_get(self, repo, tenant_ctx) -> None:
        e = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=f"INV-{uuid.uuid4().hex[:6]}",
            name="Repo Test",
            amount=Decimal("99.99"),
        )
        saved = await repo.save(e)
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.code == saved.code
        assert fetched.amount == Decimal("99.99")

    async def test_rls_blocks_other_tenant(
        self, repo, db_session, tenant_ctx, other_tenant_ctx
    ) -> None:
        """TH: tenant อื่นมองไม่เห็น | EN: RLS isolates tenants"""
        e = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code="INV-RLS-1", name="RLS", amount=Decimal("1.00"),
        )
        await repo.save(e)

        # เปลี่ยน tenant ปัจจุบัน
        from sqlalchemy import text
        await db_session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"),
            {"tid": str(other_tenant_ctx["tenant_id"])},
        )
        found = await repo.get_by_id(e.id)
        assert found is None  # RLS ต้องปิด

    async def test_unique_code_conflict(self, repo, tenant_ctx) -> None:
        code = f"INV-{uuid.uuid4().hex[:6]}"
        e1 = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=code, name="A", amount=Decimal("1.00"),
        )
        await repo.save(e1)
        e2 = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=code, name="B", amount=Decimal("2.00"),
        )
        with pytest.raises(Exception):  # IntegrityError
            await repo.save(e2)
```

## 9.7 Property Test — Invariants

```python
"""
tests/property/test_{module}_invariants.py
TH: ทดสอบคุณสมบัติเชิงสัญลักษณ์ด้วย hypothesis
EN: Property-based tests with hypothesis
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st

from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.domain.exceptions import InvalidAmountError

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
    """TH: ยอด ≥ 0 สร้างได้เสมอ | EN: non-negative always valid"""
    e = {Module}.create(
        tenant_id=TENANT, code=code or "X", name="P", amount=amount,
    )
    assert e.amount >= Decimal("0.00")

@settings(max_examples=100)
@given(amount=st.decimals(
    min_value=Decimal("-9999"), max_value=Decimal("-0.01"), places=2,
))
def test_negative_amount_always_rejected(amount: Decimal) -> None:
    """TH: ยอดติดลบต้อง raise เสมอ | EN: negative always rejected"""
    with pytest.raises(InvalidAmountError):
        {Module}.create(
            tenant_id=TENANT, code="X", name="P", amount=amount,
        )

@settings(max_examples=100)
@given(
    a=amounts, b=amounts,
)
def test_sum_is_commutative(a: Decimal, b: Decimal) -> None:
    """TH: บวกสลับที่ได้ผลเท่ากัน | EN: addition commutative"""
    from app.modules.{module}.domain.value_objects import Money
    m1 = Money(a); m2 = Money(b)
    assert (m1 + m2).amount == (m2 + m1).amount
```

## 9.8 Manual Test Checklist

```markdown
# Manual Test — {module}

## Pre-conditions
- [ ] DB migrated (V001–V003)
- [ ] Redis running
- [ ] Kafka running (ถ้ามี)
- [ ] `.env` set TEST_DATABASE_URL

## Scenarios (8)
| # | Scenario | Method | Endpoint | Expected | ✅ |
|---|---|---|---|---|---|
| 1 | Create happy | POST | `/api/v1/{module}/` | 201 + body | ☐ |
| 2 | Create duplicate | POST | `/api/v1/{module}/` | 409 | ☐ |
| 3 | Create invalid amount | POST | `/api/v1/{module}/` | 422 | ☐ |
| 4 | Get by id | GET | `/api/v1/{module}/{id}` | 200 | ☐ |
| 5 | List + filter | GET | `/api/v1/{module}/?status=ACTIVE` | 200 | ☐ |
| 6 | Update | PATCH | `/api/v1/{module}/{id}` | 200 + version+1 | ☐ |
| 7 | Delete (soft) | DELETE | `/api/v1/{module}/{id}` | 204 + deleted_at | ☐ |
| 8 | Cross-tenant | GET | other tenant token | 404 | ☐ |

## Idempotency
- [ ] POST ซ้ำด้วย `Idempotency-Key` เดิม → ได้ response เดิม
- [ ] POST ด้วย key เดิม + payload ต่าง → 422

## Security
- [ ] ไม่มี token → 401
- [ ] token ผิด scope → 403
- [ ] SQL injection ที่ code → 422
```

## 9.9 Test Commands Cheatsheet

```bash
# ─── Run both ────────────────────────────────────
pytest                                  # ทั้งหมด
pytest -m unit                          # unit เท่านั้น
pytest -m integration                   # integration เท่านั้น
pytest -m "not slow"                    # ข้าม slow
pytest -m property                      # property

# ─── Single file / test ──────────────────────────
pytest tests/unit/test_inventory.py
pytest tests/unit/test_inventory.py::TestCreate::test_create_sets_defaults
pytest -k "duplicate or invalid"         # keyword match

# ─── Coverage ────────────────────────────────────
pytest --cov=app --cov-report=term-missing
pytest --cov=app --cov-report=html:htmlcov
pytest --cov=app --cov-fail-under=85

# ─── Debug ───────────────────────────────────────
pytest -x                                # หยุดที่ fail แรก
pytest --lf                              # last failed
pytest --ff                              # failed first
pytest -vv --tb=long                     # verbose + full traceback
pytest -s                                # แสดง print/stdout
pytest --pdb                             # drop เข้า pdb ตอน fail
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb   # ipdb

# ─── Parallel ────────────────────────────────────
pytest -n auto                           # ใช้ pytest-xdist

# ─── Benchmark ───────────────────────────────────
pytest --benchmark-only
pytest --benchmark-compare=0001
```

## 9.10 Coverage Map

| Layer | Coverage ขั้นต่ำ | เหตุผล |
|---|---|---|
| `domain/` | **95%** | Business logic ล้วน ไม่มี IO |
| `application/` | **90%** | Use cases |
| `infrastructure/` | **80%** | IO-bound, บางส่วน override ด้วย integration |
| `presentation/` | **70%** | Thin — วัดผ่าน integration |
| **รวมทั้งโปรเจกต์** | **85%** | CI gate |

---

# 10. 🆕 Debug Block

## 10.1 Debug Workflow

```mermaid
flowchart TD
    A[🐛 Symptom] --> B{Reproducible?}
    B -->|No| C[Add structured log + trace_id]
    B -->|Yes| D[Isolate Layer]
    C --> D
    D --> E{Domain / App / Infra / Pres?}
    E -->|Domain| F[Write failing unit test]
    E -->|App| G[Mock ports → failing unit]
    E -->|Infra| H[Check SQL / Redis / Kafka]
    E -->|Pres| I[Check schema / dependency / auth]
    F & G & H & I --> J[Root Cause Hypothesis]
    J --> K[Fix + regression test]
    K --> L[Verify + remove temp logs]
```

## 10.2 Debug Rules (ห้ามละเมิด)

```markdown
❌ ห้าม print() / pprint() ใน Production code
❌ ห้าม log PII (email, phone, เลขบัตร, token)
❌ ห้าม log secret / password / authorization header
❌ ห้าม commit debug code (breakpoint, TODO, pdb)
❌ ห้ามปิด error handler ชั่วคราวใน commit
✅ ใช้ structlog เท่านั้น
✅ log ด้วย trace_id + request_id + tenant_id
✅ ใช้ pdb/ipdb เฉพาะในเครื่อง dev
✅ ลบ breakpoint ก่อน push
```

## 10.3 Structured Logging Setup

```python
"""
app/core/logging.py
TH: ตั้งค่า structlog กลาง + PII masking
EN: Central structlog config + PII masking
"""
from __future__ import annotations

import logging
import re
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

# ─── PII masking patterns ─────────────────────────────
PII_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "***@***"),
    (re.compile(r"\b0\d{8,9}\b"), "***PHONE***"),
    (re.compile(r"\b\d{13}\b"), "***ID***"),
    (re.compile(r"(Bearer\s+)[\w\-._~+/]+=*", re.I), r"\1***"),
    (re.compile(r"(password[\"']?\s*[:=]\s*[\"']?)[^\"'\s,}]+", re.I), r"\1***"),
]

def mask_pii(_logger: Any, _name: str, event: EventDict) -> EventDict:
    """TH: ปิดบัง PII ใน log | EN: mask PII in log event"""
    for k, v in list(event.items()):
        if isinstance(v, str):
            for pat, repl in PII_PATTERNS:
                v = pat.sub(repl, v)
            event[k] = v
    return event

def configure_logging(level: str = "INFO", json: bool = False) -> None:
    """TH: ตั้งค่า logging กลาง | EN: configure global logging"""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        mask_pii,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

log = structlog.get_logger()
```

## 10.4 Request-Scoped Context (FastAPI)

```python
"""
app/core/middleware.py
TH: ผูก trace_id / request_id / tenant_id เข้า contextvar
EN: Bind trace context into contextvars per request
"""
from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            trace_id=trace_id,
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        started = time.perf_counter()
        try:
            resp = await call_next(request)
        except Exception:
            log.exception("request.failed")
            raise
        finally:
            dur_ms = (time.perf_counter() - started) * 1000
            log.info("request.done", dur_ms=round(dur_ms, 2))

        resp.headers["x-trace-id"] = trace_id
        resp.headers["x-request-id"] = request_id
        return resp
```

## 10.5 Debug Recipes — แยกตาม Layer

### 🟦 Domain Layer

```python
# TH: ตรวจ invariant ด้วย assert + message
# EN: assert invariants with explicit message
from decimal import Decimal

def create(cls, *, amount: Decimal, **kw):
    if amount < 0:
        raise InvalidAmountError(f"amount must be >= 0, got {amount!r}")
    ...
```

**Debug checklist:**
- [ ] `@dataclass(frozen=True)` → ลอง `e.code = "X"` ต้อง `FrozenInstanceError`
- [ ] ตรวจ `__eq__` / `__hash__` ของ VO
- [ ] ใช้ `repr()` ดู state ทั้งก้อน

### 🟩 Application Layer

```python
# TH: ผูก log context กับ use case
# EN: bind log context to use case
import structlog
log = structlog.get_logger()

class Create{Module}UseCase:
    async def execute(self, *, code: str, ..., idempotency_key: str):
        log.info("usecase.start", code=code, key=idempotency_key)
        try:
            ...
        except StandardException:
            log.warning("usecase.standard_error", code=code)
            raise
        except DomainError as e:
            log.warning("usecase.domain_error", code=code, err=str(e))
            raise
        except Exception:
            log.exception("usecase.unexpected", code=code)
            raise
```

**Debug checklist:**
- [ ] Mock ports (repo/cache/bus) แล้วเรียก `uc.execute()` ตรง ๆ
- [ ] ตรวจ args ที่ส่งให้ repo ด้วย `repo.save.await_args`
- [ ] ตรวจ event ที่ publish: `bus.publish.await_args.args[0]`

### 🟨 Infrastructure Layer

```python
# TH: เปิด SQL echo เฉพาะ debug
# EN: enable SQL echo only for debug
import os
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    url,
    echo=os.getenv("SQL_ECHO", "0") == "1",
    pool_pre_ping=True,
)
```

**Debug checklist:**
- [ ] `SET app.current_tenant = '...'` ก่อน query (RLS)
- [ ] `EXPLAIN (ANALYZE, BUFFERS) SELECT ...` ดู seq scan
- [ ] Redis: `redis-cli -p 6380 monitor` ดู key จริง
- [ ] Kafka: `kafka-console-consumer --topic {module}.created`
- [ ] ตรวจ `flush()` ไม่มี `commit()` ใน repo

**SQL debug query:**

```sql
-- ดู RLS policy ปัจจุบัน
SELECT * FROM pg_policies WHERE tablename = '{module}s';

-- ตรวจว่า RLS เปิดจริง
SELECT relname, relrowsecurity, relforcerowsecurity
FROM pg_class WHERE relname = '{module}s';

-- ดู tenant ปัจจุบัน
SHOW app.current_tenant;

-- ดู index ที่ใช้
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM tenant_{prefix}.{module}s
WHERE tenant_id = '...'::uuid AND status = 'ACTIVE';
```

### 🟥 Presentation Layer

```python
# TH: log payload (หลัง mask) ที่ขอบ router
# EN: log payload (masked) at router edge
import structlog
log = structlog.get_logger()

@router.post("/", status_code=201)
async def create_{module}(
    payload: {Module}CreateRequest,
    idem_key: str = Header(..., alias="Idempotency-Key"),
    uc: Create{Module}UseCase = Depends(get_create_uc),
):
    log.info("http.create.start", code=payload.code, idem=idem_key[:8])
    try:
        result = await uc.execute(**payload.model_dump(), idempotency_key=idem_key)
    except DomainError as e:
        log.warning("http.create.domain_error", err=str(e))
        raise HTTPException(400, detail=str(e)) from e
    return {Module}Response.model_validate(result, from_attributes=True)
```

**Debug checklist:**
- [ ] `curl -v` ดู header/status
- [ ] เปิด `/docs` ดู schema ตรงไหม
- [ ] `x-trace-id` propagate ครบไหม
- [ ] ตรวจ pydantic validation error detail

## 10.6 Debug Tools Cheatsheet

| เครื่องมือ | คำสั่ง | ใช้เมื่อ |
|---|---|---|
| **pdb** | `breakpoint()` | debug ทั่วไป |
| **ipdb** | `pip install ipdb` แล้ว `import ipdb; ipdb.set_trace()` | ต้องการ tab-complete |
| **pytest --pdb** | `pytest --pdb` | drop เข้า pdb ตอน test fail |
| **pytest --trace** | `pytest --trace` | step ตั้งแต่ต้น |
| **rich** | `from rich import inspect; inspect(obj, methods=True)` | ดู object สวย ๆ |
| **icecream** | `from icecream import ic; ic(x)` | แทน print debug |
| **structlog** | `log.info("k", v=...)` | log โครงสร้าง |
| **sqlalchemy echo** | `SQL_ECHO=1` | ดู SQL ที่ออก |
| **asyncpg debug** | `logging.getLogger("asyncpg").setLevel(DEBUG)` | ดู query asyncpg |
| **redis monitor** | `redis-cli -p 6380 monitor` | ดูคำสั่ง Redis |
| **kafka consumer** | `kafka-console-consumer --bootstrap-server ... --topic ...` | ดู event |
| **py-spy** | `py-spy top --pid $PID` | profiler ไม่หยุด process |
| **scalene** | `scalene app.py` | CPU + memory profiler |
| **memray** | `memray run -o out.bin app.py` | memory leak |
| **asyncio debug** | `PYTHONASYNCIODEBUG=1` | ตรวจ task ค้าง |
| **faulthandler** | `python -X faulthandler` | dump stack ตอน hang |

## 10.7 Common Issues & Fixes

| อาการ | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|---|---|---|
| `MissingGreenlet` | lazy load ใน async | ใช้ `selectinload` / `joinedload` |
| `InterfaceError: another operation in progress` | ใช้ session พร้อมกัน | 1 session ต่อ 1 request |
| `TimeoutError` pool exhausted | pool_size น้อย | เพิ่ม `pool_size`, `max_overflow` |
| RLS คืน 0 rows | ไม่ set `app.current_tenant` | `set_config(..., true)` ก่อน query |
| `InvalidRequestError: greenlet_spawn` | sync code ใน async | `await session.run_sync(...)` |
| Pydantic validation ช้า | model ซับซ้อน | ใช้ `model_config = ConfigDict(strict=True)` |
| `DuplicateCode` บ่อย | race condition | unique index + `ON CONFLICT` |
| Event ไม่ถึง consumer | Kafka offset / partition | ตรวจ consumer group + lag |
| Cache stale | invalidate ไม่ครบ | `invalidate` ใน use case |
| `Decimal` precision เพี้ยน | ปนกับ float | ห้าม float, ใช้ `Decimal(str(x))` |
| Test hang | async fixture ไม่ปิด | ใช้ `pytest-asyncio` + `AsyncIterator` |
| `RuntimeError: Event loop is closed` | engine ข้าม loop | scope fixture ให้ถูก |

## 10.8 Debug Checklist (ก่อนปิดงาน)

```markdown
- [ ] Reproducible test เขียนแล้ว (RED)
- [ ] Root cause ระบุ file:line
- [ ] Fix minimal + ไม่แตะ layer อื่น
- [ ] Regression test ผ่าน (GREEN)
- [ ] Coverage ไม่ลด
- [ ] ไม่มี print/pdb ค้างในโค้ด
- [ ] log ใหม่ไม่มี PII
- [ ] trace_id ปรากฏใน log ทุก layer
- [ ] อัปเดต CHANGELOG / RUNBOOK ถ้าจำเป็น
```

## 10.9 ENV สำหรับ Debug

```bash
# .env.debug
LOG_LEVEL=DEBUG
LOG_JSON=false
SQL_ECHO=1
PYTHONASYNCIODEBUG=1
PYTHONFAULTHANDLER=1
PYTHONUNBUFFERED=1
UVICORN_LOG_LEVEL=debug
REDIS_LOG_LEVEL=debug
```

```bash
# รัน debug mode
LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload --log-level debug

# debug pytest
pytest -vv --tb=long --log-cli-level=DEBUG -k "{module}"

# profile async
PYTHONASYNCIODEBUG=1 pytest tests/integration -k "{module}"
```

---

# 11. Quick Command Cheatsheet

```bash
# ─── A: CREATE_NEW ────────────────────────────────────
opencode -c "TEMPLATE A + module=inventory + layer=3-goods + FULL OUTPUT"

# ─── B: REFACTOR ─────────────────────────────────────
opencode -c "TEMPLATE B + target=repositories.py"

# ─── C: EXTEND ───────────────────────────────────────
opencode -c "TEMPLATE C + module=key + feature=bulk-revoke"

# ─── D: BUGFIX ───────────────────────────────────────
opencode -c "TEMPLATE D + stacktrace=[paste]"

# ─── E: SECURITY ─────────────────────────────────────
opencode -c "TEMPLATE E + target=authentication + Mode=Read-only"

# ─── F: PERFORMANCE ──────────────────────────────────
opencode -c "TEMPLATE F + target=knowledge/list + SLO p95<200ms"

# ─── G: DOCS ─────────────────────────────────────────
opencode -c "TEMPLATE G + Doc Type=README + module=events"

# ─── Scripts ─────────────────────────────────────────
create_modules.bat new inventory 3 inv --sql --tests --docs --routes
create_modules.bat template A inventory 3 inv
create_modules.bat debug inventory
create_modules.bat help

# ─── Test ────────────────────────────────────────────
pytest -m unit -q
pytest -m integration -q --cov=app
pytest --lf -vv --tb=long
pytest --pdb -k "{module}"

# ─── Debug ───────────────────────────────────────────
LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload --log-level debug
redis-cli -p 6380 monitor
py-spy top --pid $(pgrep -f "uvicorn app.main")
```

---

# 12. Universal Header

```markdown
# ═══════════════════════════════════════════════════════════════
# 🎯 OPENCODE PROMPT — [Module] / [Task A-G]
# ═══════════════════════════════════════════════════════════════

[GLOBAL CONSTRAINTS]
- ห้ามทักทาย / ห้ามสรุป / ห้ามอธิบายซ้ำ
- ตอบเฉพาะไฟล์ใน Output Scope
- โค้ดเต็ม Production-ready ห้าม `...`
- คอมเมนต์ 2 ภาษา (TH+EN)
- 3-branch / 2-branch / never-raise
- Decimal / flush() ห้าม commit()
- SQL: V001 + V002 + V003 + RLS
- Routing: app/routes.py + migrations/env.py
- Docs: README + Swagger + Postman
- Tests: unit ≥ 8 / integration / property / manual — coverage ≥ 85%
- Debug: structlog เท่านั้น / ห้าม log PII / ห้าม print

### Metadata
- Task: [A-G] | Module: [xxx] | Layer: [0-7]
- Stack: [FastAPI / Django / Both]
- Tests needed? [Yes/No] | Debug kit? [Yes/No]

### Output Scope (23 ส่วน)
01-16: Details → Checklist
17: SQL & Migration (บังคับ)
18: Routing (บังคับ)
19-21: Docs + Swagger + Postman (บังคับ)
22-23: Summary + Report
+ §9 Testing Block: conftest + unit + integration + property + manual
+ §10 Debug Block: log config + context middleware + recipes

# ═══════════════════════════════════════════════════════════════
```

---

# ✅ สรุปความสมบูรณ์ (v2.0)

| ส่วน | สถานะ |
|---|---|
| Global Constraints | ✅ |
| 23 ส่วนบังคับ | ✅ |
| 7 Task Templates (A–G) | ✅ |
| SQL & Migration Block | ✅ V001 + V002 + V003 + RLS |
| Routing Block | ✅ routes.py + env.py |
| Docs / Swagger / Postman | ✅ 4 ระบบ |
| 4 Report Templates | ✅ A/B/C/D |
| Checklists | ✅ DoD + TDD + Pre-flight + SQL + Docs |
| Scripts (Bat/PS1) | ✅ + `debug` action |
| **Testing Block (§9)** | ✅ **Test pyramid + conftest + 4 ตัวอย่างเต็ม + commands + coverage map** |
| **Debug Block (§10)** | ✅ **Workflow + rules + structlog + middleware + recipes + tools + issues + env** |
| Cheatsheet | ✅ + test/debug commands |
| Universal Header | ✅ + tests/debug flag |

## 🔑 สิ่งที่เพิ่มใน v2.0

1. **§9 Testing Block** — ครบวงจร
   - Test pyramid + coverage map ราย layer
   - `pyproject.toml` สำหรับ pytest + coverage
   - `tests/conftest.py` พร้อม fixture (event loop, tenant, DB, Redis, faker, freeze_time)
   - Unit test ตัวอย่าง 2 ชุด: **Domain** (happy/edge/error/VO) + **Use Case** (mock ports)
   - Integration test ที่ทดสอบ **RLS cross-tenant**
   - Property test ด้วย **hypothesis**
   - Manual test checklist 8 scenarios + idempotency + security
   - คำสั่ง pytest ครบ

2. **§10 Debug Block** — ครบวงจร
   - Workflow แยกตาม layer
   - กฎเหล็ก (ห้าม print, ห้าม PII)
   - **structlog** + PII masking processor
   - **RequestContextMiddleware** ผูก trace_id/request_id
   - Recipes ต่อ layer (Domain/App/Infra/Pres) + SQL debug queries
   - ตาราง tools (pdb, ipdb, py-spy, memray, ...)
   - ตาราง **Common Issues & Fixes** (12 อาการ)
   - Debug checklist + `.env.debug` + คำสั่งรัน

3. **อัปเดตที่เกี่ยวข้อง**
   - Template A: เพิ่ม `tests/conftest.py` → รวมเป็น 35 ไฟล์
   - Template B: ห้ามลด coverage
   - Template C: เพิ่ม test ตาม feature
   - Template D: ต้องมี regression test
   - `create_modules.bat` / `create_module.ps1`: เพิ่ม action `debug`
   - Pre-flight + DoD: เพิ่มเงื่อนไข test/debug
   - Universal Header: ระบุ tests/debug flag

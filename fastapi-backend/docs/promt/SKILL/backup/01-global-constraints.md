[text](01-global-constraints.md)# 📚 `reference/*.md` — ทั้ง 11 ไฟล์แบบเต็ม

> ทุกไฟล์พร้อม copy วางใน `python-ddd-clean-arch/reference/` ได้ทันที

---

## 📄 `reference/01-global-constraints.md`

```markdown
# 01 — Global Constraints

> **สถานะ:** บังคับทุก prompt · ห้ามละเมิด · ใช้แทน "system rules" ของทุก task

---

## กฎเหล็ก (Hard Rules)

```markdown
[GLOBAL CONSTRAINTS]
- ห้ามทักทาย / ห้ามสรุป / ห้ามอธิบายซ้ำ
- ตอบเฉพาะไฟล์ใน "Output Scope"
- โค้ดเต็ม Production-ready ห้าม `...` หรือ `# code here`
- ห้ามแตะไฟล์นอก Scope (ถ้าจำเป็น → ประกาศ SIDE-EFFECT WARNING)
- คอมเมนต์ 2 ภาษา (ไทย + English) สั้น กระชับ
- Type hints ครบ / Pydantic v2 / SQLAlchemy 2.0 async
- ใช้ `Decimal` เท่านั้น (ห้าม float กับเงิน/สต็อก)
- ใช้ `flush()` ห้าม `commit()` ใน Repository
- SQL: V001 create + V002 seed + V003 rollback + RLS + Trigger
- Routing: register ที่ `app/routes.py` + `migrations/env.py`
- Docs: README + OpenAPI + Postman + AsyncAPI (ถ้ามี WS)
- Tests: unit ≥ 8 / integration / property / manual — coverage ≥ 85%
- Debug: structlog เท่านั้น / ห้าม log PII / ห้าม print
- Path: `app/modules/{module}/{layer}/{file}.py`
- ข้อมูลไม่พอ → ถาม 1 คำถาม ห้ามเดา
```

---

## 1. Error Handling — 3 รูปแบบ

### 1.1 Use Case → 3-branch

```python
import structlog
log = structlog.get_logger()

class CreateXUseCase:
    async def execute(self, *, code: str, ...) -> X:
        log.info("usecase.start", code=code)
        try:
            # TH: happy path | EN: happy path
            ...
        except StandardException:
            # TH: business error ที่รู้จัก (409, 422)
            # EN: known business error
            log.warning("usecase.standard_error", code=code)
            raise
        except DomainError as e:
            # TH: domain rule ถูกละเมิด
            # EN: domain rule violated
            log.warning("usecase.domain_error", code=code, err=str(e))
            raise
        except Exception:
            # TH: unexpected — log full traceback
            # EN: unexpected — log full traceback
            log.exception("usecase.unexpected", code=code)
            raise
```

### 1.2 Repository → 2-branch

```python
class SQLAlchemyXRepository(XRepository):
    async def save(self, entity: X) -> X:
        try:
            self.session.add(entity)
            await self.session.flush()  # ห้าม commit
            return entity
        except StandardException:
            # TH: re-raise โดยไม่ log ซ้ำ (UC log แล้ว)
            raise
        except Exception as e:
            # TH: wrap เป็น infra error
            raise RepositoryError(f"save failed: {e}") from e
```

### 1.3 Cache → never-raise

```python
class RedisXCache(XCache):
    async def get(self, key: str) -> X | None:
        try:
            raw = await self.redis.get(key)
            return X.model_validate_json(raw) if raw else None
        except Exception as e:
            # TH: cache ล้มไม่ทำให้ use case ล้ม
            # EN: cache failure must not break UC
            log.warning("cache.get_failed", key=key, err=str(e))
            return None

    async def invalidate(self, key: str) -> bool:
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            log.warning("cache.invalidate_failed", key=key, err=str(e))
            return False
```

---

## 2. Type & Precision Rules

| หัวข้อ | กฎ |
|---|---|
| Money | `Decimal` เท่านั้น · `NUMERIC(15,2)` · quantize `0.01` |
| Stock | `Decimal` · quantize ตาม UoM |
| ID | `uuid.UUID` (v4 / v7) |
| Timestamps | `datetime` aware · `TIMESTAMPTZ` |
| Enums | `enum.StrEnum` (Python 3.11+) |
| Optional | `X \| None` (ไม่ใช้ `Optional[X]`) |
| Collections | `list[X]`, `dict[str, X]` (ไม่ใช้ `List`, `Dict`) |

**ห้ามเด็ดขาด:**
```python
amount = 10.5              # ❌ float
amount = Decimal(10.5)     # ❌ float→Decimal โดยตรง
amount = Decimal("10.5")   # ✅
amount = Decimal(str(x))   # ✅
```

---

## 3. Layer Import Rules

```
┌────────────────────────────────────────────┐
│ presentation  →  application  →  domain    │
│       ↓              ↓              ↑      │
│   infrastructure ────┴──────────────┘      │
└────────────────────────────────────────────┘
```

| Layer | ห้าม import |
|---|---|
| `domain/` | FastAPI, SQLAlchemy, Pydantic, Redis, Kafka, httpx |
| `application/` | FastAPI, SQLAlchemy, Redis, Kafka (ใช้ interface/port เท่านั้น) |
| `infrastructure/` | FastAPI (ยกเว้น Depends) |
| `presentation/` | SQLAlchemy (ยกเว้น type hint) |

---

## 4. Security Rules

```markdown
❌ ห้าม hardcode secret / API key / DB password
❌ ห้าม log PII (email, phone, เลขบัตร, token, password)
❌ ห้าม log Authorization header
❌ ห้าม return stacktrace ใน production response
❌ ห้าม query ข้าม tenant (RLS enforced)
❌ ห้าม UPDATE/DELETE ใน audit/event store
✅ ใช้ environment variable + pydantic-settings
✅ ใช้ mask_pii processor ใน structlog
✅ ใช้ generic message กับ client, log เต็มฝั่ง server
```

---

## 5. Idempotency Rules

ทุก mutating endpoint (POST/PUT/PATCH/DELETE) ต้องรองรับ `Idempotency-Key`:

| สถานะ | Response |
|---|---|
| key ใหม่ | lock + process + complete → 201/200 |
| key เดิม + payload เดิม | replay response เดิม (cached) |
| key เดิม + payload ต่าง | `409 Conflict` |
| key เดิม + still processing | `409 Conflict` (or `202 Accepted`) |
| key format ผิด | `422 Unprocessable Entity` |

---

## 6. Output Format Rules

```markdown
- ห้าม greeting: "สวัสดี", "Hello", "แน่นอน", "นี่คือ..."
- ห้าม summary ท้ายข้อความ
- ห้ามอธิบายซ้ำกับโค้ด
- ห้าม `...`, `# same as before`, `# TODO`
- โค้ดต้องรันได้จริง ไม่มี placeholder
- ไฟล์ไหนไม่รู้ path → ใช้ path ตาม convention เท่านั้น
- ถ้าต้องแตะนอก scope → ขึ้นต้น "⚠️ SIDE-EFFECT WARNING:"
```

---

## 7. Path Convention

```
app/modules/{module}/
  domain/           entities.py · value_objects.py · enums.py
                    events.py · exceptions.py · __init__.py
  application/      interfaces.py · use_cases.py · mappers.py
                    exceptions.py · utils.py · __init__.py
  infrastructure/   models.py · repositories.py · caches.py
                    services.py · __init__.py
  presentation/     routers.py · schemas.py · docs.py
                    dependencies.py · __init__.py
  __init__.py

db/migrations/      V001__create_{module}.sql
                    V002__seed_{module}.sql
                    V003__rollback_{module}.sql

tests/              conftest.py
                    unit/test_{module}.py
                    unit/test_{module}_use_cases.py
                    integration/test_{module}_repository.py
                    property/test_{module}_invariants.py
                    manual/manual_test_{module}.md

docs/               README_{module}.md
                    API_{module}.md

app/routes.py       (edit)
migrations/env.py   (edit)
```

---

## 8. ถาม-ตอบ เมื่อข้อมูลไม่พอ

```markdown
✅ ถาม 1 คำถาม กระชับ เฉพาะจุดที่ขาด
❌ อย่าถามหลายคำถาม
❌ อย่าเดาแล้วสร้างให้เลย
❌ อย่าเดา layer / prefix / dependencies

ตัวอย่าง:
"ข้อมูลไม่พอ: module นี้อยู่ layer ไหน (0-7)? และ prefix 3 ตัวคืออะไร?"
```

---

## 9. Definition of "Complete"

งานจะถือว่า **complete** ก็ต่อเมื่อ:

- [ ] โค้ดเต็ม ไม่มี `...`
- [ ] Type hints ครบ
- [ ] Error handling ตาม layer (3/2/never)
- [ ] Tests ครบ pyramid
- [ ] Coverage ตามเกต
- [ ] SQL V001 + V002 + V003
- [ ] Routing 2 ไฟล์
- [ ] Docs README + Swagger + Postman
- [ ] ไม่มี PII / print / float
- [ ] Report ตาม template
```

---

## 📄 `reference/02-master-structure.md`

```markdown
# 02 — Master Structure (23 ส่วนบังคับ)

> ทุก TEMPLATE A ต้องมี 23 ส่วนนี้ **เรียงตามลำดับ** · Templates B–G ใช้ subset

---

## โครง 23 ส่วน

```
01. รายละเอียด (Details)
02. หลักการทำงาน (Concept / Behavior Spec)
03. ข้อกำหนด (Requirements)
04. เป้าหมาย (Target)
05. ขอบเขต (Scope)
06. โครงสร้าง Folder + ไฟล์
07. Workflow การทำงาน
08. Affected Areas
09. รายการกระบวนการทำงาน
10. Performance Considerations
11. TDD Plan
12. ข้อห้าม (Prohibitions)
13. ข้อควรระวัง (Cautions)
14. ข้อดี (Pros)
15. ข้อเสีย (Cons)
16. Checklist การทดสอบ
17. SQL & Migration Plan
18. Routing Registration
19. Documentation Package
20. Swagger / OpenAPI Spec
21. Postman Collection
22. สรุป (Summary)
23. รายงานสรุปผลการดำเนินการ
```

---

## รายละเอียดแต่ละส่วน

### 01. รายละเอียด (Details)

ตาราง metadata มาตรฐาน:

| หัวข้อ | ค่า |
|---|---|
| Task Type | `CREATE_NEW` |
| Module | `[module]` |
| Layer | `[0-7]` |
| Stack | `[FastAPI / Django / Both]` |
| Priority | `🔴 / 🟠 / 🟡` |
| Phase | `[1-6]` |
| Prefix | `[3 chars]` |
| Dependencies | `[module list]` |
| Tables | `tenant_{tid}.[table]` |
| Endpoints | `/api/v1/[module]/` |
| Events | `[ModuleCreated, ...]` |

### 02. หลักการทำงาน (Concept / Behavior Spec)

- อธิบาย business behavior
- State machine (ถ้ามี)
- Invariants ที่ต้องคงอยู่
- Domain rules

### 03. ข้อกำหนด (Requirements)

- Functional requirements (FR)
- Non-functional requirements (NFR)
- Constraints

### 04. เป้าหมาย (Target)

- เป้าหมายระยะสั้น (feature complete)
- เป้าหมายระยะยาว (extensibility)

### 05. ขอบเขต (Scope)

- **In scope**: อะไรอยู่ใน module นี้
- **Out of scope**: อะไรไม่อยู่ (เพื่อกัน scope creep)

### 06. โครงสร้าง Folder + ไฟล์

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
└── __init__.py

db/migrations/             (3 ไฟล์)
tests/                     (5 ไฟล์)
docs/                      (2 ไฟล์)
app/routes.py              (แก้)
migrations/env.py          (แก้)
```

### 07. Workflow การทำงาน

Mermaid sequence diagram — ดูตัวอย่างเต็มใน [`03-templates-a-g.md`](03-templates-a-g.md)

### 08. Affected Areas

| ไฟล์ | Action | เหตุผล |
|---|---|---|
| `app/routes.py` | edit | register router |
| `migrations/env.py` | edit | register model |
| `app/modules/{module}/**` | new | module ใหม่ |
| `db/migrations/*` | new | 3 ไฟล์ |
| `tests/**` | new | 5 ไฟล์ |
| `docs/**` | new | 2 ไฟล์ |

### 09. รายการกระบวนการทำงาน

ลำดับขั้นตอน:
1. Client → Router (validate Pydantic)
2. Router → UseCase
3. UseCase → Idempotency (check lock)
4. UseCase → Repository (save)
5. Repository → DB (flush)
6. UseCase → Repository (read-back verify)
7. UseCase → Cache (invalidate)
8. UseCase → Idempotency (complete)
9. UseCase → EventBus (publish)
10. Router → Client (201)

### 10. Performance Considerations

| ประเด็น | แนวทาง |
|---|---|
| N+1 query | ใช้ `selectinload` / `joinedload` |
| Index | partial index + composite |
| Cache | Redis TTL 300s + invalidate on write |
| Pagination | keyset (cursor) ถ้า > 10k rows |
| Batch | bulk insert ผ่าน `insert().values([...])` |
| Connection pool | `pool_size=20, max_overflow=10` |

### 11. TDD Plan

```
RED → GREEN → REFACTOR

1. เขียน failing test ก่อน (unit)
2. เขียน minimal code ให้ผ่าน
3. Refactor โดย test ยังเขียว
4. เพิ่ม integration test (RLS)
5. เพิ่ม property test (invariants)
```

### 12. ข้อห้าม (Prohibitions)

```markdown
❌ import framework ใน domain/
❌ commit() ใน Repository
❌ raise ใน Cache
❌ float กับเงิน/สต็อก
❌ hardcode secret
❌ UPDATE/DELETE ใน audit/event store
❌ query ข้าม tenant
❌ ลบ migration V001-V003 ที่ commit แล้ว
❌ CREATE TABLE IF NOT EXISTS ใน migration หลัก
❌ print() — ใช้ structlog
❌ mock สิ่งที่ตัวเองเป็นเจ้าของ (mock เฉพาะ port)
❌ log PII / token / password
❌ return stacktrace ให้ client
```

### 13. ข้อควรระวัง (Cautions)

- Race condition บน unique code → ใช้ `ON CONFLICT`
- Timezone: เก็บ `TIMESTAMPTZ` เท่านั้น
- RLS: ต้อง `set_config` ก่อน query ทุกครั้ง
- Decimal precision: quantize ก่อน persist
- Cache stampede: ใช้ single-flight / lock
- Kafka: at-least-once → consumer ต้อง idempotent
- Async session: 1 request = 1 session
- Lazy load: ใช้ eager load เสมอใน async

### 14. ข้อดี (Pros)

- Testable (domain ไม่ผูก framework)
- Framework-agnostic
- Multi-tenant by design
- Audit-ready
- Type-safe ทั้ง stack

### 15. ข้อเสีย (Cons)

- โครงเยอะ (learning curve)
- Boilerplate สูง
- Over-engineering สำหรับ CRUD ง่าย ๆ
- ต้องเขียน test เยอะ
- Migration discipline สูง

### 16. Checklist การทดสอบ

```markdown
- [ ] Unit tests ≥ 8 ผ่าน
- [ ] Integration tests ≥ 4 ผ่าน (RLS verified)
- [ ] Property tests ≥ 3 × 100 iter
- [ ] Manual test 8 scenarios
- [ ] Coverage ≥ 85%
- [ ] Load test (ถ้ามี SLO)
- [ ] Security scan (bandit)
- [ ] Type check (mypy strict)
- [ ] Lint (ruff)
```

### 17. SQL & Migration Plan

→ ดู [`04-sql-migration.md`](04-sql-migration.md)

### 18. Routing Registration

→ ดู [`05-routing.md`](05-routing.md)

### 19. Documentation Package

→ ดู [`06-docs-postman.md`](06-docs-postman.md)

### 20. Swagger / OpenAPI Spec

→ ดู [`06-docs-postman.md`](06-docs-postman.md)

### 21. Postman Collection

→ ดู [`06-docs-postman.md`](06-docs-postman.md)

### 22. สรุป (Summary)

| รายการ | จำนวน |
|---|---|
| Python files | 23 |
| SQL files | 3 |
| Test files | 5 |
| Docs files | 2 |
| Routing (แก้) | 2 |
| **รวม** | **35** |

### 23. รายงานสรุปผลการดำเนินการ

→ ดู Report A ใน [`07-reports.md`](07-reports.md)

---

## ตัวอย่างสมบูรณ์

ดู [`examples/inventory/`](../examples/inventory/) — module ตัวอย่างเต็มที่ใช้ 23 ส่วนนี้
```

---

## 📄 `reference/03-templates-a-g.md`

```markdown
# 03 — Task Templates A–G

> 7 ประเภทงาน · เลือกใช้ตาม task type · ทุก template ใช้ Global Constraints ร่วม

---

## 📋 สารบัญ

| Template | ชื่อ | ใช้เมื่อ |
|---|---|---|
| [A](#template-a) | CREATE_NEW | สร้าง module ใหม่ |
| [B](#template-b) | REFACTOR | ปรับปรุงโค้ดเดิม |
| [C](#template-c) | EXTEND | เพิ่ม feature |
| [D](#template-d) | BUGFIX | แก้ bug |
| [E](#template-e) | SECURITY_AUDIT | ตรวจความปลอดภัย |
| [F](#template-f) | PERF_TEST | ทดสอบประสิทธิภาพ |
| [G](#template-g) | DOCUMENTATION | เขียน docs |

---

## 🎯 TEMPLATE A: CREATE_NEW {#template-a}

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

### 02. หลักการทำงาน

X คือ aggregate root ที่มี invariants:
- `amount >= 0`
- `code` unique ต่อ tenant
- state transitions: ACTIVE ↔ INACTIVE → ARCHIVED (terminal)
- soft delete: `deleted_at` set ไม่ลบจริง

### 03. ข้อกำหนด

**FR:**
- สร้าง/อ่าน/แก้/ลบ (soft)
- ระบุ tenant
- audit log
- emit events

**NFR:**
- p95 < 200ms
- RLS enforced
- Idempotency
- Coverage ≥ 85%

### 04. เป้าหมาย

Deliver: module production-ready พร้อม deploy

### 05. ขอบเขต

**In:** CRUD + search + events
**Out:** integration กับระบบอื่น (phase ถัดไป)

### 06. โครงสร้าง Folder + ไฟล์

```
app/modules/{module}/
├── domain/
│   ├── __init__.py
│   ├── entities.py
│   ├── value_objects.py
│   ├── enums.py
│   ├── events.py
│   └── exceptions.py
├── application/
│   ├── __init__.py
│   ├── interfaces.py
│   ├── use_cases.py
│   ├── mappers.py
│   ├── exceptions.py
│   └── utils.py
├── infrastructure/
│   ├── __init__.py
│   ├── models.py
│   ├── repositories.py
│   ├── caches.py
│   └── services.py
├── presentation/
│   ├── __init__.py
│   ├── routers.py
│   ├── schemas.py
│   ├── docs.py
│   └── dependencies.py
└── __init__.py

db/migrations/
├── V001__create_{module}.sql
├── V002__seed_{module}.sql
└── V003__rollback_{module}.sql

tests/
├── conftest.py
├── unit/test_{module}.py
├── unit/test_{module}_use_cases.py
├── integration/test_{module}_repository.py
├── property/test_{module}_invariants.py
└── manual/manual_test_{module}.md

docs/
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

### 08. Affected Areas

| ไฟล์ | Action |
|---|---|
| `app/modules/{module}/**` | new (23 ไฟล์) |
| `db/migrations/V00{1,2,3}__*.sql` | new (3 ไฟล์) |
| `tests/**` | new (5 ไฟล์) |
| `docs/{README,API}_{module}.md` | new (2 ไฟล์) |
| `app/routes.py` | edit (เพิ่ม include_router) |
| `migrations/env.py` | edit (เพิ่ม import model) |

### 09. รายการกระบวนการทำงาน

ตาม sequence ใน §07 — 10 ขั้น

### 10. Performance Considerations

| ประเด็น | แนวทาง |
|---|---|
| Read 1 entity | PK lookup + RLS → < 5ms |
| List 100 | partial index → < 50ms |
| Create | 1 INSERT + 1 SELECT → < 30ms |
| Cache hit | Redis → < 3ms |

### 11. TDD Plan

1. **RED**: เขียน test entities + use case (mock ports) → fail
2. **GREEN**: implement domain + application → pass
3. **REFACTOR**: extract VO, split use cases
4. **RED**: integration test (real DB + RLS) → fail
5. **GREEN**: implement infrastructure → pass
6. **RED**: property test → fail
7. **GREEN**: แก้ invariant → pass
8. **Manual**: 8 scenarios

### 12. ข้อห้าม

```markdown
❌ import framework ใน domain/
❌ commit() ใน Repository (ใช้ flush())
❌ raise ใน Cache (never-raise)
❌ float กับเงิน/สต็อก
❌ hardcode secret
❌ UPDATE/DELETE ใน audit/event store
❌ query ข้าม tenant
❌ ลบ migration V001-V003 ที่ commit แล้ว
❌ CREATE TABLE IF NOT EXISTS ใน migration หลัก
❌ print() — ใช้ structlog
❌ mock สิ่งที่ตัวเองเป็นเจ้าของ
```

### 13. ข้อควรระวัง

- Race บน unique code → `ON CONFLICT`
- Timezone → `TIMESTAMPTZ` เท่านั้น
- RLS → `set_config` ก่อน query
- Decimal → quantize `0.01`
- Cache stampede → single-flight
- Kafka at-least-once → idempotent consumer

### 14. ข้อดี

- Testable · Framework-agnostic · Multi-tenant · Audit-ready · Type-safe

### 15. ข้อเสีย

- Boilerplate สูง · Learning curve · Over-engineer สำหรับ CRUD ง่าย

### 16. Checklist การทดสอบ

```markdown
- [ ] Unit ≥ 8 pass
- [ ] Integration ≥ 4 pass (RLS verified)
- [ ] Property ≥ 3 × 100 iter
- [ ] Manual 8 scenarios
- [ ] Coverage ≥ 85%
- [ ] /docs เห็น tag ใหม่
- [ ] Postman collection ผ่าน
```

### 17. SQL & Migration Plan

→ [`04-sql-migration.md`](04-sql-migration.md)

### 18. Routing Registration

→ [`05-routing.md`](05-routing.md)

### 19-21. Docs / Swagger / Postman

→ [`06-docs-postman.md`](06-docs-postman.md)

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

→ [`07-reports.md`](07-reports.md#report-a)

---

## 🎯 TEMPLATE B: REFACTOR {#template-b}

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `REFACTOR` |
| **Target Files** | `[list]` |
| **Breaking Change** | `Yes / No` |
| **Migration Impact** | `None / New migration needed` |

### Workflow

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

### ข้อห้าม

```markdown
❌ เปลี่ยน public signature
❌ แตะ layer อื่น
❌ refactor นอกจุดที่ระบุ
❌ เพิ่ม feature ใหม่
❌ ลบ tests เดิม
❌ แก้ migration V001-V003 ที่ commit แล้ว
❌ ลด coverage
```

### Output

- ก่อน/หลัง ของแต่ละไฟล์ที่แก้
- Diff test (ก่อน/หลัง)
- Coverage report (ต้องไม่ลด)

---

## 🎯 TEMPLATE C: EXTEND {#template-c}

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `EXTEND` |
| **Module** | `[module]` |
| **Feature** | `[feature ใหม่]` |
| **New Endpoints** | `[list]` |
| **New Migration** | `V00X__{action}.sql` |

### Diff Plan

| ไฟล์ | Action | รายละเอียด |
|---|---|---|
| `domain/entities.py` | `+method` | `bulk_create()` |
| `application/use_cases.py` | `+class` | `BulkCreateUseCase` |
| `presentation/routers.py` | `+endpoint` | `POST /bulk/` |
| `presentation/schemas.py` | `+schema` | `BulkCreateRequest` |
| `tests/unit/test_{module}.py` | `+test` | `test_bulk_*` |
| `db/migrations/V004__add_bulk.sql` | `new` | index + column |

### Backward Compatibility

- ห้าม break existing endpoints
- Version ใหม่ใช้ `/v2/` (ถ้าจำเป็น)
- Deprecation notice ล่วงหน้า ≥ 1 minor

---

## 🎯 TEMPLATE D: BUGFIX {#template-d}

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `BUGFIX` |
| **Severity** | `🔴 Critical / 🟡 Major / 🟢 Minor` |
| **Env** | `dev / staging / prod` |
| **Migration Impact** | `None / New migration` |

### Bug Report (input)

```markdown
Symptom: [อาการ]
Steps: 1. ... 2. ...
Expected: [สิ่งที่ควรเกิด]
Actual: [สิ่งที่เกิด]
Stacktrace: [paste]
```

### STEP 1 — Hypothesis (รออนุมัติ)

```markdown
1. Root Cause: [ไฟล์:บรรทัด + คำอธิบาย]
2. Fix Strategy: hotfix / proper fix / refactor
3. Migration needed? Yes/No
4. Regression Test: [ชื่อ test ที่จะเพิ่ม]
5. Estimated blast radius: [กี่ไฟล์ / กี่ endpoint]
```

### STEP 2 — Fix (หลังอนุมัติ)

1. เขียน failing regression test (RED)
2. แก้ minimal ที่ root cause
3. Test เขียว (GREEN)
4. รัน full suite
5. Verify coverage ไม่ลด
6. ลบ debug code

### Output — Report B

→ [`07-reports.md`](07-reports.md#report-b)

---

## 🎯 TEMPLATE E: SECURITY_AUDIT {#template-e}

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `SECURITY_AUDIT` |
| **Standard** | `OWASP Top 10 / ASVS L2` |
| **Mode** | `Read-only / Audit+Fix` |

### Output — ตารางเท่านั้น

| # | Risk | Layer | File:Line | Severity | CWE | แนะนำแก้ | Auto-fix |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | 🔴 | CWE-XXX | ... | ✅ |

### Security Checklist

```markdown
#### A. Authentication & Authorization
- [ ] Nested JWT (JWS + JWE)
- [ ] Refresh token rotation
- [ ] RBAC ทุก endpoint
- [ ] Token expiry ≤ 15 นาที

#### B. Input Validation
- [ ] Pydantic v2 strict mode
- [ ] SQL injection (ORM parameterized)
- [ ] Mass assignment (whitelist fields)
- [ ] File upload: type + size + scan

#### C. Data Protection
- [ ] Encryption at rest (AES-256)
- [ ] TLS in transit (min 1.2)
- [ ] PII masking ใน logs
- [ ] Secret management (vault / env)

#### D. Multi-tenancy
- [ ] tenant_id ทุก query
- [ ] RLS policy ทุกตาราง
- [ ] Cross-tenant leakage test
- [ ] Tenant isolation ใน cache

#### E. API Security
- [ ] Rate limiting (per IP + per user)
- [ ] CORS policy (whitelist)
- [ ] CSRF (BFF pattern)
- [ ] Idempotency key
- [ ] Request size limit

#### F. SQL Security
- [ ] RLS enabled + forced
- [ ] FK ON DELETE ถูกต้อง
- [ ] Search_path ปลอดภัย
- [ ] Least privilege DB user
- [ ] No dynamic SQL ที่ไม่ parameterize

#### G. Dependency
- [ ] pip-audit ผ่าน
- [ ] bandit ผ่าน
- [ ] Dependencies up-to-date
```

### Output — Report C

→ [`07-reports.md`](07-reports.md#report-c)

---

## 🎯 TEMPLATE F: PERF_TEST {#template-f}

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `PERF_TEST` |
| **SLO** | `p95 < X ms, > Y rps` |
| **Tool** | `locust / k6 / pytest-benchmark` |

### Metrics

| Metric | Tool | Target | Before | After |
|---|---|---|---|---|
| p50 | pytest-benchmark | < 50ms | ? | ? |
| p95 | locust | < 200ms | ? | ? |
| p99 | locust | < 500ms | ? | ? |
| RPS | locust | > 100 | ? | ? |
| DB queries/req | SQLAlchemy events | < 5 | ? | ? |
| Seq scans | EXPLAIN | 0 | ? | ? |
| Cache hit | Redis INFO | > 80% | ? | ? |
| Memory | memray | < 200MB | ? | ? |

### Workflow

1. Baseline: รัน load test กับโค้ดปัจจุบัน
2. Profile: py-spy / scalene / EXPLAIN ANALYZE
3. Optimize: แก้ bottleneck
4. Re-test: เทียบผล
5. Report D

### Output — Report D

→ [`07-reports.md`](07-reports.md#report-d)

---

## 🎯 TEMPLATE G: DOCUMENTATION {#template-g}

| หัวข้อ | ค่า |
|---|---|
| **Task Type** | `DOCUMENTATION` |
| **Doc Type** | `README / API / ARCH / RUNBOOK / ONBOARDING / ADR` |
| **Audience** | `Dev / DevOps / PM / End-user` |

### Doc Structure

```
docs/
├── README_{module}.md          # overview + setup
├── API_{module}.md             # endpoint reference
├── ARCH_{module}.md            # design + diagram
├── RUNBOOK_{module}.md         # ops procedures
├── ONBOARDING_{module}.md      # new dev guide
├── postman/{module}.postman_collection.json
└── adr/ADR-{nnn}-{title}.md    # decision records
```

### README Template

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

### ADR Template

```markdown
# ADR-{nnn}: {Title}

## Status
Proposed / Accepted / Deprecated / Superseded

## Context
[สถานการณ์ + ปัญหา]

## Decision
[สิ่งที่ตัดสินใจ]

## Consequences
**Positive:**
**Negative:**

## Alternatives Considered
```
```

---

## 📄 `reference/04-sql-migration.md`

```markdown
# 04 — SQL & Migration Block

> 3 ไฟล์ต่อ module · V001 create · V002 seed · V003 rollback · ทุกไฟล์มี `BEGIN/COMMIT`

---

## 📄 `V001__create_{module}.sql`

```sql
-- ═══════════════════════════════════════════════════════════════
-- V001__create_{module}.sql
-- Module: {module} | Prefix: {prefix} | Layer: {layer}
-- Description: สร้างตาราง + index + RLS policy + trigger
-- ═══════════════════════════════════════════════════════════════
BEGIN;

-- ─── Sequence ─────────────────────────────────────
CREATE SEQUENCE IF NOT EXISTS {prefix}_number_seq START 1;

-- ─── Table ────────────────────────────────────────
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

-- ─── Index ────────────────────────────────────────
CREATE INDEX ix_{module}_tenant_status
    ON tenant_{prefix}.{module}s(tenant_id, status)
    WHERE deleted_at IS NULL;
CREATE INDEX ix_{module}_code
    ON tenant_{prefix}.{module}s(code);
CREATE INDEX ix_{module}_created
    ON tenant_{prefix}.{module}s(created_at DESC);

-- ─── Trigger function (shared) ────────────────────
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

-- ─── Row Level Security ───────────────────────────
ALTER TABLE tenant_{prefix}.{module}s ENABLE ROW LEVEL SECURITY;

CREATE POLICY p_{module}_tenant ON tenant_{prefix}.{module}s
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
```

---

## 📄 `V002__seed_{module}.sql`

```sql
-- ═══════════════════════════════════════════════════════════════
-- V002__seed_{module}.sql
-- Description: seed ข้อมูลตั้งต้น (system default)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO tenant_{prefix}.{module}s (tenant_id, code, name, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'SYS-DEFAULT',
    'System Default',
    'ACTIVE'
)
ON CONFLICT (tenant_id, code) DO NOTHING;

COMMIT;
```

---

## 📄 `V003__rollback_{module}.sql`

```sql
-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_{module}.sql
-- Description: rollback ทั้งหมด (ใช้ตอน dev/staging เท่านั้น)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER  IF EXISTS trg_{module}_updated_at ON tenant_{prefix}.{module}s;
DROP POLICY   IF EXISTS p_{module}_tenant       ON tenant_{prefix}.{module}s;
DROP TABLE    IF EXISTS tenant_{prefix}.{module}s CASCADE;
DROP SEQUENCE IF EXISTS {prefix}_number_seq;

COMMIT;
```

---

## 📄 Update `migrations/env.py`

เพิ่ม import ที่ด้านบน:

```python
# TH: register model เพื่อให้ Alembic/SQLAlchemy metadata รู้จัก
# EN: register model so Alembic/SQLAlchemy metadata knows it
from app.modules.{module}.infrastructure.models import {Module}Model  # noqa: F401
```

---

## 🔍 SQL Debug Queries

```sql
-- ดู RLS policies ทั้งหมด
SELECT * FROM pg_policies WHERE tablename = '{module}s';

-- ตรวจว่า RLS เปิดจริง
SELECT relname, relrowsecurity, relforcerowsecurity
FROM pg_class
WHERE relname = '{module}s';

-- ดู tenant ปัจจุบันของ session
SHOW app.current_tenant;

-- ตรวจ index ที่ใช้ (ควรเห็น Index Scan ไม่ใช่ Seq Scan)
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM tenant_{prefix}.{module}s
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'::uuid
  AND status = 'ACTIVE'
  AND deleted_at IS NULL;

-- ดู size ของตาราง + index
SELECT pg_size_pretty(pg_total_relation_size('tenant_{prefix}.{module}s'));

-- ดู slow queries (ต้องเปิด pg_stat_statements)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query ILIKE '%{module}s%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## ✅ Migration Checklist

```markdown
- [ ] V001: ไม่ใช้ `IF NOT EXISTS` (ให้ error ถ้าซ้ำ)
- [ ] V001: BEGIN / COMMIT ครบ
- [ ] V001: คอลัมน์ครบ (id, tenant_id, version, created_at, updated_at, deleted_at)
- [ ] V001: CONSTRAINT ครบ (CHECK, UNIQUE, FK)
- [ ] V001: Partial index บน (tenant_id, status) WHERE deleted_at IS NULL
- [ ] V001: ENABLE ROW LEVEL SECURITY
- [ ] V001: CREATE POLICY ใช้ current_setting
- [ ] V001: BEFORE UPDATE trigger
- [ ] V002: ON CONFLICT DO NOTHING
- [ ] V003: DROP ... CASCADE
- [ ] env.py: import model
- [ ] รัน migration test: `alembic upgrade head` + `alembic downgrade -1`
```

---

## 🚫 ข้อห้าม

```markdown
❌ CREATE TABLE IF NOT EXISTS ใน migration หลัก
❌ COMMIT ซ้อนใน transaction
❌ แก้ V001-V003 ที่ commit แล้ว → สร้าง V004 ใหม่แทน
❌ DROP TABLE โดยไม่มี CASCADE ใน rollback
❌ ลืม ENABLE ROW LEVEL SECURITY
❌ Policy ที่ไม่มี tenant_id check
❌ FK ON DELETE ไม่ระบุ (default = NO ACTION)
❌ Index บนคอลัมน์ที่ cardinality ต่ำ (เช่น status เดี่ยว ๆ)
```

---

## 📊 Naming Convention

| ประเภท | Pattern | ตัวอย่าง |
|---|---|---|
| Table | `{module}s` | `invoices` |
| Schema | `tenant_{prefix}` | `tenant_inv` |
| Sequence | `{prefix}_number_seq` | `inv_number_seq` |
| Unique | `uq_{module}_{col}` | `uq_invoice_code` |
| Check | `ck_{module}_{col}` | `ck_invoice_amount` |
| Index | `ix_{module}_{cols}` | `ix_invoice_tenant_status` |
| Trigger | `trg_{module}_{action}` | `trg_invoice_updated_at` |
| Policy | `p_{module}_{scope}` | `p_invoice_tenant` |
| FK | `fk_{module}_{ref}` | `fk_invoice_tenant` |
```

---

## 📄 `reference/05-routing.md`

```markdown
# 05 — Routing Block

> ต้อง register 2 ไฟล์: `app/routes.py` (router) + `migrations/env.py` (model)

---

## 📄 `app/routes.py`

```python
"""
app/routes.py
TH: รวม router ทั้งหมดของระบบ แยกตาม layer
EN: Aggregate all routers by layer
"""
from fastapi import APIRouter

# ─── Layer 0: Core ────────────────────────────────
from app.modules.events.presentation.routers import router as events_router
from app.modules.audit.presentation.routers import router as audit_router
from app.modules.idempotency.presentation.routers import router as idem_router

# ─── Layer 1: Foundation ──────────────────────────
from app.modules.tenant.presentation.routers import router as tenant_router
from app.modules.user.presentation.routers import router as user_router
from app.modules.auth.presentation.routers import router as auth_router

# ─── Layer 2: Money ───────────────────────────────
from app.modules.invoice.presentation.routers import router as invoice_router
from app.modules.payment.presentation.routers import router as payment_router

# ─── Layer 3: Goods ───────────────────────────────
from app.modules.{module}.presentation.routers import router as {module}_router  # ← เพิ่ม

# ─── API v1 ───────────────────────────────────────
api_router = APIRouter(prefix="/api/v1")

# Layer 0
api_router.include_router(events_router)
api_router.include_router(audit_router)
api_router.include_router(idem_router)

# Layer 1
api_router.include_router(auth_router)
api_router.include_router(tenant_router)
api_router.include_router(user_router)

# Layer 2
api_router.include_router(invoice_router)
api_router.include_router(payment_router)

# Layer 3
api_router.include_router({module}_router)  # ← เพิ่ม

# ─── Root ─────────────────────────────────────────
from app.core.health import router as health_router

router = APIRouter()
router.include_router(api_router)
router.include_router(health_router)
```

---

## 📄 `presentation/routers.py`

```python
"""
app/modules/{module}/presentation/routers.py
TH: HTTP router ของ module {module}
EN: HTTP router for {module} module
"""
from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.modules.{module}.application.exceptions import (
    DuplicateCodeError,
    {Module}NotFoundError,
)
from app.modules.{module}.application.use_cases import (
    Create{Module}UseCase,
    Delete{Module}UseCase,
    Get{Module}UseCase,
    List{Module}UseCase,
    Update{Module}UseCase,
)
from app.modules.{module}.domain.exceptions import DomainError
from app.modules.{module}.presentation.dependencies import (
    get_create_uc,
    get_delete_uc,
    get_get_uc,
    get_list_uc,
    get_update_uc,
)
from app.modules.{module}.presentation.docs import (
    RESPONSE_CREATE_201,
    RESPONSE_ERROR_400,
    RESPONSE_ERROR_404,
    RESPONSE_ERROR_409,
    RESPONSE_ERROR_422,
)
from app.modules.{module}.presentation.schemas import (
    {Module}CreateRequest,
    {Module}ListResponse,
    {Module}Response,
    {Module}UpdateRequest,
)

log = structlog.get_logger()
router = APIRouter(prefix="/{module}", tags=["{Module}"])


# ═══════════════════════════════════════════════════════════════
# CREATE
# ═══════════════════════════════════════════════════════════════
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง {module}",
    operation_id="create_{module}",
    response_model={Module}Response,
    responses={
        201: RESPONSE_CREATE_201,
        400: RESPONSE_ERROR_400,
        409: RESPONSE_ERROR_409,
        422: RESPONSE_ERROR_422,
    },
)
async def create_{module}(
    payload: {Module}CreateRequest,
    idem_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
    uc: Annotated[Create{Module}UseCase, Depends(get_create_uc)],
) -> {Module}Response:
    """TH: สร้าง entity ใหม่ (idempotent) | EN: Create entity (idempotent)"""
    log.info("http.create.start", code=payload.code, idem=idem_key[:8])
    try:
        entity = await uc.execute(**payload.model_dump(), idempotency_key=idem_key)
    except DuplicateCodeError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return {Module}Response.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════════
@router.get(
    "/",
    summary="รายการ {module}",
    operation_id="list_{module}",
    response_model={Module}ListResponse,
)
async def list_{module}(
    uc: Annotated[List{Module}UseCase, Depends(get_list_uc)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> {Module}ListResponse:
    """TH: list + filter + paginate | EN: list with filter + pagination"""
    items, total = await uc.execute(status=status_filter, q=q, limit=limit, offset=offset)
    return {Module}ListResponse(
        items=[{Module}Response.model_validate(x, from_attributes=True) for x in items],
        total=total,
        limit=limit,
        offset=offset,
    )


# ═══════════════════════════════════════════════════════════════
# GET BY ID
# ═══════════════════════════════════════════════════════════════
@router.get(
    "/{entity_id}",
    summary="ดู {module} ตาม id",
    operation_id="get_{module}",
    response_model={Module}Response,
    responses={404: RESPONSE_ERROR_404},
)
async def get_{module}(
    entity_id: uuid.UUID,
    uc: Annotated[Get{Module}UseCase, Depends(get_get_uc)],
) -> {Module}Response:
    try:
        entity = await uc.execute(entity_id=entity_id)
    except {Module}NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return {Module}Response.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════════
@router.patch(
    "/{entity_id}",
    summary="แก้ไข {module}",
    operation_id="update_{module}",
    response_model={Module}Response,
    responses={404: RESPONSE_ERROR_404, 409: RESPONSE_ERROR_409},
)
async def update_{module}(
    entity_id: uuid.UUID,
    payload: {Module}UpdateRequest,
    uc: Annotated[Update{Module}UseCase, Depends(get_update_uc)],
) -> {Module}Response:
    try:
        entity = await uc.execute(entity_id=entity_id, **payload.model_dump(exclude_unset=True))
    except {Module}NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return {Module}Response.model_validate(entity, from_attributes=True)


# ═══════════════════════════════════════════════════════════════
# DELETE (soft)
# ═══════════════════════════════════════════════════════════════
@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ลบ {module} (soft delete)",
    operation_id="delete_{module}",
    responses={404: RESPONSE_ERROR_404},
)
async def delete_{module}(
    entity_id: uuid.UUID,
    uc: Annotated[Delete{Module}UseCase, Depends(get_delete_uc)],
) -> None:
    try:
        await uc.execute(entity_id=entity_id)
    except {Module}NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
```

---

## 📄 `presentation/dependencies.py`

```python
"""
app/modules/{module}/presentation/dependencies.py
TH: DI container ของ module
EN: DI container for module
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.context import RequestContext, get_context
from app.core.events import EventBus, get_event_bus
from app.core.idempotency import IdempotencyStore, get_idempotency_store
from app.modules.{module}.application.use_cases import (
    Create{Module}UseCase,
    Delete{Module}UseCase,
    Get{Module}UseCase,
    List{Module}UseCase,
    Update{Module}UseCase,
)
from app.modules.{module}.infrastructure.caches import Redis{Module}Cache
from app.modules.{module}.infrastructure.repositories import SQLAlchemy{Module}Repository


def get_{module}_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLAlchemy{Module}Repository:
    return SQLAlchemy{Module}Repository(session=session)


def get_{module}_cache() -> Redis{Module}Cache:
    return Redis{Module}Cache()


# ─── Use Case factories ───────────────────────────
async def get_create_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    cache: Annotated[Redis{Module}Cache, Depends(get_{module}_cache)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    idem: Annotated[IdempotencyStore, Depends(get_idempotency_store)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> Create{Module}UseCase:
    return Create{Module}UseCase(repo=repo, cache=cache, bus=bus, idem=idem, ctx=ctx)


async def get_get_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    cache: Annotated[Redis{Module}Cache, Depends(get_{module}_cache)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> Get{Module}UseCase:
    return Get{Module}UseCase(repo=repo, cache=cache, ctx=ctx)


async def get_list_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> List{Module}UseCase:
    return List{Module}UseCase(repo=repo, ctx=ctx)


async def get_update_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    cache: Annotated[Redis{Module}Cache, Depends(get_{module}_cache)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> Update{Module}UseCase:
    return Update{Module}UseCase(repo=repo, cache=cache, bus=bus, ctx=ctx)


async def get_delete_uc(
    repo: Annotated[SQLAlchemy{Module}Repository, Depends(get_{module}_repo)],
    cache: Annotated[Redis{Module}Cache, Depends(get_{module}_cache)],
    bus: Annotated[EventBus, Depends(get_event_bus)],
    ctx: Annotated[RequestContext, Depends(get_context)],
) -> Delete{Module}UseCase:
    return Delete{Module}UseCase(repo=repo, cache=cache, bus=bus, ctx=ctx)
```

---

## ✅ Routing Checklist

```markdown
- [ ] import router ใน `app/routes.py`
- [ ] `include_router({module}_router)` อยู่ layer ถูก
- [ ] prefix ไม่ซ้ำกับ module อื่น
- [ ] tags ถูกต้อง (แสดงใน Swagger)
- [ ] เปิด `http://localhost:8000/docs` → เห็น endpoint ใหม่
- [ ] เปิด `http://localhost:8000/openapi.json` → เห็น schema
- [ ] `migrations/env.py` import model แล้ว
- [ ] ทดสอบ `GET /api/v1/{module}/` → 200
```

---

## 🚫 ข้อห้าม

```markdown
❌ prefix ซ้ำกับ module อื่น
❌ ใส่ router ผิด layer
❌ ลืม import model ใน env.py
❌ tag ซ้ำ / สะกดผิด
❌ business logic ใน router
❌ return ORM object ตรง ๆ (ต้องผ่าน schema)
❌ ใช้ Depends ที่ไม่ cache (ควรใช้ cache=True default)
```
```

---

## 📄 `reference/06-docs-postman.md`

```markdown
# 06 — Documentation / Swagger / Postman Block

> 4 ระบบ: README · OpenAPI · Swagger metadata · Postman collection

---

## 📄 `docs/README_{module}.md`

```markdown
# Module: {module}

> Layer: {layer} · Prefix: `{prefix}` · Version: 1.0.0

## Purpose

[อธิบายวัตถุประสงค์ของ module ใน 2-3 บรรทัด]

## Architecture

```mermaid
graph TD
    R[Router] --> UC[UseCase]
    UC --> D[Domain]
    UC --> Repo[Repository]
    UC --> Cache[Cache]
    UC --> Bus[EventBus]
    Repo --> DB[(PostgreSQL)]
    Cache --> Redis[(Redis)]
    Bus --> Kafka[(Kafka)]
```

## Dependencies

| Module | Version | เหตุผล |
|---|---|---|
| tenant | ≥ 1.0 | multi-tenant |
| user | ≥ 1.0 | auth context |
| audit | ≥ 1.0 | event log |

## Database Schema

```sql
CREATE TABLE tenant_{prefix}.{module}s (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    code VARCHAR(50) NOT NULL,
    ...
);
```

## API Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/{module}/` | สร้างใหม่ | ✅ |
| GET | `/api/v1/{module}/` | list | ✅ |
| GET | `/api/v1/{module}/{id}` | ดูตาม id | ✅ |
| PATCH | `/api/v1/{module}/{id}` | แก้ไข | ✅ |
| DELETE | `/api/v1/{module}/{id}` | soft delete | ✅ |

## Permissions

| Role | Create | Read | Update | Delete |
|---|---|---|---|---|
| admin | ✅ | ✅ | ✅ | ✅ |
| manager | ✅ | ✅ | ✅ | ❌ |
| staff | ✅ | ✅ | ❌ | ❌ |
| viewer | ❌ | ✅ | ❌ | ❌ |

## Domain Events

| Event | Trigger | Payload |
|---|---|---|
| `{Module}Created` | after create | id, code, tenant_id |
| `{Module}Updated` | after update | id, changes |
| `{Module}Deleted` | after soft delete | id, deleted_at |

## Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
KAFKA_BOOTSTRAP=localhost:9092
```

## Setup

```bash
# migrate
alembic upgrade head

# run
uvicorn app.main:app --reload
```

## Testing

```bash
pytest tests/unit/test_{module}.py -v
pytest tests/integration/test_{module}_repository.py -v
pytest --cov=app.modules.{module} --cov-fail-under=85
```

## Usage Example

```bash
# create
curl -X POST http://localhost:8000/api/v1/{module}/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"code":"X-001","name":"Sample","amount":"100.00"}'

# response
{
  "id": "01H...",
  "code": "X-001",
  "name": "Sample",
  "amount": "100.00",
  "status": "ACTIVE",
  "version": 1,
  "created_at": "2025-01-15T10:00:00Z"
}
```

## Known Limitations

- ไม่รองรับ bulk > 1000 records ต่อ request
- Cache TTL = 300s
- ไม่มี WebSocket

## Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2025-01-15 | initial release |
```

---

## 📄 `docs/API_{module}.md`

```markdown
# API Reference — {Module}

Base URL: `{BASE_URL}/api/v1/{module}`

## Authentication

ทุก request ต้องมี:
```
Authorization: Bearer <JWT>
Idempotency-Key: <uuid>   # เฉพาะ POST/PATCH/DELETE
```

## Endpoints

### POST / — สร้างใหม่

**Request:**
```json
{
  "code": "X-001",
  "name": "Sample",
  "amount": "100.00",
  "metadata": {}
}
```

**Response 201:**
```json
{
  "id": "01H...",
  "code": "X-001",
  ...
}
```

**Errors:**

| Status | Code | Description |
|---|---|---|
| 400 | `DOMAIN_ERROR` | amount < 0 |
| 409 | `DUPLICATE_CODE` | code ซ้ำใน tenant |
| 422 | `VALIDATION_ERROR` | schema ไม่ถูก |
| 422 | `IDEMPOTENCY_MISMATCH` | key เดิม payload ต่าง |

### GET / — List

**Query params:**

| Param | Type | Default | Description |
|---|---|---|---|
| status | string | — | `ACTIVE` / `INACTIVE` / `ARCHIVED` |
| q | string | — | search code/name |
| limit | int | 20 | max 100 |
| offset | int | 0 | — |

**Response 200:**
```json
{
  "items": [...],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### GET /{id} — Get by ID

**Response 404** ถ้าไม่พบ (หรือ tenant อื่น)

### PATCH /{id} — Update

**Request:** (partial)
```json
{
  "name": "New Name",
  "amount": "200.00"
}
```

**Optimistic lock:**
```json
{
  "version": 1,
  "name": "New Name"
}
```
ถ้า version ไม่ตรง → `409 VERSION_CONFLICT`

### DELETE /{id} — Soft Delete

**Response 204** — ตั้ง `deleted_at`

---

## Rate Limits

| Endpoint | Limit |
|---|---|
| POST | 100 / min / tenant |
| GET | 1000 / min / tenant |
| DELETE | 50 / min / tenant |

## Error Format

```json
{
  "detail": "message",
  "code": "ERROR_CODE",
  "trace_id": "abc123..."
}
```
```

---

## 📄 `presentation/docs.py`

```python
"""
app/modules/{module}/presentation/docs.py
TH: OpenAPI response metadata
EN: OpenAPI response metadata
"""
RESPONSE_CREATE_201 = {
    "description": "สร้างสำเร็จ",
    "content": {
        "application/json": {
            "example": {
                "id": "01HXYZ...",
                "code": "X-001",
                "name": "Sample",
                "amount": "100.00",
                "status": "ACTIVE",
                "version": 1,
                "created_at": "2025-01-15T10:00:00Z",
            }
        }
    },
}

RESPONSE_ERROR_400 = {
    "description": "Domain error",
    "content": {
        "application/json": {
            "example": {"detail": "amount must be >= 0", "code": "DOMAIN_ERROR"}
        }
    },
}

RESPONSE_ERROR_404 = {
    "description": "ไม่พบ entity",
    "content": {
        "application/json": {
            "example": {"detail": "entity not found", "code": "NOT_FOUND"}
        }
    },
}

RESPONSE_ERROR_409 = {
    "description": "Conflict (duplicate / version)",
    "content": {
        "application/json": {
            "example": {"detail": "code X-001 already exists", "code": "DUPLICATE_CODE"}
        }
    },
}

RESPONSE_ERROR_422 = {
    "description": "Validation error",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {"loc": ["body", "amount"], "msg": "invalid", "type": "value_error"}
                ]
            }
        }
    },
}
```

---

## 📄 Swagger Metadata — Router

ดูตัวอย่างเต็มใน [`05-routing.md`](05-routing.md#-presentationrouterspy)

จุดสำคัญ:
- `operation_id` ไม่ซ้ำ
- `summary` ภาษาไทย
- `tags` PascalCase
- `responses` ระบุ 4xx ครบ
- `response_model` ชัดเจน

---

## 📄 Postman Collection

```json
{
  "info": {
    "name": "ERPIoT — {Module}",
    "_postman_id": "00000000-0000-0000-0000-{module}00000000",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    { "key": "base_url", "value": "http://localhost:8000" },
    { "key": "token", "value": "" },
    { "key": "tenant_id", "value": "00000000-0000-0000-0000-000000000001" }
  ],
  "auth": {
    "type": "bearer",
    "bearer": [{ "key": "token", "value": "{{token}}", "type": "string" }]
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/v1/auth/login",
            "body": {
              "mode": "raw",
              "raw": "{\"email\":\"admin@example.com\",\"password\":\"***\"}"
            }
          }
        }
      ]
    },
    {
      "name": "{Module} — Create",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Idempotency-Key", "value": "{{$guid}}" },
          { "key": "Content-Type", "value": "application/json" }
        ],
        "url": "{{base_url}}/api/v1/{module}/",
        "body": {
          "mode": "raw",
          "raw": "{\"code\":\"X-001\",\"name\":\"Sample\",\"amount\":\"100.00\"}"
        }
      }
    },
    {
      "name": "{Module} — List",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/{module}/?limit=20&offset=0"
      }
    },
    {
      "name": "{Module} — Get",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/{module}/{{entity_id}}"
      }
    },
    {
      "name": "{Module} — Update",
      "request": {
        "method": "PATCH",
        "header": [
          { "key": "Idempotency-Key", "value": "{{$guid}}" }
        ],
        "url": "{{base_url}}/api/v1/{module}/{{entity_id}}",
        "body": {
          "mode": "raw",
          "raw": "{\"name\":\"Updated\"}"
        }
      }
    },
    {
      "name": "{Module} — Delete",
      "request": {
        "method": "DELETE",
        "header": [
          { "key": "Idempotency-Key", "value": "{{$guid}}" }
        ],
        "url": "{{base_url}}/api/v1/{module}/{{entity_id}}"
      }
    },
    {
      "name": "Health",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    }
  ]
}
```

---

## ✅ Docs Checklist

```markdown
- [ ] README_{module}.md ครบ 13 หัวข้อ
- [ ] API_{module}.md มี request/response ตัวอย่าง
- [ ] Swagger metadata ครบ (operation_id, responses)
- [ ] Postman collection import ได้ ไม่มี error
- [ ] /docs แสดง tag + endpoint
- [ ] /openapi.json valid (ตรวจผ่าน swagger editor)
- [ ] ทุก error code มี description
```
```

---

## 📄 `reference/07-reports.md`

```markdown
# 07 — Report Templates

> 4 report: A (Completion) · B (Bugfix) · C (Security) · D (Performance)

---

## 📊 Report A: Task Completion {#report-a}

```markdown
# 📋 Task Report — {TaskType} / {Module}

**Date:** YYYY-MM-DD · **Duration:** Xh · **Engineer:** [name]

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

## 📁 ไฟล์ที่สร้าง/แก้ไข

| Path | Action | Lines |
|---|---|---|
| `app/modules/{module}/domain/entities.py` | new | 120 |
| `app/modules/{module}/application/use_cases.py` | new | 250 |
| `app/routes.py` | edit | +3 |
| `migrations/env.py` | edit | +2 |
| ... | ... | ... |

## 🧪 Test Result

```
pytest --cov=app.modules.{module}
==================== 42 passed in 3.2s ====================
TOTAL coverage: 91%
```

## 📊 Coverage per Layer

| Layer | Coverage | Target | Pass |
|---|---|---|---|
| domain/ | 97% | 95% | ✅ |
| application/ | 92% | 90% | ✅ |
| infrastructure/ | 83% | 80% | ✅ |
| presentation/ | 74% | 70% | ✅ |
| **รวม** | **91%** | **85%** | ✅ |

## 🚀 Deploy Notes

- Migration: `alembic upgrade head`
- Env vars ใหม่: ไม่มี
- Breaking change: ไม่มี
- Rollback: `alembic downgrade -1`

## ⚠️ Known Issues

- Cache TTL 300s (ยังไม่ tune)
- ยังไม่มี bulk endpoint

## 📝 Follow-up Tasks

- [ ] เพิ่ม bulk create (V004)
- [ ] เพิ่ม Kafka consumer สำหรับ event
- [ ] Benchmark p95 < 100ms
```

---

## 📊 Report B: Bug Fix {#report-b}

```markdown
# 🐛 Bug Fix Report — {bug_id}

**Severity:** 🔴 Critical · **Env:** prod · **Reported:** YYYY-MM-DD

## 🔍 Root Cause

**File:** `app/modules/{module}/application/use_cases.py:142`
**Line:** `entity = await self.repo.save(entity)` — ไม่ได้ flush ก่อน return

**คำอธิบาย:**
Use case return entity ที่ยังไม่ persist → caller พยายามใช้ id ที่ยังเป็น None → 500

## 🛠️ Fix

```diff
- entity = await self.repo.save(entity)
- return entity
+ entity = await self.repo.save(entity)
+ await self.session.flush()
+ fetched = await self.repo.get_by_id(entity.id)  # read-back verify
+ return fetched
```

## 🧪 Regression Test

เพิ่มใน `tests/unit/test_{module}_use_cases.py`:

```python
async def test_readback_verification(self, uc, repo) -> None:
    """TH: ต้องเรียก get_by_id หลัง save | EN: read-back verify"""
    await uc.execute(code="X", name="Y", amount=Decimal("1.00"), idempotency_key="k-1")
    repo.get_by_id.assert_awaited_once()
```

## 📊 Impact

- Users affected: ทั้งหมดที่ใช้ create
- Data loss: ไม่มี (transaction ทำงานถูก)
- Rollback: revert commit `abc123`

## ✅ Verification

- [x] Regression test pass
- [x] Full suite pass
- [x] Smoke test staging pass
- [x] Coverage ไม่ลด
- [x] Deploy production
- [x] Monitor 24h ไม่มี error
```

---

## 📊 Report C: Security Audit {#report-c}

```markdown
# 🔐 Security Audit Report — {scope}

**Date:** YYYY-MM-DD · **Standard:** OWASP Top 10 + ASVS L2
**Mode:** Read-only · **Auditor:** [name]

## Summary

| Severity | Count |
|---|---|
| 🔴 Critical | 0 |
| 🟠 High | 2 |
| 🟡 Medium | 5 |
| 🟢 Low | 3 |
| **รวม** | **10** |

## Findings

| # | Risk | Layer | File:Line | Severity | CWE | แนะนำแก้ | Auto-fix |
|---|---|---|---|---|---|---|---|
| 1 | Missing rate limit on POST | presentation | `routers.py:45` | 🟠 | CWE-770 | เพิ่ม slowapi | ✅ |
| 2 | Token ไม่ rotate | auth | `auth/service.py:88` | 🟠 | CWE-384 | ใช้ refresh rotation | ❌ |
| 3 | Log payload เต็ม (มี email) | application | `use_cases.py:120` | 🟡 | CWE-532 | mask_pii | ✅ |
| 4 | CORS allow * | main | `main.py:30` | 🟡 | CWE-942 | whitelist origin | ✅ |
| 5 | ไม่มี request size limit | main | `main.py:45` | 🟡 | CWE-400 | limit 1MB | ✅ |
| 6 | session cookie ไม่ secure | auth | `auth/router.py:15` | 🟡 | CWE-614 | secure=True | ✅ |
| 7 | ไม่ check tenant_id ใน cache key | infrastructure | `caches.py:22` | 🟡 | CWE-639 | include tenant | ✅ |
| 8 | Dependency เก่า (CVE-2024-XXXX) | deps | `pyproject.toml:18` | 🟢 | CWE-1035 | pip install -U | ✅ |
| 9 | ไม่มี CSP header | main | `main.py:20` | 🟢 | CWE-693 | add CSP | ✅ |
| 10 | Comment เปิดเผย internal path | domain | `entities.py:45` | 🟢 | CWE-200 | ลบ comment | ✅ |

## Checklist Result

```
A. Authentication & Authorization      8/10
B. Input Validation                   9/10
C. Data Protection                    8/10
D. Multi-tenancy                      7/10
E. API Security                       6/10
F. SQL Security                       9/10
G. Dependency                         8/10
```

## Recommendations (Priority Order)

1. **Fix now (High):** #1, #2
2. **Fix this sprint (Medium):** #3, #4, #5, #6, #7
3. **Backlog (Low):** #8, #9, #10
```

---

## 📊 Report D: Performance {#report-d}

```markdown
# ⚡ Performance Report — {target}

**Date:** YYYY-MM-DD · **Tool:** locust + pytest-benchmark
**SLO:** p95 < 200ms, > 100 rps

## Metrics

| Metric | Before | After | Δ | Target | ผ่าน? |
|---|---|---|---|---|---|
| p50 | 85ms | 32ms | -62% | < 50ms | ✅ |
| p95 | 420ms | 148ms | -65% | < 200ms | ✅ |
| p99 | 890ms | 310ms | -65% | < 500ms | ✅ |
| RPS | 45 | 210 | +367% | > 100 | ✅ |
| DB queries/req | 12 | 3 | -75% | < 5 | ✅ |
| Seq scans | 3 | 0 | -100% | 0 | ✅ |
| Cache hit | 0% | 87% | +87 | > 80% | ✅ |
| Memory | 480MB | 210MB | -56% | < 300MB | ✅ |

## Bottleneck Analysis

### Before

```
[████████████████████] DB Query (N+1)       55%
[██████] JSON serialize                     15%
[████] Validation                           12%
[███] Other                                 18%
```

### After

```
[████████] Cache hit                        40%
[████] DB Query (batch)                     20%
[███] JSON serialize                        15%
[███] Validation                            12%
[███] Other                                 13%
```

## Changes

1. **N+1 fix:** ใช้ `selectinload` → 12 queries → 3 queries
2. **Redis cache:** TTL 300s → hit rate 87%
3. **Partial index:** `(tenant_id, status) WHERE deleted_at IS NULL`
4. **Connection pool:** size 10 → 20
5. **Response streaming:** ลด memory 56%

## Load Test Config

```python
# locustfile.py
from locust import HttpUser, task, between

class {Module}User(HttpUser):
    wait_time = between(0.5, 2)

    @task(10)
    def list(self):
        self.client.get("/api/v1/{module}/?limit=20")

    @task(3)
    def create(self):
        self.client.post(
            "/api/v1/{module}/",
            json={"code": f"X-{uuid4()}", "name": "T", "amount": "1.00"},
            headers={"Idempotency-Key": str(uuid4())},
        )
```

**Run:**
```bash
locust -f locustfile.py --host=http://localhost:8000 \
       --users 200 --spawn-rate 20 --run-time 5m --headless
```

## Verification

- [x] Load test 5 นาที ไม่มี error
- [x] p95 < 200ms ตลอดช่วง
- [x] Memory leak: ไม่มี (คงที่ ~210MB)
- [x] DB CPU < 40%
- [x] Redis hit rate > 80%
```
```

---

## 📄 `reference/08-checklists.md`

```markdown
# 08 — Checklists

> 5 checklist: DoD · SQL · TDD · Pre-flight · Security

---

## ✅ Definition of Done (DoD)

### Code

```markdown
- [ ] Domain ไม่ import framework (FastAPI/SQLAlchemy/Pydantic)
- [ ] ใช้ `Decimal` ทั้งหมดที่เกี่ยวกับเงิน/สต็อก
- [ ] Repository ใช้ `flush()` ไม่มี `commit()`
- [ ] Cache never-raise (log + return None/False)
- [ ] Error handling 3-branch (UC) / 2-branch (Repo) / never (Cache)
- [ ] Type hints ครบทุก function (input + output)
- [ ] docstring 2 ภาษา (TH + EN) สั้น
- [ ] ไม่มี `print()` — ใช้ `structlog`
- [ ] ไม่มี `TODO` / `FIXME` / `...` / `pass` ที่ไม่จำเป็น
- [ ] ไม่มี hardcoded secret / API key / connection string
- [ ] Ruff lint ผ่าน (0 warnings)
- [ ] Mypy strict ผ่าน (0 errors)
```

### SQL

```markdown
- [ ] V001: CREATE TABLE (ไม่มี IF NOT EXISTS)
- [ ] V001: คอลัมน์ครบ (id, tenant_id, code, name, status, amount,
      metadata, version, created_at, updated_at, deleted_at)
- [ ] V001: CONSTRAINT (UNIQUE, CHECK, FK)
- [ ] V001: Index (partial + composite + created_at desc)
- [ ] V001: ENABLE ROW LEVEL SECURITY
- [ ] V001: CREATE POLICY (tenant_id = current_setting)
- [ ] V001: BEFORE UPDATE trigger (updated_at)
- [ ] V002: seed + ON CONFLICT DO NOTHING
- [ ] V003: rollback + CASCADE
- [ ] ทุกไฟล์มี BEGIN / COMMIT
- [ ] migrations/env.py: import model แล้ว
- [ ] `alembic upgrade head` ผ่าน
- [ ] `alembic downgrade -1` ผ่าน
- [ ] `alembic upgrade head` อีกครั้ง ผ่าน
```

### Routing

```markdown
- [ ] register ใน `app/routes.py`
- [ ] register ใน `migrations/env.py`
- [ ] อยู่ layer ถูกต้อง
- [ ] prefix ไม่ซ้ำ
- [ ] `/docs` เห็น tag ใหม่
- [ ] `/openapi.json` valid
- [ ] `curl GET /api/v1/{module}/` → 200
```

### Tests

```markdown
- [ ] Unit ≥ 8 tests
  - [ ] happy path
  - [ ] edge case (zero, boundary)
  - [ ] error case (domain exception)
  - [ ] value object behavior
  - [ ] use case with mocks
  - [ ] cache never-raise
  - [ ] read-back verification
  - [ ] idempotency replay
- [ ] Integration ≥ 4 tests
  - [ ] save → get round-trip
  - [ ] RLS blocks other tenant
  - [ ] unique constraint violation
  - [ ] soft delete filter
- [ ] Property ≥ 3 tests × 100 iter
  - [ ] non-negative amount valid
  - [ ] negative amount rejected
  - [ ] addition commutative
- [ ] Manual test 8 scenarios
  - [ ] Create happy 201
  - [ ] Duplicate 409
  - [ ] Invalid 422
  - [ ] Get by id 200
  - [ ] List + filter 200
  - [ ] Update 200 + version+1
  - [ ] Delete 204 + deleted_at
  - [ ] Cross-tenant 404
- [ ] Coverage ≥ 85% (CI gate)
  - [ ] domain ≥ 95%
  - [ ] application ≥ 90%
  - [ ] infrastructure ≥ 80%
  - [ ] presentation ≥ 70%
```

### Docs

```markdown
- [ ] README_{module}.md ครบ 13 หัวข้อ
- [ ] API_{module}.md มี request/response
- [ ] Swagger metadata (operation_id, responses)
- [ ] Postman collection import ได้
- [ ] Architecture diagram (Mermaid)
- [ ] Changelog entry
```

### Debug

```markdown
- [ ] ไม่มี `print()` / `pdb` / `breakpoint()` ในโค้ด
- [ ] structlog bind context (trace_id, request_id, tenant_id)
- [ ] PII masking enabled
- [ ] ไม่มี PII ใน log (ตรวจ 3 sample logs)
- [ ] trace_id propagate ผ่าน header ครบ
```

---

## ✅ SQL Migration Checklist

```markdown
### V001 create
- [ ] BEGIN / COMMIT
- [ ] CREATE SEQUENCE (ถ้ามี)
- [ ] CREATE TABLE (ไม่มี IF NOT EXISTS)
- [ ] PRIMARY KEY (UUID default gen_random_uuid)
- [ ] tenant_id UUID NOT NULL
- [ ] version INTEGER NOT NULL DEFAULT 1
- [ ] created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- [ ] updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- [ ] deleted_at TIMESTAMPTZ (nullable)
- [ ] UNIQUE (tenant_id, code)
- [ ] CHECK (amount >= 0)
- [ ] CHECK (status IN (...))
- [ ] INDEX partial (tenant_id, status) WHERE deleted_at IS NULL
- [ ] INDEX (code)
- [ ] INDEX (created_at DESC)
- [ ] ALTER TABLE ... ENABLE ROW LEVEL SECURITY
- [ ] CREATE POLICY p_{module}_tenant USING (tenant_id = current_setting(...))
- [ ] TRIGGER BEFORE UPDATE (updated_at)

### V002 seed
- [ ] BEGIN / COMMIT
- [ ] INSERT ... ON CONFLICT (tenant_id, code) DO NOTHING

### V003 rollback
- [ ] BEGIN / COMMIT
- [ ] DROP TRIGGER IF EXISTS
- [ ] DROP POLICY IF EXISTS
- [ ] DROP TABLE IF EXISTS ... CASCADE
- [ ] DROP SEQUENCE IF EXISTS
```

---

## ✅ TDD Flow Checklist

### Step 1: RED

```markdown
- [ ] เขียน test ก่อน implement
- [ ] test fail (รันดู error message)
- [ ] cover happy path
- [ ] cover edge cases
- [ ] cover error cases
```

### Step 2: GREEN

```markdown
- [ ] เขียน minimal code ให้ผ่าน
- [ ] ห้าม over-engineer
- [ ] test เขียวทุกตัว
- [ ] รัน full suite (ไม่มี regression)
```

### Step 3: REFACTOR

```markdown
- [ ] extract method / class ที่ซ้ำ
- [ ] rename ให้ชัดเจน
- [ ] behavior คงเดิม (test ยังเขียว)
- [ ] Coverage ไม่ลด
- [ ] No duplication (DRY)
```

### Step 4: INTEGRATION

```markdown
- [ ] เพิ่ม integration test (DB จริง)
- [ ] ทดสอบ RLS cross-tenant
- [ ] ทดสอบ unique constraint
- [ ] ทดสอบ transaction rollback
```

### Step 5: PROPERTY

```markdown
- [ ] เขียน hypothesis test
- [ ] 100+ iterations
- [ ] ไม่มี falsifying example
- [ ] shrink ทำงาน (ถ้า fail)
```

---

## ✅ Pre-Flight Checklist

ก่อนส่ง prompt ให้ OpenCode:

```markdown
- [ ] ใส่ Global Constraints
- [ ] ระบุ Task Type (A-G)
- [ ] ระบุ Module + Layer + Stack
- [ ] ระบุ Output Scope (รายชื่อไฟล์)
- [ ] SQL needed? Yes/No
- [ ] Routing update? Yes/No
- [ ] Docs needed? Yes/No
- [ ] Postman needed? Yes/No
- [ ] Tests needed? Yes/No
- [ ] Debug kit? Yes/No
- [ ] ถ้า Bugfix → มี stacktrace + repro steps
- [ ] ถ้า Security → ระบุ Mode (Read-only / Audit+Fix)
- [ ] ถ้า Perf → ระบุ SLO ชัดเจน
- [ ] ถ้าข้อมูลไม่พอ → ถาม 1 คำถามก่อน
```

---

## ✅ Security Checklist

```markdown
### A. Authentication & Authorization
- [ ] Nested JWT (JWS + JWE)
- [ ] Refresh token rotation
- [ ] RBAC ทุก endpoint
- [ ] Token expiry ≤ 15 นาที
- [ ] Logout = revoke refresh
- [ ] Session fixation protection

### B. Input Validation
- [ ] Pydantic v2 strict mode
- [ ] Max length ทุก string
- [ ] Whitelist enum
- [ ] SQL injection (ORM parameterized)
- [ ] Mass assignment (whitelist fields)
- [ ] File upload: type + size + scan
- [ ] SSRF protection (whitelist domains)
- [ ] XXE disabled (XML parser)

### C. Data Protection
- [ ] Encryption at rest (AES-256)
- [ ] TLS in transit (min 1.2)
- [ ] PII masking ใน logs
- [ ] Secret management (vault / env)
- [ ] Key rotation policy
- [ ] Backup encryption

### D. Multi-tenancy
- [ ] tenant_id ทุก query
- [ ] RLS policy ทุกตาราง
- [ ] Cross-tenant leakage test
- [ ] Tenant isolation ใน cache key
- [ ] Tenant ใน audit log
- [ ] Row-level validation ก่อน save

### E. API Security
- [ ] Rate limiting (per IP + per user)
- [ ] CORS whitelist
- [ ] CSRF (BFF pattern หรือ same-site cookie)
- [ ] Idempotency key
- [ ] Request size limit (1MB)
- [ ] Timeout (read 30s, write 60s)
- [ ] Circuit breaker (external calls)

### F. SQL Security
- [ ] RLS enabled + forced
- [ ] FK ON DELETE ถูกต้อง
- [ ] Search_path ปลอดภัย
- [ ] Least privilege DB user
- [ ] No dynamic SQL
- [ ] Stored procedure audit

### G. Dependency
- [ ] pip-audit ผ่าน
- [ ] bandit ผ่าน (0 high)
- [ ] Dependencies up-to-date
- [ ] SBOM generate
```

---

## ✅ Review Checklist (ก่อน merge)

```markdown
- [ ] PR description ชัดเจน
- [ ] Linked issue
- [ ] Tests pass (CI เขียว)
- [ ] Coverage ≥ 85%
- [ ] Lint / type check pass
- [ ] Migration test ผ่าน (up + down)
- [ ] Breaking change documented
- [ ] Changelog updated
- [ ] Docs updated
- [ ] Reviewer approved
```
```

---

## 📄 `reference/09-testing.md`

```markdown
# 09 — Testing Block

> Test pyramid · conftest · templates · commands · coverage map

---

## 9.1 Test Pyramid

```mermaid
graph TD
    A["🔺 E2E / Manual (5%)<br/>8 scenarios"] --> B["🔷 Integration (25%)<br/>Repository + DB + Redis"]
    B --> C["🟩 Unit (70%)<br/>Domain / UseCase / Mapper"]
    C --> D["🟪 Property (bonus)<br/>Hypothesis invariants"]
```

| ระดับ | เป้าหมาย | เครื่องมือ | จำนวนขั้นต่ำ |
|---|---|---|---|
| Unit | Domain + Application logic | pytest + pytest-asyncio + unittest.mock | ≥ 8 / module |
| Integration | Repository + SQL + RLS | pytest + testcontainers + asyncpg | ≥ 4 / module |
| Property | Invariants | hypothesis | ≥ 3 / module |
| Manual | Smoke E2E | Postman / curl | 8 scenarios |

---

## 9.2 Dependencies (`pyproject.toml`)

```toml
[project.optional-dependencies]
test = [
    "pytest==8.3.*",
    "pytest-asyncio==0.24.*",
    "pytest-cov==6.0.*",
    "pytest-benchmark==5.1.*",
    "pytest-xdist==3.6.*",
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
    --cov-report=xml:coverage.xml
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
    "@abstractmethod",
]
```

---

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
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
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
def fake_clock() -> Any:
    from freezegun import freeze_time
    with freeze_time("2025-01-15 10:00:00+07:00") as frozen:
        yield frozen


@pytest.fixture
def decimal_factory() -> Any:
    def _make(value: str | int) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    return _make
```

---

## 9.4 Unit Test — Domain Template

```python
"""
tests/unit/test_{module}.py — Domain Layer
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


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def make_{module}(tenant_id: uuid.UUID):
    def _make(
        code: str = "INV-001",
        name: str = "Sample",
        amount: Decimal = Decimal("100.00"),
        status: {Module}Status = {Module}Status.ACTIVE,
    ) -> {Module}:
        return {Module}.create(
            tenant_id=tenant_id, code=code, name=name,
            amount=amount, status=status,
        )
    return _make


class TestCreate:
    def test_create_sets_defaults(self, make_{module}) -> None:
        e = make_{module}()
        assert e.id is not None
        assert e.version == 1
        assert e.status is {Module}Status.ACTIVE
        assert e.deleted_at is None

    def test_create_with_zero_amount(self, make_{module}) -> None:
        e = make_{module}(amount=Decimal("0.00"))
        assert e.amount == Decimal("0.00")


class TestEdgeCases:
    def test_code_is_immutable(self, make_{module}) -> None:
        e = make_{module}()
        with pytest.raises(AttributeError):
            e.code = "NEW"  # type: ignore[misc]

    def test_amount_precision_quantized(self, make_{module}) -> None:
        e = make_{module}(amount=Decimal("100.005"))
        assert e.amount == Decimal("100.01")


class TestErrors:
    def test_negative_amount_raises(self, make_{module}) -> None:
        with pytest.raises(InvalidAmountError):
            make_{module}(amount=Decimal("-1.00"))

    def test_invalid_status_transition(self, make_{module}) -> None:
        e = make_{module}(status={Module}Status.ARCHIVED)
        with pytest.raises(InvalidStatusTransitionError):
            e.activate()

    def test_empty_code_raises(self, make_{module}) -> None:
        with pytest.raises(ValueError, match="code"):
            make_{module}(code="")


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

---

## 9.5 Unit Test — Use Case Template

```python
"""
tests/unit/test_{module}_use_cases.py — Application Layer
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
    r.get_by_code.return_value = None
    r.save.side_effect = lambda e: e
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
def uc(repo, cache, event_bus, idem, tenant_ctx) -> Create{Module}UseCase:
    return Create{Module}UseCase(
        repo=repo, cache=cache, event_bus=event_bus,
        idempotency=idem, ctx=tenant_ctx,
    )


class TestCreateUseCase:
    async def test_happy_path(self, uc, repo, event_bus) -> None:
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
        cache.invalidate.side_effect = RuntimeError("redis down")
        out = await uc.execute(
            code="INV-002", name="X", amount=Decimal("1.00"),
            idempotency_key="k-3",
        )
        assert out.code == "INV-002"
        event_bus.publish.assert_awaited_once()

    async def test_readback_verification(self, uc, repo) -> None:
        await uc.execute(
            code="INV-003", name="X", amount=Decimal("1.00"),
            idempotency_key="k-4",
        )
        repo.get_by_id.assert_awaited_once()
```

---

## 9.6 Integration Test — Repository + RLS

```python
"""
tests/integration/test_{module}_repository.py
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import text

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
        e = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code="INV-RLS-1", name="RLS", amount=Decimal("1.00"),
        )
        await repo.save(e)

        await db_session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"),
            {"tid": str(other_tenant_ctx["tenant_id"])},
        )
        found = await repo.get_by_id(e.id)
        assert found is None

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
        with pytest.raises(Exception):
            await repo.save(e2)

    async def test_soft_delete_filter(self, repo, tenant_ctx) -> None:
        e = {Module}.create(
            tenant_id=tenant_ctx["tenant_id"],
            code=f"INV-{uuid.uuid4().hex[:6]}",
            name="Soft", amount=Decimal("1.00"),
        )
        saved = await repo.save(e)
        await repo.soft_delete(saved.id)
        found = await repo.get_by_id(saved.id)
        assert found is None
```

---

## 9.7 Property Test — Invariants

```python
"""
tests/property/test_{module}_invariants.py
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st

from app.modules.{module}.domain.entities import {Module}
from app.modules.{module}.domain.exceptions import InvalidAmountError
from app.modules.{module}.domain.value_objects import Money

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
    e = {Module}.create(
        tenant_id=TENANT, code=code or "X", name="P", amount=amount,
    )
    assert e.amount >= Decimal("0.00")


@settings(max_examples=100)
@given(amount=st.decimals(
    min_value=Decimal("-9999"), max_value=Decimal("-0.01"), places=2,
))
def test_negative_amount_always_rejected(amount: Decimal) -> None:
    with pytest.raises(InvalidAmountError):
        {Module}.create(
            tenant_id=TENANT, code="X", name="P", amount=amount,
        )


@settings(max_examples=100)
@given(a=amounts, b=amounts)
def test_sum_is_commutative(a: Decimal, b: Decimal) -> None:
    m1 = Money(a); m2 = Money(b)
    assert (m1 + m2).amount == (m2 + m1).amount
```

---

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

---

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
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb

# ─── Parallel ────────────────────────────────────
pytest -n auto                           # pytest-xdist

# ─── Benchmark ───────────────────────────────────
pytest --benchmark-only
pytest --benchmark-compare=0001
```

---

## 9.10 Coverage Map

| Layer | Coverage ขั้นต่ำ | เหตุผล |
|---|---|---|
| `domain/` | **95%** | Business logic ล้วน ไม่มี IO |
| `application/` | **90%** | Use cases |
| `infrastructure/` | **80%** | IO-bound, บางส่วน override ด้วย integration |
| `presentation/` | **70%** | Thin — วัดผ่าน integration |
| **รวมทั้งโปรเจกต์** | **85%** | CI gate |
```

---

## 📄 `reference/10-debug.md`

```markdown
# 10 — Debug Block

> Workflow · Rules · structlog · Middleware · Recipes · Tools · Common Issues

---

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

---

## 10.2 Debug Rules

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

---

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

PII_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "***@***"),
    (re.compile(r"\b0\d{8,9}\b"), "***PHONE***"),
    (re.compile(r"\b\d{13}\b"), "***ID***"),
    (re.compile(r"(Bearer\s+)[\w\-._~+/]+=*", re.I), r"\1***"),
    (re.compile(r"(password[\"']?\s*[:=]\s*[\"']?)[^\"'\s,}]+", re.I), r"\1***"),
]


def mask_pii(_logger: Any, _name: str, event: EventDict) -> EventDict:
    for k, v in list(event.items()):
        if isinstance(v, str):
            for pat, repl in PII_PATTERNS:
                v = pat.sub(repl, v)
            event[k] = v
    return event


def configure_logging(level: str = "INFO", json: bool = False) -> None:
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
    processors.append(
        structlog.processors.JSONRenderer() if json
        else structlog.dev.ConsoleRenderer(colors=True)
    )
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

---

## 10.4 Request Context Middleware

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

---

## 10.5 Recipes — แยกตาม Layer

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

**Checklist:**
- [ ] `@dataclass(frozen=True)` → ลอง `e.code = "X"` ต้อง `FrozenInstanceError`
- [ ] ตรวจ `__eq__` / `__hash__` ของ VO
- [ ] ใช้ `repr()` ดู state ทั้งก้อน

### 🟩 Application Layer

```python
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

**Checklist:**
- [ ] Mock ports (repo/cache/bus) แล้วเรียก `uc.execute()` ตรง ๆ
- [ ] ตรวจ args ที่ส่งให้ repo ด้วย `repo.save.await_args`
- [ ] ตรวจ event ที่ publish: `bus.publish.await_args.args[0]`

### 🟨 Infrastructure Layer

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    url,
    echo=os.getenv("SQL_ECHO", "0") == "1",
    pool_pre_ping=True,
)
```

**Checklist:**
- [ ] `SET app.current_tenant = '...'` ก่อน query (RLS)
- [ ] `EXPLAIN (ANALYZE, BUFFERS) SELECT ...` ดู seq scan
- [ ] Redis: `redis-cli -p 6380 monitor` ดู key จริง
- [ ] Kafka: `kafka-console-consumer --topic {module}.created`
- [ ] ตรวจ `flush()` ไม่มี `commit()` ใน repo

**SQL debug queries:**

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

**Checklist:**
- [ ] `curl -v` ดู header/status
- [ ] เปิด `/docs` ดู schema ตรงไหม
- [ ] `x-trace-id` propagate ครบไหม
- [ ] ตรวจ pydantic validation error detail

---

## 10.6 Debug Tools Cheatsheet

| เครื่องมือ | คำสั่ง | ใช้เมื่อ |
|---|---|---|
| **pdb** | `breakpoint()` | debug ทั่วไป |
| **ipdb** | `import ipdb; ipdb.set_trace()` | tab-complete |
| **pytest --pdb** | `pytest --pdb` | drop เข้า pdb ตอน fail |
| **pytest --trace** | `pytest --trace` | step ตั้งแต่ต้น |
| **rich** | `from rich import inspect; inspect(obj, methods=True)` | ดู object |
| **icecream** | `from icecream import ic; ic(x)` | แทน print debug |
| **structlog** | `log.info("k", v=...)` | log โครงสร้าง |
| **sqlalchemy echo** | `SQL_ECHO=1` | ดู SQL ที่ออก |
| **asyncpg debug** | `logging.getLogger("asyncpg").setLevel(DEBUG)` | ดู query |
| **redis monitor** | `redis-cli -p 6380 monitor` | ดูคำสั่ง Redis |
| **kafka consumer** | `kafka-console-consumer ...` | ดู event |
| **py-spy** | `py-spy top --pid $PID` | profiler |
| **scalene** | `scalene app.py` | CPU + memory |
| **memray** | `memray run -o out.bin app.py` | memory leak |
| **asyncio debug** | `PYTHONASYNCIODEBUG=1` | task ค้าง |
| **faulthandler** | `python -X faulthandler` | dump stack ตอน hang |

---

## 10.7 Common Issues & Fixes

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `MissingGreenlet` | lazy load ใน async | ใช้ `selectinload` / `joinedload` |
| `InterfaceError: another operation in progress` | ใช้ session พร้อมกัน | 1 session ต่อ 1 request |
| `TimeoutError` pool exhausted | pool_size น้อย | เพิ่ม `pool_size`, `max_overflow` |
| RLS คืน 0 rows | ไม่ set `app.current_tenant` | `set_config(..., true)` ก่อน query |
| `InvalidRequestError: greenlet_spawn` | sync code ใน async | `await session.run_sync(...)` |
| Pydantic validation ช้า | model ซับซ้อน | `model_config = ConfigDict(strict=True)` |
| `DuplicateCode` บ่อย | race condition | unique index + `ON CONFLICT` |
| Event ไม่ถึง consumer | Kafka offset / partition | ตรวจ consumer group + lag |
| Cache stale | invalidate ไม่ครบ | `invalidate` ใน use case |
| `Decimal` precision เพี้ยน | ปนกับ float | ห้าม float, ใช้ `Decimal(str(x))` |
| Test hang | async fixture ไม่ปิด | `pytest-asyncio` + `AsyncIterator` |
| `RuntimeError: Event loop is closed` | engine ข้าม loop | scope fixture ให้ถูก |

---

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

---

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
```

---

## 📄 `reference/11-cheatsheet.md`

```markdown
# 11 — Quick Command Cheatsheet

> รวมทุกคำสั่งที่ใช้บ่อย · copy-paste ได้เลย

---

## 🎯 Templates A–G

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
```

---

## 🛠️ Scripts

```bash
# ─── Windows ─────────────────────────────────────────
create_modules.bat new inventory 3 inv --sql --tests --docs --routes
create_modules.bat template A inventory 3 inv
create_modules.bat sql invoice inv
create_modules.bat routes inventory
create_modules.bat test inventory
create_modules.bat docs inventory
create_modules.bat debug inventory
create_modules.bat all sales 4 sal --force
create_modules.bat help

# ─── Linux / macOS ───────────────────────────────────
./scripts/new_module.sh inventory 3 inv --sql --tests --docs --routes
./scripts/new_module.sh help
```

---

## 🗄️ Database

```bash
# ─── Migration ───────────────────────────────────────
alembic upgrade head                     # apply ทั้งหมด
alembic upgrade +1                       # apply ทีละไฟล์
alembic downgrade -1                     # rollback 1 ไฟล์
alembic history                          # ดู history
alembic current                          # ดู version ปัจจุบัน
alembic revision -m "add column"         # สร้าง migration ใหม่

# ─── psql ────────────────────────────────────────────
psql $DATABASE_URL
\dt tenant_inv.*                         # list tables
\d+ tenant_inv.invoices                  # describe table
\dp tenant_inv.invoices                  # list policies
SHOW app.current_tenant;                 # ดู tenant ปัจจุบัน
SELECT * FROM pg_policies WHERE tablename = 'invoices';
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;   # query plan
```

---

## 🧪 Testing

```bash
# ─── Run ─────────────────────────────────────────────
pytest                                   # ทั้งหมด
pytest -m unit                           # unit
pytest -m integration                    # integration
pytest -m property                       # property
pytest -m "not slow"                     # ข้าม slow
pytest -n auto                           # parallel

# ─── Single ──────────────────────────────────────────
pytest tests/unit/test_inventory.py
pytest tests/unit/test_inventory.py::TestCreate::test_create_sets_defaults
pytest -k "duplicate or invalid"

# ─── Coverage ────────────────────────────────────────
pytest --cov=app --cov-report=term-missing
pytest --cov=app --cov-report=html:htmlcov
pytest --cov=app --cov-fail-under=85

# ─── Debug ───────────────────────────────────────────
pytest -x                                # stop on first fail
pytest --lf                              # last failed
pytest --ff                              # failed first
pytest -vv --tb=long                     # verbose
pytest -s                                # show stdout
pytest --pdb                             # drop to pdb
pytest --trace                           # step from start
pytest --log-cli-level=DEBUG             # show logs

# ─── Benchmark ───────────────────────────────────────
pytest --benchmark-only
pytest --benchmark-compare=0001
```

---

## 🐛 Debug

```bash
# ─── Run in debug ────────────────────────────────────
LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload --log-level debug
PYTHONASYNCIODEBUG=1 PYTHONFAULTHANDLER=1 uvicorn app.main:app

# ─── Redis ───────────────────────────────────────────
redis-cli -p 6380 monitor                # stream commands
redis-cli -p 6380 keys "inv:*"           # list keys
redis-cli -p 6380 get "inv:xxx"          # read key
redis-cli -p 6380 ttl "inv:xxx"          # check TTL
redis-cli -p 6380 info stats             # stats

# ─── Kafka ───────────────────────────────────────────
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic inventory.created \
  --from-beginning

kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group inventory-svc

# ─── Profiling ───────────────────────────────────────
py-spy top --pid $(pgrep -f "uvicorn app.main")
py-spy record -o profile.svg --pid $PID --duration 30
scalene app/main.py
memray run -o out.bin app/main.py
memray flamegraph out.bin

# ─── Network ─────────────────────────────────────────
curl -v http://localhost:8000/api/v1/inventory/
curl -X POST http://localhost:8000/api/v1/inventory/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"code":"INV-001","name":"Test","amount":"100.00"}'

http :8000/api/v1/inventory/            # httpie
http POST :8000/api/v1/inventory/ \
  code=INV-001 name=Test amount=100.00 \
  Idempotency-Key:$(uuidgen)
```

---

## 🔍 Quality

```bash
# ─── Lint ────────────────────────────────────────────
ruff check .                             # lint
ruff check --fix .                       # auto-fix
ruff format .                            # format

# ─── Type ────────────────────────────────────────────
mypy app/                                # type check
mypy --strict app/                       # strict mode

# ─── Security ────────────────────────────────────────
bandit -r app/                           # security scan
pip-audit                                # dependency CVE
safety check                             # alternative

# ─── Pre-commit ──────────────────────────────────────
pre-commit install
pre-commit run --all-files
```

---

## 📦 Dependencies

```bash
# ─── Install ─────────────────────────────────────────
pip install -e ".[test]"                 # editable + test deps
pip install -e ".[dev,test]"             # + dev
uv sync --all-extras                     # uv

# ─── Update ──────────────────────────────────────────
pip list --outdated
pip-compile requirements.in
uv lock --upgrade

# ─── Audit ───────────────────────────────────────────
pip-audit
pip-audit --fix
```

---

## 🚀 Deploy

```bash
# ─── Local ───────────────────────────────────────────
uvicorn app.main:app --reload --port 8000
gunicorn app.main:app -k uvicorn.workers.UvicornWorker \
  --workers 4 --bind 0.0.0.0:8000

# ─── Docker ──────────────────────────────────────────
docker build -t erp-iot:latest .
docker run -p 8000:8000 --env-file .env erp-iot:latest

# ─── Docker Compose ──────────────────────────────────
docker compose up -d
docker compose logs -f app
docker compose down -v
```

---

## 🎯 Universal Header (copy ทั้งก้อน)

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

## 📋 Quick Reference

| ต้องการ | คำสั่ง |
|---|---|
| สร้าง module ใหม่ | `create_modules.bat new {name} {layer} {prefix} --all` |
| Apply migration | `alembic upgrade head` |
| รัน tests | `pytest -m unit -q` |
| Coverage | `pytest --cov=app --cov-fail-under=85` |
| Lint + format | `ruff check --fix . && ruff format .` |
| Type check | `mypy --strict app/` |
| Security scan | `bandit -r app/ && pip-audit` |
| Debug server | `LOG_LEVEL=DEBUG SQL_ECHO=1 uvicorn app.main:app --reload` |
| Redis monitor | `redis-cli -p 6380 monitor` |
| Profile | `py-spy top --pid $(pgrep -f uvicorn)` |
| Generate prompt | `create_modules.bat template A {name} {layer} {prefix}` |
```

---

# ✅ สรุปไฟล์ทั้ง 11

| # | ไฟล์ | ขนาด | หัวข้อ |
|---|---|---|---|
| 1 | `01-global-constraints.md` | กลาง | กฎเหล็ก · error handling · layers · security |
| 2 | `02-master-structure.md` | กลาง | 23 ส่วน + รายละเอียดแต่ละส่วน |
| 3 | `03-templates-a-g.md` | ใหญ่ | 7 templates เต็ม |
| 4 | `04-sql-migration.md` | กลาง | V001/V002/V003 + debug queries |
| 5 | `05-routing.md` | กลาง | routes.py + routers.py + dependencies.py |
| 6 | `06-docs-postman.md` | กลาง | README + API + Swagger + Postman |
| 7 | `07-reports.md` | กลาง | Report A/B/C/D |
| 8 | `08-checklists.md` | กลาง | DoD + SQL + TDD + Security + Pre-flight |
| 9 | `09-testing.md` | ใหญ่ | Pyramid + conftest + 4 test templates |
| 10 | `10-debug.md` | ใหญ่ | Workflow + structlog + middleware + recipes |
| 11 | `11-cheatsheet.md` | กลาง | ทุกคำสั่งที่ใช้บ่อย |

---

## 🚀 ขั้นตอนถัดไป

```bash
# 1. สร้าง folder
mkdir -p python-ddd-clean-arch/reference
cd python-ddd-clean-arch

# 2. copy แต่ละไฟล์ด้านบนไปวาง
# (copy เนื้อหาใน code block แต่ละหัวข้อ)

# 3. ตรวจสอบ
ls reference/
# 01-global-constraints.md
# 02-master-structure.md
# 03-templates-a-g.md
# 04-sql-migration.md
# 05-routing.md
# 06-docs-postman.md
# 07-reports.md
# 08-checklists.md
# 09-testing.md
# 10-debug.md
# 11-cheatsheet.md

# 4. ตรวจ frontmatter (ไฟล์ SKILL.md ต้อง link ครบ)
grep -o "reference/[0-9][0-9]-[a-z-]*\.md" SKILL.md | sort -u

# 5. ใช้งาน
claude "/python-ddd-clean-arch สร้าง module inventory"
```
 
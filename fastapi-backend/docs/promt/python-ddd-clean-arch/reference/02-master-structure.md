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

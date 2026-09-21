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

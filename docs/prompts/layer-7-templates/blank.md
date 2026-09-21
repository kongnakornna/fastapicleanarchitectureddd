### 📄 Module 7.3: `blank` (Empty Template)

### Metadata

| หัวข้อ | รายละเอียด |
|---|---|
| **ชื่อ Module** | `blank` |
| **Layer** | `7` (Templates) |
| **Priority** | 🟢 |
| **Phase** | 1 |
| **Dependencies** | ไม่มี |
| **Domain Concepts** | `BlankEntity` (entity) |
| **Prefix** | `blk` |
| **Tables** | `tenant_blk.blanks` |

### 🎯 Prompt (Copy ทั้งหมด)

```markdown
# สร้าง Module `blank`

## บริบท
- Empty template — ใช้เป็น starting point สำหรับ module ใหม่
- ทุกไฟล์มี TODO comments
- แสดง structure ครบ 23 ไฟล์
- Developer เติม business logic เอง

## ข้อกำหนด

### 1. Domain Layer

**`domain/entities.py`**
```python
@dataclass
class BlankEntity(BaseEntity):
    """Blank entity — เอนทิตีเปล่า (TODO: rename + add fields)"""
    # TODO: Add your fields here
    code: str = ""
    name: str = ""

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        # TODO: Add validation rules
        if not self.code:
            raise DomainError("Code is required")
```

### 2-4. Application / Infrastructure / Presentation

> ทุกไฟล์มี TODO comments — เติมตาม business requirements

### 5-7. Invariants / Events / Tests

- Invariants: TODO
- Events: `BlankCreated`, `BlankUpdated`, `BlankDeleted`
- Tests: skeleton + TODO

## Output
- 23 ไฟล์ (skeleton)
- Comment 2 ภาษา
- พร้อมรัน
```

### 📄 SQL Migration สำหรับ `blank`

**`db/migrations/V001__create_blank.sql`**
```sql
BEGIN;

CREATE TABLE tenant_blk.blanks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL,
    code            VARCHAR(50) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    metadata        JSONB DEFAULT '{}'::jsonb,
    version         INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    CONSTRAINT uq_blanks_code UNIQUE (tenant_id, code)
);

CREATE INDEX ix_blanks_tenant ON tenant_blk.blanks(tenant_id) WHERE deleted_at IS NULL;

ALTER TABLE tenant_blk.blanks ENABLE ROW LEVEL SECURITY;
CREATE POLICY p_blanks_tenant ON tenant_blk.blanks
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

COMMIT;
```

**`db/migrations/V002__seed_blank.sql`**
```sql
BEGIN;
-- TODO: Add seed data if needed
COMMIT;
```

**`db/migrations/V003__rollback_blank.sql`**
```sql
BEGIN;
DROP TABLE IF EXISTS tenant_blk.blanks CASCADE;
COMMIT;
```

---

## ✅ สรุป Layer 7 (Templates) — 3/65 ไฟล์

| # | Module | Prefix | Output | วัตถุประสงค์ |
|---|---|---|---|---|
| 7.1 | `health` | `hlth` | ~10 ไฟล์ | Health check endpoint |
| 7.2 | `example` | `ex` | 23 ไฟล์ | Reference implementation |
| 7.3 | `blank` | `blk` | 23 ไฟล์ | Empty template |

---

# 🎉 สรุปทั้งหมด — 65/65 Modules ครบทุก Layer

## สรุปตาม Layer

| Layer | ชื่อ | Modules | Output รวม |
|---|---|---|---|
| **0** | Core | 6 | ~84 ไฟล์ |
| **1** | Foundation | 8 | 184 ไฟล์ |
| **2** | Money Path | 7 | 161 ไฟล์ |
| **3** | Goods Path | 13 | 299 ไฟล์ |
| **4** | Operations | 13 | 299 ไฟล์ |
| **5** | Intelligence | 7 | 161 ไฟล์ |
| **6** | Monitoring | 8 | 184 ไฟล์ |
| **7** | Templates | 3 | ~56 ไฟล์ |
| | **รวม** | **65** | **~1,428 ไฟล์** |

## 🚀 ขั้นตอนการทำงาน

```
┌──────────────────────────────────────────────────────────┐
│  Phase 1: Layer 0 + Layer 1 + Layer 2 + Layer 3          │
│  (Core + Foundation + Money + Goods)                     │
│  → 34 modules → ~728 ไฟล์                                │
├──────────────────────────────────────────────────────────┤
│  Phase 2: Layer 4 + Layer 5                              │
│  (Operations + Intelligence)                             │
│  → 20 modules → ~460 ไฟล์                                │
├──────────────────────────────────────────────────────────┤
│  Phase 3: Layer 6 + Layer 7                              │
│  (Monitoring + Templates)                                │
│  → 11 modules → ~240 ไฟล์                                │
└──────────────────────────────────────────────────────────┘
```

## 📋 Checklist ก่อนส่ง (ทุก Module)

- [ ] Domain layer ไม่ import framework
- [ ] ใช้ `flush()` ไม่ใช่ `commit()` ใน repository
- [ ] Cache never raises
- [ ] Error handling ถูก shape (3/2/never)
- [ ] Idempotency ครบ (money/goods path)
- [ ] Audit log ครบ
- [ ] Read-back verification ครบ
- [ ] Tests ครบ 4 ประเภท (unit/integration/property/manual)
- [ ] SQL migrations ครบ 3 ไฟล์ (V001/V002/V003)
- [ ] RLS policy present
- [ ] Comment 2 ภาษา
- [ ] พร้อมรัน

## 🎯 วิธีใช้

```bash
# 1. สร้างโฟลเดอร์
mkdir -p docs/prompts/{layer-0-core,layer-1-foundation,layer-2-money-path,layer-3-goods-path,layer-4-operations,layer-5-intelligence,layer-6-monitoring,layer-7-templates}

# 2. Copy prompt ที่ต้องการจากหัวข้อด้านบน

# 3. วางใน AI (ChatGPT/Claude/Gemini)

# 4. AI จะสร้าง 23 ไฟล์

# 5. รัน tests
uv run pytest tests/unit/test_{module}.py -v
uv run pytest tests/integration/test_{module}_repository.py -v
uv run pytest tests/property/test_{module}_invariants.py -v
```

---

**เสร็จสมบูรณ์ — 65 modules / 8 layers / ~1,428 ไฟล์** ✅****

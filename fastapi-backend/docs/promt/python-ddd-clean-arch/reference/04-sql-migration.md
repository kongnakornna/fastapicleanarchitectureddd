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

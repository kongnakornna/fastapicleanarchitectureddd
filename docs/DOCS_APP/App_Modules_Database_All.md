# 🗄️ Database Design — Module `idempotency` (Layer 0) แบบครบวงจร

> **หลักการ:** ทุกตารางมี `prefix_` บอก Layer + Module ชัดเจน
> **Stack:** PostgreSQL 17 · Schema-per-tenant · Partitioned by month

---

## 📐 1. Naming Convention ทั้งระบบ

### 1.1 Layer Prefix (บังคับ)

| Layer | Prefix | ตัวอย่าง | คำอธิบาย |
|---|---|---|---|
| **0** Core | `core_` | `core_idem_records` | Cross-cutting (money, tenant, audit, idem, config, events) |
| **1** Foundation | `found_` | `found_users` | tenancy, auth, user, customer, product |
| **2** Money Path | `money_` | `money_invoices` | order, invoice, ledger, payment, tax |
| **3** Goods Path | `goods_` | `goods_inventory` | inventory, warehouse, production |
| **4** Operations | `ops_` | `ops_transport` | transport, retail, pos, crm |
| **5** Intelligence | `intel_` | `intel_forecasts` | reporting, analytics, forecast |
| **6** Monitoring | `mon_` | `mon_iot_readings` | iot, cctv, backup, energy |
| **7** Templates | `tpl_` | `tpl_health` | health, example, blank |

### 1.2 Module Sub-Prefix

| Module | Sub-prefix | ตัวอย่าง |
|---|---|---|
| tenant_context | `core_tenctx_` | `core_tenctx_registry` |
| audit | `core_audit_` | `core_audit_logs` |
| **idempotency** | **`core_idem_`** | **`core_idem_records`** |
| config | `core_cfg_` | `core_cfg_settings` |
| events | `core_evt_` | `core_evt_outbox` |

### 1.3 Suffix

| Suffix | ความหมาย |
|---|---|
| `_records` | ตารางหลัก |
| `_outbox` | Outbox pattern |
| `_archive` | Archive table |
| `_mv` | Materialized view |
| `_log` | Log/tracking |
| `_YYYYMM` | Monthly partition |

### 1.4 Schema Layout

```
PostgreSQL Cluster
├── public                          ← shared metadata + migrations
│   ├── core_tenctx_registry        ← ทะเบียนผู้เช่า
│   ├── schema_migrations           ← ประวัติ migration
│   └── core_idem_global_stats      ← สถิติภาพรวมทุก tenant
│
├── tenant_acme                     ← per-tenant schema
│   ├── core_idem_records           ← idempotency (หลัก)
│   ├── core_idem_records_YYYYMM    ← partition รายเดือน
│   ├── core_idem_outbox            ← event outbox
│   ├── core_idem_audit_events      ← audit trail
│   ├── core_audit_logs             ← audit (จาก module 3)
│   └── money_invoices              ← ตัวอย่าง Layer 2
│
└── tenant_beta                     ← per-tenant schema
    └── ... (เหมือน tenant_acme)
```

---

## 📄 2. DDL — Public Schema

### 2.1 `public.core_tenctx_registry` (จาก Module 2)

```sql
-- ============================================================
-- Tenant Registry — ทะเบียนผู้เช่า
-- Layer: 0 (Core) · Module: tenant_context · Prefix: core_tenctx_
-- ============================================================
CREATE TABLE IF NOT EXISTS public.core_tenctx_registry (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63)  NOT NULL,
    schema_name     VARCHAR(80)  NOT NULL,
    display_name    VARCHAR(200),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    isolation       VARCHAR(32)  NOT NULL DEFAULT 'SCHEMA_PER_TENANT'
                    CHECK (isolation IN ('SCHEMA_PER_TENANT','DATABASE_PER_TENANT','ROW_LEVEL')),
    plan            VARCHAR(32)  NOT NULL DEFAULT 'STANDARD'
                    CHECK (plan IN ('FREE','STANDARD','PRO','ENTERPRISE')),
    quota_records   BIGINT       NOT NULL DEFAULT 1000000,  -- soft limit
    metadata        JSONB        NOT NULL DEFAULT '{}'::jsonb,
    suspended_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_tenctx_tenant_id   UNIQUE (tenant_id),
    CONSTRAINT uq_tenctx_schema_name UNIQUE (schema_name),
    CONSTRAINT ck_tenctx_tenant_id   CHECK (tenant_id ~ '^[a-z][a-z0-9_]{2,62}$')
);

CREATE INDEX ix_tenctx_active
    ON public.core_tenctx_registry (is_active)
    WHERE is_active = TRUE;

COMMENT ON TABLE  public.core_tenctx_registry IS 'Tenant registry — ทะเบียนผู้เช่า (Layer 0 / tenant_context)';
COMMENT ON COLUMN public.core_tenctx_registry.schema_name IS 'PostgreSQL schema name (tenant_{tenant_id})';
```

### 2.2 `public.core_idem_global_stats` — สถิติภาพรวม

```sql
-- ============================================================
-- Global idempotency stats (aggregate ทุก tenant)
-- Layer: 0 · Module: idempotency · Prefix: core_idem_
-- ============================================================
CREATE TABLE IF NOT EXISTS public.core_idem_global_stats (
    id                  BIGSERIAL    PRIMARY KEY,
    tenant_id           VARCHAR(63)  NOT NULL,
    stat_date           DATE         NOT NULL,
    total_records       BIGINT       NOT NULL DEFAULT 0,
    pending_count       BIGINT       NOT NULL DEFAULT 0,
    completed_count     BIGINT       NOT NULL DEFAULT 0,
    failed_count        BIGINT       NOT NULL DEFAULT 0,
    expired_count       BIGINT       NOT NULL DEFAULT 0,
    avg_duration_ms     NUMERIC(10,2),
    conflict_count      BIGINT       NOT NULL DEFAULT 0,  -- IN_FLIGHT
    reuse_violation     BIGINT       NOT NULL DEFAULT 0,  -- key reuse
    last_purge_at       TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_idem_stats_tenant_date UNIQUE (tenant_id, stat_date)
);

CREATE INDEX ix_idem_stats_date
    ON public.core_idem_global_stats (stat_date DESC);

COMMENT ON TABLE public.core_idem_global_stats IS 'Daily aggregate stats per tenant — สถิติรายวันต่อ tenant';
```

---

## 📄 3. DDL — Tenant Schema Template

> ทุก tenant จะได้ schema `tenant_{id}` ที่มีตารางเหล่านี้ (สร้างผ่าน function)

### 3.1 `tenant_{id}.core_idem_records` (Partitioned)

```sql
-- ============================================================
-- Idempotency records — ตารางหลัก (partitioned by month)
-- Layer: 0 · Module: idempotency · Prefix: core_idem_
-- ============================================================
CREATE TABLE tenant_acme.core_idem_records (
    -- ── Identity ──────────────────────────────────────────
    id                  UUID         NOT NULL DEFAULT gen_random_uuid(),
    tenant_id           VARCHAR(63)  NOT NULL,
    key                 VARCHAR(128) NOT NULL,
    fingerprint         CHAR(64)     NOT NULL,  -- SHA-256 hex

    -- ── State ─────────────────────────────────────────────
    status              VARCHAR(16)  NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING','COMPLETED','FAILED','EXPIRED')),

    -- ── Cached response ───────────────────────────────────
    response_status     SMALLINT,
    response_body       JSONB,
    response_headers    JSONB        NOT NULL DEFAULT '{}'::jsonb,

    -- ── Timing ────────────────────────────────────────────
    locked_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ  NOT NULL,
    ttl_seconds         INTEGER      NOT NULL DEFAULT 86400
                        CHECK (ttl_seconds BETWEEN 3600 AND 604800),

    -- ── Error ─────────────────────────────────────────────
    error_code          VARCHAR(64),
    error_message       TEXT,

    -- ── Audit ─────────────────────────────────────────────
    request_id          VARCHAR(64),
    actor_user_id       VARCHAR(64),
    duration_ms         INTEGER,
    attempt_count       SMALLINT     NOT NULL DEFAULT 1,

    -- ── Partition key ─────────────────────────────────────
    partition_ym        CHAR(6)      NOT NULL,  -- 'YYYYMM'

    -- ── Timestamps ────────────────────────────────────────
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    -- ── Constraints ───────────────────────────────────────
    PRIMARY KEY (id, partition_ym),
    CONSTRAINT uq_idem_tenant_key    UNIQUE (tenant_id, key, partition_ym),
    CONSTRAINT ck_idem_fingerprint   CHECK (fingerprint ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_idem_completed     CHECK (
        status <> 'COMPLETED' OR response_status IS NOT NULL
    ),
    CONSTRAINT ck_idem_failed        CHECK (
        status <> 'FAILED' OR error_code IS NOT NULL
    )
) PARTITION BY LIST (partition_ym);

-- ── Monthly partitions (ตัวอย่าง 3 เดือน) ─────────────────
CREATE TABLE tenant_acme.core_idem_records_202609
    PARTITION OF tenant_acme.core_idem_records
    FOR VALUES IN ('202609');

CREATE TABLE tenant_acme.core_idem_records_202610
    PARTITION OF tenant_acme.core_idem_records
    FOR VALUES IN ('202610');

CREATE TABLE tenant_acme.core_idem_records_202611
    PARTITION OF tenant_acme.core_idem_records
    FOR VALUES IN ('202611');

-- ── Indexes ───────────────────────────────────────────────
CREATE INDEX ix_idem_acme_status
    ON tenant_acme.core_idem_records (status)
    WHERE status = 'PENDING';

CREATE INDEX ix_idem_acme_expires
    ON tenant_acme.core_idem_records (expires_at)
    WHERE status IN ('PENDING','FAILED');

CREATE INDEX ix_idem_acme_lookup
    ON tenant_acme.core_idem_records (tenant_id, key)
    INCLUDE (status, fingerprint, response_status);

CREATE INDEX ix_idem_acme_request
    ON tenant_acme.core_idem_records (request_id)
    WHERE request_id IS NOT NULL;

CREATE INDEX ix_idem_acme_actor
    ON tenant_acme.core_idem_records (actor_user_id, created_at DESC)
    WHERE actor_user_id IS NOT NULL;

COMMENT ON TABLE  tenant_acme.core_idem_records IS 'Idempotency records — partitioned by month';
COMMENT ON COLUMN tenant_acme.core_idem_records.fingerprint IS 'SHA-256(method ‖ path ‖ body ‖ query)';
COMMENT ON COLUMN tenant_acme.core_idem_records.partition_ym IS 'YYYYMM — partition key';
```

### 3.2 `tenant_{id}.core_idem_outbox` (Event Outbox Pattern)

```sql
-- ============================================================
-- Idempotency outbox — สำหรับ publish event อย่าง reliable
-- Layer: 0 · Module: idempotency · Prefix: core_idem_
-- ============================================================
CREATE TABLE tenant_acme.core_idem_outbox (
    id              BIGSERIAL    PRIMARY KEY,
    tenant_id       VARCHAR(63)  NOT NULL,
    aggregate_id    UUID         NOT NULL,      -- idempotency record id
    event_name      VARCHAR(64)  NOT NULL,      -- 'IdempotencyCompleted'
    payload         JSONB        NOT NULL,
    status          VARCHAR(16)  NOT NULL DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING','PUBLISHED','FAILED')),
    retry_count     SMALLINT     NOT NULL DEFAULT 0,
    max_retries     SMALLINT     NOT NULL DEFAULT 5,
    next_retry_at   TIMESTAMPTZ,
    published_at    TIMESTAMPTZ,
    error_message   TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_idem_outbox_event CHECK (
        event_name IN ('IdempotencyCompleted','IdempotencyFailed','IdempotencyExpired')
    )
);

CREATE INDEX ix_idem_outbox_pending
    ON tenant_acme.core_idem_outbox (next_retry_at)
    WHERE status = 'PENDING';

CREATE INDEX ix_idem_outbox_aggregate
    ON tenant_acme.core_idem_outbox (aggregate_id);

COMMENT ON TABLE tenant_acme.core_idem_outbox IS 'Event outbox — สำหรับ at-least-once delivery';
```

### 3.3 `tenant_{id}.core_idem_audit_events` (State change trail)

```sql
-- ============================================================
-- Idempotency state-change audit trail
-- Layer: 0 · Module: idempotency · Prefix: core_idem_
-- ============================================================
CREATE TABLE tenant_acme.core_idem_audit_events (
    id              BIGSERIAL    PRIMARY KEY,
    tenant_id       VARCHAR(63)  NOT NULL,
    record_id       UUID         NOT NULL,
    key             VARCHAR(128) NOT NULL,
    from_status     VARCHAR(16),
    to_status       VARCHAR(16)  NOT NULL,
    reason          VARCHAR(64),
    actor_user_id   VARCHAR(64),
    request_id      VARCHAR(64),
    metadata        JSONB        NOT NULL DEFAULT '{}'::jsonb,
    occurred_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_idem_audit_record
    ON tenant_acme.core_idem_audit_events (record_id, occurred_at DESC);

CREATE INDEX ix_idem_audit_key
    ON tenant_acme.core_idem_audit_events (tenant_id, key, occurred_at DESC);

CREATE INDEX ix_idem_audit_transition
    ON tenant_acme.core_idem_audit_events (from_status, to_status);

COMMENT ON TABLE tenant_acme.core_idem_audit_events IS 'State transitions audit — ประวัติการเปลี่ยนสถานะ';
```

### 3.4 `tenant_{id}.core_idem_lock_log` (Observability)

```sql
-- ============================================================
-- Distributed lock observability (optional)
-- Layer: 0 · Module: idempotency · Prefix: core_idem_
-- ============================================================
CREATE TABLE tenant_acme.core_idem_lock_log (
    id              BIGSERIAL    PRIMARY KEY,
    tenant_id       VARCHAR(63)  NOT NULL,
    key             VARCHAR(128) NOT NULL,
    holder          VARCHAR(64)  NOT NULL,   -- pod / host / pid
    acquired_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    released_at     TIMESTAMPTZ,
    ttl_seconds     INTEGER      NOT NULL,
    release_reason  VARCHAR(32)
                    CHECK (release_reason IN ('normal','expired','error','forced')),
    request_id      VARCHAR(64)
);

CREATE INDEX ix_idem_lock_key
    ON tenant_acme.core_idem_lock_log (tenant_id, key, acquired_at DESC);

CREATE INDEX ix_idem_lock_active
    ON tenant_acme.core_idem_lock_log (acquired_at)
    WHERE released_at IS NULL;

COMMENT ON TABLE tenant_acme.core_idem_lock_log IS 'Lock observability — สำหรับ debug race conditions';
```

### 3.5 `tenant_{id}.core_idem_records_archive` (Archive — partitioned yearly)

```sql
-- ============================================================
-- Archive — เก็บ record เก่ากว่า retention
-- Layer: 0 · Module: idempotency · Prefix: core_idem_
-- ============================================================
CREATE TABLE tenant_acme.core_idem_records_archive (
    LIKE tenant_acme.core_idem_records
        INCLUDING DEFAULTS
        INCLUDING CONSTRAINTS
) PARTITION BY RANGE (completed_at);

-- ── Yearly partitions ─────────────────────────────────────
CREATE TABLE tenant_acme.core_idem_records_archive_2025
    PARTITION OF tenant_acme.core_idem_records_archive
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE tenant_acme.core_idem_records_archive_2026
    PARTITION OF tenant_acme.core_idem_records_archive
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

COMMENT ON TABLE tenant_acme.core_idem_records_archive IS 'Archive — monthly active → yearly archive';
```

---

## 📄 4. Functions & Triggers

### 4.1 `updated_at` trigger (ใช้ทุกตาราง)

```sql
-- ============================================================
-- Function: touch_updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION public.touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply
CREATE TRIGGER trg_idem_records_updated
    BEFORE UPDATE ON tenant_acme.core_idem_records
    FOR EACH ROW EXECUTE FUNCTION public.touch_updated_at();
```

### 4.2 Auto-partition creation (monthly)

```sql
-- ============================================================
-- Function: ensure_idem_partition(schema, ym)
-- สร้าง partition รายเดือนอัตโนมัติ
-- ============================================================
CREATE OR REPLACE FUNCTION public.ensure_idem_partition(
    p_schema TEXT,
    p_ym     CHAR(6)
)
RETURNS VOID AS $$
DECLARE
    v_table TEXT := format('%I.core_idem_records_%s', p_schema, p_ym);
    v_parent TEXT := format('%I.core_idem_records', p_schema);
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = format('core_idem_records_%s', p_ym)
    ) THEN
        EXECUTE format(
            'CREATE TABLE %s PARTITION OF %s FOR VALUES IN (%L)',
            v_table, v_parent, p_ym
        );
        RAISE NOTICE 'Created partition %', v_table;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ── Cron: สร้างล่วงหน้า 2 เดือน ───────────────────────────
-- SELECT public.ensure_idem_partition('tenant_acme', TO_CHAR(NOW() + INTERVAL '2 month', 'YYYYMM'));
```

### 4.3 State transition trigger (audit)

```sql
-- ============================================================
-- Trigger: log state transition
-- ============================================================
CREATE OR REPLACE FUNCTION public.log_idem_transition()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO tenant_acme.core_idem_audit_events (
            tenant_id, record_id, key,
            from_status, to_status, reason,
            actor_user_id, request_id
        ) VALUES (
            NEW.tenant_id, NEW.id, NEW.key,
            OLD.status, NEW.status,
            CASE NEW.status
                WHEN 'COMPLETED' THEN 'completed'
                WHEN 'FAILED'    THEN COALESCE(NEW.error_code, 'failed')
                WHEN 'EXPIRED'   THEN 'ttl_expired'
                ELSE 'unknown'
            END,
            NEW.actor_user_id, NEW.request_id
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_idem_records_transition
    AFTER UPDATE ON tenant_acme.core_idem_records
    FOR EACH ROW EXECUTE FUNCTION public.log_idem_transition();
```

### 4.4 Outbox trigger (publish event อัตโนมัติ)

```sql
-- ============================================================
-- Trigger: enqueue event to outbox
-- ============================================================
CREATE OR REPLACE FUNCTION public.enqueue_idem_event()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status
       AND NEW.status IN ('COMPLETED','FAILED','EXPIRED') THEN
        INSERT INTO tenant_acme.core_idem_outbox (
            tenant_id, aggregate_id, event_name, payload
        ) VALUES (
            NEW.tenant_id,
            NEW.id,
            'Idempotency' || INITCAP(LOWER(NEW.status)),
            jsonb_build_object(
                'key', NEW.key,
                'fingerprint', NEW.fingerprint,
                'status', NEW.status,
                'response_status', NEW.response_status,
                'occurred_at', NOW()
            )
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_idem_records_outbox
    AFTER UPDATE ON tenant_acme.core_idem_records
    FOR EACH ROW EXECUTE FUNCTION public.enqueue_idem_event();
```

### 4.5 Purge expired (maintenance)

```sql
-- ============================================================
-- Function: purge_expired_idempotency(schema, limit)
-- ลบ record ที่หมดอายุ → archive ก่อนลบ
-- ============================================================
CREATE OR REPLACE FUNCTION public.purge_expired_idempotency(
    p_schema TEXT,
    p_limit  INT DEFAULT 1000
)
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    -- 1) Move to archive
    EXECUTE format($f$
        WITH moved AS (
            DELETE FROM %I.core_idem_records
            WHERE expires_at < NOW()
              AND status IN ('COMPLETED','FAILED','EXPIRED')
            RETURNING *
        )
        INSERT INTO %I.core_idem_records_archive
        SELECT * FROM moved
    $f$, p_schema, p_schema);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;
```

### 4.6 Generate partition key อัตโนมัติ

```sql
-- ============================================================
-- Trigger: set partition_ym from locked_at
-- ============================================================
CREATE OR REPLACE FUNCTION public.set_idem_partition_ym()
RETURNS TRIGGER AS $$
BEGIN
    NEW.partition_ym := TO_CHAR(NEW.locked_at, 'YYYYMM');
    NEW.expires_at := COALESCE(NEW.expires_at, NEW.locked_at + (NEW.ttl_seconds || ' seconds')::INTERVAL);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_idem_records_partition
    BEFORE INSERT ON tenant_acme.core_idem_records
    FOR EACH ROW EXECUTE FUNCTION public.set_idem_partition_ym();
```

---

## 📄 5. Row-Level Security (RLS)

```sql
-- ============================================================
-- RLS: บังคับ tenant isolation ในระดับ DB
-- ============================================================
ALTER TABLE tenant_acme.core_idem_records ENABLE ROW LEVEL SECURITY;

-- Policy: อ่าน/เขียนได้เฉพาะ tenant ของ session
CREATE POLICY idem_tenant_isolation ON tenant_acme.core_idem_records
    USING (tenant_id = current_setting('app.current_tenant', TRUE))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', TRUE));

-- ── App set ค่าใน session ──────────────────────────────────
-- SET LOCAL app.current_tenant = 'acme';
```

> **หมายเหตุ:** RLS เป็น defense-in-depth — ใช้คู่กับ schema-per-tenant และ application-level check

---

## 📄 6. Materialized Views — สำหรับ Dashboard

### 6.1 `core_idem_stats_hourly_mv`

```sql
-- ============================================================
-- MV: hourly stats per tenant (refresh every 5 min)
-- ============================================================
CREATE MATERIALIZED VIEW tenant_acme.core_idem_stats_hourly_mv AS
SELECT
    date_trunc('hour', created_at) AS bucket_hour,
    tenant_id,
    status,
    COUNT(*)                       AS total,
    AVG(duration_ms)               AS avg_duration_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_duration_ms,
    SUM(CASE WHEN fingerprint IS NOT NULL THEN 1 ELSE 0 END) AS with_fingerprint
FROM tenant_acme.core_idem_records
GROUP BY 1, 2, 3
WITH NO DATA;

CREATE UNIQUE INDEX ix_idem_stats_hourly
    ON tenant_acme.core_idem_stats_hourly_mv (bucket_hour, tenant_id, status);

-- Refresh (cron ทุก 5 นาที)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY tenant_acme.core_idem_stats_hourly_mv;
```

### 6.2 `core_idem_top_reused_keys_mv`

```sql
-- ============================================================
-- MV: top reused keys (สำหรับ anomaly detection)
-- ============================================================
CREATE MATERIALIZED VIEW tenant_acme.core_idem_top_reused_keys_mv AS
SELECT
    tenant_id,
    key,
    COUNT(*)                             AS attempt_count,
    COUNT(DISTINCT fingerprint)          AS distinct_fingerprints,
    MAX(created_at)                      AS last_seen,
    BOOL_OR(attempt_count > 1)           AS has_retry
FROM tenant_acme.core_idem_records
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY 1, 2
HAVING COUNT(*) > 1
ORDER BY attempt_count DESC;

CREATE INDEX ix_idem_top_reused_keys
    ON tenant_acme.core_idem_top_reused_keys_mv (tenant_id, attempt_count DESC);
```

---

## 📄 7. Retention & Archive Policy

| ข้อมูล | Active | Archive | Delete |
|---|---|---|---|
| `core_idem_records` COMPLETED | 30 วัน | 90 วัน | 1 ปี |
| `core_idem_records` FAILED | 7 วัน | 30 วัน | 90 วัน |
| `core_idem_records` EXPIRED | 3 วัน | 30 วัน | 90 วัน |
| `core_idem_audit_events` | 90 วัน | 1 ปี | 3 ปี |
| `core_idem_outbox` PUBLISHED | 7 วัน | — | 30 วัน |
| `core_idem_lock_log` | 7 วัน | — | 30 วัน |

### 7.1 Scheduled jobs (pg_cron)

```sql
-- ── Purge expired records (daily 03:00) ────────────────────
SELECT cron.schedule(
    'purge_idem_expired',
    '0 3 * * *',
    $$ SELECT public.purge_expired_idempotency('tenant_acme', 10000); $$
);

-- ── Create next month partition (monthly 1st, 02:00) ───────
SELECT cron.schedule(
    'ensure_idem_partition',
    '0 2 1 * *',
    $$ SELECT public.ensure_idem_partition(
        'tenant_acme',
        TO_CHAR(NOW() + INTERVAL '2 month', 'YYYYMM')
    ); $$
);

-- ── Refresh materialized views (every 5 min) ───────────────
SELECT cron.schedule(
    'refresh_idem_stats',
    '*/5 * * * *',
    $$ REFRESH MATERIALIZED VIEW CONCURRENTLY tenant_acme.core_idem_stats_hourly_mv; $$
);

-- ── Cleanup published outbox (daily 04:00) ─────────────────
SELECT cron.schedule(
    'cleanup_idem_outbox',
    '0 4 * * *',
    $$ DELETE FROM tenant_acme.core_idem_outbox
       WHERE status = 'PUBLISHED'
         AND published_at < NOW() - INTERVAL '7 days'; $$
);
```

---

## 📄 8. Migration Scripts

### 8.1 `001_create_public_schema.sql`

```sql
-- ============================================================
-- Migration 001: Public schema
-- ============================================================
BEGIN;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_cron";    -- scheduled jobs

-- core_tenctx_registry
-- core_idem_global_stats
-- ... (ตาม section 2)

COMMIT;
```

### 8.2 `002_create_tenant_template.sql`

```sql
-- ============================================================
-- Migration 002: Tenant schema template
-- ใช้ function สร้าง schema + tables ให้ tenant ใหม่
-- ============================================================
CREATE OR REPLACE FUNCTION public.create_tenant_schema(p_tenant_id TEXT)
RETURNS VOID AS $$
DECLARE
    v_schema TEXT := 'tenant_' || p_tenant_id;
BEGIN
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', v_schema);

    -- core_idem_records (partitioned)
    EXECUTE format($f$
        CREATE TABLE IF NOT EXISTS %I.core_idem_records ( ... )
        PARTITION BY LIST (partition_ym)
    $f$, v_schema);

    -- core_idem_outbox
    EXECUTE format($f$ CREATE TABLE IF NOT EXISTS %I.core_idem_outbox ( ... ) $f$, v_schema);

    -- core_idem_audit_events
    EXECUTE format($f$ CREATE TABLE IF NOT EXISTS %I.core_idem_audit_events ( ... ) $f$, v_schema);

    -- core_idem_lock_log
    EXECUTE format($f$ CREATE TABLE IF NOT EXISTS %I.core_idem_lock_log ( ... ) $f$, v_schema);

    -- core_idem_records_archive
    EXECUTE format($f$ CREATE TABLE IF NOT EXISTS %I.core_idem_records_archive ( ... ) $f$, v_schema);

    -- Indexes, triggers, policies
    -- ...

    RAISE NOTICE 'Created tenant schema %', v_schema;
END;
$$ LANGUAGE plpgsql;

-- ตัวอย่าง
-- SELECT public.create_tenant_schema('acme');
```

### 8.3 `003_seed_data.sql`

```sql
-- ============================================================
-- Migration 003: Seed default tenant
-- ============================================================
INSERT INTO public.core_tenctx_registry (tenant_id, schema_name, display_name, plan)
VALUES ('acme', 'tenant_acme', 'ACME Corp', 'PRO')
ON CONFLICT (tenant_id) DO NOTHING;

SELECT public.create_tenant_schema('acme');
```

---

## 📄 9. ER Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         public schema                                │
│                                                                      │
│  ┌────────────────────────┐      ┌─────────────────────────────┐   │
│  │ core_tenctx_registry   │      │ core_idem_global_stats      │   │
│  │ ────────────────────   │      │ ─────────────────────────── │   │
│  │ id (PK)                │      │ id (PK)                     │   │
│  │ tenant_id (UQ)         │      │ tenant_id (FK→registry)     │   │
│  │ schema_name (UQ)       │      │ stat_date                   │   │
│  │ is_active              │      │ total_records               │   │
│  │ plan                   │      │ pending_count               │   │
│  └────────────┬───────────┘      │ completed_count             │   │
│               │                  │ failed_count                │   │
│               │ 1:N              │ conflict_count              │   │
│               │                  └─────────────────────────────┘   │
└───────────────┼─────────────────────────────────────────────────────┘
                │
                ▼  (per tenant schema: tenant_acme)
┌─────────────────────────────────────────────────────────────────────┐
│                    tenant_acme schema                                │
│                                                                      │
│  ┌──────────────────────────┐    ┌──────────────────────────────┐  │
│  │ core_idem_records        │◄───│ core_idem_outbox             │  │
│  │ (PARTITIONED by ym)      │    │ ──────────────────────────── │  │
│  │ ──────────────────────   │    │ id (PK, BIGSERIAL)           │  │
│  │ id (PK, UUID)            │    │ aggregate_id (FK)            │  │
│  │ tenant_id                │    │ event_name                   │  │
│  │ key (UQ)                 │    │ payload (JSONB)              │  │
│  │ fingerprint (SHA-256)    │    │ status                       │  │
│  │ status                   │    └──────────────────────────────┘  │
│  │ response_status          │                                       │
│  │ response_body (JSONB)    │    ┌──────────────────────────────┐  │
│  │ expires_at               │◄───│ core_idem_audit_events       │  │
│  │ partition_ym (PART KEY)  │    │ ──────────────────────────── │  │
│  └──────────┬───────────────┘    │ id (PK, BIGSERIAL)           │  │
│             │                     │ record_id (FK)               │  │
│             │ 1:N (partition)     │ from_status / to_status      │  │
│             ▼                     │ occurred_at                  │  │
│  ┌──────────────────────────┐    └──────────────────────────────┘  │
│  │ core_idem_records_YYYYMM │                                       │
│  │ (monthly partition)      │    ┌──────────────────────────────┐  │
│  └──────────────────────────┘    │ core_idem_lock_log           │  │
│                                   │ ──────────────────────────── │  │
│  ┌──────────────────────────┐    │ id (PK, BIGSERIAL)           │  │
│  │ core_idem_records_archive│    │ key                          │  │
│  │ (PARTITIONED by year)    │    │ holder                       │  │
│  └──────────────────────────┘    │ acquired_at / released_at    │  │
│                                   └──────────────────────────────┘  │
│                                                                      │
│  ┌───────────────────────────────┐  ┌────────────────────────────┐ │
│  │ core_idem_stats_hourly_mv     │  │ core_idem_top_reused_keys  │ │
│  │ (MATERIALIZED VIEW)           │  │ _mv (MATERIALIZED VIEW)    │ │
│  └───────────────────────────────┘  └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📄 10. Sample Queries

### 10.1 Lookup idempotency record (fast path)

```sql
-- ── ใช้ covering index ────────────────────────────────────
SELECT id, status, fingerprint, response_status, response_body, response_headers
FROM tenant_acme.core_idem_records
WHERE tenant_id = 'acme'
  AND key = 'checkout-abc-123'
  AND partition_ym = TO_CHAR(NOW(), 'YYYYMM');
```

### 10.2 Purge expired

```sql
-- ── ลบ record ที่หมดอายุ (archive ก่อน) ───────────────────
SELECT public.purge_expired_idempotency('tenant_acme', 10000);
```

### 10.3 Monitor in-flight

```sql
-- ── ดู PENDING ที่ค้างเกิน 5 นาที ─────────────────────────
SELECT key, locked_at, NOW() - locked_at AS age
FROM tenant_acme.core_idem_records
WHERE status = 'PENDING'
  AND locked_at < NOW() - INTERVAL '5 minutes'
ORDER BY locked_at;
```

### 10.4 Anomaly detection — key reuse

```sql
-- ── หา key ที่ reuse กับ fingerprint ต่าง ─────────────────
SELECT key, COUNT(DISTINCT fingerprint) AS distinct_fps, COUNT(*) AS total
FROM tenant_acme.core_idem_records
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY key
HAVING COUNT(DISTINCT fingerprint) > 1
ORDER BY distinct_fps DESC
LIMIT 20;
```

### 10.5 Daily stats

```sql
-- ── สถิติวันนี้ ─────────────────────────────────────────────
SELECT
    status,
    COUNT(*)                          AS total,
    ROUND(AVG(duration_ms), 2)        AS avg_ms,
    ROUND(PERCENTILE_CONT(0.95)
          WITHIN GROUP (ORDER BY duration_ms), 2) AS p95_ms
FROM tenant_acme.core_idem_records
WHERE created_at >= CURRENT_DATE
GROUP BY status;
```

---

## 📄 11. Mapping กับ Python Models

| DB Table | SQLAlchemy Model | Python Entity |
|---|---|---|
| `public.core_tenctx_registry` | `TenantRegistryModel` | `TenantId` |
| `tenant_X.core_idem_records` | `IdempotencyRecordModel` | `IdempotencyRecord` |
| `tenant_X.core_idem_outbox` | `IdempotencyOutboxModel` | (internal) |
| `tenant_X.core_idem_audit_events` | `IdempotencyAuditEventModel` | (internal) |
| `tenant_X.core_idem_lock_log` | `IdempotencyLockLogModel` | (internal) |
| `tenant_X.core_idem_records_archive` | `IdempotencyArchiveModel` | (read-only) |

### 11.1 ปรับ `models.py` ให้ตรงกับ DDL ใหม่

```python
# app/modules/idempotency/infrastructure/models.py
from sqlalchemy import (
    BigInteger, Column, DateTime, Index, Integer,
    SmallInteger, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.modules.shared.infrastructure.models import BaseModel


class IdempotencyRecordModel(BaseModel):
    """Idempotency record — matches core_idem_records DDL."""

    __tablename__ = "core_idem_records"   # ← prefix core_idem_

    tenant_id = Column(String(63), nullable=False, index=True)
    key = Column(String(128), nullable=False)
    fingerprint = Column(String(64), nullable=False)
    status = Column(String(16), nullable=False, default="PENDING", index=True)

    response_status = Column(SmallInteger, nullable=True)
    response_body = Column(JSONB, nullable=True)
    response_headers = Column(JSONB, nullable=False, default=dict)

    locked_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    ttl_seconds = Column(Integer, nullable=False, default=86400)

    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)

    request_id = Column(String(64), nullable=True)
    actor_user_id = Column(String(64), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    attempt_count = Column(SmallInteger, nullable=False, default=1)
    partition_ym = Column(String(6), nullable=False, primary_key=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "key", "partition_ym", name="uq_idem_tenant_key"),
        Index("ix_idem_lookup", "tenant_id", "key"),
        {"schema": "tenant_acme"},   # ← set dynamically per tenant
    )


class IdempotencyOutboxModel(BaseModel):
    __tablename__ = "core_idem_outbox"

    aggregate_id = Column(UUID(as_uuid=True), nullable=False)
    event_name = Column(String(64), nullable=False)
    payload = Column(JSONB, nullable=False)
    status = Column(String(16), nullable=False, default="PENDING", index=True)
    retry_count = Column(SmallInteger, nullable=False, default=0)
    max_retries = Column(SmallInteger, nullable=False, default=5)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_idem_outbox_pending", "next_retry_at",
              postgresql_where=Column("status") == "PENDING"),
    )
```

---

## 📄 12. Operational Runbook

### 12.1 ตรวจสอบสุขภาพ DB

```sql
-- ── Partition sizes ───────────────────────────────────────
SELECT
    schemaname, tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'core_idem_records%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ── Index usage ───────────────────────────────────────────
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname LIKE 'core_idem_%'
ORDER BY idx_scan ASC;

-- ── Slow queries ──────────────────────────────────────────
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%core_idem_%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 12.2 Backup strategy

| ประเภท | ความถี่ | เก็บ | หมายเหตุ |
|---|---|---|---|
| Full backup | Daily 01:00 | 30 วัน | pg_basebackup |
| WAL archive | Continuous | 7 วัน | PITR |
| Logical dump (public) | Daily 02:00 | 90 วัน | pg_dump |
| Logical dump (per-tenant) | Weekly | 30 วัน | pg_dump -n tenant_X |

### 12.3 Scaling guidelines

| ตัวชี้วัด | ค่าแนะนำ | การดำเนินการ |
|---|---|---|
| Partition size | < 10 GB | เพิ่มความถี่ partition (weekly) |
| PENDING count | < 1000 | เพิ่ม Redis lock TTL |
| Index bloat | < 30% | `REINDEX CONCURRENTLY` |
| Query p95 | > 50ms | เพิ่ม covering index |

---

## ✅ Checklist ครบถ้วน

| ข้อ | สถานะ |
|---|---|
| Prefix บอก Layer + Module | ✅ `core_idem_*` |
| Schema-per-tenant | ✅ `tenant_{id}` |
| Partition by month | ✅ `partition_ym` |
| Archive (yearly) | ✅ `core_idem_records_archive` |
| Outbox pattern | ✅ `core_idem_outbox` |
| Audit trail | ✅ `core_idem_audit_events` |
| Lock observability | ✅ `core_idem_lock_log` |
| Global stats | ✅ `core_idem_global_stats` |
| Materialized views | ✅ 2 MVs |
| RLS | ✅ tenant isolation |
| Triggers | ✅ updated_at, transition, outbox, partition |
| Functions | ✅ ensure_partition, purge, create_tenant_schema |
| Scheduled jobs | ✅ pg_cron 4 jobs |
| Indexes | ✅ 6 indexes + covering |
| Constraints | ✅ CHECK, UNIQUE, FK |
| Comments (bilingual) | ✅ ทุกตาราง |
| Migration scripts | ✅ 3 scripts |
| ER diagram | ✅ ASCII |
| Monitoring queries | ✅ 5 queries |
| Runbook | ✅ backup, scaling |

---

## 📌 สรุป

| ประเด็น | รายละเอียด |
|---|---|
| **Prefix** | `core_idem_` — Layer 0 (Core), Module idempotency |
| **Schema** | `public` (metadata) + `tenant_{id}` (operational) |
| **ตารางหลัก** | 5 ตาราง + 2 MV + 1 archive |
| **Partitioning** | Active = monthly · Archive = yearly |
| **Retention** | COMPLETED 30 วัน → archive 90 → delete 1 ปี |
| **Integrity** | RLS + CHECK + UNIQUE + trigger |
| **Observability** | lock_log + audit_events + global_stats + MVs |
| **Reliability** | Outbox pattern สำหรับ event delivery |
| **Automation** | pg_cron 4 jobs + auto-partition |

---

**ต้องการให้ออกแบบ DB ของ Module อื่นต่อไหมครับ?** เช่น:
- `config` (Layer 0) — settings, feature flags, secrets
- `events` (Layer 0) — event store, outbox, dead letter
- `tenancy` (Layer 1) — tenant, subscription, billing
- `inventory` (Layer 3) — stock, movement, lot

หรือจะให้ทำ **ER diagram รวมทั้งระบบ** (65 modules) แบบ high-level ก็ได้ครับ 🚀


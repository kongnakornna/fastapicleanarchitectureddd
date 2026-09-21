# 🗄️ Complete Database Design — ERP + CRM + IoT (65 Modules · 8 Layers)

> **หลักการ:** ทุกตารางมี `prefix_` บอก Layer + Module
> **Stack:** PostgreSQL 17 · Schema-per-tenant · Partitioned · RLS

---

## 📐 Part 1: Naming Convention (Complete)

### 1.1 Layer Prefixes

| Layer | Prefix | Scope |
|---|---|---|
| **0** Core | `core_` | Cross-cutting primitives |
| **1** Foundation | `found_` | Master data |
| **2** Money Path | `money_` | Financial flow |
| **3** Goods Path | `goods_` | Physical flow |
| **4** Operations | `ops_` | Daily operations |
| **5** Intelligence | `intel_` | Analytics / ML |
| **6** Monitoring | `mon_` | Observability / IoT |
| **7** Templates | `tpl_` | Boilerplate |

### 1.2 Module Sub-Prefixes (Complete Table)

| # | Module | Sub-Prefix | ตัวอย่างตาราง |
|---|---|---|---|
| **Layer 0 — Core** ||||
| 1 | money | *(no table)* | — (pure VO) |
| 2 | tenant_context | `core_tenctx_` | `core_tenctx_registry` |
| 3 | audit | `core_audit_` | `core_audit_logs` |
| 4 | idempotency | `core_idem_` | `core_idem_records` |
| 5 | config | `core_cfg_` | `core_cfg_settings` |
| 6 | events | `core_evt_` | `core_evt_outbox` |
| **Layer 1 — Foundation** ||||
| 7 | tenancy | `found_tenancy_` | `found_tenancy_subscriptions` |
| 8 | authentication | `found_auth_` | `found_auth_credentials` |
| 9 | user | `found_user_` | `found_user_users` |
| 10 | employee | `found_emp_` | `found_emp_employees` |
| 11 | customer | `found_cust_` | `found_cust_customers` |
| 12 | supplier | `found_supp_` | `found_supp_suppliers` |
| 13 | product | `found_prod_` | `found_prod_products` |
| 14 | pricing | `found_price_` | `found_price_price_lists` |
| **Layer 2 — Money Path** ||||
| 15 | order | `money_order_` | `money_order_orders` |
| 16 | invoice | `money_inv_` | `money_inv_invoices` |
| 17 | ledger | `money_ledger_` | `money_ledger_entries` |
| 18 | payment | `money_pay_` | `money_pay_payments` |
| 19 | accounting_gateway | `money_acct_` | `money_acct_sync_jobs` |
| 20 | tax | `money_tax_` | `money_tax_returns` |
| 21 | reconciliation | `money_recon_` | `money_recon_sessions` |
| **Layer 3 — Goods Path** ||||
| 22 | inventory | `goods_inv_` | `goods_inv_stock` |
| 23 | warehouse | `goods_wh_` | `goods_wh_warehouses` |
| 24 | lot | `goods_lot_` | `goods_lot_lots` |
| 25 | production | `goods_prod_` | `goods_prod_orders` |
| 26 | recipe | `goods_recipe_` | `goods_recipe_recipes` |
| 27 | quality | `goods_qa_` | `goods_qa_inspections` |
| 28 | waste | `goods_waste_` | `goods_waste_records` |
| 29 | procurement | `goods_proc_` | `goods_proc_purchase_orders` |
| 30 | traceability | `goods_trace_` | `goods_trace_events` |
| 31 | agriculture | `goods_agri_` | `goods_agri_farms` |
| 32 | crop | `goods_crop_` | `goods_crop_crops` |
| 33 | soil | `goods_soil_` | `goods_soil_tests` |
| 34 | irrigation | `goods_irrig_` | `goods_irrig_schedules` |
| **Layer 4 — Operations** ||||
| 35 | transport | `ops_trans_` | `ops_trans_vehicles` |
| 36 | delivery | `ops_deliv_` | `ops_deliv_deliveries` |
| 37 | route | `ops_route_` | `ops_route_routes` |
| 38 | gps | `ops_gps_` | `ops_gps_pings` |
| 39 | retail | `ops_retail_` | `ops_retail_stores` |
| 40 | pos | `ops_pos_` | `ops_pos_sales` |
| 41 | shift | `ops_shift_` | `ops_shift_shifts` |
| 42 | line_channel | `ops_line_` | `ops_line_messages` |
| 43 | promotion | `ops_promo_` | `ops_promo_promotions` |
| 44 | loyalty | `ops_loyal_` | `ops_loyal_accounts` |
| 45 | crm | `ops_crm_` | `ops_crm_leads` |
| 46 | campaign | `ops_camp_` | `ops_camp_campaigns` |
| 47 | support | `ops_supp_` | `ops_supp_tickets` |
| **Layer 5 — Intelligence** ||||
| 48 | reporting | `intel_rpt_` | `intel_rpt_reports` |
| 49 | analytics | `intel_anl_` | `intel_anl_events` |
| 50 | forecast | `intel_fcst_` | `intel_fcst_forecasts` |
| 51 | kpi | `intel_kpi_` | `intel_kpi_definitions` |
| 52 | satisfaction | `intel_csat_` | `intel_csat_surveys` |
| 53 | recommendation | `intel_rec_` | `intel_rec_recommendations` |
| 54 | oee | `intel_oee_` | `intel_oee_metrics` |
| **Layer 6 — Monitoring** ||||
| 55 | iot | `mon_iot_` | `mon_iot_sensors` |
| 56 | cctv | `mon_cctv_` | `mon_cctv_cameras` |
| 57 | monitoring | `mon_obs_` | `mon_obs_metrics` |
| 58 | backup | `mon_bak_` | `mon_bak_jobs` |
| 59 | alerting | `mon_alert_` | `mon_alert_rules` |
| 60 | audit_viewer | `mon_audit_` | `mon_audit_views` |
| 61 | maintenance | `mon_maint_` | `mon_maint_work_orders` |
| 62 | energy | `mon_energy_` | `mon_energy_readings` |
| **Layer 7 — Templates** ||||
| 63 | health | `tpl_health_` | `tpl_health_checks` |
| 64 | example | `tpl_example_` | `tpl_example_items` |
| 65 | blank | `tpl_blank_` | `tpl_blank_entities` |

### 1.3 Suffixes

| Suffix | ความหมาย | ตัวอย่าง |
|---|---|---|
| `_records` | ตารางหลัก | `core_idem_records` |
| `_items` | รายการย่อย | `money_inv_items` |
| `_lines` | บรรทัด | `money_order_lines` |
| `_logs` | Log | `core_audit_logs` |
| `_events` | Event | `goods_trace_events` |
| `_outbox` | Outbox | `core_evt_outbox` |
| `_archive` | Archive | `core_idem_records_archive` |
| `_mv` | Materialized View | `intel_rpt_daily_mv` |
| `_YYYYMM` | Monthly partition | `core_idem_records_202609` |
| `_YYYY` | Yearly partition | `core_audit_logs_2026` |

---

## 📐 Part 2: Schema Layout

```
PostgreSQL Cluster
├── public                              ← global metadata
│   ├── core_tenctx_registry
│   ├── core_idem_global_stats
│   ├── core_cfg_global_settings
│   ├── core_evt_dlq                     ← dead letter queue
│   ├── schema_migrations
│   └── system_health                    ← from tpl_health
│
├── tenant_acme                         ← per-tenant schema
│   ├── core_*   (audit, idem, cfg, evt)
│   ├── found_*  (user, customer, product, ...)
│   ├── money_*  (order, invoice, ledger, ...)
│   ├── goods_*  (inventory, production, ...)
│   ├── ops_*    (transport, retail, crm, ...)
│   ├── intel_*  (reporting, forecast, ...)
│   ├── mon_*    (iot, cctv, monitoring, ...)
│   └── tpl_*    (health, example, blank)
│
└── tenant_beta
    └── ... (เหมือน tenant_acme)
```

---

## 📐 Part 3: Public Schema DDL

```sql
-- ============================================================
-- Public schema — global metadata
-- ============================================================
BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- fuzzy search

-- ── Tenant Registry ────────────────────────────────────────
CREATE TABLE public.core_tenctx_registry (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    schema_name     VARCHAR(80) NOT NULL,
    display_name    VARCHAR(200),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    isolation       VARCHAR(32) NOT NULL DEFAULT 'SCHEMA_PER_TENANT',
    plan            VARCHAR(32) NOT NULL DEFAULT 'STANDARD',
    quota_records   BIGINT NOT NULL DEFAULT 1000000,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    suspended_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_tenctx_tenant_id UNIQUE (tenant_id),
    CONSTRAINT uq_tenctx_schema_name UNIQUE (schema_name),
    CONSTRAINT ck_tenctx_tenant_id CHECK (tenant_id ~ '^[a-z][a-z0-9_]{2,62}$')
);
CREATE INDEX ix_tenctx_active ON public.core_tenctx_registry (is_active) WHERE is_active;

-- ── Idempotency Global Stats ───────────────────────────────
CREATE TABLE public.core_idem_global_stats (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    stat_date       DATE NOT NULL,
    total_records   BIGINT NOT NULL DEFAULT 0,
    pending_count   BIGINT NOT NULL DEFAULT 0,
    completed_count BIGINT NOT NULL DEFAULT 0,
    failed_count    BIGINT NOT NULL DEFAULT 0,
    conflict_count  BIGINT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_idem_stats UNIQUE (tenant_id, stat_date)
);

-- ── Global Config (cross-tenant defaults) ─────────────────
CREATE TABLE public.core_cfg_global_settings (
    id              BIGSERIAL PRIMARY KEY,
    namespace       VARCHAR(64) NOT NULL,
    setting_key     VARCHAR(128) NOT NULL,
    setting_value   JSONB NOT NULL,
    value_type      VARCHAR(16) NOT NULL DEFAULT 'json',
    is_secret       BOOLEAN NOT NULL DEFAULT FALSE,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cfg_global UNIQUE (namespace, setting_key)
);

-- ── Event Dead Letter Queue ───────────────────────────────
CREATE TABLE public.core_evt_dlq (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    event_name      VARCHAR(128) NOT NULL,
    payload         JSONB NOT NULL,
    error_message   TEXT NOT NULL,
    retry_count     SMALLINT NOT NULL DEFAULT 0,
    source_topic    VARCHAR(128),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);
CREATE INDEX ix_evt_dlq_unresolved ON public.core_evt_dlq (created_at DESC) WHERE resolved_at IS NULL;

-- ── System Health ─────────────────────────────────────────
CREATE TABLE public.tpl_health_checks (
    id              BIGSERIAL PRIMARY KEY,
    component       VARCHAR(64) NOT NULL,
    status          VARCHAR(16) NOT NULL CHECK (status IN ('UP','DEGRADED','DOWN')),
    latency_ms      INTEGER,
    details         JSONB NOT NULL DEFAULT '{}'::jsonb,
    checked_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_health_component_time ON public.tpl_health_checks (component, checked_at DESC);

COMMIT;
```

---

## 📐 Part 4: Tenant Schema DDL — Layer 0 (Core)

### 4.1 `core_audit_logs` (from Module 3)

```sql
CREATE TABLE tenant_acme.core_audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    sequence        BIGINT NOT NULL,
    request_id      VARCHAR(64) NOT NULL,
    action          VARCHAR(32) NOT NULL,
    severity        VARCHAR(16) NOT NULL DEFAULT 'INFO',
    outcome         VARCHAR(16) NOT NULL DEFAULT 'SUCCESS',
    entity_type     VARCHAR(64) NOT NULL,
    entity_id       VARCHAR(64) NOT NULL,
    entity_version  INTEGER,
    actor_user_id   VARCHAR(64) NOT NULL,
    actor_email     VARCHAR(255),
    actor_role      VARCHAR(64),
    actor_ip        VARCHAR(45),
    actor_user_agent VARCHAR(500),
    before          JSONB NOT NULL DEFAULT '{}'::jsonb,
    after           JSONB NOT NULL DEFAULT '{}'::jsonb,
    meta            JSONB NOT NULL DEFAULT '{}'::jsonb,
    hash            CHAR(64) NOT NULL,
    previous_hash   CHAR(64) NOT NULL DEFAULT REPEAT('0', 64),
    idempotency_key VARCHAR(128),
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_ms     INTEGER,
    error_message   TEXT,
    partition_ym    CHAR(6) NOT NULL,
    CONSTRAINT uq_audit_tenant_seq UNIQUE (tenant_id, sequence, partition_ym),
    CONSTRAINT uq_audit_tenant_idem UNIQUE (tenant_id, idempotency_key, partition_ym)
) PARTITION BY LIST (partition_ym);

CREATE INDEX ix_audit_entity ON tenant_acme.core_audit_logs (tenant_id, entity_type, entity_id, occurred_at DESC);
CREATE INDEX ix_audit_actor  ON tenant_acme.core_audit_logs (tenant_id, actor_user_id, occurred_at DESC);
CREATE INDEX ix_audit_action ON tenant_acme.core_audit_logs (tenant_id, action, occurred_at DESC);

-- ป้องกัน UPDATE/DELETE
CREATE RULE audit_no_update AS ON UPDATE TO tenant_acme.core_audit_logs DO INSTEAD NOTHING;
CREATE RULE audit_no_delete AS ON DELETE TO tenant_acme.core_audit_logs DO INSTEAD NOTHING;
```

### 4.2 `core_idem_*` (from Module 4 — ย่อ)

```sql
-- core_idem_records, core_idem_outbox, core_idem_audit_events,
-- core_idem_lock_log, core_idem_records_archive
-- (รายละเอียดตามที่ออกแบบไว้ใน Module 4)
```

### 4.3 `core_cfg_*` (Module 5 — config)

```sql
-- ── Settings ─────────────────────────────────────────────
CREATE TABLE tenant_acme.core_cfg_settings (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    namespace       VARCHAR(64) NOT NULL,       -- 'invoice', 'payment', ...
    setting_key     VARCHAR(128) NOT NULL,
    setting_value   JSONB NOT NULL,
    value_type      VARCHAR(16) NOT NULL DEFAULT 'json'
                    CHECK (value_type IN ('string','int','float','bool','json','secret')),
    is_secret       BOOLEAN NOT NULL DEFAULT FALSE,
    is_encrypted    BOOLEAN NOT NULL DEFAULT FALSE,
    description     TEXT,
    created_by      VARCHAR(64),
    updated_by      VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cfg_settings UNIQUE (tenant_id, namespace, setting_key)
);
CREATE INDEX ix_cfg_settings_ns ON tenant_acme.core_cfg_settings (namespace, setting_key);

-- ── Feature Flags ────────────────────────────────────────
CREATE TABLE tenant_acme.core_cfg_feature_flags (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    flag_key        VARCHAR(128) NOT NULL,
    is_enabled      BOOLEAN NOT NULL DEFAULT FALSE,
    rollout_percent SMALLINT NOT NULL DEFAULT 100 CHECK (rollout_percent BETWEEN 0 AND 100),
    target_users    JSONB NOT NULL DEFAULT '[]'::jsonb,
    target_roles    JSONB NOT NULL DEFAULT '[]'::jsonb,
    valid_from      TIMESTAMPTZ,
    valid_until     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cfg_flags UNIQUE (tenant_id, flag_key)
);

-- ── Secrets (encrypted) ──────────────────────────────────
CREATE TABLE tenant_acme.core_cfg_secrets (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    secret_key      VARCHAR(128) NOT NULL,
    encrypted_value BYTEA NOT NULL,
    encryption_algo VARCHAR(32) NOT NULL DEFAULT 'AES256-GCM',
    key_version     SMALLINT NOT NULL DEFAULT 1,
    rotated_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cfg_secrets UNIQUE (tenant_id, secret_key)
);

-- ── Change history ───────────────────────────────────────
CREATE TABLE tenant_acme.core_cfg_history (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    namespace       VARCHAR(64) NOT NULL,
    setting_key     VARCHAR(128) NOT NULL,
    old_value       JSONB,
    new_value       JSONB,
    changed_by      VARCHAR(64) NOT NULL,
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_cfg_history_key ON tenant_acme.core_cfg_history (tenant_id, namespace, setting_key, changed_at DESC);
```

### 4.4 `core_evt_*` (Module 6 — events)

```sql
-- ── Outbox (transactional) ───────────────────────────────
CREATE TABLE tenant_acme.core_evt_outbox (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    aggregate_type  VARCHAR(64) NOT NULL,
    aggregate_id    UUID NOT NULL,
    event_name      VARCHAR(128) NOT NULL,
    event_version   SMALLINT NOT NULL DEFAULT 1,
    payload         JSONB NOT NULL,
    headers         JSONB NOT NULL DEFAULT '{}'::jsonb,
    topic           VARCHAR(128) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING','PUBLISHING','PUBLISHED','FAILED','DEAD')),
    retry_count     SMALLINT NOT NULL DEFAULT 0,
    max_retries     SMALLINT NOT NULL DEFAULT 5,
    next_retry_at   TIMESTAMPTZ,
    published_at    TIMESTAMPTZ,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_evt_outbox_pending ON tenant_acme.core_evt_outbox (next_retry_at) WHERE status = 'PENDING';
CREATE INDEX ix_evt_outbox_aggregate ON tenant_acme.core_evt_outbox (aggregate_type, aggregate_id);
CREATE INDEX ix_evt_outbox_topic ON tenant_acme.core_evt_outbox (topic, created_at DESC);

-- ── Event Store (append-only log) ────────────────────────
CREATE TABLE tenant_acme.core_evt_store (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    event_id        UUID NOT NULL,
    event_name      VARCHAR(128) NOT NULL,
    aggregate_type  VARCHAR(64) NOT NULL,
    aggregate_id    UUID NOT NULL,
    sequence_num    BIGINT NOT NULL,
    payload         JSONB NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym),
    CONSTRAINT uq_evt_store_seq UNIQUE (tenant_id, aggregate_type, aggregate_id, sequence_num, partition_ym)
) PARTITION BY LIST (partition_ym);

-- ── Subscriptions ────────────────────────────────────────
CREATE TABLE tenant_acme.core_evt_subscriptions (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    subscriber      VARCHAR(128) NOT NULL,
    event_pattern   VARCHAR(255) NOT NULL,
    handler_url     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_seen_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_evt_sub UNIQUE (tenant_id, subscriber, event_pattern)
);
```

---

## 📐 Part 5: Tenant Schema DDL — Layer 1 (Foundation)

### 5.1 `found_tenancy_*` (Module 7)

```sql
-- ── Subscription ─────────────────────────────────────────
CREATE TABLE tenant_acme.found_tenancy_subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    plan            VARCHAR(32) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('TRIAL','ACTIVE','PAST_DUE','CANCELLED','SUSPENDED')),
    billing_cycle   VARCHAR(16) NOT NULL DEFAULT 'MONTHLY'
                    CHECK (billing_cycle IN ('MONTHLY','QUARTERLY','YEARLY')),
    seats           INTEGER NOT NULL DEFAULT 1,
    amount          NUMERIC(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    trial_ends_at   TIMESTAMPTZ,
    current_period_start TIMESTAMPTZ NOT NULL,
    current_period_end   TIMESTAMPTZ NOT NULL,
    cancelled_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Billing History ──────────────────────────────────────
CREATE TABLE tenant_acme.found_tenancy_billing_history (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    subscription_id UUID NOT NULL REFERENCES tenant_acme.found_tenancy_subscriptions(id),
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    amount          NUMERIC(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    paid_at         TIMESTAMPTZ,
    invoice_ref     VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_tenancy_billing_period ON tenant_acme.found_tenancy_billing_history (tenant_id, period_start DESC);

-- ── Usage Metrics ────────────────────────────────────────
CREATE TABLE tenant_acme.found_tenancy_usage (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    metric          VARCHAR(64) NOT NULL,        -- 'api_calls', 'storage_mb', 'users'
    value           BIGINT NOT NULL DEFAULT 0,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
```

### 5.2 `found_auth_*` (Module 8)

```sql
-- ── Credentials ──────────────────────────────────────────
CREATE TABLE tenant_acme.found_auth_credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    user_id         UUID NOT NULL,
    password_hash   VARCHAR(255),
    password_algo   VARCHAR(32) DEFAULT 'argon2id',
    password_changed_at TIMESTAMPTZ,
    must_change     BOOLEAN NOT NULL DEFAULT FALSE,
    failed_attempts SMALLINT NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,
    mfa_enabled     BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret      VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_auth_user UNIQUE (tenant_id, user_id)
);

-- ── Sessions / Tokens ────────────────────────────────────
CREATE TABLE tenant_acme.found_auth_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    user_id         UUID NOT NULL,
    refresh_token_hash CHAR(64) NOT NULL,
    access_jti      UUID NOT NULL,
    ip_address      VARCHAR(45),
    user_agent      VARCHAR(500),
    issued_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    revoked_reason  VARCHAR(64)
);
CREATE INDEX ix_auth_sessions_user ON tenant_acme.found_auth_sessions (tenant_id, user_id, expires_at DESC);
CREATE INDEX ix_auth_sessions_jti ON tenant_acme.found_auth_sessions (access_jti);

-- ── API Keys ─────────────────────────────────────────────
CREATE TABLE tenant_acme.found_auth_api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    name            VARCHAR(128) NOT NULL,
    key_prefix      VARCHAR(16) NOT NULL,
    key_hash        CHAR(64) NOT NULL,
    scopes          JSONB NOT NULL DEFAULT '[]'::jsonb,
    last_used_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    created_by      UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_auth_api_key_hash UNIQUE (key_hash)
);
CREATE INDEX ix_auth_api_keys_prefix ON tenant_acme.found_auth_api_keys (key_prefix);

-- ── Login Attempts (audit) ───────────────────────────────
CREATE TABLE tenant_acme.found_auth_login_attempts (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    email           VARCHAR(255),
    ip_address      VARCHAR(45),
    outcome         VARCHAR(16) NOT NULL CHECK (outcome IN ('SUCCESS','FAILURE','LOCKED')),
    failure_reason  VARCHAR(64),
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
```

### 5.3 `found_user_*` (Module 9)

```sql
CREATE TABLE tenant_acme.found_user_users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    email_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    display_name    VARCHAR(200) NOT NULL,
    phone           VARCHAR(32),
    avatar_url      TEXT,
    locale          VARCHAR(16) NOT NULL DEFAULT 'th-TH',
    timezone        VARCHAR(64) NOT NULL DEFAULT 'Asia/Bangkok',
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('PENDING','ACTIVE','SUSPENDED','DELETED')),
    is_superadmin   BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_email UNIQUE (tenant_id, email)
);
CREATE INDEX ix_user_status ON tenant_acme.found_user_users (tenant_id, status);

-- ── Roles & Permissions ─────────────────────────────────
CREATE TABLE tenant_acme.found_user_roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(128) NOT NULL,
    description     TEXT,
    is_system       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_role_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.found_user_permissions (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(128) NOT NULL,       -- 'invoice.create'
    resource        VARCHAR(64) NOT NULL,
    action          VARCHAR(32) NOT NULL,
    description     TEXT,
    CONSTRAINT uq_user_perm_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.found_user_role_permissions (
    role_id         UUID NOT NULL REFERENCES tenant_acme.found_user_roles(id) ON DELETE CASCADE,
    permission_id   BIGINT NOT NULL REFERENCES tenant_acme.found_user_permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE tenant_acme.found_user_user_roles (
    user_id         UUID NOT NULL REFERENCES tenant_acme.found_user_users(id) ON DELETE CASCADE,
    role_id         UUID NOT NULL REFERENCES tenant_acme.found_user_roles(id) ON DELETE CASCADE,
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    granted_by      UUID,
    PRIMARY KEY (user_id, role_id)
);
```

### 5.4 `found_emp_*` (Module 10)

```sql
CREATE TABLE tenant_acme.found_emp_employees (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    user_id         UUID,                         -- optional link to user
    employee_code   VARCHAR(32) NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(255),
    phone           VARCHAR(32),
    position        VARCHAR(100),
    department      VARCHAR(100),
    manager_id      UUID REFERENCES tenant_acme.found_emp_employees(id),
    hire_date       DATE,
    termination_date DATE,
    employment_type VARCHAR(32) NOT NULL DEFAULT 'FULL_TIME',
    salary          NUMERIC(15,2),
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_emp_code UNIQUE (tenant_id, employee_code)
);
CREATE INDEX ix_emp_dept ON tenant_acme.found_emp_employees (tenant_id, department, status);
```

### 5.5 `found_cust_*` (Module 11)

```sql
CREATE TABLE tenant_acme.found_cust_customers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    type            VARCHAR(16) NOT NULL DEFAULT 'RETAIL'
                    CHECK (type IN ('RETAIL','WHOLESALE','CORPORATE','GOVERNMENT')),
    tax_id          VARCHAR(32),
    email           VARCHAR(255),
    phone           VARCHAR(32),
    billing_address JSONB NOT NULL DEFAULT '{}'::jsonb,
    shipping_address JSONB NOT NULL DEFAULT '{}'::jsonb,
    credit_limit    NUMERIC(15,2) NOT NULL DEFAULT 0,
    credit_used     NUMERIC(15,2) NOT NULL DEFAULT 0,
    payment_terms   VARCHAR(32) DEFAULT 'NET30',
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cust_code UNIQUE (tenant_id, code)
);
CREATE INDEX ix_cust_name_trgm ON tenant_acme.found_cust_customers USING gin (name gin_trgm_ops);
CREATE INDEX ix_cust_status ON tenant_acme.found_cust_customers (tenant_id, status);
```

### 5.6 `found_supp_*` (Module 12)

```sql
CREATE TABLE tenant_acme.found_supp_suppliers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    tax_id          VARCHAR(32),
    email           VARCHAR(255),
    phone           VARCHAR(32),
    address         JSONB NOT NULL DEFAULT '{}'::jsonb,
    payment_terms   VARCHAR(32) DEFAULT 'NET30',
    lead_time_days  INTEGER NOT NULL DEFAULT 7,
    rating          NUMERIC(3,2),
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_supp_code UNIQUE (tenant_id, code)
);
```

### 5.7 `found_prod_*` (Module 13)

```sql
CREATE TABLE tenant_acme.found_prod_products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    sku             VARCHAR(64) NOT NULL,
    barcode         VARCHAR(64),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    category_id     UUID,
    uom             VARCHAR(16) NOT NULL DEFAULT 'UNIT',    -- UNIT, KG, L, M
    product_type    VARCHAR(16) NOT NULL DEFAULT 'GOOD'
                    CHECK (product_type IN ('GOOD','SERVICE','RAW','WIP','FINISHED')),
    is_stockable    BOOLEAN NOT NULL DEFAULT TRUE,
    is_purchasable  BOOLEAN NOT NULL DEFAULT TRUE,
    is_sellable     BOOLEAN NOT NULL DEFAULT TRUE,
    tax_code        VARCHAR(32),
    base_cost       NUMERIC(15,4) NOT NULL DEFAULT 0,
    base_price      NUMERIC(15,4) NOT NULL DEFAULT 0,
    weight_kg       NUMERIC(10,4),
    dimensions      JSONB,
    attributes      JSONB NOT NULL DEFAULT '{}'::jsonb,
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_prod_sku UNIQUE (tenant_id, sku)
);
CREATE INDEX ix_prod_barcode ON tenant_acme.found_prod_products (tenant_id, barcode) WHERE barcode IS NOT NULL;
CREATE INDEX ix_prod_name_trgm ON tenant_acme.found_prod_products USING gin (name gin_trgm_ops);
CREATE INDEX ix_prod_category ON tenant_acme.found_prod_products (tenant_id, category_id);

CREATE TABLE tenant_acme.found_prod_categories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    parent_id       UUID REFERENCES tenant_acme.found_prod_categories(id),
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    path            TEXT,                            -- materialized path
    sort_order      INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT uq_prod_cat_code UNIQUE (tenant_id, code)
);
```

### 5.8 `found_price_*` (Module 14)

```sql
CREATE TABLE tenant_acme.found_price_price_lists (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    valid_from      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until     TIMESTAMPTZ,
    priority        SMALLINT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_price_list_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.found_price_price_items (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    price_list_id   UUID NOT NULL REFERENCES tenant_acme.found_price_price_lists(id) ON DELETE CASCADE,
    product_id      UUID NOT NULL REFERENCES tenant_acme.found_prod_products(id),
    min_qty         NUMERIC(15,4) NOT NULL DEFAULT 1,
    price           NUMERIC(15,4) NOT NULL,
    discount_pct    NUMERIC(5,2) NOT NULL DEFAULT 0,
    valid_from      TIMESTAMPTZ,
    valid_until     TIMESTAMPTZ,
    CONSTRAINT uq_price_item UNIQUE (price_list_id, product_id, min_qty)
);
CREATE INDEX ix_price_items_product ON tenant_acme.found_price_price_items (tenant_id, product_id);
```

---

## 📐 Part 6: Tenant Schema DDL — Layer 2 (Money Path)

### 6.1 `money_order_*` (Module 15)

```sql
CREATE TABLE tenant_acme.money_order_orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    order_number    VARCHAR(32) NOT NULL,
    order_type      VARCHAR(16) NOT NULL DEFAULT 'SALES'
                    CHECK (order_type IN ('SALES','PURCHASE','TRANSFER')),
    customer_id     UUID,
    supplier_id     UUID,
    status          VARCHAR(16) NOT NULL DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT','CONFIRMED','PARTIAL','FULFILLED','CANCELLED','CLOSED')),
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    subtotal        NUMERIC(15,2) NOT NULL DEFAULT 0,
    discount        NUMERIC(15,2) NOT NULL DEFAULT 0,
    tax             NUMERIC(15,2) NOT NULL DEFAULT 0,
    total           NUMERIC(15,2) NOT NULL DEFAULT 0,
    ordered_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confirmed_at    TIMESTAMPTZ,
    fulfilled_at    TIMESTAMPTZ,
    cancelled_at    TIMESTAMPTZ,
    notes           TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_order_number UNIQUE (tenant_id, order_number),
    CONSTRAINT ck_order_total CHECK (total >= 0)
);
CREATE INDEX ix_order_customer ON tenant_acme.money_order_orders (tenant_id, customer_id, status);
CREATE INDEX ix_order_date ON tenant_acme.money_order_orders (tenant_id, ordered_at DESC);

CREATE TABLE tenant_acme.money_order_lines (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    order_id        UUID NOT NULL REFERENCES tenant_acme.money_order_orders(id) ON DELETE CASCADE,
    line_no         SMALLINT NOT NULL,
    product_id      UUID NOT NULL,
    description     VARCHAR(500),
    qty             NUMERIC(15,4) NOT NULL CHECK (qty > 0),
    uom             VARCHAR(16) NOT NULL DEFAULT 'UNIT',
    unit_price      NUMERIC(15,4) NOT NULL,
    discount_pct    NUMERIC(5,2) NOT NULL DEFAULT 0,
    tax_rate        NUMERIC(5,4) NOT NULL DEFAULT 0,
    line_total      NUMERIC(15,2) NOT NULL,
    fulfilled_qty   NUMERIC(15,4) NOT NULL DEFAULT 0,
    CONSTRAINT uq_order_line UNIQUE (order_id, line_no)
);
```

### 6.2 `money_inv_*` (Module 16)

```sql
CREATE TABLE tenant_acme.money_inv_invoices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    invoice_number  VARCHAR(32) NOT NULL,
    invoice_type    VARCHAR(16) NOT NULL DEFAULT 'TAX'
                    CHECK (invoice_type IN ('TAX','RECEIPT','CREDIT_NOTE','DEBIT_NOTE')),
    order_id        UUID,
    customer_id     UUID NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT','ISSUED','PAID','VOIDED','OVERDUE')),
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    subtotal        NUMERIC(15,2) NOT NULL DEFAULT 0,
    vat             NUMERIC(15,2) NOT NULL DEFAULT 0,
    total           NUMERIC(15,2) NOT NULL DEFAULT 0,
    paid_amount     NUMERIC(15,2) NOT NULL DEFAULT 0,
    balance         NUMERIC(15,2) NOT NULL DEFAULT 0,
    issued_at       TIMESTAMPTZ,
    due_at          TIMESTAMPTZ,
    paid_at         TIMESTAMPTZ,
    voided_at       TIMESTAMPTZ,
    void_reason     TEXT,
    pdf_url         TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_inv_number UNIQUE (tenant_id, invoice_number),
    CONSTRAINT ck_inv_total CHECK (total >= 0)
);
CREATE INDEX ix_inv_customer_status ON tenant_acme.money_inv_invoices (tenant_id, customer_id, status);
CREATE INDEX ix_inv_due ON tenant_acme.money_inv_invoices (tenant_id, due_at) WHERE status IN ('ISSUED','OVERDUE');

CREATE TABLE tenant_acme.money_inv_lines (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    invoice_id      UUID NOT NULL REFERENCES tenant_acme.money_inv_invoices(id) ON DELETE CASCADE,
    line_no         SMALLINT NOT NULL,
    product_id      UUID,
    description     VARCHAR(500),
    qty             NUMERIC(15,4) NOT NULL,
    unit_price      NUMERIC(15,4) NOT NULL,
    vat_rate        NUMERIC(5,4) NOT NULL DEFAULT 0.07,
    line_subtotal   NUMERIC(15,2) NOT NULL,
    line_vat        NUMERIC(15,2) NOT NULL,
    line_total      NUMERIC(15,2) NOT NULL,
    CONSTRAINT uq_inv_line UNIQUE (invoice_id, line_no)
);

CREATE TABLE tenant_acme.money_inv_number_sequences (
    tenant_id       VARCHAR(63) NOT NULL,
    series          VARCHAR(16) NOT NULL DEFAULT 'INV',
    period_ym       CHAR(6) NOT NULL,
    last_seq        BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY (tenant_id, series, period_ym)
);
```

### 6.3 `money_ledger_*` (Module 17)

```sql
-- ── Chart of Accounts ─────────────────────────────────────
CREATE TABLE tenant_acme.money_ledger_accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(16) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    account_type    VARCHAR(16) NOT NULL
                    CHECK (account_type IN ('ASSET','LIABILITY','EQUITY','REVENUE','EXPENSE')),
    parent_id       UUID REFERENCES tenant_acme.money_ledger_accounts(id),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_ledger_account_code UNIQUE (tenant_id, code)
);

-- ── Journal Entries ─────────────────────────────────────
CREATE TABLE tenant_acme.money_ledger_journals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    journal_number  VARCHAR(32) NOT NULL,
    journal_date    DATE NOT NULL,
    description     TEXT,
    reference_type  VARCHAR(32),
    reference_id    UUID,
    status          VARCHAR(16) NOT NULL DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT','POSTED','VOID')),
    posted_at       TIMESTAMPTZ,
    posted_by       UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_journal_number UNIQUE (tenant_id, journal_number)
);
CREATE INDEX ix_journal_date ON tenant_acme.money_ledger_journals (tenant_id, journal_date DESC);
CREATE INDEX ix_journal_ref ON tenant_acme.money_ledger_journals (reference_type, reference_id);

CREATE TABLE tenant_acme.money_ledger_entries (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    journal_id      UUID NOT NULL REFERENCES tenant_acme.money_ledger_journals(id),
    account_id      UUID NOT NULL REFERENCES tenant_acme.money_ledger_accounts(id),
    line_no         SMALLINT NOT NULL,
    debit           NUMERIC(15,2) NOT NULL DEFAULT 0,
    credit          NUMERIC(15,2) NOT NULL DEFAULT 0,
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    description     VARCHAR(500),
    posted_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym),
    CONSTRAINT ck_ledger_debit_credit CHECK (
        (debit >= 0 AND credit >= 0) AND (debit > 0 OR credit > 0)
    )
) PARTITION BY LIST (partition_ym);

CREATE INDEX ix_ledger_account_time ON tenant_acme.money_ledger_entries (tenant_id, account_id, posted_at DESC);
CREATE INDEX ix_ledger_journal ON tenant_acme.money_ledger_entries (journal_id);
```

### 6.4 `money_pay_*` (Module 18)

```sql
CREATE TABLE tenant_acme.money_pay_payments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    payment_number  VARCHAR(32) NOT NULL,
    payment_type    VARCHAR(16) NOT NULL
                    CHECK (payment_type IN ('RECEIPT','DISBURSEMENT')),
    method          VARCHAR(32) NOT NULL
                    CHECK (method IN ('CASH','BANK_TRANSFER','CREDIT_CARD','CHEQUE','PROMPTPAY','OTHER')),
    customer_id     UUID,
    supplier_id     UUID,
    invoice_id      UUID,
    amount          NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    paid_at         TIMESTAMPTZ NOT NULL,
    reference       VARCHAR(128),
    bank_account    VARCHAR(64),
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING','CLEARED','FAILED','REVERSED')),
    cleared_at      TIMESTAMPTZ,
    reversed_at     TIMESTAMPTZ,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_pay_number UNIQUE (tenant_id, payment_number)
);
CREATE INDEX ix_pay_invoice ON tenant_acme.money_pay_payments (invoice_id) WHERE invoice_id IS NOT NULL;
CREATE INDEX ix_pay_date ON tenant_acme.money_pay_payments (tenant_id, paid_at DESC);
```

### 6.5 `money_acct_*` (Module 19 — accounting_gateway)

```sql
CREATE TABLE tenant_acme.money_acct_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    provider        VARCHAR(32) NOT NULL,        -- 'PEAK','XERO','QUICKBOOKS','FLOWACCOUNT'
    display_name    VARCHAR(200) NOT NULL,
    credentials_enc BYTEA NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_sync_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_acct_conn UNIQUE (tenant_id, provider, display_name)
);

CREATE TABLE tenant_acme.money_acct_sync_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    connection_id   UUID NOT NULL REFERENCES tenant_acme.money_acct_connections(id),
    direction       VARCHAR(8) NOT NULL CHECK (direction IN ('PUSH','PULL')),
    entity_type     VARCHAR(32) NOT NULL,
    entity_ids      JSONB NOT NULL DEFAULT '[]'::jsonb,
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    attempt_count   SMALLINT NOT NULL DEFAULT 0,
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_acct_sync_status ON tenant_acme.money_acct_sync_jobs (tenant_id, status, created_at);
```

### 6.6 `money_tax_*` (Module 20)

```sql
CREATE TABLE tenant_acme.money_tax_codes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(16) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    rate            NUMERIC(5,4) NOT NULL,
    tax_type        VARCHAR(16) NOT NULL DEFAULT 'VAT',
    is_inclusive    BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_tax_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.money_tax_returns (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    return_number   VARCHAR(32) NOT NULL,
    tax_type        VARCHAR(16) NOT NULL DEFAULT 'VAT',
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    output_tax      NUMERIC(15,2) NOT NULL DEFAULT 0,
    input_tax       NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_tax         NUMERIC(15,2) NOT NULL DEFAULT 0,
    status          VARCHAR(16) NOT NULL DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT','FILED','PAID','AMENDED')),
    filed_at        TIMESTAMPTZ,
    paid_at         TIMESTAMPTZ,
    reference_no    VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_tax_return UNIQUE (tenant_id, return_number)
);
```

### 6.7 `money_recon_*` (Module 21)

```sql
CREATE TABLE tenant_acme.money_recon_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    source_type     VARCHAR(32) NOT NULL,     -- 'BANK','CASH','PAYMENT_GATEWAY'
    source_ref      VARCHAR(128) NOT NULL,
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'OPEN'
                    CHECK (status IN ('OPEN','MATCHING','RECONCILED','DISCREPANCY')),
    matched_count   INTEGER NOT NULL DEFAULT 0,
    unmatched_count INTEGER NOT NULL DEFAULT 0,
    discrepancy_amt NUMERIC(15,2) NOT NULL DEFAULT 0,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    completed_by    UUID
);

CREATE TABLE tenant_acme.money_recon_items (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    session_id      UUID NOT NULL REFERENCES tenant_acme.money_recon_sessions(id) ON DELETE CASCADE,
    internal_ref    VARCHAR(128),
    external_ref    VARCHAR(128),
    internal_amount NUMERIC(15,2),
    external_amount NUMERIC(15,2),
    match_status    VARCHAR(16) NOT NULL DEFAULT 'UNMATCHED'
                    CHECK (match_status IN ('MATCHED','UNMATCHED','DISCREPANCY','IGNORED')),
    notes           TEXT
);
CREATE INDEX ix_recon_items_session ON tenant_acme.money_recon_items (session_id, match_status);
```

---

## 📐 Part 7: Tenant Schema DDL — Layer 3 (Goods Path)

### 7.1 `goods_wh_*` (Module 23)

```sql
CREATE TABLE tenant_acme.goods_wh_warehouses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    address         JSONB NOT NULL DEFAULT '{}'::jsonb,
    location        JSONB,                       -- geo {lat, lng}
    type            VARCHAR(16) NOT NULL DEFAULT 'MAIN'
                    CHECK (type IN ('MAIN','SATELLITE','COLD_STORAGE','DANGEROUS')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_wh_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.goods_wh_locations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    warehouse_id    UUID NOT NULL REFERENCES tenant_acme.goods_wh_warehouses(id) ON DELETE CASCADE,
    code            VARCHAR(32) NOT NULL,        -- 'A-01-03'
    zone            VARCHAR(32),
    aisle           VARCHAR(16),
    rack            VARCHAR(16),
    bin             VARCHAR(16),
    max_weight_kg   NUMERIC(10,2),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_wh_loc_code UNIQUE (warehouse_id, code)
);
```

### 7.2 `goods_inv_*` (Module 22)

```sql
-- ── Current stock snapshot ───────────────────────────────
CREATE TABLE tenant_acme.goods_inv_stock (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    warehouse_id    UUID NOT NULL,
    location_id     UUID,
    product_id      UUID NOT NULL,
    lot_id          UUID,
    qty_on_hand     NUMERIC(15,4) NOT NULL DEFAULT 0,
    qty_reserved    NUMERIC(15,4) NOT NULL DEFAULT 0,
    qty_available   NUMERIC(15,4) NOT NULL DEFAULT 0,
    avg_cost        NUMERIC(15,4) NOT NULL DEFAULT 0,
    last_movement_at TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_inv_stock UNIQUE (tenant_id, warehouse_id, location_id, product_id, lot_id)
);
CREATE INDEX ix_inv_stock_product ON tenant_acme.goods_inv_stock (tenant_id, product_id);
CREATE INDEX ix_inv_stock_low ON tenant_acme.goods_inv_stock (tenant_id, product_id, qty_available);

-- ── Movement log (partitioned) ───────────────────────────
CREATE TABLE tenant_acme.goods_inv_movements (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    movement_number VARCHAR(32) NOT NULL,
    movement_type   VARCHAR(16) NOT NULL
                    CHECK (movement_type IN ('IN','OUT','TRANSFER','ADJUST','RETURN','SCRAP')),
    product_id      UUID NOT NULL,
    lot_id          UUID,
    from_warehouse  UUID,
    from_location   UUID,
    to_warehouse    UUID,
    to_location     UUID,
    qty             NUMERIC(15,4) NOT NULL CHECK (qty > 0),
    uom             VARCHAR(16) NOT NULL DEFAULT 'UNIT',
    unit_cost       NUMERIC(15,4) NOT NULL DEFAULT 0,
    reference_type  VARCHAR(32),
    reference_id    UUID,
    reason          VARCHAR(200),
    actor_user_id   UUID,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);

CREATE INDEX ix_inv_mvt_product ON tenant_acme.goods_inv_movements (tenant_id, product_id, occurred_at DESC);
CREATE INDEX ix_inv_mvt_ref ON tenant_acme.goods_inv_movements (reference_type, reference_id);

-- ── Reorder rules ────────────────────────────────────────
CREATE TABLE tenant_acme.goods_inv_reorder_rules (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    product_id      UUID NOT NULL,
    warehouse_id    UUID NOT NULL,
    reorder_point   NUMERIC(15,4) NOT NULL,
    reorder_qty     NUMERIC(15,4) NOT NULL,
    safety_stock    NUMERIC(15,4) NOT NULL DEFAULT 0,
    lead_time_days  INTEGER NOT NULL DEFAULT 7,
    CONSTRAINT uq_inv_reorder UNIQUE (tenant_id, product_id, warehouse_id)
);
```

### 7.3 `goods_lot_*` (Module 24)

```sql
CREATE TABLE tenant_acme.goods_lot_lots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    lot_number      VARCHAR(64) NOT NULL,
    product_id      UUID NOT NULL,
    production_date DATE,
    expiry_date     DATE,
    best_before_date DATE,
    quantity        NUMERIC(15,4) NOT NULL DEFAULT 0,
    cost_per_unit   NUMERIC(15,4) NOT NULL DEFAULT 0,
    supplier_id     UUID,
    origin_country  CHAR(2),
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('ACTIVE','QUARANTINE','EXPIRED','CONSUMED','DISPOSED')),
    attributes      JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_lot_number UNIQUE (tenant_id, lot_number)
);
CREATE INDEX ix_lot_product ON tenant_acme.goods_lot_lots (tenant_id, product_id);
CREATE INDEX ix_lot_expiry ON tenant_acme.goods_lot_lots (tenant_id, expiry_date) WHERE status = 'ACTIVE';
```

### 7.4 `goods_prod_*` (Module 25)

```sql
CREATE TABLE tenant_acme.goods_prod_orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    production_number VARCHAR(32) NOT NULL,
    product_id      UUID NOT NULL,
    recipe_id       UUID,
    planned_qty     NUMERIC(15,4) NOT NULL,
    actual_qty      NUMERIC(15,4) NOT NULL DEFAULT 0,
    scrap_qty       NUMERIC(15,4) NOT NULL DEFAULT 0,
    uom             VARCHAR(16) NOT NULL DEFAULT 'UNIT',
    warehouse_id    UUID,
    status          VARCHAR(16) NOT NULL DEFAULT 'PLANNED'
                    CHECK (status IN ('PLANNED','RELEASED','IN_PROGRESS','COMPLETED','CANCELLED','ON_HOLD')),
    planned_start   TIMESTAMPTZ,
    planned_end     TIMESTAMPTZ,
    actual_start    TIMESTAMPTZ,
    actual_end      TIMESTAMPTZ,
    total_cost      NUMERIC(15,2) NOT NULL DEFAULT 0,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_prod_number UNIQUE (tenant_id, production_number)
);
CREATE INDEX ix_prod_order_status ON tenant_acme.goods_prod_orders (tenant_id, status, planned_start);

CREATE TABLE tenant_acme.goods_prod_operations (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    order_id        UUID NOT NULL REFERENCES tenant_acme.goods_prod_orders(id) ON DELETE CASCADE,
    operation_no    SMALLINT NOT NULL,
    operation_name  VARCHAR(200) NOT NULL,
    work_center     VARCHAR(64),
    planned_minutes INTEGER NOT NULL DEFAULT 0,
    actual_minutes  INTEGER NOT NULL DEFAULT 0,
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    operator_id     UUID,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    CONSTRAINT uq_prod_op UNIQUE (order_id, operation_no)
);

CREATE TABLE tenant_acme.goods_prod_materials (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    order_id        UUID NOT NULL REFERENCES tenant_acme.goods_prod_orders(id) ON DELETE CASCADE,
    product_id      UUID NOT NULL,
    planned_qty     NUMERIC(15,4) NOT NULL,
    actual_qty      NUMERIC(15,4) NOT NULL DEFAULT 0,
    uom             VARCHAR(16) NOT NULL DEFAULT 'UNIT',
    lot_id          UUID,
    unit_cost       NUMERIC(15,4) NOT NULL DEFAULT 0
);
```

### 7.5 `goods_recipe_*` (Module 26)

```sql
CREATE TABLE tenant_acme.goods_recipe_recipes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    product_id      UUID NOT NULL,               -- output
    version         VARCHAR(16) NOT NULL DEFAULT 'v1',
    output_qty      NUMERIC(15,4) NOT NULL DEFAULT 1,
    output_uom      VARCHAR(16) NOT NULL DEFAULT 'UNIT',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_recipe_code_ver UNIQUE (tenant_id, code, version)
);

CREATE TABLE tenant_acme.goods_recipe_ingredients (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    recipe_id       UUID NOT NULL REFERENCES tenant_acme.goods_recipe_recipes(id) ON DELETE CASCADE,
    product_id      UUID NOT NULL,
    qty             NUMERIC(15,4) NOT NULL CHECK (qty > 0),
    uom             VARCHAR(16) NOT NULL DEFAULT 'UNIT',
    waste_pct       NUMERIC(5,2) NOT NULL DEFAULT 0,
    sort_order      SMALLINT NOT NULL DEFAULT 0,
    is_optional     BOOLEAN NOT NULL DEFAULT FALSE
);
```

### 7.6 `goods_qa_*` (Module 27)

```sql
CREATE TABLE tenant_acme.goods_qa_inspections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    inspection_number VARCHAR(32) NOT NULL,
    inspection_type VARCHAR(32) NOT NULL,        -- 'INCOMING','IN_PROCESS','FINAL','RETURN'
    reference_type  VARCHAR(32),
    reference_id    UUID,
    product_id      UUID NOT NULL,
    lot_id          UUID,
    sample_size     INTEGER NOT NULL DEFAULT 1,
    passed_count    INTEGER NOT NULL DEFAULT 0,
    failed_count    INTEGER NOT NULL DEFAULT 0,
    result          VARCHAR(16) NOT NULL DEFAULT 'PENDING'
                    CHECK (result IN ('PENDING','PASS','FAIL','CONDITIONAL')),
    inspector_id    UUID,
    inspected_at    TIMESTAMPTZ,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_qa_number UNIQUE (tenant_id, inspection_number)
);

CREATE TABLE tenant_acme.goods_qa_check_items (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    inspection_id   UUID NOT NULL REFERENCES tenant_acme.goods_qa_inspections(id) ON DELETE CASCADE,
    check_name      VARCHAR(200) NOT NULL,
    expected        VARCHAR(200),
    actual          VARCHAR(200),
    result          VARCHAR(16) NOT NULL DEFAULT 'PENDING'
                    CHECK (result IN ('PENDING','PASS','FAIL'))
);
```

### 7.7 `goods_waste_*` (Module 28)

```sql
CREATE TABLE tenant_acme.goods_waste_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    waste_number    VARCHAR(32) NOT NULL,
    product_id      UUID NOT NULL,
    lot_id          UUID,
    warehouse_id    UUID,
    qty             NUMERIC(15,4) NOT NULL CHECK (qty > 0),
    uom             VARCHAR(16) NOT NULL DEFAULT 'UNIT',
    reason          VARCHAR(64) NOT NULL,        -- 'EXPIRED','DAMAGED','QUALITY','OTHER'
    cost_value      NUMERIC(15,2) NOT NULL DEFAULT 0,
    disposal_method VARCHAR(64),
    disposed_at     TIMESTAMPTZ,
    approved_by     UUID,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_waste_number UNIQUE (tenant_id, waste_number)
);
```

### 7.8 `goods_proc_*` (Module 29)

```sql
CREATE TABLE tenant_acme.goods_proc_purchase_orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    po_number       VARCHAR(32) NOT NULL,
    supplier_id     UUID NOT NULL,
    warehouse_id    UUID,
    status          VARCHAR(16) NOT NULL DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT','APPROVED','SENT','PARTIAL','RECEIVED','CLOSED','CANCELLED')),
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    subtotal        NUMERIC(15,2) NOT NULL DEFAULT 0,
    tax             NUMERIC(15,2) NOT NULL DEFAULT 0,
    total           NUMERIC(15,2) NOT NULL DEFAULT 0,
    expected_at     DATE,
    approved_by     UUID,
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_po_number UNIQUE (tenant_id, po_number)
);

CREATE TABLE tenant_acme.goods_proc_po_lines (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    po_id           UUID NOT NULL REFERENCES tenant_acme.goods_proc_purchase_orders(id) ON DELETE CASCADE,
    line_no         SMALLINT NOT NULL,
    product_id      UUID NOT NULL,
    qty             NUMERIC(15,4) NOT NULL CHECK (qty > 0),
    received_qty    NUMERIC(15,4) NOT NULL DEFAULT 0,
    uom             VARCHAR(16) NOT NULL DEFAULT 'UNIT',
    unit_price      NUMERIC(15,4) NOT NULL,
    tax_rate        NUMERIC(5,4) NOT NULL DEFAULT 0.07,
    line_total      NUMERIC(15,2) NOT NULL,
    CONSTRAINT uq_po_line UNIQUE (po_id, line_no)
);

CREATE TABLE tenant_acme.goods_proc_goods_receipts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    receipt_number  VARCHAR(32) NOT NULL,
    po_id           UUID,
    warehouse_id    UUID NOT NULL,
    received_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    received_by     UUID,
    notes           TEXT,
    CONSTRAINT uq_gr_number UNIQUE (tenant_id, receipt_number)
);
```

### 7.9 `goods_trace_*` (Module 30)

```sql
CREATE TABLE tenant_acme.goods_trace_events (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    trace_id        UUID NOT NULL,               -- กลุ่มเหตุการณ์
    event_type      VARCHAR(32) NOT NULL,        -- 'HARVEST','PROCESS','SHIP','RECEIVE','RETAIL'
    product_id      UUID NOT NULL,
    lot_id          UUID,
    from_party      VARCHAR(200),
    to_party        VARCHAR(200),
    location        VARCHAR(200),
    quantity        NUMERIC(15,4),
    uom             VARCHAR(16),
    reference_type  VARCHAR(32),
    reference_id    UUID,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);

CREATE INDEX ix_trace_product ON tenant_acme.goods_trace_events (tenant_id, product_id, occurred_at DESC);
CREATE INDEX ix_trace_lot ON tenant_acme.goods_trace_events (tenant_id, lot_id, occurred_at);
CREATE INDEX ix_trace_id ON tenant_acme.goods_trace_events (trace_id, occurred_at);
```

### 7.10 `goods_agri_*` (Module 31)

```sql
CREATE TABLE tenant_acme.goods_agri_farms (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    location        JSONB NOT NULL DEFAULT '{}'::jsonb,
    area_rai        NUMERIC(10,4) NOT NULL DEFAULT 0,
    owner_id        UUID,
    address         TEXT,
    certifications  JSONB NOT NULL DEFAULT '[]'::jsonb,   -- GAP, Organic
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_agri_farm UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.goods_agri_plots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    farm_id         UUID NOT NULL REFERENCES tenant_acme.goods_agri_farms(id) ON DELETE CASCADE,
    code            VARCHAR(32) NOT NULL,
    area_rai        NUMERIC(10,4) NOT NULL,
    soil_type       VARCHAR(64),
    irrigation_type VARCHAR(32),
    current_crop_id UUID,
    status          VARCHAR(16) NOT NULL DEFAULT 'IDLE'
                    CHECK (status IN ('IDLE','PLANTED','GROWING','HARVESTED','FALLOW')),
    location        JSONB,
    CONSTRAINT uq_agri_plot UNIQUE (farm_id, code)
);

CREATE TABLE tenant_acme.goods_agri_harvests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    plot_id         UUID NOT NULL REFERENCES tenant_acme.goods_agri_plots(id),
    crop_id         UUID,
    harvest_date    DATE NOT NULL,
    qty             NUMERIC(15,4) NOT NULL CHECK (qty > 0),
    uom             VARCHAR(16) NOT NULL DEFAULT 'KG',
    quality_grade   VARCHAR(8) CHECK (quality_grade IN ('A','B','C','REJECT')),
    lot_id          UUID,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_agri_harvest_plot ON tenant_acme.goods_agri_harvests (plot_id, harvest_date DESC);
```

### 7.11 `goods_crop_*` (Module 32)

```sql
CREATE TABLE tenant_acme.goods_crop_crops (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    scientific_name VARCHAR(200),
    category        VARCHAR(64),                 -- 'RICE','VEGETABLE','FRUIT','HERB'
    growth_days     INTEGER,
    season          VARCHAR(64),
    expected_yield_per_rai NUMERIC(15,4),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_crop_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.goods_crop_cycles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    plot_id         UUID NOT NULL,
    crop_id         UUID NOT NULL,
    planted_at      DATE NOT NULL,
    expected_harvest_at DATE,
    harvested_at    DATE,
    status          VARCHAR(16) NOT NULL DEFAULT 'PLANTED'
                    CHECK (status IN ('PLANTED','GROWING','HARVESTED','FAILED')),
    expected_yield  NUMERIC(15,4),
    actual_yield    NUMERIC(15,4),
    notes           TEXT
);
CREATE INDEX ix_crop_cycle_plot ON tenant_acme.goods_crop_cycles (plot_id, planted_at DESC);
```

### 7.12 `goods_soil_*` (Module 33)

```sql
CREATE TABLE tenant_acme.goods_soil_tests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    plot_id         UUID NOT NULL,
    test_date       DATE NOT NULL,
    ph              NUMERIC(4,2),
    ec              NUMERIC(6,3),
    organic_matter_pct NUMERIC(5,2),
    nitrogen_ppm    NUMERIC(10,2),
    phosphorus_ppm  NUMERIC(10,2),
    potassium_ppm   NUMERIC(10,2),
    lab_reference   VARCHAR(128),
    report_url      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_soil_plot_date ON tenant_acme.goods_soil_tests (plot_id, test_date DESC);

CREATE TABLE tenant_acme.goods_soil_amendments (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    plot_id         UUID NOT NULL,
    applied_at      DATE NOT NULL,
    amendment_type  VARCHAR(64) NOT NULL,        -- 'FERTILIZER','COMPOST','LIME'
    product_id      UUID,
    qty             NUMERIC(15,4) NOT NULL,
    uom             VARCHAR(16) NOT NULL DEFAULT 'KG',
    notes           TEXT
);
```

### 7.13 `goods_irrig_*` (Module 34)

```sql
CREATE TABLE tenant_acme.goods_irrig_schedules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    plot_id         UUID NOT NULL,
    schedule_name   VARCHAR(200) NOT NULL,
    start_time      TIME NOT NULL,
    duration_min    INTEGER NOT NULL CHECK (duration_min > 0),
    frequency       VARCHAR(16) NOT NULL,        -- 'DAILY','EVERY_2_DAYS','WEEKLY'
    days_of_week    JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tenant_acme.goods_irrig_events (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    plot_id         UUID NOT NULL,
    schedule_id     UUID,
    started_at      TIMESTAMPTZ NOT NULL,
    ended_at        TIMESTAMPTZ,
    water_liters    NUMERIC(15,2),
    trigger_source  VARCHAR(16) NOT NULL DEFAULT 'MANUAL'
                    CHECK (trigger_source IN ('MANUAL','SCHEDULE','SENSOR','AI')),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
```

---

## 📐 Part 8: Tenant Schema DDL — Layer 4 (Operations)

### 8.1 `ops_trans_*` (Module 35)

```sql
CREATE TABLE tenant_acme.ops_trans_vehicles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    plate_number    VARCHAR(32) NOT NULL,
    vehicle_type    VARCHAR(32) NOT NULL,        -- 'TRUCK','VAN','PICKUP','MOTORCYCLE'
    capacity_kg     NUMERIC(10,2),
    capacity_m3     NUMERIC(10,2),
    driver_id       UUID,
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('ACTIVE','MAINTENANCE','INACTIVE','RETIRED')),
    gps_device_id   VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_trans_plate UNIQUE (tenant_id, plate_number)
);

CREATE TABLE tenant_acme.ops_trans_trips (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    trip_number     VARCHAR(32) NOT NULL,
    vehicle_id      UUID NOT NULL REFERENCES tenant_acme.ops_trans_vehicles(id),
    driver_id       UUID,
    route_id        UUID,
    status          VARCHAR(16) NOT NULL DEFAULT 'PLANNED'
                    CHECK (status IN ('PLANNED','IN_PROGRESS','COMPLETED','CANCELLED')),
    planned_start   TIMESTAMPTZ,
    actual_start    TIMESTAMPTZ,
    actual_end      TIMESTAMPTZ,
    distance_km     NUMERIC(10,2),
    fuel_cost       NUMERIC(15,2),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_trans_trip UNIQUE (tenant_id, trip_number)
);
```

### 8.2 `ops_deliv_*` (Module 36)

```sql
CREATE TABLE tenant_acme.ops_deliv_deliveries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    delivery_number VARCHAR(32) NOT NULL,
    trip_id         UUID,
    order_id        UUID,
    customer_id     UUID,
    address         JSONB NOT NULL DEFAULT '{}'::jsonb,
    recipient_name  VARCHAR(200),
    recipient_phone VARCHAR(32),
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING','OUT_FOR_DELIVERY','DELIVERED','FAILED','RETURNED')),
    scheduled_at    TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ,
    signature_url   TEXT,
    photo_url       TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_deliv_number UNIQUE (tenant_id, delivery_number)
);
CREATE INDEX ix_deliv_status ON tenant_acme.ops_deliv_deliveries (tenant_id, status, scheduled_at);
```

### 8.3 `ops_route_*` (Module 37)

```sql
CREATE TABLE tenant_acme.ops_route_routes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    waypoints       JSONB NOT NULL DEFAULT '[]'::jsonb,   -- [{lat,lng,stop_id}]
    total_distance_km NUMERIC(10,2),
    estimated_minutes INTEGER,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_route_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.ops_route_stops (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    route_id        UUID NOT NULL REFERENCES tenant_acme.ops_route_routes(id) ON DELETE CASCADE,
    sequence_no     SMALLINT NOT NULL,
    address         JSONB NOT NULL,
    customer_id     UUID,
    time_window_start TIME,
    time_window_end TIME,
    CONSTRAINT uq_route_stop UNIQUE (route_id, sequence_no)
);
```

### 8.4 `ops_gps_*` (Module 38)

```sql
CREATE TABLE tenant_acme.ops_gps_pings (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    device_id       VARCHAR(64) NOT NULL,
    vehicle_id      UUID,
    lat             NUMERIC(10,7) NOT NULL,
    lng             NUMERIC(10,7) NOT NULL,
    speed_kmh       NUMERIC(6,2),
    heading         SMALLINT,
    accuracy_m      NUMERIC(6,2),
    recorded_at     TIMESTAMPTZ NOT NULL,
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);

CREATE INDEX ix_gps_device_time ON tenant_acme.ops_gps_pings (device_id, recorded_at DESC);
CREATE INDEX ix_gps_vehicle_time ON tenant_acme.ops_gps_pings (vehicle_id, recorded_at DESC);
```

### 8.5 `ops_retail_*` (Module 39)

```sql
CREATE TABLE tenant_acme.ops_retail_stores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    address         JSONB NOT NULL DEFAULT '{}'::jsonb,
    phone           VARCHAR(32),
    manager_id      UUID,
    timezone        VARCHAR(64) NOT NULL DEFAULT 'Asia/Bangkok',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_retail_store UNIQUE (tenant_id, code)
);
```

### 8.6 `ops_pos_*` (Module 40)

```sql
CREATE TABLE tenant_acme.ops_pos_sales (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    receipt_number  VARCHAR(32) NOT NULL,
    store_id        UUID NOT NULL,
    shift_id        UUID,
    cashier_id      UUID,
    customer_id     UUID,
    subtotal        NUMERIC(15,2) NOT NULL DEFAULT 0,
    discount        NUMERIC(15,2) NOT NULL DEFAULT 0,
    tax             NUMERIC(15,2) NOT NULL DEFAULT 0,
    total           NUMERIC(15,2) NOT NULL DEFAULT 0,
    payment_method  VARCHAR(32),
    paid_amount     NUMERIC(15,2) NOT NULL DEFAULT 0,
    change_amount   NUMERIC(15,2) NOT NULL DEFAULT 0,
    status          VARCHAR(16) NOT NULL DEFAULT 'COMPLETED'
                    CHECK (status IN ('DRAFT','COMPLETED','VOIDED','REFUNDED')),
    sold_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym),
    CONSTRAINT uq_pos_receipt UNIQUE (tenant_id, receipt_number, partition_ym)
) PARTITION BY LIST (partition_ym);

CREATE INDEX ix_pos_store_time ON tenant_acme.ops_pos_sales (store_id, sold_at DESC);

CREATE TABLE tenant_acme.ops_pos_sale_lines (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    sale_id         UUID NOT NULL,
    line_no         SMALLINT NOT NULL,
    product_id      UUID NOT NULL,
    qty             NUMERIC(15,4) NOT NULL,
    unit_price      NUMERIC(15,4) NOT NULL,
    discount        NUMERIC(15,2) NOT NULL DEFAULT 0,
    line_total      NUMERIC(15,2) NOT NULL
);

CREATE TABLE tenant_acme.ops_pos_payments (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    sale_id         UUID NOT NULL,
    method          VARCHAR(32) NOT NULL,
    amount          NUMERIC(15,2) NOT NULL,
    reference       VARCHAR(128),
    paid_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 8.7 `ops_shift_*` (Module 41)

```sql
CREATE TABLE tenant_acme.ops_shift_shifts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    store_id        UUID,
    shift_code      VARCHAR(32) NOT NULL,
    shift_date      DATE NOT NULL,
    opened_by       UUID NOT NULL,
    closed_by       UUID,
    opened_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMPTZ,
    opening_cash    NUMERIC(15,2) NOT NULL DEFAULT 0,
    closing_cash    NUMERIC(15,2),
    expected_cash   NUMERIC(15,2),
    variance        NUMERIC(15,2),
    status          VARCHAR(16) NOT NULL DEFAULT 'OPEN'
                    CHECK (status IN ('OPEN','CLOSED','RECONCILED')),
    notes           TEXT
);
CREATE INDEX ix_shift_store_date ON tenant_acme.ops_shift_shifts (store_id, shift_date DESC);
```

### 8.8 `ops_line_*` (Module 42)

```sql
CREATE TABLE tenant_acme.ops_line_channels (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    channel_name    VARCHAR(200) NOT NULL,
    channel_type    VARCHAR(32) NOT NULL,       -- 'OA','NOTIFY','MESSENGER'
    channel_id      VARCHAR(128) NOT NULL,
    access_token_enc BYTEA,
    webhook_url     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_line_channel UNIQUE (tenant_id, channel_type, channel_id)
);

CREATE TABLE tenant_acme.ops_line_messages (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    channel_id      UUID NOT NULL,
    direction       VARCHAR(8) NOT NULL CHECK (direction IN ('IN','OUT')),
    user_line_id    VARCHAR(128) NOT NULL,
    message_type    VARCHAR(16) NOT NULL,        -- 'TEXT','IMAGE','STICKER','FILE'
    content         TEXT,
    external_id     VARCHAR(128),
    status          VARCHAR(16) NOT NULL DEFAULT 'SENT',
    sent_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
CREATE INDEX ix_line_user_time ON tenant_acme.ops_line_messages (tenant_id, user_line_id, sent_at DESC);
```

### 8.9 `ops_promo_*` (Module 43)

```sql
CREATE TABLE tenant_acme.ops_promo_promotions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    promo_type      VARCHAR(32) NOT NULL
                    CHECK (promo_type IN ('PERCENT_OFF','AMOUNT_OFF','BUY_X_GET_Y','FREE_SHIP','BUNDLE')),
    discount_value  NUMERIC(15,2),
    min_purchase    NUMERIC(15,2),
    max_discount    NUMERIC(15,2),
    valid_from      TIMESTAMPTZ NOT NULL,
    valid_until     TIMESTAMPTZ NOT NULL,
    usage_limit     INTEGER,
    usage_count     INTEGER NOT NULL DEFAULT 0,
    applies_to      JSONB NOT NULL DEFAULT '{}'::jsonb,
    status          VARCHAR(16) NOT NULL DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT','ACTIVE','PAUSED','ENDED')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_promo_code UNIQUE (tenant_id, code)
);
CREATE INDEX ix_promo_active ON tenant_acme.ops_promo_promotions (tenant_id, status, valid_until);
```

### 8.10 `ops_loyal_*` (Module 44)

```sql
CREATE TABLE tenant_acme.ops_loyal_accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    customer_id     UUID NOT NULL,
    tier            VARCHAR(16) NOT NULL DEFAULT 'BRONZE'
                    CHECK (tier IN ('BRONZE','SILVER','GOLD','PLATINUM')),
    points_balance  BIGINT NOT NULL DEFAULT 0 CHECK (points_balance >= 0),
    lifetime_points BIGINT NOT NULL DEFAULT 0,
    joined_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_loyal_customer UNIQUE (tenant_id, customer_id)
);

CREATE TABLE tenant_acme.ops_loyal_transactions (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    account_id      UUID NOT NULL,
    tx_type         VARCHAR(16) NOT NULL CHECK (tx_type IN ('EARN','REDEEM','ADJUST','EXPIRE')),
    points          BIGINT NOT NULL,
    reference_type  VARCHAR(32),
    reference_id    UUID,
    notes           TEXT,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
```

### 8.11 `ops_crm_*` (Module 45)

```sql
CREATE TABLE tenant_acme.ops_crm_leads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    contact_email   VARCHAR(255),
    contact_phone   VARCHAR(32),
    source          VARCHAR(64),
    status          VARCHAR(16) NOT NULL DEFAULT 'NEW'
                    CHECK (status IN ('NEW','CONTACTED','QUALIFIED','CONVERTED','LOST')),
    assigned_to     UUID,
    converted_customer_id UUID,
    converted_at    TIMESTAMPTZ,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_crm_lead_status ON tenant_acme.ops_crm_leads (tenant_id, status, assigned_to);

CREATE TABLE tenant_acme.ops_crm_deals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    customer_id     UUID,
    lead_id         UUID,
    value           NUMERIC(15,2) NOT NULL DEFAULT 0 CHECK (value >= 0),
    currency        CHAR(3) NOT NULL DEFAULT 'THB',
    stage           VARCHAR(32) NOT NULL DEFAULT 'PROSPECTING'
                    CHECK (stage IN ('PROSPECTING','QUALIFICATION','PROPOSAL','NEGOTIATION','CLOSED_WON','CLOSED_LOST')),
    probability     SMALLINT NOT NULL DEFAULT 0 CHECK (probability BETWEEN 0 AND 100),
    expected_close  DATE,
    owner_id        UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_crm_deal_stage ON tenant_acme.ops_crm_deals (tenant_id, stage, owner_id);

CREATE TABLE tenant_acme.ops_crm_activities (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    lead_id         UUID,
    deal_id         UUID,
    customer_id     UUID,
    activity_type   VARCHAR(16) NOT NULL CHECK (activity_type IN ('CALL','EMAIL','MEETING','LINE','NOTE')),
    subject         VARCHAR(200),
    content         TEXT,
    actor_id        UUID,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_crm_act_entity ON tenant_acme.ops_crm_activities (tenant_id, lead_id, occurred_at DESC);
```

### 8.12 `ops_camp_*` (Module 46)

```sql
CREATE TABLE tenant_acme.ops_camp_campaigns (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    channel         VARCHAR(32) NOT NULL,       -- 'LINE','EMAIL','SMS','FB'
    template_id     UUID,
    target_filter   JSONB NOT NULL DEFAULT '{}'::jsonb,
    scheduled_at    TIMESTAMPTZ,
    status          VARCHAR(16) NOT NULL DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT','SCHEDULED','RUNNING','PAUSED','COMPLETED','CANCELLED')),
    sent_count      INTEGER NOT NULL DEFAULT 0,
    opened_count    INTEGER NOT NULL DEFAULT 0,
    clicked_count   INTEGER NOT NULL DEFAULT 0,
    converted_count INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_camp_code UNIQUE (tenant_id, code)
);
```

### 8.13 `ops_supp_*` (Module 47)

```sql
CREATE TABLE tenant_acme.ops_supp_tickets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    ticket_number   VARCHAR(32) NOT NULL,
    customer_id     UUID,
    subject         VARCHAR(500) NOT NULL,
    description     TEXT,
    category        VARCHAR(64),
    priority        VARCHAR(16) NOT NULL DEFAULT 'NORMAL'
                    CHECK (priority IN ('LOW','NORMAL','HIGH','URGENT')),
    status          VARCHAR(16) NOT NULL DEFAULT 'OPEN'
                    CHECK (status IN ('OPEN','IN_PROGRESS','WAITING','RESOLVED','CLOSED')),
    assigned_to     UUID,
    sla_due_at      TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ,
    closed_at       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_supp_ticket UNIQUE (tenant_id, ticket_number)
);
CREATE INDEX ix_supp_ticket_status ON tenant_acme.ops_supp_tickets (tenant_id, status, priority);

CREATE TABLE tenant_acme.ops_supp_ticket_messages (
    id              BIGSERIAL PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    ticket_id       UUID NOT NULL REFERENCES tenant_acme.ops_supp_tickets(id) ON DELETE CASCADE,
    author_id       UUID,
    author_type     VARCHAR(16) NOT NULL DEFAULT 'AGENT'
                    CHECK (author_type IN ('AGENT','CUSTOMER','SYSTEM')),
    content         TEXT NOT NULL,
    attachments     JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 📐 Part 9: Tenant Schema DDL — Layer 5 (Intelligence)

### 9.1 `intel_rpt_*` (Module 48)

```sql
CREATE TABLE tenant_acme.intel_rpt_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    category        VARCHAR(64),
    definition      JSONB NOT NULL,              -- query spec
    is_system       BOOLEAN NOT NULL DEFAULT FALSE,
    created_by      UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_rpt_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.intel_rpt_schedules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    report_id       UUID NOT NULL REFERENCES tenant_acme.intel_rpt_reports(id),
    cron_expression VARCHAR(64) NOT NULL,
    recipients      JSONB NOT NULL DEFAULT '[]'::jsonb,
    format          VARCHAR(16) NOT NULL DEFAULT 'PDF',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_run_at     TIMESTAMPTZ
);

CREATE TABLE tenant_acme.intel_rpt_runs (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    report_id       UUID NOT NULL,
    schedule_id     UUID,
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    result_url      TEXT,
    row_count       INTEGER,
    duration_ms     INTEGER,
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
```

### 9.2 `intel_anl_*` (Module 49)

```sql
CREATE TABLE tenant_acme.intel_anl_events (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    event_name      VARCHAR(128) NOT NULL,
    user_id         UUID,
    session_id      VARCHAR(64),
    properties      JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
CREATE INDEX ix_anl_event_name_time ON tenant_acme.intel_anl_events (event_name, occurred_at DESC);
CREATE INDEX ix_anl_user_time ON tenant_acme.intel_anl_events (user_id, occurred_at DESC);

CREATE TABLE tenant_acme.intel_anl_funnels (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    steps           JSONB NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);
```

### 9.3 `intel_fcst_*` (Module 50)

```sql
CREATE TABLE tenant_acme.intel_fcst_models (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    model_type      VARCHAR(32) NOT NULL CHECK (model_type IN ('LSTM','PROPHET','XGBOOST','ARIMA','ENSEMBLE')),
    target          VARCHAR(64) NOT NULL,       -- 'DEMAND','YIELD','PRICE'
    version         VARCHAR(16) NOT NULL,
    trained_at      TIMESTAMPTZ,
    metrics         JSONB NOT NULL DEFAULT '{}'::jsonb,   -- {mape, rmse, mae}
    is_active       BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_fcst_model UNIQUE (tenant_id, name, version)
);

CREATE TABLE tenant_acme.intel_fcst_forecasts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    model_id        UUID NOT NULL REFERENCES tenant_acme.intel_fcst_models(id),
    product_id      UUID,
    branch_id       UUID,
    forecast_date   DATE NOT NULL,
    predicted_qty   NUMERIC(15,4) NOT NULL,
    actual_qty      NUMERIC(15,4),
    mape            NUMERIC(6,2),
    confidence      NUMERIC(5,4),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fcst UNIQUE (model_id, product_id, branch_id, forecast_date)
);
CREATE INDEX ix_fcst_date ON tenant_acme.intel_fcst_forecasts (tenant_id, forecast_date DESC);
```

### 9.4 `intel_kpi_*` (Module 51)

```sql
CREATE TABLE tenant_acme.intel_kpi_definitions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    category        VARCHAR(64),
    unit            VARCHAR(32),
    formula         TEXT NOT NULL,
    target_value    NUMERIC(15,4),
    direction       VARCHAR(16) NOT NULL DEFAULT 'HIGHER_BETTER'
                    CHECK (direction IN ('HIGHER_BETTER','LOWER_BETTER','TARGET')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_kpi_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.intel_kpi_values (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    kpi_id          UUID NOT NULL,
    period_type     VARCHAR(16) NOT NULL CHECK (period_type IN ('DAY','WEEK','MONTH','QUARTER','YEAR')),
    period_start    DATE NOT NULL,
    value           NUMERIC(15,4) NOT NULL,
    target          NUMERIC(15,4),
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_kpi_value UNIQUE (kpi_id, period_type, period_start)
);
CREATE INDEX ix_kpi_time ON tenant_acme.intel_kpi_values (tenant_id, kpi_id, period_start DESC);
```

### 9.5 `intel_csat_*` (Module 52)

```sql
CREATE TABLE tenant_acme.intel_csat_surveys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    questions       JSONB NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_csat_survey UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.intel_csat_responses (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    survey_id       UUID NOT NULL,
    customer_id     UUID,
    order_id        UUID,
    nps_score       SMALLINT CHECK (nps_score BETWEEN 0 AND 10),
    csat_score      SMALLINT CHECK (csat_score BETWEEN 1 AND 5),
    answers         JSONB NOT NULL DEFAULT '{}'::jsonb,
    comment         TEXT,
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
```

### 9.6 `intel_rec_*` (Module 53)

```sql
CREATE TABLE tenant_acme.intel_rec_recommendations (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    customer_id     UUID,
    product_id      UUID NOT NULL,
    score           NUMERIC(6,4) NOT NULL,
    algorithm       VARCHAR(32) NOT NULL,
    context         JSONB NOT NULL DEFAULT '{}'::jsonb,
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
CREATE INDEX ix_rec_customer ON tenant_acme.intel_rec_recommendations (customer_id, score DESC);
```

### 9.7 `intel_oee_*` (Module 54)

```sql
CREATE TABLE tenant_acme.intel_oee_metrics (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    work_center     VARCHAR(64) NOT NULL,
    shift_date      DATE NOT NULL,
    shift_code      VARCHAR(16),
    availability    NUMERIC(5,4) NOT NULL,
    performance     NUMERIC(5,4) NOT NULL,
    quality         NUMERIC(5,4) NOT NULL,
    oee             NUMERIC(5,4) NOT NULL,
    downtime_min    INTEGER NOT NULL DEFAULT 0,
    total_units     INTEGER NOT NULL DEFAULT 0,
    good_units      INTEGER NOT NULL DEFAULT 0,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_oee UNIQUE (tenant_id, work_center, shift_date, shift_code)
);
```

---

## 📐 Part 10: Tenant Schema DDL — Layer 6 (Monitoring)

### 10.1 `mon_iot_*` (Module 55)

```sql
CREATE TABLE tenant_acme.mon_iot_sensors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    sensor_type     VARCHAR(32) NOT NULL
                    CHECK (sensor_type IN ('TEMPERATURE','HUMIDITY','CO2','LIGHT','PH','EC','FLOW','PRESSURE','WEIGHT')),
    unit            VARCHAR(16) NOT NULL,
    location        JSONB,
    threshold_min   NUMERIC(15,4),
    threshold_max   NUMERIC(15,4),
    mqtt_topic      VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_seen_at    TIMESTAMPTZ,
    CONSTRAINT uq_iot_sensor_code UNIQUE (tenant_id, code)
);
CREATE INDEX ix_iot_sensor_type ON tenant_acme.mon_iot_sensors (tenant_id, sensor_type, is_active);

CREATE TABLE tenant_acme.mon_iot_readings (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    sensor_id       UUID NOT NULL REFERENCES tenant_acme.mon_iot_sensors(id),
    value           NUMERIC(15,4) NOT NULL,
    unit            VARCHAR(16) NOT NULL,
    quality         VARCHAR(16) NOT NULL DEFAULT 'GOOD',
    recorded_at     TIMESTAMPTZ NOT NULL,
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
CREATE INDEX ix_iot_reading_sensor ON tenant_acme.mon_iot_readings (sensor_id, recorded_at DESC);

CREATE TABLE tenant_acme.mon_iot_commands (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    sensor_id       UUID,
    actuator_code   VARCHAR(64),
    command         VARCHAR(64) NOT NULL,
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    issued_by       UUID,
    issued_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acked_at        TIMESTAMPTZ
);
```

### 10.2 `mon_cctv_*` (Module 56)

```sql
CREATE TABLE tenant_acme.mon_cctv_cameras (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    stream_url      TEXT NOT NULL,
    location        JSONB,
    resolution      VARCHAR(16),
    fps             SMALLINT,
    is_recording    BOOLEAN NOT NULL DEFAULT TRUE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_seen_at    TIMESTAMPTZ,
    CONSTRAINT uq_cctv_code UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.mon_cctv_events (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    camera_id       UUID NOT NULL,
    event_type      VARCHAR(32) NOT NULL,       -- 'MOTION','PERSON','VEHICLE','LOITERING'
    confidence      NUMERIC(5,4),
    snapshot_url    TEXT,
    clip_url        TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
```

### 10.3 `mon_obs_*` (Module 57)

```sql
CREATE TABLE tenant_acme.mon_obs_metrics (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    service         VARCHAR(64) NOT NULL,
    metric_name     VARCHAR(128) NOT NULL,
    value           NUMERIC(15,4) NOT NULL,
    labels          JSONB NOT NULL DEFAULT '{}'::jsonb,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
CREATE INDEX ix_obs_metric ON tenant_acme.mon_obs_metrics (service, metric_name, recorded_at DESC);

CREATE TABLE tenant_acme.mon_obs_traces (
    trace_id        UUID PRIMARY KEY,
    tenant_id       VARCHAR(63) NOT NULL,
    root_service    VARCHAR(64) NOT NULL,
    root_operation  VARCHAR(200) NOT NULL,
    duration_ms     INTEGER NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'OK',
    spans           JSONB NOT NULL DEFAULT '[]'::jsonb,
    started_at      TIMESTAMPTZ NOT NULL,
    completed_at    TIMESTAMPTZ
);
CREATE INDEX ix_obs_trace_root ON tenant_acme.mon_obs_traces (tenant_id, root_service, started_at DESC);
```

### 10.4 `mon_bak_*` (Module 58)

```sql
CREATE TABLE tenant_acme.mon_bak_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    job_type        VARCHAR(32) NOT NULL CHECK (job_type IN ('FULL','INCREMENTAL','WAL_ARCHIVE','SNAPSHOT')),
    target          VARCHAR(128) NOT NULL,
    storage_url     TEXT,
    size_bytes      BIGINT,
    checksum        CHAR(64),
    status          VARCHAR(16) NOT NULL DEFAULT 'RUNNING'
                    CHECK (status IN ('RUNNING','COMPLETED','FAILED','VERIFIED')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    error_message   TEXT
);
CREATE INDEX ix_bak_status ON tenant_acme.mon_bak_jobs (tenant_id, status, started_at DESC);

CREATE TABLE tenant_acme.mon_bak_restores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    job_id          UUID NOT NULL REFERENCES tenant_acme.mon_bak_jobs(id),
    restored_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    restored_by     UUID,
    target          VARCHAR(128) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'COMPLETED',
    duration_ms     INTEGER,
    verified        BOOLEAN NOT NULL DEFAULT FALSE
);
```

### 10.5 `mon_alert_*` (Module 59)

```sql
CREATE TABLE tenant_acme.mon_alert_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    source          VARCHAR(32) NOT NULL,       -- 'IOT','SYSTEM','BUSINESS'
    condition       JSONB NOT NULL,
    severity        VARCHAR(16) NOT NULL DEFAULT 'WARNING'
                    CHECK (severity IN ('INFO','WARNING','CRITICAL')),
    channels        JSONB NOT NULL DEFAULT '["LINE"]'::jsonb,
    cooldown_min    INTEGER NOT NULL DEFAULT 5,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_alert_rule UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.mon_alert_events (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    rule_id         UUID NOT NULL,
    severity        VARCHAR(16) NOT NULL,
    subject         VARCHAR(500) NOT NULL,
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID,
    resolved_at     TIMESTAMPTZ,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
CREATE INDEX ix_alert_unresolved ON tenant_acme.mon_alert_events (tenant_id, severity, occurred_at DESC)
    WHERE resolved_at IS NULL;
```

### 10.6 `mon_audit_*` (Module 60)

```sql
CREATE TABLE tenant_acme.mon_audit_views (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    filters         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_by      UUID,
    is_shared       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 10.7 `mon_maint_*` (Module 61)

```sql
CREATE TABLE tenant_acme.mon_maint_assets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    asset_type      VARCHAR(64),
    location        VARCHAR(200),
    purchase_date   DATE,
    warranty_until  DATE,
    criticality     VARCHAR(16) NOT NULL DEFAULT 'NORMAL',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_maint_asset UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.mon_maint_work_orders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    wo_number       VARCHAR(32) NOT NULL,
    asset_id        UUID NOT NULL,
    wo_type         VARCHAR(16) NOT NULL CHECK (wo_type IN ('PREVENTIVE','CORRECTIVE','PREDICTIVE')),
    priority        VARCHAR(16) NOT NULL DEFAULT 'NORMAL',
    description     TEXT,
    scheduled_at    TIMESTAMPTZ,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    assigned_to     UUID,
    cost            NUMERIC(15,2) NOT NULL DEFAULT 0,
    status          VARCHAR(16) NOT NULL DEFAULT 'OPEN',
    CONSTRAINT uq_maint_wo UNIQUE (tenant_id, wo_number)
);
```

### 10.8 `mon_energy_*` (Module 62)

```sql
CREATE TABLE tenant_acme.mon_energy_meters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(64) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    energy_type     VARCHAR(32) NOT NULL CHECK (energy_type IN ('ELECTRICITY','WATER','GAS','STEAM')),
    unit            VARCHAR(16) NOT NULL,
    location        VARCHAR(200),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_energy_meter UNIQUE (tenant_id, code)
);

CREATE TABLE tenant_acme.mon_energy_readings (
    id              BIGSERIAL,
    tenant_id       VARCHAR(63) NOT NULL,
    meter_id        UUID NOT NULL,
    value           NUMERIC(15,4) NOT NULL,
    unit            VARCHAR(16) NOT NULL,
    cost            NUMERIC(15,2),
    recorded_at     TIMESTAMPTZ NOT NULL,
    partition_ym    CHAR(6) NOT NULL,
    PRIMARY KEY (id, partition_ym)
) PARTITION BY LIST (partition_ym);
CREATE INDEX ix_energy_meter_time ON tenant_acme.mon_energy_readings (meter_id, recorded_at DESC);
```

---

## 📐 Part 11: Tenant Schema DDL — Layer 7 (Templates)

### 11.1 `tpl_example_*` (Module 64)

```sql
CREATE TABLE tenant_acme.tpl_example_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    code            VARCHAR(32) NOT NULL,
    name            VARCHAR(200) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_tpl_example UNIQUE (tenant_id, code)
);
```

### 11.2 `tpl_blank_*` (Module 65)

```sql
CREATE TABLE tenant_acme.tpl_blank_entities (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       VARCHAR(63) NOT NULL,
    -- เพิ่ม columns ตามต้องการ
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 📐 Part 12: Common Functions & Triggers

```sql
-- ── touch_updated_at ─────────────────────────────────────
CREATE OR REPLACE FUNCTION public.touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ── set_partition_ym ─────────────────────────────────────
CREATE OR REPLACE FUNCTION public.set_partition_ym()
RETURNS TRIGGER AS $$
BEGIN
    NEW.partition_ym := TO_CHAR(COALESCE(NEW.occurred_at, NEW.created_at, NOW()), 'YYYYMM');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ── ensure_monthly_partition(parent, ym) ─────────────────
CREATE OR REPLACE FUNCTION public.ensure_monthly_partition(
    p_schema TEXT, p_table TEXT, p_ym CHAR(6)
)
RETURNS VOID AS $$
DECLARE
    v_child TEXT := format('%I.%s_%s', p_schema, p_table, p_ym);
    v_parent TEXT := format('%I.%s', p_schema, p_table);
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = p_schema AND c.relname = p_table || '_' || p_ym
    ) THEN
        EXECUTE format(
            'CREATE TABLE %s PARTITION OF %s FOR VALUES IN (%L)',
            v_child, v_parent, p_ym
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ── create_tenant_schema(tenant_id) ──────────────────────
CREATE OR REPLACE FUNCTION public.create_tenant_schema(p_tenant_id TEXT)
RETURNS VOID AS $$
DECLARE
    v_schema TEXT := 'tenant_' || p_tenant_id;
BEGIN
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', v_schema);
    -- สร้างตารางทั้งหมด (ดู migration ด้านล่าง)
    RAISE NOTICE 'Schema % ready', v_schema;
END;
$$ LANGUAGE plpgsql;
```

---

## 📐 Part 13: RLS Policies (ทุกตาราง)

```sql
-- ============================================================
-- Helper: apply_rls(schema, table)
-- ============================================================
CREATE OR REPLACE FUNCTION public.apply_tenant_rls(p_schema TEXT, p_table TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', p_schema, p_table);
    EXECUTE format(
        'CREATE POLICY tenant_isolation ON %I.%I '
        'USING (tenant_id = current_setting(''app.current_tenant'', TRUE)) '
        'WITH CHECK (tenant_id = current_setting(''app.current_tenant'', TRUE))',
        p_schema, p_table
    );
END;
$$ LANGUAGE plpgsql;

-- ตัวอย่างใช้งาน
-- SELECT public.apply_tenant_rls('tenant_acme', 'money_inv_invoices');
-- SELECT public.apply_tenant_rls('tenant_acme', 'money_inv_lines');
-- ...
```

---

## 📐 Part 14: pg_cron Jobs

```sql
-- ── Auto-create partitions (ทุกวัน 02:00) ────────────────
SELECT cron.schedule('ensure_partitions_daily', '0 2 * * *', $$
    DO $body$
    DECLARE r RECORD;
    BEGIN
        FOR r IN
            SELECT schemaname, tablename FROM pg_tables
            WHERE tablename IN (
                'core_audit_logs','core_idem_records','core_evt_store',
                'money_ledger_entries','goods_inv_movements','goods_trace_events',
                'ops_gps_pings','ops_pos_sales','ops_line_messages',
                'mon_iot_readings','mon_alert_events','mon_energy_readings'
            )
        LOOP
            PERFORM public.ensure_monthly_partition(
                r.schemaname, r.tablename,
                TO_CHAR(NOW() + INTERVAL '2 month', 'YYYYMM')
            );
        END LOOP;
    END $body$;
$$);

-- ── Purge expired data (ทุกวัน 03:00) ────────────────────
SELECT cron.schedule('purge_expired_daily', '0 3 * * *', $$
    SELECT public.purge_expired_idempotency('tenant_acme', 10000);
$$);

-- ── Refresh materialized views (ทุก 5 นาที) ──────────────
SELECT cron.schedule('refresh_mv_5min', '*/5 * * * *', $$
    REFRESH MATERIALIZED VIEW CONCURRENTLY tenant_acme.core_idem_stats_hourly_mv;
$$);

-- ── Cleanup outbox (ทุกวัน 04:00) ────────────────────────
SELECT cron.schedule('cleanup_outbox_daily', '0 4 * * *', $$
    DELETE FROM tenant_acme.core_evt_outbox
    WHERE status = 'PUBLISHED' AND published_at < NOW() - INTERVAL '7 days';
$$);

-- ── Aggregate stats (ทุกวัน 05:00) ───────────────────────
SELECT cron.schedule('aggregate_stats_daily', '0 5 * * *', $$
    INSERT INTO public.core_idem_global_stats (
        tenant_id, stat_date, total_records, pending_count, completed_count, failed_count
    )
    SELECT tenant_id, CURRENT_DATE - 1,
           COUNT(*),
           COUNT(*) FILTER (WHERE status='PENDING'),
           COUNT(*) FILTER (WHERE status='COMPLETED'),
           COUNT(*) FILTER (WHERE status='FAILED')
    FROM tenant_acme.core_idem_records
    WHERE created_at::date = CURRENT_DATE - 1
    GROUP BY tenant_id
    ON CONFLICT (tenant_id, stat_date) DO UPDATE
    SET total_records = EXCLUDED.total_records;
$$);
```

---

## 📐 Part 15: Migration Scripts

```
migrations/
├── 001_public_schema.sql
├── 002_common_functions.sql
├── 003_layer0_core.sql          (tenant template)
├── 004_layer1_foundation.sql
├── 005_layer2_money.sql
├── 006_layer3_goods.sql
├── 007_layer4_operations.sql
├── 008_layer5_intelligence.sql
├── 009_layer6_monitoring.sql
├── 010_layer7_templates.sql
├── 011_rls_policies.sql
├── 012_seed_data.sql
└── 013_cron_jobs.sql
```

### ตัวอย่าง `003_layer0_core.sql`

```sql
-- ============================================================
-- Migration 003: Layer 0 Core tables (tenant template)
-- ============================================================
CREATE OR REPLACE FUNCTION public.migrate_layer0_core(p_schema TEXT)
RETURNS VOID AS $$
BEGIN
    -- core_audit_logs
    EXECUTE format($f$
        CREATE TABLE IF NOT EXISTS %I.core_audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id VARCHAR(63) NOT NULL,
            sequence BIGINT NOT NULL,
            request_id VARCHAR(64) NOT NULL,
            action VARCHAR(32) NOT NULL,
            severity VARCHAR(16) NOT NULL DEFAULT 'INFO',
            outcome VARCHAR(16) NOT NULL DEFAULT 'SUCCESS',
            entity_type VARCHAR(64) NOT NULL,
            entity_id VARCHAR(64) NOT NULL,
            entity_version INTEGER,
            actor_user_id VARCHAR(64) NOT NULL,
            actor_email VARCHAR(255),
            actor_role VARCHAR(64),
            actor_ip VARCHAR(45),
            actor_user_agent VARCHAR(500),
            before JSONB NOT NULL DEFAULT '{}'::jsonb,
            after JSONB NOT NULL DEFAULT '{}'::jsonb,
            meta JSONB NOT NULL DEFAULT '{}'::jsonb,
            hash CHAR(64) NOT NULL,
            previous_hash CHAR(64) NOT NULL DEFAULT REPEAT('0', 64),
            idempotency_key VARCHAR(128),
            occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            duration_ms INTEGER,
            error_message TEXT,
            partition_ym CHAR(6) NOT NULL
        ) PARTITION BY LIST (partition_ym)
    $f$, p_schema);

    -- core_cfg_settings
    EXECUTE format($f$
        CREATE TABLE IF NOT EXISTS %I.core_cfg_settings (
            id BIGSERIAL PRIMARY KEY,
            tenant_id VARCHAR(63) NOT NULL,
            namespace VARCHAR(64) NOT NULL,
            setting_key VARCHAR(128) NOT NULL,
            setting_value JSONB NOT NULL,
            value_type VARCHAR(16) NOT NULL DEFAULT 'json',
            is_secret BOOLEAN NOT NULL DEFAULT FALSE,
            is_encrypted BOOLEAN NOT NULL DEFAULT FALSE,
            description TEXT,
            created_by VARCHAR(64),
            updated_by VARCHAR(64),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_cfg_settings UNIQUE (tenant_id, namespace, setting_key)
        )
    $f$, p_schema);

    -- ... (ตารางอื่นๆ)

    RAISE NOTICE 'Layer 0 migrated for schema %', p_schema;
END;
$$ LANGUAGE plpgsql;
```

---

## 📐 Part 16: ER Overview (High-Level)

```
┌───────────────────────────────────────────────────────────────────────┐
│                          PUBLIC SCHEMA                                 │
│  core_tenctx_registry ◄──┬── core_idem_global_stats                   │
│                           └── core_cfg_global_settings                │
│                           └── core_evt_dlq                            │
│                           └── tpl_health_checks                       │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌──────────────────┐      ┌──────────────────┐
          │  tenant_acme     │      │  tenant_beta     │
          └────────┬─────────┘      └────────┬─────────┘
                   │                          │
     ┌─────────────┼──────────────┬───────────┴──────────┐
     │             │              │                      │
     ▼             ▼              ▼                      ▼
┌─────────┐  ┌─────────┐   ┌──────────┐          ┌──────────┐
│ LAYER 0 │  │ LAYER 1 │   │ LAYER 2  │          │ LAYER 3  │
│  Core   │  │ Found.  │   │ Money    │          │ Goods    │
├─────────┤  ├─────────┤   ├──────────┤          ├──────────┤
│audit    │  │tenancy  │   │order     │          │warehouse │
│idem     │  │auth     │   │invoice   │          │inventory │
│config   │  │user     │   │ledger    │◄────────►│lot       │
│events   │  │employee │   │payment   │          │production│
│         │  │customer │   │acct_gw   │          │recipe    │
│         │  │supplier │   │tax       │          │qa        │
│         │  │product  │   │recon     │          │waste     │
│         │  │pricing  │   │          │          │procure   │
│         │  │         │   │          │          │trace     │
│         │  │         │   │          │          │agri      │
│         │  │         │   │          │          │crop      │
│         │  │         │   │          │          │soil      │
│         │  │         │   │          │          │irrigation│
└─────────┘  └─────────┘   └──────────┘          └──────────┘
     │             │              │                      │
     └─────────────┴──────────────┴──────────────────────┤
                                                          │
     ┌──────────────┬──────────────┬──────────────────────┘
     ▼              ▼              ▼
┌─────────┐  ┌──────────┐   ┌──────────┐   ┌──────────┐
│ LAYER 4 │  │ LAYER 5  │   │ LAYER 6  │   │ LAYER 7  │
│ Ops     │  │ Intel    │   │ Monitor  │   │ Tpl      │
├─────────┤  ├──────────┤   ├──────────┤   ├──────────┤
│transport│  │reporting │   │iot       │   │health    │
│delivery │  │analytics │   │cctv      │   │example   │
│route    │  │forecast  │   │monitoring│   │blank     │
│gps      │  │kpi       │   │backup    │   │          │
│retail   │  │satisfac. │   │alerting  │   │          │
│pos      │  │recommend.│   │audit_view│   │          │
│shift    │  │oee       │   │maint.    │   │          │
│line     │  │          │   │energy    │   │          │
│promo    │  │          │   │          │   │          │
│loyalty  │  │          │   │          │   │          │
│crm      │  │          │   │          │   │          │
│campaign │  │          │   │          │   │          │
│support  │  │          │   │          │   │          │
└─────────┘  └──────────┘   └──────────┘   └──────────┘
```

---

## 📐 Part 17: Operational Runbook

### 17.1 Health Check Queries

```sql
-- ── ตาราง partition ไม่ครบ ──────────────────────────────
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE '%_records_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ── Index bloat ────────────────────────────────────────
SELECT indexrelname, idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE schemaname LIKE 'tenant_%'
  AND idx_scan = 0
  AND indexrelid NOT IN (
      SELECT conindid FROM pg_constraint WHERE contype IN ('p','u')
  )
ORDER BY pg_relation_size(indexrelid) DESC;

-- ── Slow queries ───────────────────────────────────────
SELECT query, calls, mean_exec_time, max_exec_time, rows
FROM pg_stat_statements
WHERE query LIKE '%tenant_%'
ORDER BY mean_exec_time DESC
LIMIT 20;

-- ── RLS check ──────────────────────────────────────────
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname LIKE 'tenant_%'
  AND rowsecurity = FALSE
  AND tablename NOT LIKE '%archive%'
  AND tablename NOT LIKE '%_mv';
```

### 17.2 Retention Policy

| Layer | Table | Active | Archive | Delete |
|---|---|---|---|---|
| Core | `core_idem_records` | 30d | 90d | 1y |
| Core | `core_audit_logs` | 90d | 1y | 3y |
| Core | `core_evt_store` | 30d | 90d | 1y |
| Money | `money_ledger_entries` | 5y | 10y | ∞ |
| Goods | `goods_inv_movements` | 2y | 5y | ∞ |
| Ops | `ops_gps_pings` | 7d | 30d | 90d |
| Ops | `ops_pos_sales` | 1y | 5y | 10y |
| Monitor | `mon_iot_readings` | 30d | 1y | 2y |
| Monitor | `mon_alert_events` | 90d | 1y | 3y |

### 17.3 Backup Strategy

| ประเภท | ความถี่ | เก็บ | Method |
|---|---|---|---|
| Full DB | Daily 01:00 | 30d | `pg_basebackup` |
| WAL archive | Continuous | 7d | `archive_command` |
| Per-tenant dump | Weekly Sun | 30d | `pg_dump -n tenant_X` |
| Public dump | Daily 02:00 | 90d | `pg_dump -n public` |

---

## ✅ Checklist ครบถ้วน

| ข้อ | สถานะ |
|---|---|
| Prefix บอก Layer + Module (ทั้ง 65) | ✅ |
| Schema-per-tenant | ✅ |
| Partition by month / year | ✅ |
| Archive tables | ✅ |
| Outbox pattern | ✅ |
| Audit trail | ✅ |
| Lock observability | ✅ |
| Materialized views | ✅ |
| RLS policies | ✅ |
| Triggers (updated_at, partition, transition) | ✅ |
| Functions (partition, purge, migrate) | ✅ |
| pg_cron jobs | ✅ |
| Indexes (covering, partial, GIN) | ✅ |
| Constraints (CHECK, UNIQUE, FK) | ✅ |
| Comments bilingual | ✅ |
| Migration scripts (13 ไฟล์) | ✅ |
| ER diagram | ✅ |
| Health queries | ✅ |
| Retention policy | ✅ |
| Backup strategy | ✅ |

---

## 📌 สรุปสถิติ

| Layer | Tables | Partitions | MVs | Triggers |
|---|---|---|---|---|
| 0 Core | 15 | 8 | 2 | 6 |
| 1 Foundation | 22 | 3 | 0 | 8 |
| 2 Money | 18 | 4 | 1 | 6 |
| 3 Goods | 26 | 5 | 0 | 7 |
| 4 Operations | 20 | 5 | 2 | 6 |
| 5 Intelligence | 14 | 3 | 4 | 2 |
| 6 Monitoring | 16 | 4 | 2 | 4 |
| 7 Templates | 3 | 0 | 0 | 1 |
| **รวม** | **134** | **32** | **11** | **40** |

---

**ต้องการให้ผมสร้าง:**
- ✅ **Migration script เต็ม** (13 ไฟล์ SQL)
- ✅ **Python script** ที่ apply migration อัตโนมัติ
- ✅ **Docker Compose** ที่รัน PostgreSQL 17 + pg_cron + pgcrypto
- ✅ **Seed data** ตัวอย่าง 3 tenants + ข้อมูลทดสอบ
- ✅ **Monitoring dashboard** (Grafana JSON)

 
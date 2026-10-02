-- =====================================================================
-- tool_calling module — full DDL
-- schema: public
-- source: app/modules/tool_calling/infrastructure/models.py
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- for gen_random_uuid()

-- ─── tool_definitions ────────────────────────────────────────────────
CREATE TABLE public.tool_definitions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        UUID         NOT NULL,
    name             VARCHAR(100) NOT NULL,
    description      TEXT         NOT NULL DEFAULT '',
    parameters_json  TEXT         NOT NULL DEFAULT '{}',
    returns_json     TEXT         NOT NULL DEFAULT '{}',
    version          VARCHAR(20)  NOT NULL DEFAULT '1.0.0',
    kind             VARCHAR(20)  NOT NULL DEFAULT 'http',
    risk_level       VARCHAR(20)  NOT NULL DEFAULT 'low',
    visibility       VARCHAR(20)  NOT NULL DEFAULT 'tenant',
    timeout_seconds  INTEGER      NOT NULL DEFAULT 30,
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_tool_name UNIQUE (tenant_id, name)
);

CREATE INDEX ix_tool_def_tenant ON public.tool_definitions (tenant_id);


-- ─── tool_registrations ──────────────────────────────────────────────
CREATE TABLE public.tool_registrations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID        NOT NULL,
    tool_id             UUID        NOT NULL,
    enabled             BOOLEAN     NOT NULL DEFAULT TRUE,
    rate_limit_per_min  INTEGER     NOT NULL DEFAULT 60,
    scopes_json         TEXT        NOT NULL DEFAULT '[]',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_tool_reg_tool UNIQUE (tool_id)
);


-- ─── tool_invocations ────────────────────────────────────────────────
CREATE TABLE public.tool_invocations (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        UUID          NOT NULL,
    user_id          UUID          NOT NULL,
    tool_id          UUID          NOT NULL,
    tool_name        VARCHAR(100)  NOT NULL DEFAULT '',
    args_json        TEXT          NOT NULL DEFAULT '{}',
    result_json      TEXT          NOT NULL DEFAULT '{}',
    status           VARCHAR(20)   NOT NULL DEFAULT 'SUCCESS',
    latency_ms       INTEGER       NOT NULL DEFAULT 0,
    error_code       VARCHAR(50)   NOT NULL DEFAULT '',
    error_message    TEXT          NOT NULL DEFAULT '',
    tokens_used      INTEGER       NOT NULL DEFAULT 0,
    cost_usd         NUMERIC(12,8) NOT NULL DEFAULT 0,
    idempotency_key  VARCHAR(100)  NOT NULL DEFAULT '',
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX ix_tool_inv_tenant ON public.tool_invocations (tenant_id, created_at);
CREATE INDEX ix_tool_inv_tool   ON public.tool_invocations (tool_id,   created_at);


-- ─── tool_permissions ────────────────────────────────────────────────
CREATE TABLE public.tool_permissions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID        NOT NULL,
    tool_id     UUID        NOT NULL,
    role        VARCHAR(50) NOT NULL,
    allowed     BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_tool_perm_role UNIQUE (tool_id, role)
);
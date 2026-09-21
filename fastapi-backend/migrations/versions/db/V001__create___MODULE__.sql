-- ═══════════════════════════════════════════════════════════════
-- V001__create_money.sql
-- Module: money | Prefix: mon | Layer: 2
-- Description: สร้างตาราง + index + RLS policy + trigger
-- ═══════════════════════════════════════════════════════════════
BEGIN;

CREATE SCHEMA IF NOT EXISTS tenant_mon;
CREATE SEQUENCE IF NOT EXISTS mon_number_seq START 1;

CREATE TABLE tenant_mon.moneys (
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
    CONSTRAINT uq_money_code   UNIQUE (tenant_id, code),
    CONSTRAINT ck_money_amount CHECK (amount >= 0),
    CONSTRAINT ck_money_status CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'))
);

CREATE INDEX ix_money_tenant_status
    ON tenant_mon.moneys(tenant_id, status)
    WHERE deleted_at IS NULL;
CREATE INDEX ix_money_code ON tenant_mon.moneys(code);
CREATE INDEX ix_money_created ON tenant_mon.moneys(created_at DESC);

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_money_updated_at
    BEFORE UPDATE ON tenant_mon.moneys
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE tenant_mon.moneys ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_mon.moneys FORCE ROW LEVEL SECURITY;

CREATE POLICY p_money_tenant ON tenant_mon.moneys
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
-- ═══════════════════════════════════════════════════════════════
-- V001__create_inventory.sql
-- Module: inventory | Prefix: inv | Layer: 3
-- Description: สร้างตาราง + index + RLS policy + trigger
-- ═══════════════════════════════════════════════════════════════
BEGIN;

CREATE SCHEMA IF NOT EXISTS tenant_inv;
CREATE SEQUENCE IF NOT EXISTS inv_number_seq START 1;

CREATE TABLE tenant_inv.inventorys (
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
    CONSTRAINT uq_inventory_code   UNIQUE (tenant_id, code),
    CONSTRAINT ck_inventory_amount CHECK (amount >= 0),
    CONSTRAINT ck_inventory_status CHECK (status IN ('ACTIVE','INACTIVE','ARCHIVED'))
);

CREATE INDEX ix_inventory_tenant_status
    ON tenant_inv.inventorys(tenant_id, status)
    WHERE deleted_at IS NULL;
CREATE INDEX ix_inventory_code ON tenant_inv.inventorys(code);
CREATE INDEX ix_inventory_created ON tenant_inv.inventorys(created_at DESC);

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_inventory_updated_at
    BEFORE UPDATE ON tenant_inv.inventorys
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE tenant_inv.inventorys ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_inv.inventorys FORCE ROW LEVEL SECURITY;

CREATE POLICY p_inventory_tenant ON tenant_inv.inventorys
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
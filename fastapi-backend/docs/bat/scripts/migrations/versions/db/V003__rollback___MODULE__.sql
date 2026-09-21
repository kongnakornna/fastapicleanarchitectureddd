-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_inventory.sql
-- Description: rollback ทั้งหมด (ใช้ตอน dev/staging เท่านั้น)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER  IF EXISTS trg_inventory_updated_at ON tenant_inv.inventorys;
DROP POLICY   IF EXISTS p_inventory_tenant       ON tenant_inv.inventorys;
DROP TABLE    IF EXISTS tenant_inv.inventorys CASCADE;
DROP SEQUENCE IF EXISTS inv_number_seq;

COMMIT;
-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_money.sql
-- Description: rollback ทั้งหมด (ใช้ตอน dev/staging เท่านั้น)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER  IF EXISTS trg_money_updated_at ON tenant_mon.moneys;
DROP POLICY   IF EXISTS p_money_tenant       ON tenant_mon.moneys;
DROP TABLE    IF EXISTS tenant_mon.moneys CASCADE;
DROP SEQUENCE IF EXISTS mon_number_seq;

COMMIT;
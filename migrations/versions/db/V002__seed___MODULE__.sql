-- ═══════════════════════════════════════════════════════════════
-- V002__seed_money.sql
-- Description: seed ข้อมูลตั้งต้น (system default)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO tenant_mon.moneys (tenant_id, code, name, status, amount)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'SYS-DEFAULT',
    'System Default',
    'ACTIVE',
    0
)
ON CONFLICT (tenant_id, code) DO NOTHING;

COMMIT;
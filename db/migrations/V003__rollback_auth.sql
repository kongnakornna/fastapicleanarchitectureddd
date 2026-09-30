-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_auth.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_auth_updated ON "public"."auth_authentications";
DROP POLICY IF EXISTS p_auth_tenant ON "public"."auth_authentications";
DROP TABLE IF EXISTS "public"."auth_access_tokens" CASCADE;
DROP TABLE IF EXISTS "public"."auth_refresh_tokens" CASCADE;
DROP TABLE IF EXISTS "public"."auth_authentications" CASCADE;
DROP FUNCTION IF EXISTS public.set_updated_at_auth();

COMMIT;

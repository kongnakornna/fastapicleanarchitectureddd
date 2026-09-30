-- V005__cache_ws_bigo.sql
BEGIN;
CREATE TABLE IF NOT EXISTS "public"."bigo_cache_stats" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "namespace" varchar(100) NOT NULL DEFAULT 'bigo',
  "hits" int4 NOT NULL DEFAULT 0,
  "misses" int4 NOT NULL DEFAULT 0,
  "sets" int4 NOT NULL DEFAULT 0,
  "deletes" int4 NOT NULL DEFAULT 0,
  "errors" int4 NOT NULL DEFAULT 0,
  "hit_ratio" numeric(6,4) NOT NULL DEFAULT 0,
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_cache_stats_pkey" PRIMARY KEY ("id")
);
CREATE INDEX IF NOT EXISTS "ix_bigo_cache_stats_tenant" ON "public"."bigo_cache_stats" USING btree ("tenant_id", "captured_at" DESC);

CREATE TABLE IF NOT EXISTS "public"."bigo_ws_sessions" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "conn_id" varchar(64) NOT NULL,
  "user_id" varchar(64) NULL,
  "rooms_json" text NOT NULL DEFAULT '[]',
  "connected_at" timestamptz(6) NOT NULL DEFAULT now(),
  "disconnected_at" timestamptz(6) NULL,
  "duration_s" int4 NOT NULL DEFAULT 0,
  "messages_sent" int4 NOT NULL DEFAULT 0,
  "messages_recv" int4 NOT NULL DEFAULT 0,
  "close_reason" varchar(100) NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_ws_sessions_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_bigo_ws_conn" UNIQUE ("tenant_id", "conn_id")
);
CREATE INDEX IF NOT EXISTS "ix_bigo_ws_tenant" ON "public"."bigo_ws_sessions" USING btree ("tenant_id", "connected_at" DESC);
CREATE INDEX IF NOT EXISTS "ix_bigo_ws_user" ON "public"."bigo_ws_sessions" USING btree ("user_id");

DROP TRIGGER IF EXISTS trg_bigo_cache_stats_updated ON "public"."bigo_cache_stats";
CREATE TRIGGER trg_bigo_cache_stats_updated BEFORE UPDATE ON "public"."bigo_cache_stats"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_bigo();

DROP TRIGGER IF EXISTS trg_bigo_ws_sessions_updated ON "public"."bigo_ws_sessions";
CREATE TRIGGER trg_bigo_ws_sessions_updated BEFORE UPDATE ON "public"."bigo_ws_sessions"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_bigo();

ALTER TABLE "public"."bigo_cache_stats" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."bigo_ws_sessions"  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_bigo_cache_stats ON "public"."bigo_cache_stats";
CREATE POLICY p_bigo_cache_stats ON "public"."bigo_cache_stats"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_bigo_ws_sessions ON "public"."bigo_ws_sessions";
CREATE POLICY p_bigo_ws_sessions ON "public"."bigo_ws_sessions"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;

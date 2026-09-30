-- V004__pipeline_reports_bigo.sql
BEGIN;
CREATE TABLE IF NOT EXISTS "public"."bigo_pipeline_reports" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "trace_id" varchar(64) NOT NULL,
  "n" int4 NOT NULL DEFAULT 0,
  "complexity" varchar(20) NOT NULL DEFAULT 'O(n)',
  "status" varchar(20) NOT NULL DEFAULT 'PASS',
  "priority" varchar(20) NOT NULL DEFAULT 'normal',
  "rss_mb" numeric(20,4) NOT NULL DEFAULT 0,
  "pressure" varchar(20) NOT NULL DEFAULT 'NORMAL',
  "duration_ms" int4 NOT NULL DEFAULT 0,
  "kafka_partition" int4 NOT NULL DEFAULT 1,
  "kafka_sent" bool NOT NULL DEFAULT false,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_pipeline_reports_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_bigo_pipeline_status" CHECK (status IN ('PASS','WARNING','CRITICAL')),
  CONSTRAINT "ck_bigo_pipeline_priority" CHECK (priority IN ('high','normal','low','dlq')),
  CONSTRAINT "ck_bigo_pipeline_pressure" CHECK (pressure IN ('NORMAL','ELEVATED','HIGH','CRITICAL','OOM'))
);
CREATE INDEX IF NOT EXISTS "ix_bigo_pipeline_tenant" ON "public"."bigo_pipeline_reports" USING btree ("tenant_id", "created_at" DESC);
CREATE INDEX IF NOT EXISTS "ix_bigo_pipeline_trace" ON "public"."bigo_pipeline_reports" USING btree ("trace_id");
CREATE INDEX IF NOT EXISTS "ix_bigo_pipeline_status" ON "public"."bigo_pipeline_reports" USING btree ("tenant_id", "status", "created_at" DESC);

DROP TRIGGER IF EXISTS trg_bigo_pipeline_updated ON "public"."bigo_pipeline_reports";
CREATE TRIGGER trg_bigo_pipeline_updated BEFORE UPDATE ON "public"."bigo_pipeline_reports"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_bigo();

ALTER TABLE "public"."bigo_pipeline_reports" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_bigo_pipeline ON "public"."bigo_pipeline_reports";
CREATE POLICY p_bigo_pipeline ON "public"."bigo_pipeline_reports"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
COMMIT;

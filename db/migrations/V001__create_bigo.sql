-- V001__create_bigo.sql | Schema: public
BEGIN;

CREATE TABLE IF NOT EXISTS "public"."bigo_metrics" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "kind" varchar(50) NOT NULL,
  "name" varchar(200) NOT NULL,
  "value" numeric(20,8) NOT NULL DEFAULT 0,
  "unit" varchar(20) NOT NULL DEFAULT '',
  "labels_json" text NOT NULL DEFAULT '{}',
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_metrics_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_bigo_metric_kind" CHECK (
    kind IN ('latency','throughput','memory_rss','memory_heap',
             'cpu_percent','gc_pause','queue_depth','kafka_lag','error_rate')
  )
);
CREATE INDEX IF NOT EXISTS "ix_bigo_metric_tenant" ON "public"."bigo_metrics" USING btree ("tenant_id", "captured_at" DESC);
CREATE INDEX IF NOT EXISTS "ix_bigo_metric_kind" ON "public"."bigo_metrics" USING btree ("tenant_id", "kind", "captured_at" DESC);

CREATE TABLE IF NOT EXISTS "public"."bigo_profiles" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "function_name" varchar(200) NOT NULL,
  "module" varchar(200) NOT NULL DEFAULT '',
  "complexity" varchar(20) NOT NULL DEFAULT 'UNKNOWN',
  "sample_size" int4 NOT NULL DEFAULT 0,
  "avg_ms" numeric(20,8) NOT NULL DEFAULT 0,
  "p95_ms" numeric(20,8) NOT NULL DEFAULT 0,
  "memory_peak_mb" numeric(20,8) NOT NULL DEFAULT 0,
  "notes" text NOT NULL DEFAULT '',
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_profiles_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_bigo_profile_complexity" CHECK (
    complexity IN ('O(1)','O(log n)','O(n)','O(n log n)',
                   'O(n^2)','O(n^3)','O(2^n)','O(n!)','UNKNOWN')
  )
);
CREATE INDEX IF NOT EXISTS "ix_bigo_profile_tenant" ON "public"."bigo_profiles" USING btree ("tenant_id", "captured_at" DESC);
CREATE INDEX IF NOT EXISTS "ix_bigo_profile_function" ON "public"."bigo_profiles" USING btree ("function_name", "captured_at" DESC);

CREATE TABLE IF NOT EXISTS "public"."bigo_memory_snapshots" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "process_id" int4 NOT NULL DEFAULT 0,
  "rss_mb" numeric(20,4) NOT NULL DEFAULT 0,
  "vms_mb" numeric(20,4) NOT NULL DEFAULT 0,
  "percent" numeric(8,4) NOT NULL DEFAULT 0,
  "pressure" varchar(20) NOT NULL DEFAULT 'NORMAL',
  "top_allocations_json" text NOT NULL DEFAULT '[]',
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_memory_snapshots_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_bigo_mem_pressure" CHECK (pressure IN ('NORMAL','ELEVATED','HIGH','CRITICAL','OOM'))
);
CREATE INDEX IF NOT EXISTS "ix_bigo_mem_tenant" ON "public"."bigo_memory_snapshots" USING btree ("tenant_id", "captured_at" DESC);

CREATE TABLE IF NOT EXISTS "public"."bigo_memory_leaks" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "location" varchar(500) NOT NULL,
  "leak_type" varchar(50) NOT NULL DEFAULT 'UNKNOWN',
  "growth_mb_per_hour" numeric(20,4) NOT NULL DEFAULT 0,
  "current_bytes" int4 NOT NULL DEFAULT 0,
  "samples" int4 NOT NULL DEFAULT 0,
  "status" varchar(20) NOT NULL DEFAULT 'OPEN',
  "detected_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_memory_leaks_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_bigo_leak_type" CHECK (
    leak_type IN ('REFERENCE_CYCLE','UNBOUNDED_CACHE',
                  'LISTENER_LEAK','THREAD_LOCAL','NATIVE_BUFFER','UNKNOWN')
  ),
  CONSTRAINT "ck_bigo_leak_status" CHECK (status IN ('OPEN','INVESTIGATING','RESOLVED','IGNORED'))
);
CREATE INDEX IF NOT EXISTS "ix_bigo_leak_tenant" ON "public"."bigo_memory_leaks" USING btree ("tenant_id", "status", "detected_at" DESC);

CREATE TABLE IF NOT EXISTS "public"."bigo_kafka_topics" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "name" varchar(300) NOT NULL,
  "partitions" int4 NOT NULL DEFAULT 3,
  "replication_factor" int4 NOT NULL DEFAULT 1,
  "retention_ms" int4 NOT NULL DEFAULT 604800000,
  "max_message_bytes" int4 NOT NULL DEFAULT 1048576,
  "is_active" bool NOT NULL DEFAULT true,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_kafka_topics_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_bigo_topic_name" UNIQUE ("tenant_id", "name")
);

CREATE TABLE IF NOT EXISTS "public"."bigo_kafka_queues" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "topic" varchar(300) NOT NULL,
  "partition" int4 NOT NULL DEFAULT 0,
  "current_offset" int4 NOT NULL DEFAULT 0,
  "log_end_offset" int4 NOT NULL DEFAULT 0,
  "lag" int4 NOT NULL DEFAULT 0,
  "health" varchar(20) NOT NULL DEFAULT 'HEALTHY',
  "captured_at" timestamptz(6) NOT NULL DEFAULT now(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_kafka_queues_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_bigo_queue_health" CHECK (health IN ('HEALTHY','WARNING','DEGRADED','CRITICAL','OFFLINE'))
);
CREATE INDEX IF NOT EXISTS "ix_bigo_queue_topic" ON "public"."bigo_kafka_queues" USING btree ("topic", "partition", "captured_at" DESC);

CREATE TABLE IF NOT EXISTS "public"."bigo_kafka_consumers" (
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL,
  "group_id" varchar(300) NOT NULL,
  "topic" varchar(300) NOT NULL,
  "member_count" int4 NOT NULL DEFAULT 0,
  "total_lag" int4 NOT NULL DEFAULT 0,
  "health" varchar(20) NOT NULL DEFAULT 'HEALTHY',
  "last_commit_at" timestamptz(6) NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "bigo_kafka_consumers_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_bigo_consumer" UNIQUE ("tenant_id", "group_id", "topic"),
  CONSTRAINT "ck_bigo_consumer_health" CHECK (health IN ('HEALTHY','WARNING','DEGRADED','CRITICAL','OFFLINE'))
);

CREATE OR REPLACE FUNCTION public.set_updated_at_bigo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

ALTER TABLE "public"."bigo_metrics" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."bigo_profiles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."bigo_memory_snapshots" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."bigo_memory_leaks" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."bigo_kafka_topics" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."bigo_kafka_queues" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."bigo_kafka_consumers" ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_bigo_metric ON "public"."bigo_metrics";
CREATE POLICY p_bigo_metric ON "public"."bigo_metrics"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_bigo_profile ON "public"."bigo_profiles";
CREATE POLICY p_bigo_profile ON "public"."bigo_profiles"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_bigo_mem_snap ON "public"."bigo_memory_snapshots";
CREATE POLICY p_bigo_mem_snap ON "public"."bigo_memory_snapshots"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_bigo_mem_leak ON "public"."bigo_memory_leaks";
CREATE POLICY p_bigo_mem_leak ON "public"."bigo_memory_leaks"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_bigo_topic ON "public"."bigo_kafka_topics";
CREATE POLICY p_bigo_topic ON "public"."bigo_kafka_topics"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_bigo_queue ON "public"."bigo_kafka_queues";
CREATE POLICY p_bigo_queue ON "public"."bigo_kafka_queues"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_bigo_consumer ON "public"."bigo_kafka_consumers";
CREATE POLICY p_bigo_consumer ON "public"."bigo_kafka_consumers"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;

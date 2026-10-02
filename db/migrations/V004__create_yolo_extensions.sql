-- V004__create_yolo_extensions.sql | 9 extension tables
BEGIN;
CREATE TABLE "public"."yolo_settings" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL UNIQUE,
  "default_model" varchar(50) NOT NULL DEFAULT 'yolov8n.pt',
  "device" varchar(20) NOT NULL DEFAULT 'auto',
  "conf_threshold" numeric(4,3) NOT NULL DEFAULT 0.25,
  "iou_threshold" numeric(4,3) NOT NULL DEFAULT 0.45,
  "max_batch_size" int4 NOT NULL DEFAULT 32,
  "timeout_seconds" int4 NOT NULL DEFAULT 30,
  "cache_ttl" int4 NOT NULL DEFAULT 300,
  "artifact_bucket" varchar(200) NOT NULL DEFAULT 'yolo-artifacts',
  "enable_tensorrt" bool NOT NULL DEFAULT false,
  "enable_half" bool NOT NULL DEFAULT true,
  "max_trainings" int4 NOT NULL DEFAULT 1,
  "retention_days" int4 NOT NULL DEFAULT 90,
  "extra_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at" timestamptz NOT NULL DEFAULT now(),
  "updated_at" timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "public"."yolo_categories" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL, "parent_id" uuid,
  "slug" varchar(100) NOT NULL, "name_th" varchar(200) NOT NULL,
  "name_en" varchar(200) NOT NULL, "description" text NOT NULL DEFAULT '',
  "icon" varchar(20), "color" varchar(7) NOT NULL DEFAULT '#3B82F6',
  "sort_order" int4 NOT NULL DEFAULT 0, "is_active" bool NOT NULL DEFAULT true,
  "extra_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at" timestamptz NOT NULL DEFAULT now(),
  "updated_at" timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "uq_yolo_cat_slug" UNIQUE ("tenant_id","slug")
);
CREATE INDEX "ix_yolo_cat_tenant" ON "public"."yolo_categories" ("tenant_id");

CREATE TABLE "public"."yolo_counting_sessions" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL, "model_id" uuid NOT NULL,
  "mode" varchar(20) NOT NULL, "config_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "total_count" int4 NOT NULL DEFAULT 0,
  "status" varchar(20) NOT NULL DEFAULT 'RUNNING',
  "started_at" timestamptz NOT NULL DEFAULT now(), "finished_at" timestamptz,
  "created_at" timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "public"."yolo_counting_results" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "session_id" uuid NOT NULL, "tenant_id" uuid NOT NULL,
  "frame_index" int4, "total_count" int4 NOT NULL,
  "per_class_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "regions_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "confidence_avg" numeric(4,3), "processing_ms" int4,
  "created_at" timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX "ix_yolo_cr_session" ON "public"."yolo_counting_results" ("session_id");

CREATE TABLE "public"."yolo_diseases" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "code" varchar(100) NOT NULL UNIQUE,
  "name_th" varchar(200) NOT NULL, "name_en" varchar(200) NOT NULL,
  "pathogen_type" varchar(20) NOT NULL,
  "treatment_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "prevention_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "description" text NOT NULL DEFAULT '',
  "created_at" timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE "public"."yolo_plant_diagnoses" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL, "model_id" uuid NOT NULL, "field_id" uuid,
  "image_hash" varchar(64) NOT NULL, "plant_species" varchar(200),
  "detections_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "overall_severity" varchar(20) NOT NULL,
  "health_score" numeric(5,2),
  "recommendations" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "treatment_plan" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "confidence" numeric(4,3),
  "created_at" timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX "ix_yolo_pd_tenant" ON "public"."yolo_plant_diagnoses" ("tenant_id","created_at");

CREATE TABLE "public"."yolo_fields" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL, "name" varchar(200) NOT NULL,
  "crop_type" varchar(100) NOT NULL, "area_sqm" numeric(10,2),
  "location_lat" numeric(10,7), "location_lng" numeric(10,7),
  "planting_date" date, "expected_harvest" date, "px_per_cm" numeric(6,2),
  "status" varchar(20) NOT NULL DEFAULT 'ACTIVE',
  "extra_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at" timestamptz NOT NULL DEFAULT now(),
  "updated_at" timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX "ix_yolo_fields_tenant" ON "public"."yolo_fields" ("tenant_id");

CREATE TABLE "public"."yolo_growth_assessments" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id" uuid NOT NULL, "field_id" uuid, "plant_id" uuid,
  "model_id" uuid NOT NULL, "image_hash" varchar(64) NOT NULL,
  "stage" varchar(20) NOT NULL, "stage_confidence" numeric(4,3),
  "metrics_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "health_score" numeric(5,2), "growth_rate_pct" numeric(6,2),
  "alerts_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "recommendations" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "created_at" timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX "ix_yolo_ga_field" ON "public"."yolo_growth_assessments" ("field_id","created_at");

ALTER TABLE "public"."yolo_settings" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_categories" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_counting_sessions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_counting_results" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_plant_diagnoses" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_fields" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_growth_assessments" ENABLE ROW LEVEL SECURITY;

CREATE POLICY p_yolo_settings ON "public"."yolo_settings"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_categories ON "public"."yolo_categories"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_cs ON "public"."yolo_counting_sessions"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_cr ON "public"."yolo_counting_results"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_pd ON "public"."yolo_plant_diagnoses"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_fields ON "public"."yolo_fields"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_ga ON "public"."yolo_growth_assessments"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;

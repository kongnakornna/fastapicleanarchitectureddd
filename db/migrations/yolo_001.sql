-- =====================================================================
-- V001__create_yolo.sql | 7 base tables
-- schema: public · prefix: yolo_
-- =====================================================================

CREATE TABLE "public"."yolo_datasets" (
  "id"             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "name"           varchar(200) NOT NULL,
  "format"         varchar(20) NOT NULL DEFAULT 'yolo',
  "root_uri"       text NOT NULL DEFAULT '',
  "image_count"    int4 NOT NULL DEFAULT 0,
  "class_count"    int4 NOT NULL DEFAULT 0,
  "splits_json"    jsonb NOT NULL DEFAULT '{}'::jsonb,
  "status"         varchar(20) NOT NULL DEFAULT 'DRAFT',
  "version"        int4 NOT NULL DEFAULT 1,
  "metadata_json"  jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at"     timestamptz NOT NULL DEFAULT now(),
  "updated_at"     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "ck_yolo_ds_format" CHECK (format IN ('yolo','coco','roboflow','labelimg')),
  CONSTRAINT "ck_yolo_ds_status" CHECK (status IN ('DRAFT','READY','TRAINING','ARCHIVED')),
  CONSTRAINT "uq_yolo_ds_name_ver" UNIQUE ("tenant_id","name","version")
);
CREATE INDEX "ix_yolo_ds_tenant" ON "public"."yolo_datasets" ("tenant_id");
CREATE INDEX "ix_yolo_ds_status" ON "public"."yolo_datasets" ("tenant_id","status");

CREATE TABLE "public"."yolo_classes" (
  "id"           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "dataset_id"   uuid NOT NULL,
  "name"         varchar(100) NOT NULL,
  "class_index"  int4 NOT NULL,
  "color"        varchar(7) NOT NULL DEFAULT '#FF0000',
  "count"        int4 NOT NULL DEFAULT 0,
  "created_at"   timestamptz NOT NULL DEFAULT now(),
  "updated_at"   timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "uq_yolo_class_idx"  UNIQUE ("dataset_id","class_index"),
  CONSTRAINT "uq_yolo_class_name" UNIQUE ("dataset_id","name")
);
CREATE INDEX "ix_yolo_class_tenant"  ON "public"."yolo_classes" ("tenant_id");
CREATE INDEX "ix_yolo_class_dataset" ON "public"."yolo_classes" ("dataset_id");

CREATE TABLE "public"."yolo_images" (
  "id"                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id"         uuid NOT NULL,
  "dataset_id"        uuid NOT NULL,
  "uri"               text NOT NULL,
  "content_hash"      varchar(64) NOT NULL,
  "width"             int4 NOT NULL DEFAULT 0,
  "height"            int4 NOT NULL DEFAULT 0,
  "size_bytes"        int4 NOT NULL DEFAULT 0,
  "split"             varchar(10) NOT NULL DEFAULT 'train',
  "annotation_count"  int4 NOT NULL DEFAULT 0,
  "created_at"        timestamptz NOT NULL DEFAULT now(),
  "updated_at"        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "ck_yolo_img_split" CHECK (split IN ('train','val','test')),
  CONSTRAINT "uq_yolo_img_hash"  UNIQUE ("dataset_id","content_hash")
);
CREATE INDEX "ix_yolo_img_tenant"  ON "public"."yolo_images" ("tenant_id");
CREATE INDEX "ix_yolo_img_dataset" ON "public"."yolo_images" ("dataset_id","split");
CREATE INDEX "ix_yolo_img_hash"    ON "public"."yolo_images" ("content_hash");

CREATE TABLE "public"."yolo_annotations" (
  "id"          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id"   uuid NOT NULL,
  "image_id"    uuid NOT NULL,
  "class_id"    uuid NOT NULL,
  "x_center"    float8 NOT NULL,
  "y_center"    float8 NOT NULL,
  "width"       float8 NOT NULL,
  "height"      float8 NOT NULL,
  "confidence"  numeric(5,4) NOT NULL DEFAULT 1.0,
  "is_hard"     bool NOT NULL DEFAULT false,
  "source"      varchar(50) NOT NULL DEFAULT 'manual',
  "created_at"  timestamptz NOT NULL DEFAULT now(),
  "updated_at"  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "ck_yolo_ann_x" CHECK (x_center >= 0 AND x_center <= 1),
  CONSTRAINT "ck_yolo_ann_y" CHECK (y_center >= 0 AND y_center <= 1),
  CONSTRAINT "ck_yolo_ann_w" CHECK (width    >  0 AND width    <= 1),
  CONSTRAINT "ck_yolo_ann_h" CHECK (height   >  0 AND height   <= 1)
);
CREATE INDEX "ix_yolo_ann_tenant" ON "public"."yolo_annotations" ("tenant_id");
CREATE INDEX "ix_yolo_ann_image"  ON "public"."yolo_annotations" ("image_id");
CREATE INDEX "ix_yolo_ann_class"  ON "public"."yolo_annotations" ("class_id");

CREATE TABLE "public"."yolo_trainings" (
  "id"               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "dataset_id"       uuid NOT NULL,
  "model_type"       varchar(20) NOT NULL,
  "epochs"           int4 NOT NULL DEFAULT 100,
  "batch_size"       int4 NOT NULL DEFAULT 16,
  "imgsz"            int4 NOT NULL DEFAULT 640,
  "lr0"              numeric(12,8) NOT NULL DEFAULT 0.01,
  "device"           varchar(20) NOT NULL DEFAULT 'auto',
  "patience"         int4 NOT NULL DEFAULT 50,
  "optimizer"        varchar(20) NOT NULL DEFAULT 'auto',
  "aug_config_json"  jsonb NOT NULL DEFAULT '{}'::jsonb,
  "status"           varchar(20) NOT NULL DEFAULT 'PENDING',
  "best_model_id"    uuid,
  "progress"         int4 NOT NULL DEFAULT 0,
  "error_message"    text NOT NULL DEFAULT '',
  "started_at"       timestamptz,
  "finished_at"      timestamptz,
  "duration_ms"      int4 NOT NULL DEFAULT 0,
  "created_at"       timestamptz NOT NULL DEFAULT now(),
  "updated_at"       timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "ck_yolo_tr_status"
    CHECK (status IN ('PENDING','RUNNING','SUCCESS','FAILED','CANCELLED'))
);
CREATE INDEX "ix_yolo_tr_tenant"  ON "public"."yolo_trainings" ("tenant_id","status");
CREATE INDEX "ix_yolo_tr_dataset" ON "public"."yolo_trainings" ("dataset_id","created_at");

CREATE TABLE "public"."yolo_models" (
  "id"            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "training_id"   uuid NOT NULL,
  "name"          varchar(200) NOT NULL,
  "version"       int4 NOT NULL DEFAULT 1,
  "weights_uri"   text NOT NULL DEFAULT '',
  "weights_hash"  varchar(64) NOT NULL DEFAULT '',
  "export_uri"    text NOT NULL DEFAULT '',
  "format"        varchar(20) NOT NULL DEFAULT 'pt',
  "mAP50"         numeric(6,4) NOT NULL DEFAULT 0,
  "mAP50_95"      numeric(6,4) NOT NULL DEFAULT 0,
  "precision_"    numeric(6,4) NOT NULL DEFAULT 0,
  "recall_"       numeric(6,4) NOT NULL DEFAULT 0,
  "metrics_json"  jsonb NOT NULL DEFAULT '{}'::jsonb,
  "is_active"     bool NOT NULL DEFAULT true,
  "is_deployed"   bool NOT NULL DEFAULT false,
  "deployed_at"   timestamptz,
  "created_at"    timestamptz NOT NULL DEFAULT now(),
  "updated_at"    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "ck_yolo_model_format"
    CHECK (format IN ('pt','onnx','engine','torchscript','coreml')),
  CONSTRAINT "uq_yolo_model_name_ver" UNIQUE ("tenant_id","name","version")
);
CREATE INDEX "ix_yolo_model_tenant"   ON "public"."yolo_models" ("tenant_id");
CREATE INDEX "ix_yolo_model_training" ON "public"."yolo_models" ("training_id");
CREATE INDEX "ix_yolo_model_active"   ON "public"."yolo_models" ("tenant_id","is_active");

CREATE TABLE "public"."yolo_inferences" (
  "id"               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "model_id"         uuid NOT NULL,
  "image_hash"       varchar(64) NOT NULL DEFAULT '',
  "detections_json"  jsonb NOT NULL DEFAULT '[]'::jsonb,
  "detection_count"  int4 NOT NULL DEFAULT 0,
  "latency_ms"       int4 NOT NULL DEFAULT 0,
  "source"           varchar(20) NOT NULL DEFAULT 'api',
  "created_at"       timestamptz NOT NULL DEFAULT now(),
  "updated_at"       timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "ck_yolo_inf_source"
    CHECK (source IN ('api','batch','stream','upload'))
);
CREATE INDEX "ix_yolo_inf_tenant" ON "public"."yolo_inferences" ("tenant_id","created_at");
CREATE INDEX "ix_yolo_inf_model"  ON "public"."yolo_inferences" ("model_id","created_at");
CREATE INDEX "ix_yolo_inf_hash"   ON "public"."yolo_inferences" ("image_hash");

-- Row-Level Security
ALTER TABLE "public"."yolo_datasets"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_classes"     ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_images"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_annotations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_trainings"   ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_models"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_inferences"  ENABLE ROW LEVEL SECURITY;

CREATE POLICY p_yolo_ds ON "public"."yolo_datasets"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_cls ON "public"."yolo_classes"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_img ON "public"."yolo_images"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_ann ON "public"."yolo_annotations"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_tr ON "public"."yolo_trainings"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_model ON "public"."yolo_models"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
CREATE POLICY p_yolo_inf ON "public"."yolo_inferences"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);


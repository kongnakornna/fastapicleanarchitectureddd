-- =====================================================================
-- Migration yolo_001 — add yolo base tables  (schema: public)
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ─── yolo_datasets ───────────────────────────────────────────────────
CREATE TABLE public.yolo_datasets (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID        NOT NULL,
    name          VARCHAR(200) NOT NULL,
    format        VARCHAR(20)  NOT NULL DEFAULT 'yolo',
    root_uri      TEXT         NOT NULL DEFAULT '',
    image_count   INTEGER      NOT NULL DEFAULT 0,
    class_count   INTEGER      NOT NULL DEFAULT 0,
    splits_json   JSONB        NOT NULL DEFAULT '{}'::jsonb,
    status        VARCHAR(20)  NOT NULL DEFAULT 'DRAFT',
    version       INTEGER      NOT NULL DEFAULT 1,
    metadata_json JSONB        NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_yolo_ds_name_ver UNIQUE (tenant_id, name, version)
);
CREATE INDEX ix_yolo_ds_tenant ON public.yolo_datasets (tenant_id);

-- ─── yolo_classes ────────────────────────────────────────────────────
CREATE TABLE public.yolo_classes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID        NOT NULL,
    dataset_id  UUID        NOT NULL,
    name        VARCHAR(100) NOT NULL,
    class_index INTEGER      NOT NULL,
    color       VARCHAR(7)   NOT NULL DEFAULT '#FF0000',
    count       INTEGER      NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_yolo_class_idx UNIQUE (dataset_id, class_index)
);

-- ─── yolo_images ─────────────────────────────────────────────────────
CREATE TABLE public.yolo_images (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        UUID        NOT NULL,
    dataset_id       UUID        NOT NULL,
    uri              TEXT        NOT NULL,
    content_hash     VARCHAR(64) NOT NULL,
    width            INTEGER     NOT NULL DEFAULT 0,
    height           INTEGER     NOT NULL DEFAULT 0,
    size_bytes       INTEGER     NOT NULL DEFAULT 0,
    split            VARCHAR(10) NOT NULL DEFAULT 'train',
    annotation_count INTEGER     NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_yolo_img_hash UNIQUE (dataset_id, content_hash)
);

-- ─── yolo_annotations ────────────────────────────────────────────────
CREATE TABLE public.yolo_annotations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID         NOT NULL,
    image_id    UUID         NOT NULL,
    class_id    UUID         NOT NULL,
    x_center    DOUBLE PRECISION NOT NULL,
    y_center    DOUBLE PRECISION NOT NULL,
    width       DOUBLE PRECISION NOT NULL,
    height      DOUBLE PRECISION NOT NULL,
    confidence  NUMERIC(5,4) NOT NULL DEFAULT 1.0,
    is_hard     BOOLEAN      NOT NULL DEFAULT FALSE,
    source      VARCHAR(50)  NOT NULL DEFAULT 'manual',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ─── yolo_trainings ──────────────────────────────────────────────────
CREATE TABLE public.yolo_trainings (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        UUID         NOT NULL,
    dataset_id       UUID         NOT NULL,
    model_type       VARCHAR(20)  NOT NULL,
    epochs           INTEGER      NOT NULL DEFAULT 100,
    batch_size       INTEGER      NOT NULL DEFAULT 16,
    imgsz            INTEGER      NOT NULL DEFAULT 640,
    lr0              NUMERIC(12,8) NOT NULL DEFAULT 0.01,
    device           VARCHAR(20)  NOT NULL DEFAULT 'auto',
    patience         INTEGER      NOT NULL DEFAULT 50,
    optimizer        VARCHAR(20)  NOT NULL DEFAULT 'auto',
    aug_config_json  JSONB        NOT NULL DEFAULT '{}'::jsonb,
    status           VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
    best_model_id    UUID,
    progress         INTEGER      NOT NULL DEFAULT 0,
    error_message    TEXT         NOT NULL DEFAULT '',
    started_at       TIMESTAMPTZ,
    finished_at      TIMESTAMPTZ,
    duration_ms      INTEGER      NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ─── yolo_models ─────────────────────────────────────────────────────
CREATE TABLE public.yolo_models (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id    UUID         NOT NULL,
    training_id  UUID         NOT NULL,
    name         VARCHAR(200) NOT NULL,
    version      INTEGER      NOT NULL DEFAULT 1,
    weights_uri  TEXT         NOT NULL DEFAULT '',
    weights_hash VARCHAR(64)  NOT NULL DEFAULT '',
    export_uri   TEXT         NOT NULL DEFAULT '',
    format       VARCHAR(20)  NOT NULL DEFAULT 'pt',
    "mAP50"      NUMERIC(6,4) NOT NULL DEFAULT 0,
    "mAP50_95"   NUMERIC(6,4) NOT NULL DEFAULT 0,
    precision_   NUMERIC(6,4) NOT NULL DEFAULT 0,
    recall_      NUMERIC(6,4) NOT NULL DEFAULT 0,
    metrics_json JSONB        NOT NULL DEFAULT '{}'::jsonb,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    is_deployed  BOOLEAN      NOT NULL DEFAULT FALSE,
    deployed_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_yolo_model_name_ver UNIQUE (tenant_id, name, version)
);

-- ─── yolo_inferences ─────────────────────────────────────────────────
CREATE TABLE public.yolo_inferences (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        UUID        NOT NULL,
    model_id         UUID        NOT NULL,
    image_hash       VARCHAR(64) NOT NULL DEFAULT '',
    detections_json  JSONB       NOT NULL DEFAULT '[]'::jsonb,
    detection_count  INTEGER     NOT NULL DEFAULT 0,
    latency_ms       INTEGER     NOT NULL DEFAULT 0,
    source           VARCHAR(20) NOT NULL DEFAULT 'api',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─── Row-Level Security ──────────────────────────────────────────────
ALTER TABLE public.yolo_datasets     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_classes      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_images       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_annotations  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_trainings    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_models       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_inferences   ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_yolo_datasets_tenant    ON public.yolo_datasets;
CREATE POLICY p_yolo_datasets_tenant    ON public.yolo_datasets
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_classes_tenant     ON public.yolo_classes;
CREATE POLICY p_yolo_classes_tenant     ON public.yolo_classes
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_images_tenant      ON public.yolo_images;
CREATE POLICY p_yolo_images_tenant      ON public.yolo_images
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_annotations_tenant ON public.yolo_annotations;
CREATE POLICY p_yolo_annotations_tenant ON public.yolo_annotations
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_trainings_tenant   ON public.yolo_trainings;
CREATE POLICY p_yolo_trainings_tenant   ON public.yolo_trainings
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_models_tenant      ON public.yolo_models;
CREATE POLICY p_yolo_models_tenant      ON public.yolo_models
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_inferences_tenant  ON public.yolo_inferences;
CREATE POLICY p_yolo_inferences_tenant  ON public.yolo_inferences
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
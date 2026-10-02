-- =====================================================================
-- Migration yolo_002 — add yolo extension tables  (schema: public)
-- =====================================================================

-- ─── yolo_settings ───────────────────────────────────────────────────
CREATE TABLE public.yolo_settings (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         UUID         NOT NULL,
    default_model     VARCHAR(50)  NOT NULL DEFAULT 'yolov8n.pt',
    device            VARCHAR(20)  NOT NULL DEFAULT 'auto',
    conf_threshold    NUMERIC(4,3) NOT NULL DEFAULT 0.25,
    iou_threshold     NUMERIC(4,3) NOT NULL DEFAULT 0.45,
    max_batch_size    INTEGER      NOT NULL DEFAULT 32,
    timeout_seconds   INTEGER      NOT NULL DEFAULT 30,
    cache_ttl         INTEGER      NOT NULL DEFAULT 300,
    artifact_bucket   VARCHAR(200) NOT NULL DEFAULT 'yolo-artifacts',
    enable_tensorrt   BOOLEAN      NOT NULL DEFAULT FALSE,
    enable_half       BOOLEAN      NOT NULL DEFAULT TRUE,
    max_trainings     INTEGER      NOT NULL DEFAULT 1,
    retention_days    INTEGER      NOT NULL DEFAULT 90,
    extra_json        JSONB        NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_yolo_settings_tenant UNIQUE (tenant_id)
);

-- ─── yolo_categories ─────────────────────────────────────────────────
CREATE TABLE public.yolo_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID         NOT NULL,
    parent_id   UUID,
    slug        VARCHAR(100) NOT NULL,
    name_th     VARCHAR(200) NOT NULL,
    name_en     VARCHAR(200) NOT NULL,
    description TEXT         NOT NULL DEFAULT '',
    icon        VARCHAR(20),
    color       VARCHAR(7)   NOT NULL DEFAULT '#3B82F6',
    sort_order  INTEGER      NOT NULL DEFAULT 0,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    extra_json  JSONB        NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_yolo_cat_slug UNIQUE (tenant_id, slug)
);

-- ─── yolo_counting_sessions ──────────────────────────────────────────
CREATE TABLE public.yolo_counting_sessions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id    UUID        NOT NULL,
    model_id     UUID        NOT NULL,
    mode         VARCHAR(20) NOT NULL,
    config_json  JSONB       NOT NULL DEFAULT '{}'::jsonb,
    total_count  INTEGER     NOT NULL DEFAULT 0,
    status       VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─── yolo_counting_results ───────────────────────────────────────────
CREATE TABLE public.yolo_counting_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID         NOT NULL,
    tenant_id       UUID         NOT NULL,
    frame_index     INTEGER,
    total_count     INTEGER      NOT NULL,
    per_class_json  JSONB        NOT NULL DEFAULT '[]'::jsonb,
    regions_json    JSONB        NOT NULL DEFAULT '[]'::jsonb,
    confidence_avg  NUMERIC(4,3),
    processing_ms   INTEGER,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ─── yolo_diseases ───────────────────────────────────────────────────
CREATE TABLE public.yolo_diseases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(100) NOT NULL,
    name_th         VARCHAR(200) NOT NULL,
    name_en         VARCHAR(200) NOT NULL,
    pathogen_type   VARCHAR(20)  NOT NULL,
    description     TEXT         NOT NULL DEFAULT '',
    treatment_json  JSONB        NOT NULL DEFAULT '[]'::jsonb,
    prevention_json JSONB        NOT NULL DEFAULT '[]'::jsonb,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT uq_yolo_diseases_code UNIQUE (code)
);

-- ─── yolo_plant_diagnoses ────────────────────────────────────────────
CREATE TABLE public.yolo_plant_diagnoses (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        UUID         NOT NULL,
    model_id         UUID         NOT NULL,
    field_id         UUID,
    image_hash       VARCHAR(64)  NOT NULL,
    plant_species    VARCHAR(200),
    detections_json  JSONB        NOT NULL DEFAULT '[]'::jsonb,
    overall_severity VARCHAR(20)  NOT NULL,
    health_score     NUMERIC(5,2),
    recommendations  JSONB        NOT NULL DEFAULT '[]'::jsonb,
    treatment_plan   JSONB        NOT NULL DEFAULT '[]'::jsonb,
    confidence       NUMERIC(4,3),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ─── yolo_fields ─────────────────────────────────────────────────────
CREATE TABLE public.yolo_fields (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        UUID          NOT NULL,
    name             VARCHAR(200)  NOT NULL,
    crop_type        VARCHAR(100)  NOT NULL,
    area_sqm         NUMERIC(10,2),
    location_lat     NUMERIC(10,7),
    location_lng     NUMERIC(10,7),
    planting_date    DATE,
    expected_harvest DATE,
    px_per_cm        NUMERIC(6,2),
    status           VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE',
    extra_json       JSONB         NOT NULL DEFAULT '{}'::jsonb,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- ─── yolo_growth_assessments ─────────────────────────────────────────
CREATE TABLE public.yolo_growth_assessments (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         UUID         NOT NULL,
    field_id          UUID,
    plant_id          UUID,
    model_id          UUID         NOT NULL,
    image_hash        VARCHAR(64)  NOT NULL,
    stage             VARCHAR(20)  NOT NULL,
    stage_confidence  NUMERIC(4,3),
    metrics_json      JSONB        NOT NULL DEFAULT '{}'::jsonb,
    health_score      NUMERIC(5,2),
    growth_rate_pct   NUMERIC(6,2),
    alerts_json       JSONB        NOT NULL DEFAULT '[]'::jsonb,
    recommendations   JSONB        NOT NULL DEFAULT '[]'::jsonb,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- ─── Row-Level Security ──────────────────────────────────────────────
ALTER TABLE public.yolo_settings            ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_categories          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_counting_sessions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_counting_results    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_diseases            ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_plant_diagnoses     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_fields              ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.yolo_growth_assessments  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_yolo_settings_tenant           ON public.yolo_settings;
CREATE POLICY p_yolo_settings_tenant           ON public.yolo_settings
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_categories_tenant         ON public.yolo_categories;
CREATE POLICY p_yolo_categories_tenant         ON public.yolo_categories
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_counting_sessions_tenant  ON public.yolo_counting_sessions;
CREATE POLICY p_yolo_counting_sessions_tenant  ON public.yolo_counting_sessions
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_counting_results_tenant   ON public.yolo_counting_results;
CREATE POLICY p_yolo_counting_results_tenant   ON public.yolo_counting_results
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_diseases_tenant           ON public.yolo_diseases;
CREATE POLICY p_yolo_diseases_tenant           ON public.yolo_diseases
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
-- NOTE: yolo_diseases has NO tenant_id column in the migration — this policy
-- will fail. The Alembic migration loops over all NEW_TABLES including this
-- one, so either: (a) add tenant_id to yolo_diseases, or (b) exclude it from
-- the RLS loop. Flagging because this WILL error at apply time.

DROP POLICY IF EXISTS p_yolo_plant_diagnoses_tenant    ON public.yolo_plant_diagnoses;
CREATE POLICY p_yolo_plant_diagnoses_tenant    ON public.yolo_plant_diagnoses
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_fields_tenant             ON public.yolo_fields;
CREATE POLICY p_yolo_fields_tenant             ON public.yolo_fields
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_growth_assessments_tenant ON public.yolo_growth_assessments;
CREATE POLICY p_yolo_growth_assessments_tenant ON public.yolo_growth_assessments
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
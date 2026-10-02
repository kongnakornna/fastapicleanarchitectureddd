"""add yolo extension tables
Revision ID: yolo_002
Revises: yolo_001
Create Date: 2026-10-02
"""
from __future__ import annotations
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "yolo_002"
down_revision: Union[str, None] = "yolo_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
SCHEMA = "public"
NEW_TABLES = ("yolo_settings","yolo_categories","yolo_counting_sessions",
              "yolo_counting_results","yolo_diseases","yolo_plant_diagnoses",
              "yolo_fields","yolo_growth_assessments")


def upgrade() -> None:
    op.create_table("yolo_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("default_model", sa.String(50), nullable=False, server_default="yolov8n.pt"),
        sa.Column("device", sa.String(20), nullable=False, server_default="auto"),
        sa.Column("conf_threshold", sa.Numeric(4, 3), nullable=False, server_default="0.25"),
        sa.Column("iou_threshold", sa.Numeric(4, 3), nullable=False, server_default="0.45"),
        sa.Column("max_batch_size", sa.Integer, nullable=False, server_default="32"),
        sa.Column("timeout_seconds", sa.Integer, nullable=False, server_default="30"),
        sa.Column("cache_ttl", sa.Integer, nullable=False, server_default="300"),
        sa.Column("artifact_bucket", sa.String(200), nullable=False, server_default="yolo-artifacts"),
        sa.Column("enable_tensorrt", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("enable_half", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("max_trainings", sa.Integer, nullable=False, server_default="1"),
        sa.Column("retention_days", sa.Integer, nullable=False, server_default="90"),
        sa.Column("extra_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", name="uq_yolo_settings_tenant"),
        schema=SCHEMA)

    op.create_table("yolo_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name_th", sa.String(200), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("icon", sa.String(20), nullable=True),
        sa.Column("color", sa.String(7), nullable=False, server_default="#3B82F6"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("extra_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_yolo_cat_slug"),
        schema=SCHEMA)

    op.create_table("yolo_counting_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("config_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("total_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="RUNNING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA)

    op.create_table("yolo_counting_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("frame_index", sa.Integer, nullable=True),
        sa.Column("total_count", sa.Integer, nullable=False),
        sa.Column("per_class_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("regions_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("confidence_avg", sa.Numeric(4, 3), nullable=True),
        sa.Column("processing_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA)

    op.create_table("yolo_diseases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("name_th", sa.String(200), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=False),
        sa.Column("pathogen_type", sa.String(20), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("treatment_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("prevention_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_yolo_diseases_code"),
        schema=SCHEMA)

    op.create_table("yolo_plant_diagnoses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("image_hash", sa.String(64), nullable=False),
        sa.Column("plant_species", sa.String(200), nullable=True),
        sa.Column("detections_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("overall_severity", sa.String(20), nullable=False),
        sa.Column("health_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("recommendations", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("treatment_plan", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA)

    op.create_table("yolo_fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("crop_type", sa.String(100), nullable=False),
        sa.Column("area_sqm", sa.Numeric(10, 2), nullable=True),
        sa.Column("location_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("location_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("planting_date", sa.Date, nullable=True),
        sa.Column("expected_harvest", sa.Date, nullable=True),
        sa.Column("px_per_cm", sa.Numeric(6, 2), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("extra_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA)

    op.create_table("yolo_growth_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("plant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("image_hash", sa.String(64), nullable=False),
        sa.Column("stage", sa.String(20), nullable=False),
        sa.Column("stage_confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("metrics_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("health_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("growth_rate_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("alerts_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("recommendations", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA)

    for tbl in NEW_TABLES:
        op.execute(f"ALTER TABLE {SCHEMA}.{tbl} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            DROP POLICY IF EXISTS p_{tbl}_tenant ON {SCHEMA}.{tbl};
            CREATE POLICY p_{tbl}_tenant ON {SCHEMA}.{tbl}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        """)


def downgrade() -> None:
    for tbl in reversed(NEW_TABLES):
        op.execute(f'DROP TABLE IF EXISTS "{SCHEMA}"."{tbl}" CASCADE;')

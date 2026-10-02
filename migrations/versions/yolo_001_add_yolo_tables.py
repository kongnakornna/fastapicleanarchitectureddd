"""add yolo base tables
Revision ID: yolo_001
Revises: 36c2e35e1165
Create Date: 2026-10-02
"""
from __future__ import annotations
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "yolo_001"
down_revision: Union[str, None] = "36c2e35e1165"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
SCHEMA = "public"
TABLES = ("yolo_datasets","yolo_classes","yolo_images","yolo_annotations",
          "yolo_trainings","yolo_models","yolo_inferences")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.create_table("yolo_datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("format", sa.String(20), nullable=False, server_default="yolo"),
        sa.Column("root_uri", sa.Text, nullable=False, server_default=""),
        sa.Column("image_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("class_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("splits_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id","name","version", name="uq_yolo_ds_name_ver"),
        schema=SCHEMA)
    op.create_index("ix_yolo_ds_tenant", "yolo_datasets", ["tenant_id"], schema=SCHEMA)

    op.create_table("yolo_classes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("class_index", sa.Integer, nullable=False),
        sa.Column("color", sa.String(7), nullable=False, server_default="#FF0000"),
        sa.Column("count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("dataset_id","class_index", name="uq_yolo_class_idx"),
        schema=SCHEMA)

    op.create_table("yolo_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uri", sa.Text, nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("width", sa.Integer, nullable=False, server_default="0"),
        sa.Column("height", sa.Integer, nullable=False, server_default="0"),
        sa.Column("size_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("split", sa.String(10), nullable=False, server_default="train"),
        sa.Column("annotation_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("dataset_id","content_hash", name="uq_yolo_img_hash"),
        schema=SCHEMA)

    op.create_table("yolo_annotations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("x_center", sa.Float, nullable=False),
        sa.Column("y_center", sa.Float, nullable=False),
        sa.Column("width", sa.Float, nullable=False),
        sa.Column("height", sa.Float, nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False, server_default="1.0"),
        sa.Column("is_hard", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("source", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA)

    op.create_table("yolo_trainings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_type", sa.String(20), nullable=False),
        sa.Column("epochs", sa.Integer, nullable=False, server_default="100"),
        sa.Column("batch_size", sa.Integer, nullable=False, server_default="16"),
        sa.Column("imgsz", sa.Integer, nullable=False, server_default="640"),
        sa.Column("lr0", sa.Numeric(12, 8), nullable=False, server_default="0.01"),
        sa.Column("device", sa.String(20), nullable=False, server_default="auto"),
        sa.Column("patience", sa.Integer, nullable=False, server_default="50"),
        sa.Column("optimizer", sa.String(20), nullable=False, server_default="auto"),
        sa.Column("aug_config_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("best_model_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("progress", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=False, server_default=""),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA)

    op.create_table("yolo_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("training_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("weights_uri", sa.Text, nullable=False, server_default=""),
        sa.Column("weights_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("export_uri", sa.Text, nullable=False, server_default=""),
        sa.Column("format", sa.String(20), nullable=False, server_default="pt"),
        sa.Column("mAP50", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("mAP50_95", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("precision_", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("recall_", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("metrics_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_deployed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id","name","version", name="uq_yolo_model_name_ver"),
        schema=SCHEMA)

    op.create_table("yolo_inferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("image_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("detections_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("detection_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("source", sa.String(20), nullable=False, server_default="api"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA)

    for tbl in TABLES:
        op.execute(f"ALTER TABLE {SCHEMA}.{tbl} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            DROP POLICY IF EXISTS p_{tbl}_tenant ON {SCHEMA}.{tbl};
            CREATE POLICY p_{tbl}_tenant ON {SCHEMA}.{tbl}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        """)


def downgrade() -> None:
    for tbl in reversed(TABLES):
        op.execute(f'DROP TABLE IF EXISTS "{SCHEMA}"."{tbl}" CASCADE;')

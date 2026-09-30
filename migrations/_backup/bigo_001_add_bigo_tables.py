"""add bigo tables (10 tables)

Revision ID: bigo_001
Revises: None
Create Date: 2026-09-24
"""
from __future__ import annotations
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "bigo_001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "public"
TABLES = [
    "bigo_metrics", "bigo_profiles",
    "bigo_memory_snapshots", "bigo_memory_leaks",
    "bigo_kafka_topics", "bigo_kafka_queues", "bigo_kafka_consumers",
    "bigo_pipeline_reports", "bigo_cache_stats", "bigo_ws_sessions",
]


def upgrade() -> None:
    """TH: สร้างตาราง bigo (10 tables)"""
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # bigo_metrics
    op.create_table(
        "bigo_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("value", sa.Numeric(20, 8), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(20), nullable=False, server_default=""),
        sa.Column("labels_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "kind IN ('latency','throughput','memory_rss','memory_heap',"
            "'cpu_percent','gc_pause','queue_depth','kafka_lag','error_rate')",
            name="ck_bigo_metric_kind",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_metric_tenant", "bigo_metrics", ["tenant_id", "captured_at"], schema=SCHEMA)
    op.create_index("ix_bigo_metric_kind", "bigo_metrics", ["tenant_id", "kind", "captured_at"], schema=SCHEMA)
    op.create_index("ix_bigo_metric_name", "bigo_metrics", ["name"], schema=SCHEMA)

    # bigo_profiles
    op.create_table(
        "bigo_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("function_name", sa.String(200), nullable=False),
        sa.Column("module", sa.String(200), nullable=False, server_default=""),
        sa.Column("complexity", sa.String(20), nullable=False, server_default="UNKNOWN"),
        sa.Column("sample_size", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_ms", sa.Numeric(20, 8), nullable=False, server_default="0"),
        sa.Column("p95_ms", sa.Numeric(20, 8), nullable=False, server_default="0"),
        sa.Column("memory_peak_mb", sa.Numeric(20, 8), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text, nullable=False, server_default=""),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "complexity IN ('O(1)','O(log n)','O(n)','O(n log n)',"
            "'O(n^2)','O(n^3)','O(2^n)','O(n!)','UNKNOWN')",
            name="ck_bigo_profile_complexity",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_profile_tenant", "bigo_profiles", ["tenant_id", "captured_at"], schema=SCHEMA)
    op.create_index("ix_bigo_profile_function", "bigo_profiles", ["function_name", "captured_at"], schema=SCHEMA)

    # bigo_memory_snapshots
    op.create_table(
        "bigo_memory_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_id", sa.Integer, nullable=False, server_default="0"),
        sa.Column("rss_mb", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("vms_mb", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("percent", sa.Numeric(8, 4), nullable=False, server_default="0"),
        sa.Column("pressure", sa.String(20), nullable=False, server_default="NORMAL"),
        sa.Column("top_allocations_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "pressure IN ('NORMAL','ELEVATED','HIGH','CRITICAL','OOM')",
            name="ck_bigo_mem_pressure",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_mem_tenant", "bigo_memory_snapshots", ["tenant_id", "captured_at"], schema=SCHEMA)
    op.create_index("ix_bigo_mem_pressure", "bigo_memory_snapshots", ["tenant_id", "pressure", "captured_at"], schema=SCHEMA)

    # bigo_memory_leaks
    op.create_table(
        "bigo_memory_leaks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location", sa.String(500), nullable=False),
        sa.Column("leak_type", sa.String(50), nullable=False, server_default="UNKNOWN"),
        sa.Column("growth_mb_per_hour", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("current_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("samples", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="OPEN"),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "leak_type IN ('REFERENCE_CYCLE','UNBOUNDED_CACHE',"
            "'LISTENER_LEAK','THREAD_LOCAL','NATIVE_BUFFER','UNKNOWN')",
            name="ck_bigo_leak_type",
        ),
        sa.CheckConstraint(
            "status IN ('OPEN','INVESTIGATING','RESOLVED','IGNORED')",
            name="ck_bigo_leak_status",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_leak_tenant", "bigo_memory_leaks", ["tenant_id", "status", "detected_at"], schema=SCHEMA)

    # bigo_kafka_topics
    op.create_table(
        "bigo_kafka_topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("partitions", sa.Integer, nullable=False, server_default="3"),
        sa.Column("replication_factor", sa.Integer, nullable=False, server_default="1"),
        sa.Column("retention_ms", sa.Integer, nullable=False, server_default="604800000"),
        sa.Column("max_message_bytes", sa.Integer, nullable=False, server_default="1048576"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_bigo_topic_name"),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_topic_tenant", "bigo_kafka_topics", ["tenant_id"], schema=SCHEMA)

    # bigo_kafka_queues
    op.create_table(
        "bigo_kafka_queues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic", sa.String(300), nullable=False),
        sa.Column("partition", sa.Integer, nullable=False, server_default="0"),
        sa.Column("current_offset", sa.Integer, nullable=False, server_default="0"),
        sa.Column("log_end_offset", sa.Integer, nullable=False, server_default="0"),
        sa.Column("lag", sa.Integer, nullable=False, server_default="0"),
        sa.Column("health", sa.String(20), nullable=False, server_default="HEALTHY"),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "health IN ('HEALTHY','WARNING','DEGRADED','CRITICAL','OFFLINE')",
            name="ck_bigo_queue_health",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_queue_topic", "bigo_kafka_queues", ["topic", "partition", "captured_at"], schema=SCHEMA)
    op.create_index("ix_bigo_queue_tenant", "bigo_kafka_queues", ["tenant_id", "captured_at"], schema=SCHEMA)

    # bigo_kafka_consumers
    op.create_table(
        "bigo_kafka_consumers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("group_id", sa.String(300), nullable=False),
        sa.Column("topic", sa.String(300), nullable=False),
        sa.Column("member_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_lag", sa.Integer, nullable=False, server_default="0"),
        sa.Column("health", sa.String(20), nullable=False, server_default="HEALTHY"),
        sa.Column("last_commit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "group_id", "topic", name="uq_bigo_consumer"),
        sa.CheckConstraint(
            "health IN ('HEALTHY','WARNING','DEGRADED','CRITICAL','OFFLINE')",
            name="ck_bigo_consumer_health",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_consumer_tenant", "bigo_kafka_consumers", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_bigo_consumer_group", "bigo_kafka_consumers", ["group_id", "topic"], schema=SCHEMA)

    # bigo_pipeline_reports
    op.create_table(
        "bigo_pipeline_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=False),
        sa.Column("n", sa.Integer, nullable=False, server_default="0"),
        sa.Column("complexity", sa.String(20), nullable=False, server_default="O(n)"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PASS"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("rss_mb", sa.Numeric(20, 4), nullable=False, server_default="0"),
        sa.Column("pressure", sa.String(20), nullable=False, server_default="NORMAL"),
        sa.Column("duration_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("kafka_partition", sa.Integer, nullable=False, server_default="1"),
        sa.Column("kafka_sent", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('PASS','WARNING','CRITICAL')", name="ck_bigo_pipeline_status"),
        sa.CheckConstraint("priority IN ('high','normal','low','dlq')", name="ck_bigo_pipeline_priority"),
        sa.CheckConstraint(
            "pressure IN ('NORMAL','ELEVATED','HIGH','CRITICAL','OOM')",
            name="ck_bigo_pipeline_pressure",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_pipeline_tenant", "bigo_pipeline_reports", ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_bigo_pipeline_trace", "bigo_pipeline_reports", ["trace_id"], schema=SCHEMA)
    op.create_index("ix_bigo_pipeline_status", "bigo_pipeline_reports", ["tenant_id", "status", "created_at"], schema=SCHEMA)

    # bigo_cache_stats
    op.create_table(
        "bigo_cache_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("namespace", sa.String(100), nullable=False, server_default="bigo"),
        sa.Column("hits", sa.Integer, nullable=False, server_default="0"),
        sa.Column("misses", sa.Integer, nullable=False, server_default="0"),
        sa.Column("sets", sa.Integer, nullable=False, server_default="0"),
        sa.Column("deletes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("errors", sa.Integer, nullable=False, server_default="0"),
        sa.Column("hit_ratio", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_cache_stats_tenant", "bigo_cache_stats", ["tenant_id", "captured_at"], schema=SCHEMA)

    # bigo_ws_sessions
    op.create_table(
        "bigo_ws_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conn_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("rooms_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_s", sa.Integer, nullable=False, server_default="0"),
        sa.Column("messages_sent", sa.Integer, nullable=False, server_default="0"),
        sa.Column("messages_recv", sa.Integer, nullable=False, server_default="0"),
        sa.Column("close_reason", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "conn_id", name="uq_bigo_ws_conn"),
        schema=SCHEMA,
    )
    op.create_index("ix_bigo_ws_tenant", "bigo_ws_sessions", ["tenant_id", "connected_at"], schema=SCHEMA)
    op.create_index("ix_bigo_ws_user", "bigo_ws_sessions", ["user_id"], schema=SCHEMA)

    # Trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_bigo()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in TABLES:
        op.execute(f"""
            DROP TRIGGER IF EXISTS trg_{tbl}_updated ON public.{tbl};
            CREATE TRIGGER trg_{tbl}_updated
                BEFORE UPDATE ON public.{tbl}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_bigo();
        """)

    for tbl in TABLES:
        op.execute(f"ALTER TABLE public.{tbl} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            DROP POLICY IF EXISTS p_{tbl}_tenant ON public.{tbl};
            CREATE POLICY p_{tbl}_tenant ON public.{tbl}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        """)


def downgrade() -> None:
    """TH: ลบตาราง bigo"""
    for tbl in reversed(TABLES):
        op.execute(f"DROP POLICY IF EXISTS p_{tbl}_tenant ON public.{tbl};")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{tbl}_updated ON public.{tbl};")
        op.execute(f'DROP TABLE IF EXISTS "public"."{tbl}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_bigo();")

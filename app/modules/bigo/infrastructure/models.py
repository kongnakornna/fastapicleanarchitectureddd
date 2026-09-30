"""bigo SQLAlchemy 2.0 models — schema=public, prefix=bigo_"""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Index, Integer,
    Numeric, String, Text, UniqueConstraint, func, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "public"


class Base(DeclarativeBase):
    """TH: declarative base | EN: declarative base"""


class MetricModel(Base):
    __tablename__ = "bigo_metrics"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('latency','throughput','memory_rss','memory_heap',"
            "'cpu_percent','gc_pause','queue_depth','kafka_lag','error_rate')",
            name="ck_bigo_metric_kind",
        ),
        Index("ix_bigo_metric_tenant", "tenant_id", "captured_at"),
        Index("ix_bigo_metric_kind", "tenant_id", "kind", "captured_at"),
        Index("ix_bigo_metric_name", "name"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, server_default="0")
    unit: Mapped[str] = mapped_column(String(20), nullable=False, server_default="")
    labels_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ProfileModel(Base):
    __tablename__ = "bigo_profiles"
    __table_args__ = (
        CheckConstraint(
            "complexity IN ('O(1)','O(log n)','O(n)','O(n log n)',"
            "'O(n^2)','O(n^3)','O(2^n)','O(n!)','UNKNOWN')",
            name="ck_bigo_profile_complexity",
        ),
        Index("ix_bigo_profile_tenant", "tenant_id", "captured_at"),
        Index("ix_bigo_profile_function", "function_name", "captured_at"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    function_name: Mapped[str] = mapped_column(String(200), nullable=False)
    module: Mapped[str] = mapped_column(String(200), nullable=False, server_default="")
    complexity: Mapped[str] = mapped_column(String(20), nullable=False, server_default="UNKNOWN")
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    avg_ms: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, server_default="0")
    p95_ms: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, server_default="0")
    memory_peak_mb: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, server_default="0")
    notes: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class MemorySnapshotModel(Base):
    __tablename__ = "bigo_memory_snapshots"
    __table_args__ = (
        CheckConstraint("pressure IN ('NORMAL','ELEVATED','HIGH','CRITICAL','OOM')", name="ck_bigo_mem_pressure"),
        Index("ix_bigo_mem_tenant", "tenant_id", "captured_at"),
        Index("ix_bigo_mem_pressure", "tenant_id", "pressure", "captured_at"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    rss_mb: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, server_default="0")
    vms_mb: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, server_default="0")
    percent: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, server_default="0")
    pressure: Mapped[str] = mapped_column(String(20), nullable=False, server_default="NORMAL")
    top_allocations_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class MemoryLeakModel(Base):
    __tablename__ = "bigo_memory_leaks"
    __table_args__ = (
        CheckConstraint(
            "leak_type IN ('REFERENCE_CYCLE','UNBOUNDED_CACHE',"
            "'LISTENER_LEAK','THREAD_LOCAL','NATIVE_BUFFER','UNKNOWN')",
            name="ck_bigo_leak_type",
        ),
        CheckConstraint("status IN ('OPEN','INVESTIGATING','RESOLVED','IGNORED')", name="ck_bigo_leak_status"),
        Index("ix_bigo_leak_tenant", "tenant_id", "status", "detected_at"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    leak_type: Mapped[str] = mapped_column(String(50), nullable=False, server_default="UNKNOWN")
    growth_mb_per_hour: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, server_default="0")
    current_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    samples: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="OPEN")
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class KafkaTopicModel(Base):
    __tablename__ = "bigo_kafka_topics"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_bigo_topic_name"),
        Index("ix_bigo_topic_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    partitions: Mapped[int] = mapped_column(Integer, nullable=False, server_default="3")
    replication_factor: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    retention_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="604800000")
    max_message_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1048576")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class KafkaQueueModel(Base):
    __tablename__ = "bigo_kafka_queues"
    __table_args__ = (
        CheckConstraint("health IN ('HEALTHY','WARNING','DEGRADED','CRITICAL','OFFLINE')", name="ck_bigo_queue_health"),
        Index("ix_bigo_queue_topic", "topic", "partition", "captured_at"),
        Index("ix_bigo_queue_tenant", "tenant_id", "captured_at"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    topic: Mapped[str] = mapped_column(String(300), nullable=False)
    partition: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    current_offset: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    log_end_offset: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    lag: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    health: Mapped[str] = mapped_column(String(20), nullable=False, server_default="HEALTHY")
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class KafkaConsumerModel(Base):
    __tablename__ = "bigo_kafka_consumers"
    __table_args__ = (
        CheckConstraint("health IN ('HEALTHY','WARNING','DEGRADED','CRITICAL','OFFLINE')", name="ck_bigo_consumer_health"),
        UniqueConstraint("tenant_id", "group_id", "topic", name="uq_bigo_consumer"),
        Index("ix_bigo_consumer_tenant", "tenant_id"),
        Index("ix_bigo_consumer_group", "group_id", "topic"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    group_id: Mapped[str] = mapped_column(String(300), nullable=False)
    topic: Mapped[str] = mapped_column(String(300), nullable=False)
    member_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_lag: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    health: Mapped[str] = mapped_column(String(20), nullable=False, server_default="HEALTHY")
    last_commit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class PipelineReportModel(Base):
    __tablename__ = "bigo_pipeline_reports"
    __table_args__ = (
        CheckConstraint("status IN ('PASS','WARNING','CRITICAL')", name="ck_bigo_pipeline_status"),
        CheckConstraint("priority IN ('high','normal','low','dlq')", name="ck_bigo_pipeline_priority"),
        CheckConstraint("pressure IN ('NORMAL','ELEVATED','HIGH','CRITICAL','OOM')", name="ck_bigo_pipeline_pressure"),
        Index("ix_bigo_pipeline_tenant", "tenant_id", "created_at"),
        Index("ix_bigo_pipeline_trace", "trace_id"),
        Index("ix_bigo_pipeline_status", "tenant_id", "status", "created_at"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    n: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    complexity: Mapped[str] = mapped_column(String(20), nullable=False, server_default="O(n)")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PASS")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, server_default="normal")
    rss_mb: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, server_default="0")
    pressure: Mapped[str] = mapped_column(String(20), nullable=False, server_default="NORMAL")
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    kafka_partition: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    kafka_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class CacheStatModel(Base):
    __tablename__ = "bigo_cache_stats"
    __table_args__ = (
        Index("ix_bigo_cache_stats_tenant", "tenant_id", "captured_at"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    namespace: Mapped[str] = mapped_column(String(100), nullable=False, server_default="bigo")
    hits: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    misses: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    sets: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    deletes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    errors: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    hit_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class WSSessionModel(Base):
    __tablename__ = "bigo_ws_sessions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "conn_id", name="uq_bigo_ws_conn"),
        Index("ix_bigo_ws_tenant", "tenant_id", "connected_at"),
        Index("ix_bigo_ws_user", "user_id"),
        {"schema": SCHEMA},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    conn_id: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rooms_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    disconnected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_s: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    messages_sent: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    messages_recv: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    close_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


__all__ = [
    "Base", "MetricModel", "ProfileModel",
    "MemorySnapshotModel", "MemoryLeakModel",
    "KafkaTopicModel", "KafkaQueueModel", "KafkaConsumerModel",
    "PipelineReportModel", "CacheStatModel", "WSSessionModel",
]

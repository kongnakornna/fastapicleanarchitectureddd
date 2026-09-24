"""vector_db SQLAlchemy models — schema=public, prefix=vdb_"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Float, Index, Integer,
    String, Text, UniqueConstraint, func, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "public"


class Base(DeclarativeBase):
    """TH: base | EN: base"""


class VDBCollectionModel(Base):
    __tablename__ = "vdb_collections"
    __table_args__ = (
        CheckConstraint(
            "metric IN ('cosine','l2','ip')",
            name="ck_vdb_collection_metric",
        ),
        CheckConstraint(
            "backend IN ('pgvector','qdrant','weaviate',"
            "'pinecone','chroma','milvus')",
            name="ck_vdb_collection_backend",
        ),
        UniqueConstraint("tenant_id", "name", name="uq_vdb_collection_name"),
        Index("ix_vdb_collection_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    metric: Mapped[str] = mapped_column(String(20), nullable=False, server_default="cosine")
    backend: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pgvector")
    config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class VDBVectorModel(Base):
    __tablename__ = "vdb_vectors"
    __table_args__ = (
        Index("ix_vdb_vec_tenant_coll", "tenant_id", "collection_id"),
        Index("ix_vdb_vec_source", "collection_id", "source_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_id: Mapped[str] = mapped_column(String(200), nullable=False)
    vector_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    norm: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class VDBIndexModel(Base):
    __tablename__ = "vdb_indexes"
    __table_args__ = (
        CheckConstraint(
            "index_type IN ('hnsw','ivfflat','flat','scann','diskann')",
            name="ck_vdb_index_type",
        ),
        CheckConstraint(
            "build_status IN ('PENDING','BUILDING','READY','FAILED')",
            name="ck_vdb_index_status",
        ),
        Index("ix_vdb_index_collection", "collection_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    index_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="hnsw")
    params_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    build_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class VDBNamespaceModel(Base):
    __tablename__ = "vdb_namespaces"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "collection_id", "namespace",
            name="uq_vdb_namespace",
        ),
        Index("ix_vdb_ns_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    namespace: Mapped[str] = mapped_column(String(100), nullable=False)
    prefix: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    quota: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class VDBStatsModel(Base):
    __tablename__ = "vdb_stats"
    __table_args__ = (
        UniqueConstraint("collection_id", name="uq_vdb_stats_collection"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    vector_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    avg_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "Base", "VDBCollectionModel", "VDBVectorModel", "VDBIndexModel",
    "VDBNamespaceModel", "VDBStatsModel",
]

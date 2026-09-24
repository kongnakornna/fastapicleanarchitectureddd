"""hybrid_search SQLAlchemy models — schema=public, prefix=hs_"""
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


class HSConfigModel(Base):
    __tablename__ = "hs_configs"
    __table_args__ = (
        CheckConstraint(
            "fusion_type IN ('rrf','weighted_sum','comb_sum','comb_mnz','borda','dbsf')",
            name="ck_hs_config_fusion",
        ),
        CheckConstraint(
            "reranker_type IN ('none','cross_encoder','cohere','bge','colbert')",
            name="ck_hs_config_reranker",
        ),
        UniqueConstraint("tenant_id", "name", name="uq_hs_config_name"),
        Index("ix_hs_cfg_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    fusion_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="rrf")
    rrf_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="60")
    bm25_weight: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.5")
    vector_weight: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.5")
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
    reranker_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="none")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class HSQueryModel(Base):
    __tablename__ = "hs_queries"
    __table_args__ = (
        Index("ix_hs_q_tenant_time", "tenant_id", "created_at"),
        Index("ix_hs_q_config", "config_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    config_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class HSResultModel(Base):
    __tablename__ = "hs_results"
    __table_args__ = (
        Index("ix_hs_res_query_rank", "query_id", "rank"),
        Index("ix_hs_res_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    source_kind: Mapped[str] = mapped_column(String(20), nullable=False, server_default="hybrid")
    source_id: Mapped[str] = mapped_column(String(200), nullable=False, server_default="")
    snippet: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class HSRankingModel(Base):
    __tablename__ = "hs_rankings"
    __table_args__ = (
        Index("ix_hs_rank_query_stage", "query_id", "stage"),
        Index("ix_hs_rank_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    stage: Mapped[str] = mapped_column(String(30), nullable=False, server_default="retrieve")
    source_kind: Mapped[str] = mapped_column(String(20), nullable=False, server_default="hybrid")
    source_id: Mapped[str] = mapped_column(String(200), nullable=False, server_default="")
    raw_score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    normalized_score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    rank: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class HSRerankLogModel(Base):
    __tablename__ = "hs_rerank_logs"
    __table_args__ = (
        Index("ix_hs_rr_query", "query_id"),
        Index("ix_hs_rr_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    reranker_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="none")
    input_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    output_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "Base", "HSConfigModel", "HSQueryModel", "HSResultModel",
    "HSRankingModel", "HSRerankLogModel",
]

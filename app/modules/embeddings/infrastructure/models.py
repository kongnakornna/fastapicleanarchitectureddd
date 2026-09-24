"""embeddings SQLAlchemy models — schema=public, prefix=emb_"""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Index, Integer, Numeric,
    String, Text, UniqueConstraint, func, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "public"


class Base(DeclarativeBase):
    """TH: base | EN: base"""


class EmbProviderModel(Base):
    __tablename__ = "emb_providers"
    __table_args__ = (
        CheckConstraint(
            "provider_type IN ('openai','cohere','voyage','huggingface','bge','local')",
            name="ck_emb_provider_type",
        ),
        UniqueConstraint("tenant_id", "name", name="uq_emb_provider_name"),
        Index("ix_emb_provider_tenant", "tenant_id"),
        Index("ix_emb_provider_type", "provider_type", "is_active"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    base_url: Mapped[str] = mapped_column(String(500), nullable=False, server_default="")
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="60")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default="100")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class EmbModelModel(Base):
    __tablename__ = "emb_models"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_emb_model_name"),
        Index("ix_emb_model_tenant", "tenant_id"),
        Index("ix_emb_model_provider", "provider_id", "is_active"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False, server_default="")
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="8191")
    cost_per_1k_tokens: Mapped[Decimal] = mapped_column(
        Numeric(12, 8), nullable=False, server_default="0",
    )
    normalize: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class EmbVectorModel(Base):
    __tablename__ = "emb_vectors"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "model_id", "source_hash",
            name="uq_emb_vector_hash",
        ),
        Index("ix_emb_vec_tenant_model", "tenant_id", "model_id"),
        Index("ix_emb_vec_hash", "source_hash"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    vector_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class EmbBatchModel(Base):
    __tablename__ = "emb_batches"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING','RUNNING','DONE','FAILED','CANCELLED')",
            name="ck_emb_batch_status",
        ),
        Index("ix_emb_batch_tenant_status", "tenant_id", "status"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    completed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    failed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class EmbCacheModel(Base):
    __tablename__ = "emb_cache"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "model_id", "hash", name="uq_emb_cache_hash",
        ),
        Index("ix_emb_cache_tenant_model", "tenant_id", "model_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    vector_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    hits: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "Base", "EmbProviderModel", "EmbModelModel", "EmbVectorModel",
    "EmbBatchModel", "EmbCacheModel",
]

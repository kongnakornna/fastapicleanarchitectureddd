"""llamaindex SQLAlchemy models — schema=public, prefix=li_"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Index, Integer, String, Text,
    UniqueConstraint, func, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "public"


class Base(DeclarativeBase):
    """TH: base | EN: base"""


class LIIndexModel(Base):
    __tablename__ = "li_indexes"
    __table_args__ = (
        CheckConstraint(
            "index_type IN ('vector_store','summary','tree','keyword','kg','document_summary')",
            name="ck_li_index_type",
        ),
        UniqueConstraint("tenant_id", "name", name="uq_li_index_name"),
        Index("ix_li_index_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    index_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="vector_store")
    embed_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="text-embedding-3-small")
    storage_kind: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pgvector")
    config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class LINodeModel(Base):
    __tablename__ = "li_nodes"
    __table_args__ = (
        Index("ix_li_node_index_ord", "index_id", "ordinal"),
        Index("ix_li_node_doc", "document_id"),
        Index("ix_li_node_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    index_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True,
    )
    node_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="text")
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    relationships_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class LIQueryEngineModel(Base):
    __tablename__ = "li_query_engines"
    __table_args__ = (
        CheckConstraint(
            "response_mode IN ('compact','refine','tree_summarize','simple_summarize','no_text','generation','accumulate')",
            name="ck_li_qe_response_mode",
        ),
        UniqueConstraint("tenant_id", "index_id", "name", name="uq_li_qe_name"),
        Index("ix_li_qe_index", "index_id"),
        Index("ix_li_qe_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    index_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    retriever_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="vector")
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
    response_mode: Mapped[str] = mapped_column(String(30), nullable=False, server_default="compact")
    similarity_top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class LIDocumentModel(Base):
    __tablename__ = "li_documents"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING','PROCESSING','READY','FAILED','DELETED')",
            name="ck_li_doc_status",
        ),
        Index("ix_li_doc_index_hash", "index_id", "hash"),
        Index("ix_li_doc_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    index_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_uri: Mapped[str] = mapped_column(String(1000), nullable=False, server_default="")
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    title: Mapped[str] = mapped_column(String(500), nullable=False, server_default="")
    hash: Mapped[str] = mapped_column(String(128), nullable=False, server_default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class LIRunModel(Base):
    __tablename__ = "li_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('QUEUED','RUNNING','DONE','FAILED','CANCELLED')",
            name="ck_li_run_status",
        ),
        Index("ix_li_run_tenant_time", "tenant_id", "created_at"),
        Index("ix_li_run_user_time", "user_id", "created_at"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    index_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    query_engine_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    answer: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    source_nodes_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="QUEUED")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "Base", "LIIndexModel", "LINodeModel", "LIQueryEngineModel",
    "LIDocumentModel", "LIRunModel",
]

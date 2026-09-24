"""rag SQLAlchemy models — schema=public, prefix=rag_"""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Float, Index, Integer,
    Numeric, String, Text, UniqueConstraint, func, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "public"


class Base(DeclarativeBase):
    """TH: base | EN: base"""


class RAGDocumentModel(Base):
    __tablename__ = "rag_documents"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING','PROCESSING','READY','FAILED','DELETED')",
            name="ck_rag_doc_status",
        ),
        Index("ix_rag_doc_tenant_status", "tenant_id", "status"),
        Index("ix_rag_doc_tenant_hash", "tenant_id", "hash"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    source_uri: Mapped[str] = mapped_column(String(1000), nullable=False, server_default="")
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    title: Mapped[str] = mapped_column(String(500), nullable=False, server_default="")
    content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    hash: Mapped[str] = mapped_column(String(128), nullable=False, server_default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class RAGChunkModel(Base):
    __tablename__ = "rag_chunks"
    __table_args__ = (
        Index("ix_rag_chunk_doc_ordinal", "document_id", "ordinal"),
        Index("ix_rag_chunk_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    embedding_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class RAGPipelineModel(Base):
    __tablename__ = "rag_pipelines"
    __table_args__ = (
        CheckConstraint(
            "chunker_type IN ('fixed','recursive','semantic','markdown','code')",
            name="ck_rag_pipe_chunker",
        ),
        CheckConstraint(
            "retriever_type IN ('vector','bm25','hybrid','mmr')",
            name="ck_rag_pipe_retriever",
        ),
        CheckConstraint(
            "reranker_type IN ('none','cross_encoder','cohere','bge')",
            name="ck_rag_pipe_reranker",
        ),
        UniqueConstraint("tenant_id", "name", name="uq_rag_pipe_name"),
        Index("ix_rag_pipe_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    chunker_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="recursive")
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="512")
    chunk_overlap: Mapped[int] = mapped_column(Integer, nullable=False, server_default="50")
    retriever_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="vector")
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
    reranker_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="none")
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="text-embedding-3-small")
    generation_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="gpt-4o-mini")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class RAGRunModel(Base):
    __tablename__ = "rag_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('QUEUED','RETRIEVING','RERANKING','GENERATING','DONE','FAILED')",
            name="ck_rag_run_status",
        ),
        Index("ix_rag_run_tenant_time", "tenant_id", "created_at"),
        Index("ix_rag_run_user_time", "user_id", "created_at"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    pipeline_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    query: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    answer: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False, server_default="0")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="QUEUED")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class RAGCitationModel(Base):
    __tablename__ = "rag_citations"
    __table_args__ = (
        Index("ix_rag_cit_run_rank", "run_id", "rank"),
        Index("ix_rag_cit_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    rank: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    snippet: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class RAGRetrievalLogModel(Base):
    __tablename__ = "rag_retrieval_logs"
    __table_args__ = (
        Index("ix_rag_rlog_run_stage", "run_id", "stage"),
        Index("ix_rag_rlog_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), nullable=False, server_default="retrieve")
    top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    candidates_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "Base", "RAGDocumentModel", "RAGChunkModel", "RAGPipelineModel",
    "RAGRunModel", "RAGCitationModel", "RAGRetrievalLogModel",
]

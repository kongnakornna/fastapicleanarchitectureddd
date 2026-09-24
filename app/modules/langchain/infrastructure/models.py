"""langchain SQLAlchemy models — schema=public, prefix=lc_"""
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


class LCChainModel(Base):
    __tablename__ = "lc_chains"
    __table_args__ = (
        CheckConstraint(
            "chain_type IN ('lcel','sequential','router','map_reduce','refine','stuff')",
            name="ck_lc_chain_type",
        ),
        UniqueConstraint("tenant_id", "name", name="uq_lc_chain_name"),
        Index("ix_lc_chain_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    chain_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="lcel")
    config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    version: Mapped[str] = mapped_column(String(20), nullable=False, server_default="1.0.0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class LCAgentModel(Base):
    __tablename__ = "lc_agents"
    __table_args__ = (
        CheckConstraint(
            "agent_type IN ('react','openai_tools','plan_execute','self_ask','reflexion')",
            name="ck_lc_agent_type",
        ),
        UniqueConstraint("tenant_id", "name", name="uq_lc_agent_name"),
        Index("ix_lc_agent_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="react")
    tools_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="gpt-4o-mini")
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
    config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class LCMemoryModel(Base):
    __tablename__ = "lc_memories"
    __table_args__ = (
        CheckConstraint(
            "memory_type IN ('buffer','window','summary','summary_buffer','vector','kg')",
            name="ck_lc_memory_type",
        ),
        Index("ix_lc_memory_conv", "conversation_id"),
        Index("ix_lc_memory_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    memory_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="buffer")
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class LCRunModel(Base):
    __tablename__ = "lc_runs"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('chain','agent')",
            name="ck_lc_run_kind",
        ),
        CheckConstraint(
            "status IN ('QUEUED','RUNNING','DONE','FAILED','CANCELLED')",
            name="ck_lc_run_status",
        ),
        Index("ix_lc_run_tenant_time", "tenant_id", "created_at"),
        Index("ix_lc_run_user_time", "user_id", "created_at"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False, server_default="chain")
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    input_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    output_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="QUEUED")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 8), nullable=False, server_default="0",
    )
    error_message: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class LCTraceModel(Base):
    __tablename__ = "lc_traces"
    __table_args__ = (
        Index("ix_lc_trace_run_step", "run_id", "step"),
        Index("ix_lc_trace_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    step: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    kind: Mapped[str] = mapped_column(String(30), nullable=False, server_default="other")
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "Base", "LCChainModel", "LCAgentModel", "LCMemoryModel",
    "LCRunModel", "LCTraceModel",
]

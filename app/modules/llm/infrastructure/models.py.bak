"""llm SQLAlchemy 2.0 models — schema=public, prefix=llm_"""
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


class ProviderModel(Base):
    __tablename__ = "llm_providers"
    __table_args__ = (
        CheckConstraint(
            "provider_type IN ('openai','anthropic','local','azure')",
            name="ck_llm_provider_type",
        ),
        UniqueConstraint(
            "tenant_id", "name", name="uq_llm_provider_name",
        ),
        Index("ix_llm_provider_tenant", "tenant_id"),
        Index("ix_llm_provider_type", "provider_type", "is_active"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="",
    )
    base_url: Mapped[str] = mapped_column(
        String(500), nullable=False, server_default="",
    )
    timeout_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="60",
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="100",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"),
    )
    config_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="{}",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )


class ModelModel(Base):
    __tablename__ = "llm_models"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "name", name="uq_llm_model_name",
        ),
        Index("ix_llm_model_tenant", "tenant_id"),
        Index("ix_llm_model_provider", "provider_id", "is_active"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(
        String(200), nullable=False, server_default="",
    )
    context_window: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="4096",
    )
    max_output_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="4096",
    )
    cost_per_1k_input: Mapped[Decimal] = mapped_column(
        Numeric(12, 8), nullable=False, server_default="0",
    )
    cost_per_1k_output: Mapped[Decimal] = mapped_column(
        Numeric(12, 8), nullable=False, server_default="0",
    )
    supports_streaming: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"),
    )
    supports_tools: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )


class ConversationModel(Base):
    __tablename__ = "llm_conversations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE','ARCHIVED','DELETED')",
            name="ck_llm_conv_status",
        ),
        Index("ix_llm_conv_tenant", "tenant_id"),
        Index("ix_llm_conv_user", "user_id", "created_at"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False, server_default="",
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    system_prompt: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="",
    )
    metadata_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="{}",
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="ACTIVE",
    )
    message_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )


class MessageModel(Base):
    __tablename__ = "llm_messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('system','user','assistant','tool')",
            name="ck_llm_msg_role",
        ),
        Index("ix_llm_msg_conv", "conversation_id", "created_at"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="",
    )
    tool_calls_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="[]",
    )
    tool_call_id: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="",
    )
    tokens_input: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    tokens_output: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    finish_reason: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="",
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )


class UsageLogModel(Base):
    __tablename__ = "llm_usage_logs"
    __table_args__ = (
        Index("ix_llm_usage_tenant", "tenant_id", "created_at"),
        Index("ix_llm_usage_user", "user_id", "created_at"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
    )
    tokens_input: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    tokens_output: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 8), nullable=False, server_default="0",
    )
    source: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="chat",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )

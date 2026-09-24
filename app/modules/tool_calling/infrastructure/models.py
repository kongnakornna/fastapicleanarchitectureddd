"""tool_calling SQLAlchemy 2.0 models — schema=public, prefix=tool_"""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Index, Integer, Numeric,
    String, Text, UniqueConstraint, func, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SCHEMA = "public"


class Base(DeclarativeBase):
    """TH: declarative base | EN: declarative base"""


class ToolDefinitionModel(Base):
    __tablename__ = "tool_definitions"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('http','python','sql','shell','mcp','openapi')",
            name="ck_tool_kind",
        ),
        CheckConstraint(
            "risk_level IN ('low','medium','high','critical')",
            name="ck_tool_risk",
        ),
        CheckConstraint(
            "visibility IN ('private','tenant','public')",
            name="ck_tool_visibility",
        ),
        UniqueConstraint(
            "tenant_id", "name", name="uq_tool_name",
        ),
        Index("ix_tool_def_tenant", "tenant_id"),
        Index("ix_tool_def_kind", "kind", "is_active"),
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
    description: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="",
    )
    parameters_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="{}",
    )
    returns_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="{}",
    )
    version: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="1.0.0",
    )
    kind: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="http",
    )
    risk_level: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="low",
    )
    visibility: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="tenant",
    )
    timeout_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="30",
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


class ToolRegistrationModel(Base):
    __tablename__ = "tool_registrations"
    __table_args__ = (
        UniqueConstraint("tool_id", name="uq_tool_reg_tool"),
        Index("ix_tool_reg_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    tool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true"),
    )
    rate_limit_per_min: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="60",
    )
    scopes_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="[]",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )


class ToolInvocationModel(Base):
    __tablename__ = "tool_invocations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('SUCCESS','ERROR','TIMEOUT','DENIED','RATE_LIMITED')",
            name="ck_tool_inv_status",
        ),
        Index("ix_tool_inv_tenant", "tenant_id", "created_at"),
        Index("ix_tool_inv_tool", "tool_id", "created_at"),
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
    tool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    tool_name: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="",
    )
    args_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="{}",
    )
    result_json: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="{}",
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="SUCCESS",
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    error_code: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="",
    )
    error_message: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="",
    )
    tokens_used: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
    )
    cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 8), nullable=False, server_default="0",
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.now(),
    )


class ToolPermissionModel(Base):
    __tablename__ = "tool_permissions"
    __table_args__ = (
        UniqueConstraint(
            "tool_id", "role", name="uq_tool_perm_role",
        ),
        Index("ix_tool_perm_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    tool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    allowed: Mapped[bool] = mapped_column(
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

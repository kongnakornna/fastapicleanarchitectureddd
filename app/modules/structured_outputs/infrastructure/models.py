"""structured_outputs SQLAlchemy models — schema=public, prefix=so_"""
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


class SOSchemaModel(Base):
    __tablename__ = "so_schemas"
    __table_args__ = (
        CheckConstraint(
            "strategy IN ('json_mode','function_call','grammar','regex','prompt_only')",
            name="ck_so_schema_strategy",
        ),
        UniqueConstraint("tenant_id", "name", name="uq_so_schema_name"),
        Index("ix_so_schema_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    json_schema: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    pydantic_model: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    strict: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    strategy: Mapped[str] = mapped_column(String(20), nullable=False, server_default="json_mode")
    version: Mapped[str] = mapped_column(String(20), nullable=False, server_default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class SORequestModel(Base):
    __tablename__ = "so_requests"
    __table_args__ = (
        Index("ix_so_req_tenant_time", "tenant_id", "created_at"),
        Index("ix_so_req_schema", "schema_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    schema_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    prompt: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    temperature: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    max_repairs: Mapped[int] = mapped_column(Integer, nullable=False, server_default="2")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class SOOutputModel(Base):
    __tablename__ = "so_outputs"
    __table_args__ = (
        Index("ix_so_out_request", "request_id"),
        Index("ix_so_out_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    parsed_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(12, 8), nullable=False, server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class SOValidationModel(Base):
    __tablename__ = "so_validations"
    __table_args__ = (
        Index("ix_so_val_output", "output_id"),
        Index("ix_so_val_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    output_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    errors_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


class SORepairModel(Base):
    __tablename__ = "so_repairs"
    __table_args__ = (
        Index("ix_so_rep_output", "output_id"),
        Index("ix_so_rep_tenant", "tenant_id"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    output_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    feedback: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    raw_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
        onupdate=func.now(),
    )


__all__ = [
    "Base", "SOSchemaModel", "SORequestModel", "SOOutputModel",
    "SOValidationModel", "SORepairModel",
]

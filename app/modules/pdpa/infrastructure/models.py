"""pdpa SQLAlchemy 2.0 models"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CHAR, Boolean, CheckConstraint, DateTime, Index, Integer,
    String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """TH: declarative base | EN: declarative base"""


# ═══════════════════════════════════════════════════════════════
# consent_logs
# ═══════════════════════════════════════════════════════════════
class ConsentLogModel(Base):
    """TH: ตาราง consent_logs (append-only) | EN: consent_logs table"""
    __tablename__ = "pdpa_consent_logs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('GRANTED','REVOKED','EXPIRED')",
            name="ck_consent_status",
        ),
        CheckConstraint(
            "purpose_code IN ('DATA_COLLECTION','DATA_DELETION',"
            "'USER_ACCOUNT','USAGE_LOGS','TRANSACTION_HISTORY')",
            name="ck_consent_purpose",
        ),
        Index("ix_consent_user", "user_id", "status"),
        Index("ix_consent_tenant", "tenant_id"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    purpose_code: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="GRANTED")
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )


# ═══════════════════════════════════════════════════════════════
# dsar_requests
# ═══════════════════════════════════════════════════════════════
class DSARRequestModel(Base):
    """TH: ตาราง dsar_requests | EN: dsar_requests table"""
    __tablename__ = "pdpa_dsar_requests"
    __table_args__ = (
        CheckConstraint(
            "type IN ('ACCESS','ERASURE','WITHDRAW_CONSENT')",
            name="ck_dsar_type",
        ),
        CheckConstraint(
            "status IN ('SUBMITTED','VERIFIED','PROCESSING','COMPLETED','REJECTED')",
            name="ck_dsar_status",
        ),
        Index("ix_dsar_user", "user_id", "status"),
        Index("ix_dsar_tenant", "tenant_id"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SUBMITTED")
    reason: Mapped[str | None] = mapped_column(String(500))
    rejection_reason: Mapped[str | None] = mapped_column(String(500))
    response_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )


# ═══════════════════════════════════════════════════════════════
# privacy_policies
# ═══════════════════════════════════════════════════════════════
class PrivacyPolicyModel(Base):
    """TH: ตาราง privacy_policies | EN: privacy_policies table"""
    __tablename__ = "pdpa_privacy_policies"
    __table_args__ = (
        UniqueConstraint("tenant_id", "version", name="uq_pp_version"),
        CheckConstraint(
            "status IN ('DRAFT','PUBLISHED','SUPERSEDED','ARCHIVED')",
            name="ck_pp_status",
        ),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content_th: Mapped[str] = mapped_column(Text, nullable=False)
    content_en: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )


# ═══════════════════════════════════════════════════════════════
# cookie_consents
# ═══════════════════════════════════════════════════════════════
class CookieConsentModel(Base):
    """TH: ตาราง cookie_consents | EN: cookie_consents table"""
    __tablename__ = "pdpa_cookie_consents"
    __table_args__ = (
        Index("ix_cc_session", "session_id"),
        Index("ix_cc_user", "user_id"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    session_id: Mapped[str] = mapped_column(String(128), nullable=False)
    necessary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    analytics: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    marketing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    functional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(String(500))
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )


# ═══════════════════════════════════════════════════════════════
# idempotency_keys
# ═══════════════════════════════════════════════════════════════
class IdempotencyKeyModel(Base):
    """
    TH: ตาราง idempotency_keys | EN: idempotency_keys table

    Matches public.pdpa_idempotency_keys exactly:
      * request_hash  → CHAR(64)  (SQL column is CHAR(64), NOT VARCHAR)
      * status        → server_default 'IN_PROGRESS'
      * UNIQUE (tenant_id, idempotency_key)
    """
    __tablename__ = "pdpa_idempotency_keys"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "idempotency_key",
            name="uq_idempotency_key",
        ),
        CheckConstraint(
            "status IN ('IN_PROGRESS','COMPLETED','FAILED')",
            name="ck_idempotency_status",
        ),
        Index("ix_idempotency_keys_expires", "expires_at"),
        Index("ix_idempotency_keys_user", "user_id"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    request_method: Mapped[str] = mapped_column(String(10), nullable=False)
    request_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # CHAR(64) — fixed width, space padded. Always .strip() on read.
    request_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False,
        default="IN_PROGRESS", server_default="IN_PROGRESS",
    )

    response_status: Mapped[int | None] = mapped_column(Integer)
    response_body: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<IdempotencyKeyModel tenant={self.tenant_id} "
            f"key={self.idempotency_key!r} status={self.status}>"
        )

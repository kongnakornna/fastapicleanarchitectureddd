"""
Audit ORM Models — model ORM audit
Audit ORM Models — SQLAlchemy models for audit_logs (append-only)
"""

from __future__ import annotations

from app.modules.shared.infrastructure.models import BaseModel
from sqlalchemy import Column, DateTime, Index, String
from sqlalchemy.dialects.postgresql import JSONB


class AuditLogModel(BaseModel):
    """
    Audit log ORM model — model ORM บันทึก audit

    Table: tenant_{tid}.audit_logs
    Append-only — REVOKE UPDATE/DELETE applied in migration.
    """

    __tablename__ = "audit_logs"

    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(36), nullable=False, index=True)
    actor_id = Column(String(36), nullable=False, index=True)

    before_state = Column(JSONB, nullable=False, default=dict)
    after_state = Column(JSONB, nullable=False, default=dict)
    changes = Column(JSONB, nullable=False, default=list)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    correlation_id = Column(String(36), nullable=True, index=True)
    severity = Column(String(20), nullable=False, default="INFO", index=True)

    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_actor_time", "actor_id", "occurred_at"),
        Index("ix_audit_correlation", "correlation_id"),
        Index("ix_audit_severity_time", "severity", "occurred_at"),
        # NOTE: Append-only enforced in migration:
        #   REVOKE UPDATE, DELETE ON tenant_{tid}.audit_logs FROM app_role;
        {"schema": None},  # schema set dynamically per tenant
    )

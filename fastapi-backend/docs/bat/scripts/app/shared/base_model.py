# app/shared/base_model.py - SQLAlchemy declarative base + tenant mixin
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TenantMixin:
    """Mixin for multi-tenant tables (adds tenant_id, version, timestamps)."""

    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

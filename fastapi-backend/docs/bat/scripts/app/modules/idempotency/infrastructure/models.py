"""Idempotency infrastructure models — SQLAlchemy models"""

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


class IdempotencyRecordModel(BaseModel):
    """IdempotencyRecordModel — โมเดลบันทึก idempotency"""

    __tablename__ = "idempotency_records"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    scope = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    request_hash = Column(String(64), nullable=False)
    response_body = Column(JSONB, default=dict)
    response_status = Column(Integer)
    locked_until = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), index=True)

    __table_args__ = (
        UniqueConstraint(
            "key",
            "scope",
            "tenant_id",
            name="uq_idem_key_scope_tenant",
        ),
    )

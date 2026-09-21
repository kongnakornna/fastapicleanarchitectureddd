# events/infrastructure/models.py
# SQLAlchemy models — โมเดล SQLAlchemy

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.shared.base_model import Base


class EventStoreModel(Base):
    """Event store table — ตารางที่เก็บเหตุการณ์ (append-only)"""

    __tablename__ = "event_store"

    event_id = Column(String(36), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    correlation_id = Column(String(36), index=True, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    payload = Column(JSONB, nullable=False)
    status = Column(String(20), default="PENDING", index=True)
    retry_count = Column(Integer, default=0)
    consumed_at = Column(DateTime(timezone=True), nullable=True)

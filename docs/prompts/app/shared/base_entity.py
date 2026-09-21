# app/shared/base_entity.py - Base dataclass entity
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class BaseEntity:
    """Base entity - all domain entities inherit from this."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    version: int = 1
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
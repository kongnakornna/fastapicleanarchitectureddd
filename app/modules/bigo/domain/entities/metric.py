"""Metric entity"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class Metric:
    """TH: Metric | EN: Metric entity"""
    tenant_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    kind: str = ""
    name: str = ""
    value: float = 0.0
    unit: str = ""
    labels_json: str = ""
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

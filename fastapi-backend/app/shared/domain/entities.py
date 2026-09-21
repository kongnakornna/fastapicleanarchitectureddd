# app/modules/shared/domain/entities.py
"""
TH: Base entity ของ shared layer
EN: shared-layer base entity
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.modules.shared.domain.exceptions import DomainError, DomainErrors


@dataclass(kw_only=True, slots=True)
class BaseEntity:
    """TH: base entity | EN: base entity"""

    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=False)
    updated_at: datetime | None = field(default=None, repr=False, compare=False)
    is_active: bool = field(default=True, repr=False, compare=False)

    def mark_created(self, now: datetime) -> None:
        self.created_at = now
        self.updated_at = now

    def mark_updated(self, now: datetime) -> None:
        self.updated_at = now

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False


__all__ = ["BaseEntity", "DomainError", "DomainErrors"]
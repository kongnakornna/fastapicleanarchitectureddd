# authentication/domain/events.py - domain event names

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AuthenticationCreated:
    """Event emitted when a new authentication session is created."""

    authentication_id: UUID
    user_id: UUID
    device: str | None
    ip_address: str | None
    occurred_at: datetime


@dataclass(frozen=True)
class AuthenticationRevoked:
    """Event emitted when an authentication session is revoked."""

    authentication_id: UUID
    user_id: UUID
    device: str | None
    occurred_at: datetime


@dataclass(frozen=True)
class TokensRefreshed:
    """Event emitted when tokens are refreshed."""

    authentication_id: UUID
    user_id: UUID
    device: str | None
    occurred_at: datetime


@dataclass(frozen=True)
class SuspiciousActivityDetected:
    """Event emitted when suspicious activity is detected."""

    authentication_id: UUID | None
    user_id: UUID | None
    reason: str
    ip_address: str | None
    occurred_at: datetime

"""pdpa domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class ConsentGranted:
    consent_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    purpose_code: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ConsentRevoked:
    consent_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    purpose_code: str
    reason: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class DSARSubmitted:
    dsar_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    type: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class DSARCompleted:
    dsar_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    response_payload: dict
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class DataErasureRequested:
    dsar_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class PrivacyPolicyPublished:
    policy_id: uuid.UUID
    tenant_id: uuid.UUID
    version: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

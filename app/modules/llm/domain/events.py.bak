"""llm domain events — เหตุการณ์โดเมน llm"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class ConversationCreated:
    conversation_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    model_id: uuid.UUID
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class MessageSent:
    message_id: uuid.UUID
    conversation_id: uuid.UUID
    tenant_id: uuid.UUID
    role: str
    tokens_input: int
    tokens_output: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class CompletionGenerated:
    message_id: uuid.UUID
    tenant_id: uuid.UUID
    model_name: str
    finish_reason: str
    latency_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class ProviderRegistered:
    provider_id: uuid.UUID
    tenant_id: uuid.UUID
    provider_type: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class TokenLimitExceeded:
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    current_usage: int
    limit: int
    occurred_at: datetime = field(default_factory=_now)

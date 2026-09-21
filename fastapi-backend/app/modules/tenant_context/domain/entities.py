"""tenant_context entities — เอนทิตีบริบท.

หมายเหตุ: Module นี้เป็น pure VO — entities.py มีไว้เพื่อ re-export
RequestContext ที่อาจถูกใช้เป็น entity ในบางบริบท
Note: This module is pure VO — entities.py is kept to re-export
RequestContext which may act as an entity in some contexts.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class RequestContext:
    """RequestContext entity — บริบทคำขอ (HTTP-level metadata)."""

    method: str = "GET"
    path: str = "/"
    ip_address: str = "0.0.0.0"
    user_agent: str = ""
    started_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self):
        if not self.method:
            from .exceptions import DomainError

            raise DomainError("Method is required")
        if not self.path:
            from .exceptions import DomainError

            raise DomainError("Path is required")

"""tenancy entities — เอนทิตี Tenant."""

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from .exceptions import DomainError


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass
class BaseEntity:
    """BaseEntity — เอนทิตีฐาน."""

    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    deleted_at: datetime | None = None
    version: int = 1


@dataclass
class Tenant(BaseEntity):
    """Tenant entity — เอนทิตีผู้เช่า."""

    slug: str = ""
    name: str = ""
    plan: str = "FREE"
    status: str = "ACTIVE"
    schema_name: str = ""
    owner_email: str = ""
    trial_ends_at: datetime | None = None
    max_users: int = 5
    max_storage_gb: int = 1

    def __post_init__(self):
        self._validate()
        if not self.schema_name:
            self.schema_name = f"tenant_{self.id}"

    def _validate(self) -> None:
        if not self.slug or not re.match(r"^[a-z][a-z0-9-]{2,30}$", self.slug):
            raise DomainError(f"Invalid slug: {self.slug}")
        if not self.name:
            raise DomainError("Tenant name is required")
        if not self.owner_email:
            raise DomainError("Owner email is required")

    def activate(self) -> None:
        """Activate — เปิดใช้งาน."""
        if self.status == "ACTIVE":
            raise DomainError("Tenant already active")
        self.status = "ACTIVE"
        self.updated_at = _utcnow()

    def suspend(self, reason: str) -> None:
        """Suspend — ระงับ."""
        if self.status == "SUSPENDED":
            raise DomainError("Tenant already suspended")
        if not reason:
            raise DomainError("Suspension reason is required")
        self.status = "SUSPENDED"
        self.updated_at = _utcnow()

    def upgrade_plan(self, new_plan: str) -> None:
        """Upgrade plan — อัปเกรดแผน."""
        valid = ("FREE", "STARTER", "PROFESSIONAL", "ENTERPRISE")
        if new_plan not in valid:
            raise DomainError(f"Invalid plan: {new_plan}")
        self.plan = new_plan
        self.updated_at = _utcnow()

    def is_trial_expired(self) -> bool:
        """Check trial expired — ตรวจสอบ trial หมดอายุ."""
        if self.trial_ends_at is None:
            return False
        return _utcnow() > self.trial_ends_at

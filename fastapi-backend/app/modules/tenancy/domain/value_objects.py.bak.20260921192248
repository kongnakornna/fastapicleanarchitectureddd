"""tenancy value objects — วัตถุค่า."""

import re
from dataclasses import dataclass
from decimal import Decimal

from .exceptions import DomainError


@dataclass(frozen=True)
class TenantPlan:
    """TenantPlan VO — วัตถุแผน."""

    code: str
    name: str
    max_users: int
    max_storage_gb: int
    price_monthly: Decimal

    def __post_init__(self):
        if self.max_users <= 0:
            raise DomainError("Max users must be positive")
        if self.max_storage_gb <= 0:
            raise DomainError("Max storage must be positive")


@dataclass(frozen=True)
class TenantSlug:
    """TenantSlug VO — วัตถุ slug."""

    value: str

    PATTERN = r"^[a-z][a-z0-9-]{2,30}$"

    def __post_init__(self):
        if not re.match(self.PATTERN, self.value):
            raise DomainError(f"Invalid slug: {self.value}")

    def __str__(self) -> str:
        return self.value

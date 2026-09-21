"""123Abc entities — เอนทิตี 123abc"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from .enums import 123AbcStatus
from .exceptions import (
    DomainError,
    InvalidAmountError,
    InvalidStatusTransitionError,
)
from .value_objects import Money

MAX_CODE_LEN = 50
MAX_NAME_LEN = 200


@dataclass
class 123Abc:
    """123Abc aggregate root — รากของ aggregate"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID = field(default_factory=uuid.uuid4)
    code: str = ""
    name: str = ""
    amount: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    status: 123AbcStatus = 123AbcStatus.ACTIVE
    version: int = 1
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        tenant_id: uuid.UUID,
        code: str,
        name: str,
        amount: Decimal | Money,
        status: 123AbcStatus | None = None,
        metadata: dict | None = None,
    ) -> "123Abc":
        """TH: สร้าง entity ใหม่ | EN: create new entity"""
        if not code or len(code) > MAX_CODE_LEN:
            raise DomainError(f"code must be 1-{MAX_CODE_LEN} chars")
        if not name or len(name) > MAX_NAME_LEN:
            raise DomainError(f"name must be 1-{MAX_NAME_LEN} chars")
        money = amount if isinstance(amount, Money) else Money(amount)
        if money.is_negative():
            raise InvalidAmountError(f"amount must be >= 0, got {money.amount}")
        return cls(
            tenant_id=tenant_id,
            code=code,
            name=name,
            amount=money,
            status=status or 123AbcStatus.ACTIVE,
            metadata=metadata or {},
        )

    def activate(self) -> None:
        """TH: เปิดใช้งาน | EN: activate"""
        if self.status is 123AbcStatus.ARCHIVED:
            raise InvalidStatusTransitionError("archived is terminal")
        self.status = 123AbcStatus.ACTIVE
        self._touch()

    def deactivate(self) -> None:
        """TH: ปิดใช้งาน | EN: deactivate"""
        if self.status is 123AbcStatus.ARCHIVED:
            raise InvalidStatusTransitionError("archived is terminal")
        self.status = 123AbcStatus.INACTIVE
        self._touch()

    def archive(self) -> None:
        """TH: เก็บถาวร (terminal) | EN: archive (terminal)"""
        self.status = 123AbcStatus.ARCHIVED
        self._touch()

    def soft_delete(self) -> None:
        """TH: ลบแบบ soft | EN: soft delete"""
        self.deleted_at = datetime.utcnow()
        self._touch()

    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def rename(self, new_name: str) -> None:
        if not new_name or len(new_name) > MAX_NAME_LEN:
            raise DomainError(f"name must be 1-{MAX_NAME_LEN} chars")
        self.name = new_name
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.utcnow()
        self.version += 1
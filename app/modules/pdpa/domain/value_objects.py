"""pdpa value objects"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from ipaddress import ip_address
from uuid import UUID

from .exceptions import PDPAError


@dataclass(frozen=True, slots=True)
class ConsentId:
    value: UUID


@dataclass(frozen=True, slots=True)
class PurposeCode:
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value) > 50:
            raise PDPAError("purpose_code must be 1-50 chars")


@dataclass(frozen=True, slots=True)
class DataSubjectId:
    value: UUID


@dataclass(frozen=True, slots=True)
class Evidence:
    ip_address: str
    user_agent: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        try:
            ip_address(self.ip_address)
        except ValueError as e:
            raise PDPAError(f"invalid ip: {self.ip_address}") from e
        if len(self.user_agent) > 500:
            raise PDPAError("user_agent too long")


@dataclass(frozen=True, slots=True)
class EncryptionKeyVersion:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise PDPAError("key_version must be >= 1")

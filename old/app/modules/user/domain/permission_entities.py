from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(kw_only=True, slots=True)
class Permission:
    name: str
    description: Optional[str] = None
    resource: str
    action: str

    id: UUID = field(default=None, repr=True, compare=True)
    is_active: bool = field(default=True, repr=False, compare=False)
    created_at: datetime = field(default=None, repr=False, compare=False)
    updated_at: datetime = field(default=None, repr=False, compare=False)


@dataclass(kw_only=True, slots=True)
class Role_:
    name: str
    description: Optional[str] = None

    id: UUID = field(default=None, repr=True, compare=True)
    is_active: bool = field(default=True, repr=False, compare=False)
    created_at: datetime = field(default=None, repr=False, compare=False)
    updated_at: datetime = field(default=None, repr=False, compare=False)


@dataclass(kw_only=True, slots=True)
class UserRole:
    user_id: UUID
    role_id: UUID

    id: UUID = field(default=None, repr=True, compare=True)
    created_at: datetime = field(default=None, repr=False, compare=False)


@dataclass(kw_only=True, slots=True)
class RolePermission:
    role_id: UUID
    permission_id: UUID

    id: UUID = field(default=None, repr=True, compare=True)
    created_at: datetime = field(default=None, repr=False, compare=False)

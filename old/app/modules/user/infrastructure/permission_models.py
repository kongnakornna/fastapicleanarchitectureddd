from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, ForeignKey, DateTime, func, UUID as SQUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.settings import settings
from app.modules.shared.infrastructure.models import BaseModel


class RoleModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_roles"

    name: Mapped[str] = mapped_column(
        String(100),
        name="name",
        comment="Name of the role",
        nullable=False,
        unique=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        name="description",
        comment="Description of the role",
        nullable=True,
    )


class PermissionModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_permissions"

    name: Mapped[str] = mapped_column(
        String(100),
        name="name",
        comment="Name of the permission",
        nullable=False,
        unique=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        name="description",
        comment="Description of the permission",
        nullable=True,
    )

    resource: Mapped[str] = mapped_column(
        String(100),
        name="resource",
        comment="Resource that the permission applies to (e.g. 'user', 'session')",
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        name="action",
        comment="Action allowed on the resource (e.g. 'create', 'read', 'update', 'delete')",
        nullable=False,
    )


class UserRoleModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_user_roles"

    user_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_users.id", ondelete="CASCADE"),
        name="user_id",
        comment="Identifier of the user",
        nullable=False,
    )

    role_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_roles.id", ondelete="CASCADE"),
        name="role_id",
        comment="Identifier of the role",
        nullable=False,
    )


class RolePermissionModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_role_permissions"

    role_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_roles.id", ondelete="CASCADE"),
        name="role_id",
        comment="Identifier of the role",
        nullable=False,
    )

    permission_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_permissions.id", ondelete="CASCADE"),
        name="permission_id",
        comment="Identifier of the permission",
        nullable=False,
    )

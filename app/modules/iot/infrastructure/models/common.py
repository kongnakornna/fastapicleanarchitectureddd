"""Common base models"""
from __future__ import annotations
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel as _SharedBaseModel


class BaseModel(_SharedBaseModel):
    """TH: base model (created_at / updated_at)"""
    __abstract__ = True


class StatusModel:
    """TH: mixin status"""
    status: Mapped[int] = mapped_column(Integer, name="status", default=1)

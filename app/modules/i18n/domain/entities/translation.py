from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Translation(BaseModel):
    __tablename__ = "m_translation"

    locale: Mapped[str] = mapped_column(
        String(10), name="locale", comment="Locale code (e.g. en, pt-BR)"
    )
    key: Mapped[str] = mapped_column(
        String(255), name="key", comment="Translation key"
    )
    value: Mapped[str] = mapped_column(
        Text, name="value", comment="Translated value"
    )

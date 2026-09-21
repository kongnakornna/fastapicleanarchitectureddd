from __future__ import annotations

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Document(BaseModel):
    __tablename__ = "m_document"

    filename: Mapped[str] = mapped_column(
        String(255), name="filename", comment="Stored filename"
    )
    original_name: Mapped[str] = mapped_column(
        String(255), name="original_name", comment="Original upload filename"
    )
    mime_type: Mapped[str] = mapped_column(
        String(100), name="mime_type", comment="MIME type"
    )
    size: Mapped[int] = mapped_column(
        BigInteger, name="size", comment="File size in bytes"
    )

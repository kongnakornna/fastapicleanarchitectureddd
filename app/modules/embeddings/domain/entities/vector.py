"""EmbVector entity — alias to ORM"""
from __future__ import annotations
from app.modules.embeddings.infrastructure.models import EmbVectorModel


class EmbVector(EmbVectorModel):
    """TH: EmbVector | EN: EmbVector entity (alias)"""

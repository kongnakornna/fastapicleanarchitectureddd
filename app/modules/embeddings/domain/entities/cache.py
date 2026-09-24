"""EmbCache entity — alias to ORM"""
from __future__ import annotations
from app.modules.embeddings.infrastructure.models import EmbCacheModel


class EmbCache(EmbCacheModel):
    """TH: EmbCache | EN: EmbCache entity (alias)"""

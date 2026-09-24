"""EmbProvider entity — alias to ORM"""
from __future__ import annotations
from app.modules.embeddings.infrastructure.models import EmbProviderModel


class EmbProvider(EmbProviderModel):
    """TH: EmbProvider | EN: EmbProvider entity (alias)"""

"""EmbBatch entity — alias to ORM"""
from __future__ import annotations
from app.modules.embeddings.infrastructure.models import EmbBatchModel


class EmbBatch(EmbBatchModel):
    """TH: EmbBatch | EN: EmbBatch entity (alias)"""

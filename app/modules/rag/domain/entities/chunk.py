"""Chunk entity — alias to ORM"""
from __future__ import annotations
from app.modules.rag.infrastructure.models import RAGChunkModel


class Chunk(RAGChunkModel):
    """TH: Chunk | EN: Chunk entity (alias)"""

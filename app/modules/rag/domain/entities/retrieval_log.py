"""RetrievalLog entity — alias to ORM"""
from __future__ import annotations
from app.modules.rag.infrastructure.models import RAGRetrievalLogModel


class RetrievalLog(RAGRetrievalLogModel):
    """TH: RetrievalLog | EN: RetrievalLog entity (alias)"""

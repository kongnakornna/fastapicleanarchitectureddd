"""Document entity — alias to ORM"""
from __future__ import annotations
from app.modules.rag.infrastructure.models import RAGDocumentModel


class Document(RAGDocumentModel):
    """TH: Document | EN: Document entity (alias)"""

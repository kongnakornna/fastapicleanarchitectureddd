"""hasher"""
from __future__ import annotations
import hashlib


def document_hash(content: str) -> str:
    """TH: hash เอกสาร | EN: document hash"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

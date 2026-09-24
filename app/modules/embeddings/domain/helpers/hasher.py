"""hasher"""
from __future__ import annotations
import hashlib


def content_hash(text: str, prefix: str = "") -> str:
    """TH: hash ข้อความ | EN: content hash"""
    return hashlib.sha256(
        (prefix + text).encode("utf-8")
    ).hexdigest()

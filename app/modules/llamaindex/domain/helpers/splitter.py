"""splitter — sentence-aware text splitter"""
from __future__ import annotations
import re
from typing import Optional


_SENT_END = re.compile(r"(?<=[.!?])\s+")


def split_text(
    text: str, *, chunk_size: int = 512, chunk_overlap: int = 50,
    separators: Optional[list[str]] = None,
) -> list[str]:
    """TH: แบ่งข้อความเป็น chunk | EN: split text into chunks"""
    if not text:
        return []
    if chunk_size <= 0:
        return [text]
    step = max(1, chunk_size - max(0, chunk_overlap))

    sentences = _SENT_END.split(text)
    if len(sentences) <= 1:
        return [
            text[i : i + chunk_size]
            for i in range(0, len(text), step)
            if text[i : i + chunk_size].strip()
        ]

    chunks: list[str] = []
    buf = ""
    for sent in sentences:
        candidate = (buf + " " + sent) if buf else sent
        if len(candidate) <= chunk_size:
            buf = candidate
        else:
            if buf:
                chunks.append(buf.strip())
            if len(sent) > chunk_size:
                for i in range(0, len(sent), step):
                    piece = sent[i : i + chunk_size]
                    if piece.strip():
                        chunks.append(piece.strip())
                buf = ""
            else:
                buf = sent
    if buf:
        chunks.append(buf.strip())
    return chunks


class SentenceSplitter:
    """TH: sentence splitter (stateless) | EN: sentence splitter"""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        return split_text(
            text, chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

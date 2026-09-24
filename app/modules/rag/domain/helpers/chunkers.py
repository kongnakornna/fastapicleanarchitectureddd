"""chunkers"""
from __future__ import annotations
from typing import Optional


def _overlap_slices(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0:
        return [text]
    step = max(1, size - max(0, overlap))
    return [text[i : i + size] for i in range(0, len(text), step)]


def chunk_fixed(
    text: str, *, chunk_size: int = 512, chunk_overlap: int = 50,
) -> list[str]:
    if not text:
        return []
    return [
        c for c in _overlap_slices(text, chunk_size, chunk_overlap)
        if c.strip()
    ]


def chunk_recursive(
    text: str, *, chunk_size: int = 512, chunk_overlap: int = 50,
    separators: Optional[list[str]] = None,
) -> list[str]:
    if not text:
        return []
    seps = separators or ["\n\n", "\n", ". ", " "]

    def split_rec(segment: str, seps_left: list[str]) -> list[str]:
        if len(segment) <= chunk_size or not seps_left:
            return _overlap_slices(segment, chunk_size, chunk_overlap)
        sep = seps_left[0]
        parts = segment.split(sep)
        out: list[str] = []
        buf = ""
        for p in parts:
            candidate = (buf + sep + p) if buf else p
            if len(candidate) <= chunk_size:
                buf = candidate
            else:
                if buf:
                    out.append(buf)
                if len(p) > chunk_size:
                    out.extend(split_rec(p, seps_left[1:]))
                    buf = ""
                else:
                    buf = p
        if buf:
            out.append(buf)
        return out

    chunks = split_rec(text, seps)
    return [c.strip() for c in chunks if c.strip()]


def chunk_markdown(
    text: str, *, chunk_size: int = 512, chunk_overlap: int = 50,
) -> list[str]:
    if not text:
        return []
    blocks: list[str] = []
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("#") and buf:
            blocks.append("\n".join(buf))
            buf = [line]
        else:
            buf.append(line)
    if buf:
        blocks.append("\n".join(buf))

    out: list[str] = []
    for block in blocks:
        if len(block) <= chunk_size:
            out.append(block)
        else:
            out.extend(_overlap_slices(
                block, chunk_size, chunk_overlap,
            ))
    return [c.strip() for c in out if c.strip()]

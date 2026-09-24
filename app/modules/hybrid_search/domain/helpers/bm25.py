"""bm25 — in-memory BM25 (fallback if DB ts_rank ไม่พร้อม)"""
from __future__ import annotations
import math
import re
from collections import Counter
from typing import Any

_TOKEN = re.compile(r"\w+")


def _tok(text: str) -> list[str]:
    return _TOKEN.findall((text or "").lower())


def bm25_score(
    query: str, documents: list[dict[str, Any]],
    *, k1: float = 1.5, b: float = 0.75,
) -> list[dict[str, Any]]:
    """TH: คำนวณ BM25 (in-memory) | EN: BM25 (in-memory)"""
    q_terms = _tok(query)
    if not q_terms or not documents:
        return []

    docs_tokens = [_tok(str(d.get("text", ""))) for d in documents]
    n = len(docs_tokens)
    avgdl = sum(len(t) for t in docs_tokens) / max(1, n)

    df: Counter = Counter()
    for toks in docs_tokens:
        for t in set(toks):
            df[t] += 1

    idf = {
        t: math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
        for t in df
    }

    out: list[dict[str, Any]] = []
    for i, toks in enumerate(docs_tokens):
        tf = Counter(toks)
        dl = len(toks)
        score = 0.0
        for q in q_terms:
            if q not in tf:
                continue
            f = tf[q]
            score += idf.get(q, 0.0) * (
                (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / (avgdl or 1)))
            )
        if score > 0:
            out.append(dict(documents[i], score=score, source_id=
                            str(documents[i].get("source_id") or i)))
    out.sort(key=lambda x: x["score"], reverse=True)
    for i, h in enumerate(out, start=1):
        h["rank"] = i
    return out

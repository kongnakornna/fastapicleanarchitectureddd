"""fusion — RRF, WeightedSum, CombSUM, CombMNZ"""
from __future__ import annotations
from typing import Any


def _ranked(lists: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for src_i, lst in enumerate(lists):
        for rank, hit in enumerate(lst, start=1):
            sid = str(hit.get("source_id") or hit.get("id") or "")
            if not sid:
                continue
            entry = merged.setdefault(sid, {
                "source_id": sid, "doc": hit, "ranks": [], "scores": [],
            })
            entry["ranks"].append(rank)
            entry["scores"].append(float(hit.get("score", 0.0)))
    return list(merged.values())


def rrf_fuse(
    ranked_lists: list[list[dict[str, Any]]], k: int = 60,
) -> list[dict[str, Any]]:
    """TH: Reciprocal Rank Fusion | EN: RRF"""
    if not ranked_lists:
        return []
    merged = _ranked(ranked_lists)
    out = []
    for entry in merged:
        score = sum(1.0 / (k + r) for r in entry["ranks"])
        doc = dict(entry["doc"])
        doc["score"] = score
        doc["source_id"] = entry["source_id"]
        out.append(doc)
    out.sort(key=lambda x: x["score"], reverse=True)
    for i, h in enumerate(out, start=1):
        h["rank"] = i
    return out


def weighted_sum_fuse(
    ranked_lists: list[list[dict[str, Any]]], weights: list[float],
) -> list[dict[str, Any]]:
    """TH: Weighted Sum Fusion | EN: WeightedSum"""
    if not ranked_lists:
        return []
    # normalize weights per source
    norm_lists: list[dict[str, float]] = []
    for lst in ranked_lists:
        if not lst:
            norm_lists.append({})
            continue
        scores = [float(h.get("score", 0.0)) for h in lst]
        lo, hi = min(scores), max(scores)
        span = (hi - lo) or 1.0
        norm_lists.append({
            str(h.get("source_id") or h.get("id") or ""):
                (float(h.get("score", 0.0)) - lo) / span
            for h in lst
        })

    merged: dict[str, dict[str, Any]] = {}
    for src_i, lst in enumerate(ranked_lists):
        w = weights[src_i] if src_i < len(weights) else 1.0
        for h in lst:
            sid = str(h.get("source_id") or h.get("id") or "")
            if not sid:
                continue
            entry = merged.setdefault(sid, {
                "source_id": sid, "doc": h, "score": 0.0,
            })
            entry["score"] += w * norm_lists[src_i].get(sid, 0.0)
    out = [dict(v["doc"], score=v["score"], source_id=v["source_id"])
           for v in merged.values()]
    out.sort(key=lambda x: x["score"], reverse=True)
    for i, h in enumerate(out, start=1):
        h["rank"] = i
    return out


def comb_sum_fuse(
    ranked_lists: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """TH: CombSUM | EN: CombSUM"""
    merged: dict[str, dict[str, Any]] = {}
    for lst in ranked_lists:
        for h in lst:
            sid = str(h.get("source_id") or h.get("id") or "")
            if not sid:
                continue
            entry = merged.setdefault(sid, {
                "source_id": sid, "doc": h, "score": 0.0,
            })
            entry["score"] += float(h.get("score", 0.0))
    out = [dict(v["doc"], score=v["score"], source_id=v["source_id"])
           for v in merged.values()]
    out.sort(key=lambda x: x["score"], reverse=True)
    for i, h in enumerate(out, start=1):
        h["rank"] = i
    return out


def comb_mnz_fuse(
    ranked_lists: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """TH: CombMNZ = CombSUM * |{i: score_i > 0}| | EN: CombMNZ"""
    merged: dict[str, dict[str, Any]] = {}
    for lst in ranked_lists:
        for h in lst:
            sid = str(h.get("source_id") or h.get("id") or "")
            if not sid:
                continue
            entry = merged.setdefault(sid, {
                "source_id": sid, "doc": h, "score": 0.0, "nz": 0,
            })
            s = float(h.get("score", 0.0))
            entry["score"] += s
            if s > 0:
                entry["nz"] += 1
    out = [
        dict(v["doc"], score=v["score"] * v["nz"], source_id=v["source_id"])
        for v in merged.values()
    ]
    out.sort(key=lambda x: x["score"], reverse=True)
    for i, h in enumerate(out, start=1):
        h["rank"] = i
    return out

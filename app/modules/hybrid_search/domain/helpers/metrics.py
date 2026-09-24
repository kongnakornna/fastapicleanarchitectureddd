"""metrics — MRR, NDCG, Recall@k, Precision@k"""
from __future__ import annotations
import math


def mrr(ranks: list[int]) -> float:
    """TH: Mean Reciprocal Rank | EN: MRR"""
    valid = [r for r in ranks if r > 0]
    if not valid:
        return 0.0
    return sum(1.0 / r for r in valid) / len(valid)


def ndcg(relevances: list[float], k: int = 10) -> float:
    """TH: NDCG@k | EN: NDCG@k"""
    if not relevances:
        return 0.0
    top = relevances[:k]
    dcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(top))
    ideal = sorted(relevances, reverse=True)[:k]
    idcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(ideal))
    if idcg == 0:
        return 0.0
    return dcg / idcg


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """TH: Recall@k | EN: Recall@k"""
    if not relevant:
        return 0.0
    top = retrieved[:k]
    return sum(1 for x in top if x in relevant) / len(relevant)


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """TH: Precision@k | EN: Precision@k"""
    if k <= 0:
        return 0.0
    top = retrieved[:k]
    if not top:
        return 0.0
    return sum(1 for x in top if x in relevant) / len(top)

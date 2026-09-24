"""metric helpers"""
from __future__ import annotations
import math
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", (text or "").lower())


def exact_match(pred: str, ref: str) -> float:
    return 1.0 if (pred or "").strip().lower() == (ref or "").strip().lower() else 0.0


def f1_score(pred: str, ref: str) -> float:
    p = _tokenize(pred)
    r = _tokenize(ref)
    if not p or not r:
        return 0.0
    common = Counter(p) & Counter(r)
    overlap = sum(common.values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(p)
    recall = overlap / len(r)
    return 2 * precision * recall / (precision + recall)


def _lcs(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def rouge_l(pred: str, ref: str) -> float:
    p = _tokenize(pred)
    r = _tokenize(ref)
    if not p or not r:
        return 0.0
    lcs = _lcs(p, r)
    if lcs == 0:
        return 0.0
    precision = lcs / len(p)
    recall = lcs / len(r)
    return 2 * precision * recall / (precision + recall)


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    top = retrieved[:k]
    if not top:
        return 0.0
    return sum(1 for x in top if x in relevant) / len(top)


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top = retrieved[:k]
    return sum(1 for x in top if x in relevant) / len(relevant)


def mrr(ranks: list[int]) -> float:
    if not ranks:
        return 0.0
    return sum(1.0 / r for r in ranks if r > 0) / len(ranks)


def ndcg(relevances: list[float], k: int = 10) -> float:
    if not relevances:
        return 0.0
    top = relevances[:k]
    dcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(top))
    ideal = sorted(relevances, reverse=True)[:k]
    idcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(ideal))
    if idcg == 0:
        return 0.0
    return dcg / idcg


def ragas_score(
    faithfulness: float, answer_relevance: float,
    context_precision: float, context_recall: float,
) -> float:
    vals = [faithfulness, answer_relevance, context_precision, context_recall]
    if any(v <= 0 for v in vals):
        return 0.0
    return 4 / sum(1.0 / v for v in vals)


def pass_threshold(score: float, threshold: float) -> bool:
    return score >= threshold

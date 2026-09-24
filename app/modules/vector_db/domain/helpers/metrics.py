"""similarity metrics"""
from __future__ import annotations
import math


def norm_l2(v: list[float]) -> float:
    """TH: L2 norm | EN: L2 norm"""
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """TH: cosine similarity | EN: cosine similarity"""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = norm_l2(a)
    nb = norm_l2(b)
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (na * nb)


def l2_distance(a: list[float], b: list[float]) -> float:
    """TH: L2 distance | EN: L2 distance"""
    if not a or not b or len(a) != len(b):
        return float("inf")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def inner_product(a: list[float], b: list[float]) -> float:
    """TH: inner product | EN: inner product"""
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))

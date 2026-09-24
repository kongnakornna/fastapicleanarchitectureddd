"""normalizer"""
from __future__ import annotations
import math


def normalize_vector(vector: list[float]) -> list[float]:
    """TH: L2 normalize | EN: L2 normalize"""
    if not vector:
        return vector
    norm = math.sqrt(sum(x * x for x in vector))
    if norm <= 0.0:
        return vector
    return [x / norm for x in vector]

"""Big-O complexity analyzer"""
from __future__ import annotations
import math
import time
from typing import Any, Callable

from app.modules.bigo.domain.enums import ComplexityClass
from app.modules.bigo.domain.value_objects import Complexity


_CANDIDATES: list[tuple[ComplexityClass, Callable[[int], float]]] = [
    (ComplexityClass.CONSTANT, lambda n: 1.0),
    (ComplexityClass.LOGARITHMIC, lambda n: math.log2(max(n, 2))),
    (ComplexityClass.LINEAR, lambda n: float(n)),
    (ComplexityClass.LINEARITHMIC, lambda n: n * math.log2(max(n, 2))),
    (ComplexityClass.QUADRATIC, lambda n: float(n) ** 2),
    (ComplexityClass.CUBIC, lambda n: float(n) ** 3),
    (ComplexityClass.EXPONENTIAL, lambda n: 2.0 ** min(n, 63)),
]


def measure_scaling(
    fn: Callable[[int], Any],
    sizes: list[int] | None = None,
    repeats: int = 3,
) -> list[tuple[int, float]]:
    sizes = sizes or [10, 50, 100, 500, 1000, 5000, 10000]
    results: list[tuple[int, float]] = []
    for n in sizes:
        best = float("inf")
        for _ in range(repeats):
            t0 = time.perf_counter()
            try:
                fn(n)
            except Exception:
                best = float("inf")
                break
            elapsed = time.perf_counter() - t0
            best = min(best, elapsed)
        if best != float("inf") and best > 0:
            results.append((n, best))
    return results


def fit_complexity(samples: list[tuple[int, float]]) -> Complexity:
    if len(samples) < 3:
        return Complexity(
            cls=ComplexityClass.UNKNOWN,
            sample_size=len(samples),
            notes="need >= 3 samples",
        )

    best_class = ComplexityClass.UNKNOWN
    best_error = float("inf")
    coeffs: list[tuple[str, float]] = []
    xs = [t for _, t in samples]

    for cls, fn in _CANDIDATES:
        ys = [fn(n) for n, _ in samples]
        if any(math.isinf(y) or math.isnan(y) for y in ys):
            continue
        denom = sum(y * y for y in ys)
        if denom == 0:
            continue
        k = sum(x * y for x, y in zip(xs, ys)) / denom
        residuals = [x - k * y for x, y in zip(xs, ys)]
        sse = sum(r * r for r in residuals)
        coeffs.append((cls.value, k))
        if sse < best_error:
            best_error = sse
            best_class = cls

    mean_t = sum(t for _, t in samples) / len(samples)
    ss_total = sum((t - mean_t) ** 2 for _, t in samples)
    r2 = max(0.0, 1.0 - best_error / ss_total) if ss_total > 0 else 0.0

    return Complexity(
        cls=best_class,
        sample_size=len(samples),
        r_squared=r2,
        coefficients=tuple(coeffs),
    )


def analyze_complexity(
    fn: Callable[[int], Any],
    sizes: list[int] | None = None,
    repeats: int = 3,
) -> Complexity:
    samples = measure_scaling(fn, sizes=sizes, repeats=repeats)
    return fit_complexity(samples)

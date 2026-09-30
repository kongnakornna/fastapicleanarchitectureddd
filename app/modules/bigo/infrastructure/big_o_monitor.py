"""BigOMonitor — policy checks + dynamic complexity analysis"""
from __future__ import annotations

from typing import Any, Callable, Iterable

from app.modules.bigo.domain.enums import ComplexityClass, Priority
from app.modules.bigo.domain.helpers import analyze_complexity
from app.modules.bigo.domain.pipeline_config import PipelineConfig
from app.modules.bigo.domain.value_objects import Complexity, ComplexityPolicy
from app.modules.bigo.infrastructure.metrics_registry import MetricsRegistry

_COMPLEXITY_ORDER: dict[str, int] = {
    "O(1)": 0, "O(log n)": 1, "O(n)": 2,
    "O(n log n)": 3, "O(n^2)": 4, "O(n^3)": 5,
    "O(2^n)": 6, "O(n!)": 7, "UNKNOWN": -1,
}


class BigOMonitor:
    """TH: ตรวจสอบ Big-O + policy enforcement"""

    def __init__(
        self,
        config: PipelineConfig,
        metrics: MetricsRegistry | None = None,
    ) -> None:
        self._config = config
        self._metrics = metrics or MetricsRegistry()
        self._policies: dict[str, ComplexityPolicy] = {
            "O(1)": ComplexityPolicy(ComplexityClass.CONSTANT, 10_000_000, partition=Priority.HIGH),
            "O(log n)": ComplexityPolicy(ComplexityClass.LOGARITHMIC, 10_000_000, partition=Priority.HIGH),
            "O(n)": ComplexityPolicy(ComplexityClass.LINEAR, config.max_n_linear,
                                     warn_ratio=config.warn_ratio, partition=Priority.NORMAL),
            "O(n log n)": ComplexityPolicy(ComplexityClass.LINEARITHMIC, config.max_n_linearithmic,
                                           warn_ratio=config.warn_ratio, partition=Priority.NORMAL),
            "O(n^2)": ComplexityPolicy(ComplexityClass.QUADRATIC, config.max_n_quadratic,
                                       warn_ratio=config.warn_ratio, partition=Priority.LOW),
            "O(n^3)": ComplexityPolicy(ComplexityClass.CUBIC, config.max_n_cubic,
                                       warn_ratio=config.warn_ratio, partition=Priority.LOW),
            "O(2^n)": ComplexityPolicy(ComplexityClass.EXPONENTIAL, 25,
                                       warn_ratio=config.warn_ratio, partition=Priority.LOW),
        }

    def check(self, n: int, algorithm_type: str = "O(n)") -> tuple[str, Priority]:
        policy = self._policies.get(algorithm_type)
        if policy is None:
            self._metrics.incr("bigo.check", status="UNKNOWN", complexity=algorithm_type)
            return "PASS", Priority.NORMAL
        status = policy.classify(n)
        self._metrics.incr("bigo.check", status=status, complexity=algorithm_type)
        self._metrics.observe("bigo.n", n, complexity=algorithm_type)
        return status, policy.partition

    def analyze(
        self,
        fn: Callable[[int], Any],
        sizes: Iterable[int] | None = None,
        repeats: int = 3,
    ) -> Complexity:
        sizes_list = list(sizes or self._config.sample_sizes)
        result = analyze_complexity(fn, sizes=sizes_list, repeats=repeats)
        self._metrics.observe("bigo.analyze.r_squared", result.r_squared)
        return result

    @staticmethod
    def compare(a: str, b: str) -> int:
        return _COMPLEXITY_ORDER.get(a, -1) - _COMPLEXITY_ORDER.get(b, -1)

    def policies(self) -> dict[str, ComplexityPolicy]:
        return dict(self._policies)

    def register_policy(self, policy: ComplexityPolicy) -> None:
        self._policies[policy.cls.value] = policy

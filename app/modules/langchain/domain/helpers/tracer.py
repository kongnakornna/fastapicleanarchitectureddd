"""tracer — step-by-step run recorder"""
from __future__ import annotations
import time
from typing import Any


class Tracer:
    """TH: บันทึก trace step | EN: trace recorder"""

    def __init__(self) -> None:
        self._steps: list[dict[str, Any]] = []
        self._t0 = time.monotonic()
        self._step_no = 0

    def record(self, kind: str, payload: dict[str, Any]) -> None:
        self._step_no += 1
        self._steps.append({
            "step": self._step_no,
            "kind": kind,
            "payload": payload,
            "latency_ms": int((time.monotonic() - self._t0) * 1000),
        })

    def steps(self) -> list[dict[str, Any]]:
        return list(self._steps)

    def total_ms(self) -> int:
        return int((time.monotonic() - self._t0) * 1000)

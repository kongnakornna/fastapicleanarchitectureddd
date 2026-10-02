"""Product counting domain"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from app.modules.yolo.domain.value_objects import Detection


@dataclass(frozen=True, slots=True)
class CountingConfig:
    mode: str = "shelf"
    line_position: float = 0.5
    line_orientation: str = "vertical"
    class_filter: tuple[int, ...] = ()
    min_confidence: float = 0.5
    merge_distance: float = 0.05
    track_persistence: int = 5
    deduplication: bool = True

    def __post_init__(self) -> None:
        if self.mode not in ("shelf", "conveyor", "checkout", "warehouse"):
            raise ValueError(f"invalid mode: {self.mode}")
        if not 0.0 <= self.line_position <= 1.0:
            raise ValueError("line_position must be in [0,1]")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be in [0,1]")


@dataclass(frozen=True, slots=True)
class CountingResult:
    total_count: int
    per_class_count: tuple[tuple[str, int], ...] = ()
    regions: tuple[dict[str, Any], ...] = ()
    confidence_avg: float = 0.0
    processing_ms: int = 0
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"total_count": self.total_count,
                "per_class_count": [{"class_name": n, "count": c}
                                     for n, c in self.per_class_count],
                "regions": list(self.regions),
                "confidence_avg": self.confidence_avg,
                "processing_ms": self.processing_ms,
                "warnings": list(self.warnings)}


class ProductCounter:
    def __init__(self, config: CountingConfig) -> None:
        self._config = config

    def count(self, detections: list[Detection],
               img_size: tuple[int, int]) -> CountingResult:
        import time
        t0 = time.monotonic()
        filtered = self._filter(detections)
        if self._config.mode == "shelf":
            result = self._count_shelf(filtered)
        elif self._config.mode == "conveyor":
            result = self._count_conveyor(filtered)
        elif self._config.mode == "checkout":
            result = self._count_checkout(filtered)
        else:
            result = self._count_warehouse(filtered)
        ms = int((time.monotonic() - t0) * 1000)
        return CountingResult(
            total_count=result["total"],
            per_class_count=tuple(result["per_class"].items()),
            regions=tuple(result["regions"]),
            confidence_avg=result["conf_avg"],
            processing_ms=ms)

    def _filter(self, detections: list[Detection]) -> list[Detection]:
        out: list[Detection] = []
        for d in detections:
            if d.confidence < self._config.min_confidence:
                continue
            if self._config.class_filter and d.class_id not in self._config.class_filter:
                continue
            out.append(d)
        return out

    def _count_shelf(self, detections: list[Detection]) -> dict[str, Any]:
        if not detections:
            return {"total": 0, "per_class": {}, "regions": [], "conf_avg": 0.0}
        sorted_d = sorted(detections, key=lambda d: d.bbox.y_center)
        rows: list[list[Detection]] = [[]]
        prev_y = sorted_d[0].bbox.y_center
        gap = 0.1
        for d in sorted_d:
            if d.bbox.y_center - prev_y > gap:
                rows.append([])
            rows[-1].append(d)
            prev_y = d.bbox.y_center
        per_class: dict[str, int] = {}
        regions: list[dict[str, Any]] = []
        for i, row in enumerate(rows):
            ys = [d.bbox.y_center for d in row]
            regions.append({"row": i + 1, "count": len(row),
                             "y_range": [min(ys), max(ys)]})
            for d in row:
                per_class[d.class_name] = per_class.get(d.class_name, 0) + 1
        conf_avg = sum(d.confidence for d in detections) / len(detections)
        return {"total": len(detections), "per_class": per_class,
                "regions": regions, "conf_avg": conf_avg}

    def _count_conveyor(self, detections: list[Detection]) -> dict[str, Any]:
        line = self._config.line_position
        crossed = []
        for d in detections:
            if self._config.line_orientation == "vertical":
                if d.bbox.x_center > line:
                    crossed.append(d)
            else:
                if d.bbox.y_center > line:
                    crossed.append(d)
        per_class: dict[str, int] = {}
        for d in crossed:
            per_class[d.class_name] = per_class.get(d.class_name, 0) + 1
        conf_avg = (sum(d.confidence for d in crossed) / len(crossed)
                     if crossed else 0.0)
        return {"total": len(crossed), "per_class": per_class,
                "regions": [{"line": line,
                              "orientation": self._config.line_orientation}],
                "conf_avg": conf_avg}

    def _count_checkout(self, detections: list[Detection]) -> dict[str, Any]:
        merged = self._merge_overlapping(detections)
        per_class: dict[str, int] = {}
        for d in merged:
            per_class[d.class_name] = per_class.get(d.class_name, 0) + 1
        conf_avg = (sum(d.confidence for d in merged) / len(merged)
                     if merged else 0.0)
        return {"total": len(merged), "per_class": per_class,
                "regions": [], "conf_avg": conf_avg}

    def _count_warehouse(self, detections: list[Detection]) -> dict[str, Any]:
        return self._count_checkout(detections)

    def _merge_overlapping(self, detections: list[Detection]) -> list[Detection]:
        if not self._config.deduplication:
            return detections
        result: list[Detection] = []
        used = [False] * len(detections)
        for i, d1 in enumerate(detections):
            if used[i]:
                continue
            for j in range(i + 1, len(detections)):
                if used[j]:
                    continue
                d2 = detections[j]
                dist = ((d1.bbox.x_center - d2.bbox.x_center) ** 2
                         + (d1.bbox.y_center - d2.bbox.y_center) ** 2) ** 0.5
                if dist < self._config.merge_distance:
                    used[j] = True
            result.append(d1)
        return result

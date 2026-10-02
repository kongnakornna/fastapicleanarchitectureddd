"""YOLO format helpers"""
from __future__ import annotations
from textwrap import dedent


def bbox_to_yolo(class_id: int, x_center: float, y_center: float,
                 width: float, height: float) -> str:
    return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"


def yolo_to_bbox(line: str) -> tuple[int, float, float, float, float]:
    parts = line.strip().split()
    if len(parts) != 5:
        raise ValueError(f"invalid YOLO line: {line!r}")
    return int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])


def write_dataset_yaml(classes: list[str], root: str,
                       splits: dict[str, str]) -> str:
    names = "\n".join(f"  {i}: {n}" for i, n in enumerate(classes))
    return dedent(f"""\
        path: {root}
        train: {splits.get('train', 'images/train')}
        val: {splits.get('val', 'images/val')}
        test: {splits.get('test', '')}
        names:
        {names}
    """).strip()

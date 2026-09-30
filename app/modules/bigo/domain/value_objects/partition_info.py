"""PartitionInfo VO"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PartitionInfo:
    partition: int
    leader: int
    replicas: tuple[int, ...]
    isr: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.partition < 0:
            raise ValueError("partition must be >= 0")

    @property
    def is_healthy(self) -> bool:
        return len(self.isr) == len(self.replicas)

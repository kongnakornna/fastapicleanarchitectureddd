"""KafkaLag VO"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KafkaLag:
    topic: str
    partition: int
    current_offset: int
    log_end_offset: int
    lag: int = 0

    def __post_init__(self) -> None:
        if self.partition < 0:
            raise ValueError("partition must be >= 0")
        if self.current_offset < 0 or self.log_end_offset < 0:
            raise ValueError("offsets must be non-negative")
        if self.lag < 0:
            raise ValueError("lag must be non-negative")

    @classmethod
    def compute(
        cls, topic: str, partition: int,
        current_offset: int, log_end_offset: int,
    ) -> "KafkaLag":
        return cls(
            topic=topic, partition=partition,
            current_offset=current_offset,
            log_end_offset=log_end_offset,
            lag=max(0, log_end_offset - current_offset),
        )

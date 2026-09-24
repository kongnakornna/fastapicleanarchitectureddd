"""TokenUsage value object — ใช้ Decimal เท่านั้น"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """TH: การใช้ token | EN: token usage VO"""
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal = Decimal("0")

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def __post_init__(self) -> None:
        if self.input_tokens < 0 or self.output_tokens < 0:
            raise ValueError("tokens must be non-negative")
        if self.cost_usd < 0:
            raise ValueError("cost must be non-negative")

"""ChatOptions value object"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ChatOptions:
    """TH: ตัวเลือกการแชท | EN: chat options VO"""
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: int = 1024
    stop: tuple[str, ...] = ()
    tools: tuple[dict[str, Any], ...] = ()
    tool_choice: str = "auto"
    stream: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be 0.0-2.0")
        if not 0.0 <= self.top_p <= 1.0:
            raise ValueError("top_p must be 0.0-1.0")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")

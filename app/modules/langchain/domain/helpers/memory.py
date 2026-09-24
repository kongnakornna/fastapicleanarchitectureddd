"""memory helpers — Buffer, Window, SummaryBuffer"""
from __future__ import annotations
import json
from typing import Any


def approx_token_count(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)


class BufferMemory:
    """TH: เก็บ message ทั้งหมด | EN: full buffer memory"""

    def __init__(self, max_tokens: int = 4096) -> None:
        self._max = max_tokens
        self._messages: list[dict[str, Any]] = []

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        self._trim()

    def messages(self) -> list[dict[str, Any]]:
        return list(self._messages)

    def _trim(self) -> None:
        total = sum(approx_token_count(m.get("content", ""))
                    for m in self._messages)
        while total > self._max and len(self._messages) > 1:
            removed = self._messages.pop(0)
            total -= approx_token_count(removed.get("content", ""))

    def snapshot(self) -> dict[str, Any]:
        payload = self.messages()
        return {
            "memory_type": "buffer",
            "payload": payload,
            "size_bytes": len(json.dumps(payload, default=str).encode("utf-8")),
        }


class WindowMemory(BufferMemory):
    """TH: sliding window N messages | EN: window memory"""

    def __init__(self, window_size: int = 10, max_tokens: int = 4096) -> None:
        super().__init__(max_tokens=max_tokens)
        self._window = window_size

    def _trim(self) -> None:
        super()._trim()
        if len(self._messages) > self._window:
            self._messages = self._messages[-self._window:]

    def snapshot(self) -> dict[str, Any]:
        s = super().snapshot()
        s["memory_type"] = "window"
        return s


class SummaryBufferMemory(BufferMemory):
    """TH: buffer + summary placeholder | EN: summary-buffer memory"""

    def __init__(self, max_tokens: int = 4096, summary_threshold: int = 2048) -> None:
        super().__init__(max_tokens=max_tokens)
        self._threshold = summary_threshold
        self._summary = ""

    def set_summary(self, text: str) -> None:
        self._summary = text or ""

    def snapshot(self) -> dict[str, Any]:
        s = super().snapshot()
        s["memory_type"] = "summary_buffer"
        s["payload"] = [{"role": "system", "content": self._summary}] + s["payload"]
        return s

"""structured_outputs enums"""
from __future__ import annotations
from enum import Enum


class SOStrategy(str, Enum):
    """TH: กลยุทธ์การบังคับ JSON | EN: Structured output strategy"""
    JSON_MODE = "json_mode"
    FUNCTION_CALL = "function_call"
    GRAMMAR = "grammar"
    REGEX = "regex"
    PROMPT_ONLY = "prompt_only"

    def __str__(self) -> str:
        return str(self.value)


class SOStatus(str, Enum):
    """TH: สถานะ | EN: Status"""
    PENDING = "PENDING"
    VALID = "VALID"
    INVALID = "INVALID"
    REPAIRED = "REPAIRED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return str(self.value)

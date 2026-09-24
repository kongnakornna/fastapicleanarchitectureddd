from __future__ import annotations

from enum import Enum


class TokenType(str, Enum):
    BEARER = "Bearer"
    REFRESH = "Refresh"

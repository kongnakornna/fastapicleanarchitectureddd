from __future__ import annotations

from enum import Enum


class WebSocketMessageType(str, Enum):
    NOTIFICATION = "notification"

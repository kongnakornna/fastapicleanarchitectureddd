"""
Application Exceptions — ข้อยกเว้นของ config
ConfigException: ข้อผิดพลาดทั่วไป
ConfigKeyNotFoundException: ไม่พบ key ที่ระบุ
"""

from __future__ import annotations

from core.application.exceptions import StandardException


class ConfigException(StandardException):
    """Config exception — ข้อผิดพลาดทั่วไปของ config"""

    def __init__(self, message: str = "Config operation failed") -> None:
        super().__init__(message=message, code="CONFIG_ERROR")
        self.message = message


class ConfigKeyNotFoundException(ConfigException):
    """Config key not found — ไม่พบ config key ที่ระบุ"""

    def __init__(self, key: str) -> None:
        super().__init__(message=f"Config key not found: {key}")
        self.code = "CONFIG_KEY_NOT_FOUND"
        self.key = key

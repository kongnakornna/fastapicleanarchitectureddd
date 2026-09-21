"""
Domain Exceptions — ข้อยกเว้นของโดเมน config
ConfigDomainError: ข้อผิดพลาดเชิงโดเมนของ config
"""

from __future__ import annotations

from app.shared.exceptions import DomainException


class ConfigDomainError(DomainException):
    """
    Config domain error — ข้อผิดพลาดเชิงโดเมนของ config
    ใช้เมื่อ invariant ของ config ถูกทำลาย
    """

    code = "CFG_DOMAIN_ERROR"


class InvalidConfigKeyError(ConfigDomainError):
    """Invalid config key — รูปแบบ key ไม่ถูกต้อง"""

    code = "CFG_INVALID_KEY"

    def __init__(self, key: str) -> None:
        super().__init__(f"Invalid config key: {key}")
        self.key = key


class InvalidConfigValueError(ConfigDomainError):
    """Invalid config value — ค่าไม่ตรงกับชนิดที่กำหนด"""

    code = "CFG_INVALID_VALUE"

    def __init__(self, key: str, value_type: str, reason: str = "") -> None:
        msg = f"Invalid value for '{key}' as {value_type}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.key = key
        self.value_type = value_type


__all__ = [
    "ConfigDomainError",
    "InvalidConfigKeyError",
    "InvalidConfigValueError",
]

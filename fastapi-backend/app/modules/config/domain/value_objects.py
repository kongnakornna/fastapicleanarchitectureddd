"""
Domain Value Objects — วัตถุค่าในโดเมน config
ConfigKey: ตรวจสอบรูปแบบ key และแยก namespace
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# โมดูลกลางของโปรเจกต์ (สมมติว่ามีอยู่แล้ว)
from core.domain.exceptions import DomainError

# รูปแบบ key ที่ถูกต้อง: เริ่มด้วยตัวพิมพ์เล็ก ตามด้วย a-z, 0-9, _, .
CONFIG_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_.]*$")


@dataclass(frozen=True)
class ConfigKey:
    """
    Config key VO — วัตถุกุญแจ config

    Attributes:
        value: ค่า key ที่ผ่านการตรวจสอบแล้ว

    Raises:
        DomainError: หากรูปแบบ key ไม่ถูกต้อง
    """

    value: str

    def __post_init__(self) -> None:
        """ตรวจสอบรูปแบบ key — ต้องตรงตาม CONFIG_KEY_PATTERN"""
        if not self.value:
            raise DomainError("Config key required")
        if not CONFIG_KEY_PATTERN.match(self.value):
            raise DomainError(f"Invalid config key: {self.value}")

    def namespace(self) -> str:
        """
        คืน namespace ของ key
        ตัวอย่าง: 'app.theme.color' → 'app'
        """
        return self.value.split(".", 1)[0]

    def __str__(self) -> str:
        return self.value

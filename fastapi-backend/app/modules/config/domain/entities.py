"""
Domain Entities — เอนทิตีในโดเมน config
ConfigEntry: รายการตั้งค่าเดียว รองรับ type-safe และ secret masking
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from typing import Any

from core.domain.entities import BaseEntity
from core.domain.exceptions import DomainError

from .enums import ConfigScope, ConfigType

# รูปแบบ key ที่ถูกต้อง
CONFIG_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_.]*$")


@dataclass
class ConfigEntry(BaseEntity):
    """
    Config entry — เอนทิตีรายการตั้งค่า

    Attributes:
        key: ค่ากุญแจ config (รูปแบบ ^[a-z][a-z0-9_.]*$)
        value: ค่าที่เก็บ (string เสมอ — secret จะถูกเข้ารหัสแล้ว)
        value_type: ชนิดของค่า (ConfigType)
        scope: ขอบเขต (GLOBAL/TENANT/USER)
        scope_id: รหัสของ scope (tenant_id หรือ user_id)
        is_secret: เป็นความลับหรือไม่
        description: คำอธิบาย
    """

    key: str = ""
    value: str = ""
    value_type: str = ConfigType.STRING.value
    scope: str = ConfigScope.TENANT.value
    scope_id: str = ""
    is_secret: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        """ตรวจสอบความถูกต้องหลังสร้าง"""
        self._validate()

    def _validate(self) -> None:
        """
        ตรวจสอบ invariant ของ ConfigEntry
        - key ต้องไม่ว่างและตรงรูปแบบ
        """
        if not self.key:
            raise DomainError("Config key required")
        if not CONFIG_KEY_PATTERN.match(self.key):
            raise DomainError(f"Invalid key format: {self.key}")

    def typed_value(self) -> Any:
        """
        คืนค่าตามชนิด (type-safe)
        - int → int
        - decimal → Decimal
        - bool → bool
        - json → dict/list
        - อื่น ๆ → str

        Raises:
            DomainError: หากแปลงค่าไม่ได้
        """
        try:
            if self.value_type == ConfigType.INT.value:
                return int(self.value)
            if self.value_type == ConfigType.DECIMAL.value:
                return Decimal(self.value)
            if self.value_type == ConfigType.BOOL.value:
                return self.value.lower() in ("1", "true", "yes")
            if self.value_type == ConfigType.JSON.value:
                return json.loads(self.value)
            return self.value
        except (ValueError, InvalidOperation, json.JSONDecodeError) as e:
            raise DomainError(
                f"Cannot convert config '{self.key}' to {self.value_type}: {e}"
            )

    def mask(self) -> ConfigEntry:
        """
        ปิดบังค่า secret — คืน copy ที่ value = '***' หาก is_secret
        ใช้ก่อนส่งออกผ่าน API
        """
        if self.is_secret:
            return replace(self, value="***")
        return self

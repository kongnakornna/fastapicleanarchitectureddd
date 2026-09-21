"""
Presentation Schemas — Pydantic schema ของ config
ConfigEntrySchema, ConfigSetRequest, ConfigListResponse
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..domain.enums import ConfigScope, ConfigType

# รูปแบบ key ที่ถูกต้อง (sync กับ domain)
KEY_PATTERN = r"^[a-z][a-z0-9_.]*$"


class ConfigEntrySchema(BaseModel):
    """
    Config entry response — schema สำหรับตอบกลับ
    secret จะถูก mask เป็น '***'
    """

    model_config = ConfigDict(from_attributes=True)

    key: str = Field(..., description="Config key")
    value: str = Field(..., description="Config value (masked if secret)")
    value_type: str = Field(..., description="string|int|decimal|bool|json|secret")
    scope: str = Field(..., description="GLOBAL|TENANT|USER")
    scope_id: str = Field(..., description="Scope identifier")
    is_secret: bool = Field(False, description="Is secret value")
    description: str = Field("", description="Description")
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ConfigSetRequest(BaseModel):
    """
    Config set request — payload สำหรับ PUT /{key}/
    """

    value: str = Field(..., description="Raw value as string")
    value_type: str = Field(
        ConfigType.STRING.value,
        description="string|int|decimal|bool|json|secret",
    )
    scope: str = Field(
        ConfigScope.TENANT.value,
        description="GLOBAL|TENANT|USER",
    )
    scope_id: str = Field("", description="Scope identifier (empty = use context)")
    is_secret: bool = Field(False, description="Encrypt at rest")
    description: str = Field("", description="Optional description")

    @field_validator("value_type")
    @classmethod
    def _validate_value_type(cls, v: str) -> str:
        allowed = {t.value for t in ConfigType}
        if v not in allowed:
            raise ValueError(f"value_type must be one of {sorted(allowed)}")
        return v

    @field_validator("scope")
    @classmethod
    def _validate_scope(cls, v: str) -> str:
        allowed = {s.value for s in ConfigScope}
        if v not in allowed:
            raise ValueError(f"scope must be one of {sorted(allowed)}")
        return v


class ConfigListQuery(BaseModel):
    """Query params สำหรับ GET /"""

    scope: str = Field(ConfigScope.TENANT.value)
    scope_id: str = Field("", description="Empty = use tenant context")

    @field_validator("scope")
    @classmethod
    def _validate_scope(cls, v: str) -> str:
        allowed = {s.value for s in ConfigScope}
        if v not in allowed:
            raise ValueError(f"scope must be one of {sorted(allowed)}")
        return v


class ConfigTypedResponse(BaseModel):
    """Response พร้อม typed value"""

    key: str
    value: Any
    value_type: str
    scope: str
    scope_id: str
    is_secret: bool = False


__all__ = [
    "ConfigEntrySchema",
    "ConfigListQuery",
    "ConfigSetRequest",
    "ConfigTypedResponse",
]

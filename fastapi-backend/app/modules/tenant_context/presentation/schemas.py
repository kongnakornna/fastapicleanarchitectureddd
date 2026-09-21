"""tenant_context presentation schemas — Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantContextSchema(BaseModel):
    """TenantContextSchema — schema สำหรับ tenant context."""

    tenant_id: str
    user_id: str | None = None
    correlation_id: str
    request_id: str = ""
    locale: str = "th-TH"
    timezone: str = "Asia/Bangkok"
    schema_name: str = ""
    established_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SwitchTenantRequest(BaseModel):
    """SwitchTenantRequest — คำขอเปลี่ยน tenant."""

    tenant_id: str = Field(..., min_length=1, max_length=64)
    user_id: str | None = Field(default=None, max_length=64)


class SwitchTenantResponse(BaseModel):
    """SwitchTenantResponse — ผลลัพธ์การเปลี่ยน tenant."""

    tenant_id: str
    correlation_id: str
    schema_name: str
    switched: bool = True

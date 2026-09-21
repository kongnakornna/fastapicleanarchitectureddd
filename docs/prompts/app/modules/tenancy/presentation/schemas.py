"""tenancy presentation schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    """TenantCreate — schema สร้าง tenant."""
    slug: str = Field(..., pattern=r"^[a-z][a-z0-9-]{2,30}$")
    name: str = Field(..., min_length=1, max_length=200)
    owner_email: str = Field(..., max_length=255)
    plan: str = Field(default="FREE")


class TenantResponse(BaseModel):
    """TenantResponse — schema ตอบกลับ."""
    id: str
    slug: str
    name: str
    plan: str
    status: str
    schema_name: str
    owner_email: str
    max_users: int
    max_storage_gb: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SuspendRequest(BaseModel):
    """SuspendRequest — คำขอระงับ."""
    reason: str = Field(..., min_length=1, max_length=500)


class UpgradeRequest(BaseModel):
    """UpgradeRequest — คำขออัปเกรด."""
    plan: str = Field(..., pattern=r"^(FREE|STARTER|PROFESSIONAL|ENTERPRISE)$")
"""pdpa Pydantic v2 schemas"""
from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.pdpa.domain.enums import (
    ConsentStatus, DSARStatus, DSARType,
    PrivacyPolicyStatus, PurposeCategory,
)


# ─── Consent ────────────────────────────────────────────────────
class ConsentCreateRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    user_id: uuid.UUID
    purpose_code: PurposeCategory
    ip_address: str = Field(min_length=7, max_length=45)
    user_agent: str = Field(max_length=500)
    expires_at: datetime | None = None


class ConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    purpose_code: PurposeCategory
    status: ConsentStatus
    granted_at: datetime
    revoked_at: datetime | None
    expires_at: datetime | None
    version: int


class ConsentRevokeRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    reason: str = Field(default="user_withdrawal", max_length=200)


# ─── DSAR ───────────────────────────────────────────────────────
class DSARCreateRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    user_id: uuid.UUID
    type: DSARType
    reason: str | None = Field(default=None, max_length=500)


class DSARProcessRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    response_payload: dict[str, object] = Field(default_factory=dict)


class DSARResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    type: DSARType
    status: DSARStatus
    submitted_at: datetime
    verified_at: datetime | None
    completed_at: datetime | None
    deadline_at: datetime
    version: int


# ─── Privacy Policy ─────────────────────────────────────────────
class PrivacyPolicyCreateRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    version: int = Field(ge=1)
    content_th: str = Field(min_length=1)
    content_en: str = Field(min_length=1)


class PrivacyPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    version: int
    content_th: str
    content_en: str
    status: PrivacyPolicyStatus
    effective_from: datetime
    published_at: datetime | None


# ─── Cookie Consent ─────────────────────────────────────────────
class CookieConsentRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    session_id: str = Field(min_length=8, max_length=128)
    analytics: bool = False
    marketing: bool = False
    functional: bool = False


class CookieConsentUpdateRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    analytics: bool | None = None
    marketing: bool | None = None
    functional: bool | None = None


class CookieConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    session_id: str
    necessary: bool
    analytics: bool
    marketing: bool
    functional: bool
    accepted_at: datetime
    withdrawn_at: datetime | None
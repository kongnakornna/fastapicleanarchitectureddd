"""user Pydantic v2 schemas"""
from __future__ import annotations

import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.modules.shared.domain.enums import Role
from app.modules.user.domain.enums import (
    Gender, OnlineStatus, UserStatus,
)


# ═════════════════════════════════════════════════════════
# RE-EXPORTS (backward compatibility)
# ═════════════════════════════════════════════════════════
from app.modules.shared.presentation.schemas import (  # noqa: F401, E402
    CreateResponse as CreateResponse,
)


# ═════════════════════════════════════════════════════════
# REQUEST
# ═════════════════════════════════════════════════════════
class CreateRequest(BaseModel):
    """TH: request สร้าง user | EN: create-user request"""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    preferred_name: str | None = Field(default=None, max_length=100)
    nickname: str | None = Field(default=None, max_length=100)

    username: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str | None = None
    mobile_number: str | None = None
    line_id: str | None = Field(default=None, max_length=100)
    id_card: str | None = Field(default=None, max_length=20)

    gender: Gender | None = None
    birthdate: date | None = None

    password: str = Field(min_length=8, max_length=64)

    network_id: int | None = None
    network_type_id: int | None = None
    type_id: int | None = None
    system_id: str | None = None
    location_id: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", value):
            raise ValueError("Name contains invalid characters.")
        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.@-]+$", value):
            raise ValueError(
                "Username may contain letters, digits, '.', '_', '@', '-'."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be ≥ 8 chars.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain uppercase.")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain lowercase.")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain special char.")
        return password

    model_config = ConfigDict(
        title="CreateRequest", extra="forbid",
        str_strip_whitespace=True,
    )


# ═════════════════════════════════════════════════════════
# RESPONSE
# ═════════════════════════════════════════════════════════
class MeResponse(BaseModel):
    """TH: response /me | EN: /me response"""

    id: int
    first_name: str
    last_name: str
    preferred_name: str
    full_name: str | None = None
    nickname: str | None = None
    username: str
    email: str
    phone: str | None = None
    mobile_number: str | None = None
    line_id: str | None = None
    gender: Gender | None = None
    birthdate: date | None = None
    avatar: str | None = None
    avatar_path: str | None = None
    role: Role
    status: UserStatus
    online_status: OnlineStatus
    is_verified: bool = False
    is_superuser: bool = False
    last_sign_in_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(
        title="MeResponse", extra="forbid",
        str_strip_whitespace=True,
    )

from __future__ import annotations

import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.enums import Role
from app.modules.shared.presentation.schemas import (
    CreateResponse as CreateResponse,  # noqa: PLC0414
)
from app.modules.user.domain.enums import Gender


# ═════════════════════════════════════════════════════════════════
# REQUEST
# ═════════════════════════════════════════════════════════════════
class CreateRequest(BaseModel):
    """TH: request model สร้าง user | EN: create-user request model"""

    first_name: str = Field(min_length=1, max_length=100, examples=["John"])
    last_name: str = Field(min_length=1, max_length=100, examples=["Doe"])
    preferred_name: str | None = Field(default=None, max_length=100)

    gender: Gender | None = Field(default=None)
    birthdate: date | None = Field(default=None)

    email: EmailStr = Field(examples=["johndoe@domain.com"])
    phone: str | None = Field(default=None)
    password: str = Field(min_length=8, max_length=64)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", value):
            raise ValueError(
                "Name must contain only letters, spaces, apostrophes, and hyphens."
            )
        return value

    @field_validator("preferred_name")
    @classmethod
    def validate_preferred_name(cls, value: str | None) -> str | None:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, value: date | None) -> date | None:
        if value is None:
            return None
        today = datetime.now(BRASILIA_TZ).date()
        min_year = date(1900, 1, 1)
        if value > today:
            raise ValueError("Birthdate cannot be a future date.")
        if value < min_year:
            raise ValueError("Birthdate cannot be before January 1, 1900.")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if isinstance(value, str) and value.strip() == "":
            return None
        stripped = re.sub(r"[+\-()]", "", value)
        if not stripped.isdigit():
            raise ValueError(
                "Phone number must contain only digits, '+', '-', '(' and ')'."
            )
        if not (7 <= len(stripped) <= 15):
            raise ValueError("Phone number must have between 7 and 15 digits.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if len(password) > 64:
            raise ValueError("Password must be at most 64 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character.")
        return password

    model_config = ConfigDict(
        title="CreateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "preferred_name": "Joe",
                "email": "johndoe@domain.com",
                "phone": "+555472664275",
                "password": "MyP@ssword123",
                "birthdate": "1995-01-01",
                "gender": "male",
            },
        },
    )


# ═════════════════════════════════════════════════════════════════
# RESPONSE
# ═════════════════════════════════════════════════════════════════
class MeResponse(BaseModel):
    """
    TH: response ของ /me — สะท้อน schema จริงของ DB
        (gender/birthdate/phone เป็น nullable จึงต้อง optional ที่นี่ด้วย)

    EN: /me response — mirrors the actual DB schema where
        gender/birthdate/phone are nullable, so they must be optional here.
    """

    first_name: str
    last_name: str
    preferred_name: str
    gender: Gender | None = None            # ← แก้: nullable
    birthdate: date | None = None           # ← แก้: nullable
    email: str
    phone: str | None = None
    role: Role
    created_at: datetime

    model_config = ConfigDict(
        title="MeResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "preferred_name": "Joe",
                "gender": "male",
                "birthdate": "1995-01-01",
                "email": "johndoe@domain.com",
                "phone": "+555472664275",
                "role": "user",
                "created_at": "2024-05-01T12:00:00Z",
            },
        },
    )

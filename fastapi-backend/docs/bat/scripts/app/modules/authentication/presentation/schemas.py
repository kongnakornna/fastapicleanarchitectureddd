from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, model_validator

from app.modules.shared.domain.enums import ResponseMessages, Role


# ============================================================================
# ACCESS TOKEN INFO
# ============================================================================
class AccessTokenInfo(BaseModel):
    """Access token metadata returned with login response."""

    created_at: datetime
    expires_at: datetime
    claims: dict

    model_config = ConfigDict(
        title="AccessTokenInfo",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "description": "Access token metadata (created_at, expires_at, claims).",
            "example": {
                "created_at": "2026-09-20T10:47:51.493046Z",
                "expires_at": "2026-09-20T11:17:51.493046Z",
                "claims": {
                    "iss": "erp-iot-api",
                    "sub": "550e8400-e29b-41d4-a716-446655440000",
                    "aud": "erp-iot-client",
                    "iat": 1758365271,
                    "nbf": 1758365271,
                    "exp": 1758367071,
                    "jti": "660e8400-e29b-41d4-a716-446655440001",
                    "grant_id": "admin@example.com",
                    "scope": "admin",
                },
            },
        },
    )


# ============================================================================
# USER INFO
# ============================================================================
class UserInfo(BaseModel):
    """User information returned with login response."""

    first_name: str
    last_name: str
    preferred_name: str
    gender: str
    birthdate: date
    email: EmailStr
    phone: str | None = None
    role: Role
    created_at: str

    model_config = ConfigDict(
        title="UserInfo",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "description": "User information returned with login response.",
            "example": {
                "first_name": "System",
                "last_name": "Admin",
                "preferred_name": "Admin",
                "gender": "other",
                "birthdate": "1990-01-01",
                "email": "admin@example.com",
                "phone": None,
                "role": "admin",
                "created_at": "2026-09-19T08:57:37.641459Z",
            },
        },
    )


# ============================================================================
# RESPONSE
# ============================================================================
class LoginResponse(BaseModel):
    """
    Response model for login.

    Structure:
    {
        "message": "User logged in successfully",
        "access_token": "...",
        "refresh_token": "...",
        "token_info": {
            "created_at": "...",
            "expires_at": "...",
            "claims": { ... }
        },
        "info": { ... }
    }
    """

    message: str = ResponseMessages.LOGIN_SUCCESS.value
    access_token: str
    refresh_token: str
    token_info: AccessTokenInfo
    info: UserInfo

    model_config = ConfigDict(
        title="LoginResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user login.",
            "example": {
                "message": ResponseMessages.LOGIN_SUCCESS.value,
                "access_token": "eyJhbGciOi...",
                "refresh_token": "eyJhbGciOi...",
                "token_info": {
                    "created_at": "2026-09-20T10:47:51.493046Z",
                    "expires_at": "2026-09-20T11:17:51.493046Z",
                    "claims": {
                        "iss": "erp-iot-api",
                        "sub": "550e8400-e29b-41d4-a716-446655440000",
                        "aud": "erp-iot-client",
                        "iat": 1758365271,
                        "nbf": 1758365271,
                        "exp": 1758367071,
                        "jti": "660e8400-e29b-41d4-a716-446655440001",
                        "grant_id": "admin@example.com",
                        "scope": "admin",
                    },
                },
                "info": {
                    "first_name": "System",
                    "last_name": "Admin",
                    "preferred_name": "Admin",
                    "gender": "other",
                    "birthdate": "1990-01-01",
                    "email": "admin@example.com",
                    "phone": None,
                    "role": "admin",
                    "created_at": "2026-09-19T08:57:37.641459Z",
                },
            },
        },
    )


class RefreshResponse(BaseModel):
    """Response model for refresh."""

    message: str = ResponseMessages.REFRESH_SUCCESS.value

    model_config = ConfigDict(
        title="RefreshResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user refresh.",
            "example": {"message": ResponseMessages.REFRESH_SUCCESS.value},
        },
    )


class LogoutResponse(BaseModel):
    """Response model for logout."""

    message: str = ResponseMessages.LOGOUT_SUCCESS.value

    model_config = ConfigDict(
        title="LogoutResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user logout.",
            "example": {"message": ResponseMessages.LOGOUT_SUCCESS.value},
        },
    )


# ============================================================================
# SIGN UP
# ============================================================================
class SignUpRequest(BaseModel):
    """
    Request model for sign up.

    รองรับ 2 รูปแบบการส่งชื่อ:
        1. ส่ง full_name มาเป็นก้อนเดียว → ระบบ split เป็น first_name/last_name
        2. ส่ง first_name และ/หรือ last_name มาตรง ๆ

    หลัง validate แล้ว จะมีทั้ง full_name, first_name และ last_name ครบ
    """

    # ── ชื่อ (ส่งแบบไหนก็ได้) ─────────────────────────────────────────
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    # ── ข้อมูลบัญชี ──────────────────────────────────────────────────
    username: str
    email: EmailStr
    phone_number: str | None = None

    # ── รหัสผ่าน ────────────────────────────────────────────────────
    password: str
    confirm_password: str

    # ── เงื่อนไขการสมัคร ─────────────────────────────────────────────
    agree_terms: bool

    model_config = ConfigDict(
        title="SignUpRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "phone_number": "+555472664275",
                "password": "MyP@ssword123",
                "confirm_password": "MyP@ssword123",
                "agree_terms": True,
            },
        },
    )

    # ------------------------------------------------------------------
    # VALIDATORS
    # ------------------------------------------------------------------
    @model_validator(mode="after")
    def normalize_name(self) -> SignUpRequest:
        """
        Normalize ชื่อให้ครบทั้ง 3 field

        ลำดับความสำคัญ:
            1. ถ้าส่ง first_name และ/หรือ last_name มา → ใช้ค่านั้นเป็นหลัก
            2. ถ้าส่งแค่ full_name → split ที่ช่องว่างแรกเป็น first/last
            3. ถ้าไม่ส่งชื่อมาเลย → raise error
        """
        has_explicit_name = bool(self.first_name or self.last_name)

        if not has_explicit_name and self.full_name:
            parts = self.full_name.strip().split(maxsplit=1)
            self.first_name = parts[0] if parts else ""
            self.last_name = parts[1] if len(parts) > 1 else ""

        if not (self.first_name or self.last_name):
            raise ValueError("ต้องระบุ full_name หรือ first_name/last_name อย่างน้อยหนึ่งอย่าง")

        if not self.full_name:
            self.full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()

        if not self.first_name:
            self.first_name = ""
        if not self.last_name:
            self.last_name = ""

        return self

    @model_validator(mode="after")
    def passwords_match(self) -> SignUpRequest:
        """ตรวจว่า password กับ confirm_password ตรงกัน"""
        if self.password != self.confirm_password:
            raise ValueError("password และ confirm_password ไม่ตรงกัน")
        return self

    @model_validator(mode="after")
    def terms_accepted(self) -> SignUpRequest:
        """บังคับให้ยอมรับเงื่อนไขก่อนสมัคร"""
        if not self.agree_terms:
            raise ValueError("ต้องยอมรับเงื่อนไขการใช้งาน (agree_terms)")
        return self


class SignUpResponse(BaseModel):
    """
    Response model for sign up.

    คืนข้อมูลผู้ใช้ที่สมัครสำเร็จ — ไม่คืน password หรือ hashed_password
    ใช้ extra="ignore" เพื่อทน field เกินที่ mapper อาจส่งมา
    """

    message: str = ResponseMessages.SUCCESS.value
    id: UUID
    first_name: str
    last_name: str
    preferred_name: str
    email: EmailStr
    phone: str | None = None
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        title="SignUpResponse",
        str_strip_whitespace=True,
        extra="ignore",
        json_schema_extra={
            "description": "Response model for successful user sign up.",
            "example": {
                "message": ResponseMessages.SUCCESS.value,
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "first_name": "John",
                "last_name": "Doe",
                "preferred_name": "John",
                "email": "johndoe@example.com",
                "phone": "+555472664275",
                "role": "user",
                "is_active": True,
                "created_at": "2026-09-21T12:00:00Z",
                "updated_at": "2026-09-21T12:00:00Z",
            },
        },
    )


# ============================================================================
# FORGOT PASSWORD
# ============================================================================
class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password."""

    email: EmailStr

    model_config = ConfigDict(
        title="ForgotPasswordRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={"example": {"email": "johndoe@example.com"}},
    )


class ForgotPasswordResponse(BaseModel):
    """Response model for forgot password."""

    message: str = ResponseMessages.SUCCESS.value

    model_config = ConfigDict(
        title="ForgotPasswordResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.SUCCESS.value},
        },
    )


# ============================================================================
# RESET PASSWORD
# ============================================================================
class ResetPasswordRequest(BaseModel):
    """Request model for reset password."""

    code: str
    password: str
    confirm_password: str

    model_config = ConfigDict(
        title="ResetPasswordRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "code": "ABC123",
                "password": "NewP@ssword123",
                "confirm_password": "NewP@ssword123",
            },
        },
    )


class ResetPasswordResponse(BaseModel):
    """Response model for reset password."""

    message: str = ResponseMessages.SUCCESS.value

    model_config = ConfigDict(
        title="ResetPasswordResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.SUCCESS.value},
        },
    )


# ============================================================================
# LOCK SCREEN
# ============================================================================
class LockScreenRequest(BaseModel):
    """Request model for lock screen."""

    password: str

    model_config = ConfigDict(
        title="LockScreenRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={"example": {"password": "MyP@ssword123"}},
    )


class LockScreenResponse(BaseModel):
    """Response model for lock screen."""

    message: str = ResponseMessages.SUCCESS.value

    model_config = ConfigDict(
        title="LockScreenResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.SUCCESS.value},
        },
    )


# ============================================================================
# TWO-STEP VERIFICATION
# ============================================================================
class TwoStepVerificationRequest(BaseModel):
    """Request model for two-step verification."""

    country_code: str
    phone_number: str

    model_config = ConfigDict(
        title="TwoStepVerificationRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"country_code": "+1", "phone_number": "8566728552"},
        },
    )


class TwoStepVerificationResponse(BaseModel):
    """Response model for two-step verification."""

    message: str = ResponseMessages.SUCCESS.value

    model_config = ConfigDict(
        title="TwoStepVerificationResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.SUCCESS.value},
        },
    )


# ============================================================================
# TWO-STEP CODE
# ============================================================================
class TwoStepCodeRequest(BaseModel):
    """Request model for two-step code."""

    code: str
    dont_ask_again: bool = False

    model_config = ConfigDict(
        title="TwoStepCodeRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"code": "123456", "dont_ask_again": False},
        },
    )


class TwoStepCodeResponse(BaseModel):
    """Response model for two-step code."""

    message: str = ResponseMessages.SUCCESS.value
    access_token: str | None = None
    refresh_token: str | None = None

    model_config = ConfigDict(
        title="TwoStepCodeResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "message": ResponseMessages.SUCCESS.value,
                "access_token": "eyJhbGciOi...",
                "refresh_token": "eyJhbGciOi...",
            },
        },
    )

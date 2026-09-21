from pydantic import BaseModel, ConfigDict, Field

from app.modules.shared.application.enums import ResponseMessages


# RESPONSE
class LoginResponse(BaseModel):
    message: str = ResponseMessages.LOGIN_SUCCESS.value
    token_type: str = Field(
        default="Bearer",
        title="Token Type",
        description="The type of the access token.",
        examples=["Bearer"],
        json_schema_extra={"example": "Bearer", "readOnly": True},
    )
    access_token: str = Field(
        title="Access Token",
        description="The JWT access token used for authentication.",
        json_schema_extra={
            "example": "eyJhbGciOiJSUzI1NiIsInR5cCI6...",
            "readOnly": True,
        },
    )
    refresh_token: str = Field(
        title="Refresh Token",
        description="The JWT refresh token used to obtain a new access token.",
        json_schema_extra={
            "example": "eyJhbGciOiJSUzI1NiIsInR5cCI6...",
            "readOnly": True,
        },
    )

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
                "token_type": "Bearer",
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6...",
                "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6...",
            },
        },
    )


class RefreshResponse(BaseModel):
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


class RegisterResponse(BaseModel):
    message: str = ResponseMessages.CREATED.value

    model_config = ConfigDict(
        title="RegisterResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user registration.",
            "example": {"message": ResponseMessages.CREATED.value},
        },
    )

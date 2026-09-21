from __future__ import annotations

from http import HTTPStatus

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import ResponseMessages


# ============================================================================
# GENERIC EXCEPTIONS
# ============================================================================
class AuthenticationException(StandardException):
    """Generic exception for authentication module."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "Case 1 An unexpected error occurred while processing the request at the authentication module."
            },
        )


class AuthenticationTokenException(StandardException):
    """Exception for token processing errors."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while processing the authentication token. Please login again or contact support."
            },
        )


class HashingException(StandardException):
    """Exception for hashing errors."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while hashing the password. Please try again."
            },
        )


class RefreshTokenException(StandardException):
    """Exception for refresh token errors."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while processing the refresh token. Please login again or contact support."
            },
        )


# ============================================================================
# SPECIFIC EXCEPTIONS
# ============================================================================
class InvalidCredentialsException(StandardException):
    """Exception when credentials are invalid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid credentials for login.",
                "errors_th": "ข้อมูลเข้าสู่ระบบไม่ถูกต้อง",
            },
        )


class AuthenticationCookiesNotProvidedException(StandardException):
    """Exception when cookies are not found."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Authentication cookies doest not exist. Please login again or contact support.",
                "errors_th": "ไม่พบคุกกี้สำหรับการยืนยันตัวตน กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationTokenExpiredException(StandardException):
    """Exception when token has expired."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Token has expired. Please login again or contact support.",
                "errors_th": "โทเค็นหมดอายุแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationTokenNotYetValidException(StandardException):
    """Exception when token is not yet valid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Token is not yet valid. Please login again or contact support.",
                "errors_th": "โทเค็นยังไม่พร้อมใช้งาน กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationTokenMalformedError(StandardException):
    """Exception when token format is malformed."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Malformed authentication token. Please login again or contact support.",
                "errors_th": "โทเค็นการยืนยันตัวตนมีรูปแบบไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationTokenInvalidException(StandardException):
    """Exception when token is invalid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid authentication token. The provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "โทเค็นการยืนยันตัวตนไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class ModifiedTokenException(StandardException):
    """Exception when token has been modified."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "The authentication token has been modified. Please login again or contact support.",
                "errors_th": "โทเค็นการยืนยันตัวตนถูกแก้ไขเปลี่ยนแปลง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class UserHasNotPermissionException(StandardException):
    """Exception when user lacks permission."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "User does not have permission to perform this action.",
                "errors_th": "ผู้ใช้ไม่มีสิทธิ์ดำเนินการนี้",
            },
        )


class RefreshTokenNotProvidedException(StandardException):
    """Exception when refresh token is not provided."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Refresh token not provided. Please login again or contact support.",
                "errors_th": "ไม่ได้ระบุรีเฟรชโทเค็น กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenExpiredException(StandardException):
    """Exception when refresh token has expired."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Refresh token has expired. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นหมดอายุแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenNotYetValidException(StandardException):
    """Exception when refresh token is not yet valid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Refresh token is not yet valid. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นยังไม่พร้อมใช้งาน กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenMalformedError(StandardException):
    """Exception when refresh token format is malformed."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Malformed refresh token. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นมีรูปแบบไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenInvalidEndpoint(StandardException):
    """Exception when refresh endpoint is invalid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid endpoint for refresh token. Please login again or contact support.",
                "errors_th": "ปลายทางสำหรับรีเฟรชโทเค็นไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenInvalidException(StandardException):
    """Exception when refresh token is invalid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid refresh token. The provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenInvalidDeviceException(StandardException):
    """Exception when device does not match refresh token."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid refresh token data. The provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "ข้อมูลรีเฟรชโทเค็นไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationInvalidDeviceException(StandardException):
    """Exception when device does not match authentication."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid authentication data. The provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "ข้อมูลการยืนยันตัวตนไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class LogoutInvalidEndpoint(StandardException):
    """Exception when logout endpoint is invalid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid endpoint for logout. Please login again or contact support.",
                "errors_th": "ปลายทางสำหรับออกจากระบบไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


# ============================================================================
# SIGN UP / PASSWORD RESET EXCEPTIONS
# ============================================================================
class EmailAlreadyExistsException(StandardException):
    """Exception when email already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            message=ResponseMessages.CONFLICT.value,
            data={
                "errors": f"Email '{email}' already exists.",
                "errors_th": f"อีเมล '{email}' มีอยู่ในระบบแล้ว",
            },
        )


class UsernameAlreadyExistsException(StandardException):
    """Exception when username already exists."""

    def __init__(self, username: str) -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            message=ResponseMessages.CONFLICT.value,
            data={
                "errors": f"Username '{username}' already exists.",
                "errors_th": f"ชื่อผู้ใช้ '{username}' มีอยู่ในระบบแล้ว",
            },
        )


class InvalidResetCodeException(StandardException):
    """Exception when reset code is invalid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=ResponseMessages.VALIDATION_ERROR.value,
            data={
                "errors": "Invalid or expired reset code.",
                "errors_th": "รหัสสำหรับรีเซ็ตรหัสผ่านไม่ถูกต้องหรือหมดอายุแล้ว",
            },
        )


class InvalidOtpCodeException(StandardException):
    """Exception when OTP code is invalid."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=ResponseMessages.VALIDATION_ERROR.value,
            data={
                "errors": "Invalid or expired OTP code.",
                "errors_th": "รหัส OTP ไม่ถูกต้องหรือหมดอายุแล้ว",
            },
        )


class PasswordMismatchException(StandardException):
    """Exception when passwords do not match."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=ResponseMessages.VALIDATION_ERROR.value,
            data={
                "errors": "Passwords do not match.",
                "errors_th": "รหัสผ่านไม่ตรงกัน",
            },
        )


class AccountLockedException(StandardException):
    """Exception when account is locked."""

    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Account is locked. Please contact support.",
                "errors_th": "บัญชีถูกล็อก กรุณาติดต่อฝ่ายสนับสนุน",
            },
        )

from __future__ import annotations

from http import HTTPStatus

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import ResponseMessages


# GENERIC EXCEPTIONS
class AuthenticationException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while processing the request at the authentication module."
            },
        )


class AuthenticationTokenException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while processing the authentication token. Please login again or contact support."
            },
        )


class HashingException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while hashing the password. Please try again."
            },
        )


class RefreshTokenException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An error occurred while processing the refresh token. Please login again or contact support."
            },
        )


# SPECIFIC EXCEPTIONS
class InvalidCredentialsException(StandardException):
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
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid authentication token. the provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "โทเค็นการยืนยันตัวตนไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class ModifiedTokenException(StandardException):
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
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid refresh token. the provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "รีเฟรชโทเค็นไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class RefreshTokenInvalidDeviceException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid refresh token data. the provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "ข้อมูลรีเฟรชโทเค็นไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class AuthenticationInvalidDeviceException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid authentication data. the provided token is not valid or has been revoked. Please login again or contact support.",
                "errors_th": "ข้อมูลการยืนยันตัวตนไม่ถูกต้อง โทเค็นที่ให้มาไม่ถูกต้องหรือถูกเพิกถอนแล้ว กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )


class LogoutInvalidEndpoint(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid endpoint for logout. Please login again or contact support.",
                "errors_th": "ปลายทางสำหรับออกจากระบบไม่ถูกต้อง กรุณาเข้าสู่ระบบใหม่หรือติดต่อฝ่ายสนับสนุน",
            },
        )

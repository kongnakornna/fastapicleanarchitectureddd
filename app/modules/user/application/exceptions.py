"""user application exceptions"""
from __future__ import annotations
from http import HTTPStatus

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import ResponseMessages


class UserException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={"errors": "Unexpected error at user module."},
        )


class UserEmailAlreadyExistsException(StandardException):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            message=ResponseMessages.CONFLICT.value,
            data={"errors": f"User email '{email}' already exists."},
        )


class UsernameAlreadyExistsException(StandardException):
    def __init__(self, username: str) -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            message=ResponseMessages.CONFLICT.value,
            data={"errors": f"Username '{username}' already exists."},
        )


class UserEmailNotFoundException(StandardException):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"User email '{email}' not found."},
        )


class UserIdNotFoundException(StandardException):
    def __init__(self, user_id: int) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"User '{user_id}' not found."},
        )


class UserAlreadyDeletedException(StandardException):
    def __init__(self, user_id: int) -> None:
        super().__init__(
            status_code=HTTPStatus.GONE,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"User '{user_id}' was soft-deleted."},
        )


class CookieManagementException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={"errors": "Unexpected error while managing user cookie."},
        )

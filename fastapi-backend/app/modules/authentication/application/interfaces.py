from __future__ import annotations

from typing import Protocol

from app.modules.authentication.domain.entities import Authentication
from app.modules.user.domain.entities import User


class IAuthenticationRepository(Protocol):
    """Interface for repository (Database operations)."""

    # CREATE
    async def create(self, authentication: Authentication) -> Authentication: ...

    # READ
    async def get_by_user_id_agent_and_device(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_access_token_by_authentication(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_refresh_token_by_authentication(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    # UPDATE
    async def update(self, authentication: Authentication) -> Authentication: ...

    # DELETE
    async def delete(self, authentication: Authentication) -> Authentication: ...


class IAuthenticationCache(Protocol):
    """Interface for cache (Redis operations)."""

    # CREATE
    async def insert_by_access_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None: ...

    async def insert_by_refresh_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None: ...

    # READ
    async def get_by_access_token(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    async def get_by_refresh_token(
        self, authentication: Authentication
    ) -> Authentication | None: ...

    # DELETE
    async def delete_by_access_token(self, authentication: Authentication) -> None: ...

    async def delete_by_refresh_token(self, authentication: Authentication) -> None: ...


class ITokenService(Protocol):
    """Interface for token operations."""

    async def generate(self, authentication: Authentication) -> Authentication: ...

    async def hash_tokens(self, authentication: Authentication) -> Authentication: ...

    async def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool: ...

    def hash_password(self, plain_password: str) -> str: ...

    async def verify_access_token(self, token: str) -> Authentication: ...

    async def verify_refresh_token(self, token: str) -> Authentication: ...


class ISignUpService(Protocol):
    """Interface for sign up operations."""

    async def create_user(self, user: User) -> User: ...


class IEmailService(Protocol):
    """Interface for email operations."""

    async def send_password_reset_email(self, email: str, reset_code: str) -> None: ...

    async def send_otp_sms(self, phone_number: str, otp_code: str) -> None: ...

    async def send_welcome_email(self, email: str, name: str) -> None: ...

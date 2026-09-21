from __future__ import annotations

from app.core.security import (
    generate_tokens,
    hash_password,
    hash_tokens,
    verify_password,
)
from app.modules.authentication.application.interfaces import ITokenService
from app.modules.authentication.domain.entities import Authentication


class TokenService(ITokenService):
    """Implementation of ITokenService."""

    async def generate(self, authentication: Authentication) -> Authentication:
        """Generate JWT tokens."""
        return generate_tokens(authentication)

    async def hash_tokens(self, authentication: Authentication) -> Authentication:
        """Hash tokens."""
        return hash_tokens(authentication)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return verify_password(plain_password, hashed_password)

    def hash_password(self, plain_password: str) -> str:
        """Hash password."""
        return hash_password(plain_password)

    async def verify_access_token(self, token: str) -> Authentication:
        """Verify access token and return Authentication entity."""
        from app.core.security import verify_access_token as _verify

        return _verify(token)

    async def verify_refresh_token(self, token: str) -> Authentication:
        """Verify refresh token and return Authentication entity."""
        from app.core.security import verify_refresh_token as _verify

        return _verify(token)

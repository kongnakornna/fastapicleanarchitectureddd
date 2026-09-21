# Full Code ทุกไฟล์ - Authentication Module

ผมจะเขียน full code ให้ครบทุกไฟล์ตามโครงสร้าง Clean Architecture + DDD ครับ

---

## 1. `domain/enums.py`

```python
from __future__ import annotations

from enum import Enum


class TokenType(str, Enum):
    BEARER = "Bearer"
```

---

## 2. `domain/events.py`

```python
# authentication/domain/events.py - domain event names

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AuthenticationCreated:
    """Event emitted when a new authentication session is created."""

    authentication_id: UUID
    user_id: UUID
    device: str | None
    ip_address: str | None
    occurred_at: datetime


@dataclass(frozen=True)
class AuthenticationRevoked:
    """Event emitted when an authentication session is revoked."""

    authentication_id: UUID
    user_id: UUID
    device: str | None
    occurred_at: datetime


@dataclass(frozen=True)
class TokensRefreshed:
    """Event emitted when tokens are refreshed."""

    authentication_id: UUID
    user_id: UUID
    device: str | None
    occurred_at: datetime


@dataclass(frozen=True)
class SuspiciousActivityDetected:
    """Event emitted when suspicious activity is detected."""

    authentication_id: UUID | None
    user_id: UUID | None
    reason: str
    ip_address: str | None
    occurred_at: datetime
```

---

## 3. `domain/exceptions.py`

```python
from __future__ import annotations

from app.modules.shared.domain.entities import DomainError


class AuthenticationDomainError(DomainError):
    """Domain rule violation for authentication."""

    code = "auth_DOMAIN_ERROR"


class InvalidTokenError(AuthenticationDomainError):
    """Raised when a token is invalid."""

    code = "auth_INVALID_TOKEN"


class TokenExpiredError(AuthenticationDomainError):
    """Raised when a token has expired."""

    code = "auth_TOKEN_EXPIRED"


class TokenNotYetValidError(AuthenticationDomainError):
    """Raised when a token is not yet valid."""

    code = "auth_TOKEN_NOT_YET_VALID"


class TokenRevokedError(AuthenticationDomainError):
    """Raised when a token has been revoked."""

    code = "auth_TOKEN_REVOKED"
```

---

## 4. `domain/value_objects.py`

```python
from __future__ import annotations

from uuid import UUID

from app.modules.shared.domain.entities import DomainError


class BaseClaims:
    """Base class for JWT Claims - immutable."""

    iss: str  # issuer
    sub: UUID  # subject
    aud: str  # audience
    iat: int  # issued at
    nbf: int  # not before
    exp: int  # expiration
    jti: UUID  # JWT ID

    def __setattr__(self, name: str, value) -> None:
        """Block attribute modification after object creation."""
        raise AttributeError(f"{type(self).__name__} is immutable.")

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
    ) -> None:
        object.__setattr__(self, "iss", iss.strip() if iss else iss)
        object.__setattr__(self, "sub", sub)
        object.__setattr__(self, "aud", aud.strip() if aud else aud)
        object.__setattr__(self, "iat", iat)
        object.__setattr__(self, "nbf", nbf)
        object.__setattr__(self, "exp", exp)
        object.__setattr__(self, "jti", jti)

    def _validate_base(self, prefix: str = "Claims") -> None:
        """Validate base claims fields."""
        if not self.iss:
            raise DomainError(f"{prefix} issuer (iss) is required.")

        if not self.sub:
            raise DomainError(f"{prefix} subject (sub) is required.")

        if not self.aud:
            raise DomainError(f"{prefix} audience (aud) is required.")

        if self.iat is None:
            raise DomainError(f"{prefix} issued at (iat) is required.")
        if not isinstance(self.iat, int) or self.iat <= 0:
            raise DomainError(
                f"{prefix} issued at (iat) must be a positive integer Unix timestamp."
            )

        if self.nbf is None:
            raise DomainError(f"{prefix} not before (nbf) is required.")
        if not isinstance(self.nbf, int) or self.nbf <= 0:
            raise DomainError(
                f"{prefix} not before (nbf) must be a positive integer Unix timestamp."
            )
        if self.nbf < self.iat:
            raise DomainError(
                f"{prefix} not before (nbf) cannot be earlier than issued at (iat)."
            )

        if self.exp is None:
            raise DomainError(f"{prefix} expiration (exp) is required.")
        if not isinstance(self.exp, int) or self.exp <= 0:
            raise DomainError(
                f"{prefix} expiration (exp) must be a positive integer Unix timestamp."
            )
        if self.exp <= self.iat:
            raise DomainError(
                f"{prefix} expiration (exp) must be after issued at (iat)."
            )

        if not self.jti:
            raise DomainError(f"{prefix} JWT ID (jti) is required.")

    def _base_to_dict(self) -> dict:
        """Convert to dict."""
        return {
            "iss": self.iss,
            "sub": str(self.sub),
            "aud": self.aud,
            "iat": self.iat,
            "nbf": self.nbf,
            "exp": self.exp,
            "jti": str(self.jti),
        }

    @staticmethod
    def _base_kwargs_from_dict(data: dict) -> dict:
        """Build kwargs from dict."""
        return {
            "iss": data["iss"],
            "sub": UUID(data["sub"]) if isinstance(data["sub"], str) else data["sub"],
            "aud": data["aud"],
            "iat": data["iat"],
            "nbf": data["nbf"],
            "exp": data["exp"],
            "jti": UUID(data["jti"]) if isinstance(data["jti"], str) else data["jti"],
        }


class Claims(BaseClaims):
    """Claims for Access Token."""

    grant_id: str
    scope: str

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
        grant_id: str | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__(iss=iss, sub=sub, aud=aud, iat=iat, nbf=nbf, exp=exp, jti=jti)
        object.__setattr__(self, "grant_id", grant_id)
        object.__setattr__(self, "scope", scope.strip().lower() if scope else scope)
        self._validate()

    def _validate(self) -> None:
        self._validate_base()
        if not self.grant_id:
            raise DomainError("Claims grant_id is required.")
        if not self.scope:
            raise DomainError("Claims scope is required.")

    def to_dict(self) -> dict:
        return {
            **self._base_to_dict(),
            "grant_id": self.grant_id,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Claims:
        return cls(
            **cls._base_kwargs_from_dict(data),
            grant_id=data["grant_id"],
            scope=data["scope"],
        )

    def __str__(self) -> str:
        return (
            f"Claims(iss={self.iss}, sub={self.sub}, jti={self.jti}, "
            f"grant_id={self.grant_id}, scope={self.scope})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Claims):
            return False
        return (
            self.iss == other.iss
            and self.sub == other.sub
            and self.aud == other.aud
            and self.jti == other.jti
            and self.grant_id == other.grant_id
            and self.scope == other.scope
        )

    def __hash__(self) -> int:
        return hash((self.iss, self.sub, self.aud, self.jti, self.grant_id, self.scope))


class RefreshClaims(BaseClaims):
    """Claims for Refresh Token."""

    client_id: str
    grant_id: str
    scope: str

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
        client_id: str | None = None,
        grant_id: str | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__(iss=iss, sub=sub, aud=aud, iat=iat, nbf=nbf, exp=exp, jti=jti)
        object.__setattr__(
            self, "client_id", client_id.strip().lower() if client_id else client_id
        )
        object.__setattr__(self, "grant_id", grant_id.strip() if grant_id else grant_id)
        object.__setattr__(
            self, "scope", " ".join(scope.lower().split()) if scope else scope
        )
        self._validate()

    def _validate(self) -> None:
        self._validate_base("Refresh claims")
        if not self.client_id:
            raise DomainError("Refresh claims client_id is required.")
        if not self.grant_id:
            raise DomainError("Refresh claims grant_id is required.")
        if not self.scope:
            raise DomainError("Refresh claims scope is required.")

    def to_dict(self) -> dict:
        return {
            **self._base_to_dict(),
            "client_id": self.client_id,
            "grant_id": self.grant_id,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> RefreshClaims:
        return cls(
            **cls._base_kwargs_from_dict(data),
            client_id=data["client_id"],
            grant_id=data["grant_id"],
            scope=data["scope"],
        )

    def __str__(self) -> str:
        return (
            f"RefreshClaims(iss={self.iss}, sub={self.sub}, "
            f"jti={self.jti}, client_id={self.client_id}, scope={self.scope})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, RefreshClaims):
            return False
        return (
            self.iss == other.iss
            and self.sub == other.sub
            and self.aud == other.aud
            and self.jti == other.jti
            and self.client_id == other.client_id
            and self.grant_id == other.grant_id
            and self.scope == other.scope
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.iss,
                self.sub,
                self.aud,
                self.jti,
                self.client_id,
                self.grant_id,
                self.scope,
            )
        )
```

---

## 5. `domain/entities.py`

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.modules.authentication.domain.value_objects import Claims, RefreshClaims
from app.modules.shared.domain.enums import Role
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class Authentication:
    """Entity representing a user's login session on a specific device."""

    # === Identity & Attributes ===
    ip_address: str | None = field(default=None, repr=True, compare=True)
    user_agent: str | None = field(default=None, repr=True, compare=True)
    device: str | None = field(default=None, repr=True, compare=True)
    location: str | None = field(default=None, repr=True, compare=False)
    accept_language: str | None = field(default=None, repr=True, compare=False)
    accept_encoding: str | None = field(default=None, repr=True, compare=False)
    origin: str | None = field(default=None, repr=True, compare=False)
    referer: str | None = field(default=None, repr=True, compare=False)

    # === Application Generated Fields ===
    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=False)
    last_updated_at: datetime | None = field(default=None, repr=False, compare=False)
    blacklisted: bool = field(init=False, default=False, repr=False, compare=False)

    # === Foreign Entities ===
    user: User = field(compare=True, repr=True)
    refresh_token: RefreshToken | None = field(default=None, compare=True, repr=True)

    def __post_init__(self):
        self._normalize()

    def _normalize(self):
        self.ip_address = self.ip_address.lower().strip() if self.ip_address else ""
        self.user_agent = self.user_agent.lower().strip() if self.user_agent else ""
        self.accept_language = (
            self.accept_language.lower().strip() if self.accept_language else None
        )
        self.accept_encoding = (
            self.accept_encoding.lower().strip() if self.accept_encoding else None
        )
        self.origin = self.origin.lower().strip() if self.origin else ""
        self.referer = self.referer.lower().strip() if self.referer else None
        self.location = self.location.lower().strip() if self.location else None

    def update_last_updated_at(self, now: datetime) -> None:
        self.last_updated_at = now

    def create_tokens(
        self,
        now: datetime,
        refresh_expires_at: datetime,
        access_expires_at: datetime,
    ) -> Authentication:
        """Create new tokens for a new authentication."""
        self.refresh_token = RefreshToken(
            expires_at=refresh_expires_at,
            access_token=AccessToken(expires_at=access_expires_at),
        )
        self.refresh_token.generate_created_at(now)
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.access_token.generate_created_at(now)
        return self

    def renew_tokens(
        self,
        now: datetime,
        refresh_expires_at: datetime,
        access_expires_at: datetime,
    ) -> Authentication:
        """Renew tokens for an existing authentication."""
        self.update_last_updated_at(now)
        self.refresh_token.expires_at = refresh_expires_at
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.update_previous_hashed_jti()
        self.refresh_token.activate()
        self.refresh_token.access_token.expires_at = access_expires_at
        self.refresh_token.access_token.generate_created_at(now)
        self.refresh_token.access_token.update_previous_hashed_jti()
        self.refresh_token.access_token.activate()
        return self

    def refresh_access_token(
        self, now: datetime, access_expires_at: datetime
    ) -> Authentication:
        """Refresh only the access token."""
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.update_previous_hashed_jti()
        self.refresh_token.access_token.expires_at = access_expires_at
        self.refresh_token.access_token.generate_created_at(now)
        self.refresh_token.access_token.update_previous_hashed_jti()
        return self

    def revoke(self, now: datetime) -> Authentication:
        """Revoke the authentication (logout)."""
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.revoke(now)
        return self


@dataclass(kw_only=True, slots=True)
class RefreshToken:
    """Entity representing a refresh token."""

    token: str | None = field(default=None, repr=False, compare=False)
    hashed_jti: str | None = field(default=None, repr=False, compare=True)
    previous_hashed_jti: str | None = field(default=None, repr=False, compare=True)

    # Application generated fields
    replaced_by_token: UUID | None = field(default=None, repr=False, compare=False)
    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=True)
    updated_at: datetime | None = field(default=None, repr=False, compare=False)
    expires_at: datetime | None = field(default=None, repr=False, compare=False)
    revoked: bool = field(init=False, default=False, repr=False, compare=False)
    revoked_at: datetime | None = field(
        init=False, default=None, repr=False, compare=False
    )
    refresh_claims: RefreshClaims | None = field(
        default=None, repr=False, compare=False
    )

    # Foreign entities
    access_token: AccessToken | None = field(default=None, repr=False, compare=False)

    def revoke(self, now: datetime) -> None:
        """Revoke the refresh token and its associated access token."""
        self.revoked = True
        self.revoked_at = now
        if self.access_token:
            self.access_token.revoke(now)

    def activate(self) -> None:
        """Reactivate the token."""
        self.revoked = False
        self.revoked_at = None

    def generate_created_at(self, dt: datetime) -> None:
        self.created_at = dt

    def generate_updated_at(self, dt: datetime) -> None:
        self.updated_at = dt

    def update_previous_hashed_jti(self) -> None:
        """Keep previous hashed_jti for token rotation."""
        self.previous_hashed_jti = self.hashed_jti

    def set_claims(
        self,
        iss: str,
        sub: UUID,
        aud: str,
        jti: UUID,
        client_id: str,
        grant_id: str,
        scope: str,
    ) -> None:
        """Build claims for the refresh token."""
        self.refresh_claims = RefreshClaims(
            iss=iss,
            sub=sub,
            aud=aud,
            iat=int(self.updated_at.timestamp()),
            nbf=int(self.updated_at.timestamp()),
            exp=int(self.expires_at.timestamp()),
            jti=jti,
            client_id=client_id,
            grant_id=grant_id,
            scope=scope,
        )


@dataclass(kw_only=True, slots=True)
class AccessToken:
    """Entity representing an access token."""

    token: str | None = field(default=None, repr=False, compare=False)
    hashed_jti: str | None = field(default=None, repr=False, compare=True)
    previous_hashed_jti: str | None = field(default=None, repr=False, compare=True)
    permission: Role = field(default=Role.USER, repr=False, compare=False)

    # Application generated fields
    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=True)
    expires_at: datetime | None = field(default=None, repr=False, compare=False)
    claims: Claims | None = field(default=None, repr=False, compare=False)
    revoked: bool = field(init=False, default=False, repr=False, compare=False)
    revoked_at: datetime | None = field(
        init=False, default=None, repr=False, compare=False
    )

    def revoke(self, now: datetime) -> None:
        self.revoked = True
        self.revoked_at = now

    def activate(self) -> None:
        self.revoked = False
        self.revoked_at = None

    def generate_created_at(self, dt: datetime) -> None:
        self.created_at = dt

    def update_previous_hashed_jti(self) -> None:
        self.previous_hashed_jti = self.hashed_jti

    def set_claims(
        self, iss: str, sub: UUID, aud: str, jti: UUID, grant_id: str, scope: str
    ) -> None:
        """Build claims for the access token."""
        self.claims = Claims(
            iss=iss,
            sub=sub,
            aud=aud,
            iat=int(self.created_at.timestamp()),
            nbf=int(self.created_at.timestamp()),
            exp=int(self.expires_at.timestamp()),
            jti=jti,
            grant_id=grant_id,
            scope=scope,
        )
```

---

## 6. `application/interfaces.py`

```python
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
```

---

## 7. `application/exceptions.py`

```python
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
                "errors": "An unexpected error occurred while processing the request at the authentication module."
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
```

---

## 8. `application/mappers.py`

```python
from __future__ import annotations

import json
from datetime import date, datetime
from uuid import UUID

from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.authentication.domain.entities import (
    AccessToken,
    Authentication,
    RefreshToken,
)
from app.modules.authentication.domain.value_objects import Claims, RefreshClaims
from app.modules.authentication.infrastructure.models import (
    AccessTokenModel,
    AuthenticationModel,
    RefreshTokenModel,
)
from app.modules.authentication.presentation.schemas import (
    ForgotPasswordResponse,
    LockScreenResponse,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    ResetPasswordResponse,
    SignUpResponse,
    TwoStepCodeResponse,
    TwoStepVerificationResponse,
    UserInfo,
)
from app.modules.shared.application.utils import BRASILIA_TZ, resolve_client_ip
from app.modules.shared.domain.enums import Role
from app.modules.shared.domain.value_objects import Name
from app.modules.user.application.mappers import (
    model_entity_mapper as user_model_entity_mapper,
)
from app.modules.user.domain.entities import User
from app.modules.user.domain.enums import Gender


# ============================================================================
# ENTITY / DTOS
# ============================================================================
def login_entity_mapper(
    authentication: OAuth2PasswordRequestForm,
    request: Request,
) -> Authentication:
    """Transform HTTP request → Authentication entity."""
    return Authentication(
        user=User(email=authentication.username, password=authentication.password),
        ip_address=resolve_client_ip(
            x_forwarded_for=request.headers.get("x-forwarded-for"),
            x_real_ip=request.headers.get("x-real-ip"),
            peer_host=request.client.host if request.client else None,
        ),
        user_agent=request.headers.get("user-agent"),
        device=getattr(request.state, "device_id", None),
        accept_language=request.headers.get("accept-language"),
        accept_encoding=request.headers.get("accept_encoding"),
        origin=request.headers.get("origin"),
        referer=request.headers.get("referer"),
        location=getattr(request.state, "location", None),
        refresh_token=RefreshToken(access_token=AccessToken()),
    )


def entity_login_mapper(_authentication: Authentication) -> LoginResponse:
    """Transform Authentication entity → LoginResponse."""
    user = _authentication.user

    user_info = UserInfo(
        first_name=user.name.first_name if user.name else "",
        last_name=user.name.last_name if user.name else "",
        preferred_name=user.name.preferred_name if user.name else "",
        gender=user.gender.value if user.gender else "other",
        birthdate=user.birthdate if user.birthdate else date(1990, 1, 1),
        email=str(user.email) if user.email else "",
        phone=str(user.phone) if user.phone else None,
        role=user.role if user.role else Role.USER,
        created_at=user.created_at.isoformat() if user.created_at else "",
    )

    return LoginResponse(
        access_token=_authentication.refresh_token.access_token.token,
        refresh_token=_authentication.refresh_token.token,
        info=user_info,
    )


def refresh_entity_mapper(authentication: Authentication) -> Authentication:
    return authentication


def entity_refresh_mapper(_authentication: Authentication) -> RefreshResponse:
    return RefreshResponse()


def logout_entity_mapper(authentication: Authentication) -> Authentication:
    return authentication


def entity_logout_mapper(_authentication: Authentication) -> LogoutResponse:
    return LogoutResponse()


def entity_sign_up_mapper(_user: User) -> SignUpResponse:
    return SignUpResponse()


def entity_forgot_password_mapper(_user: User | None) -> ForgotPasswordResponse:
    return ForgotPasswordResponse()


def entity_reset_password_mapper(_user: User) -> ResetPasswordResponse:
    return ResetPasswordResponse()


def entity_lock_screen_mapper(_user: User) -> LockScreenResponse:
    return LockScreenResponse()


def entity_two_step_verification_mapper(
    _user: User,
) -> TwoStepVerificationResponse:
    return TwoStepVerificationResponse()


def entity_two_step_code_mapper(
    _authentication: Authentication,
) -> TwoStepCodeResponse:
    return TwoStepCodeResponse(
        access_token=_authentication.refresh_token.access_token.token,
        refresh_token=_authentication.refresh_token.token,
    )


def access_token_entity_mapper(claims: dict) -> Authentication:
    """Transform JWT claims → Authentication entity (for access token)."""
    access = AccessToken(
        claims=Claims.from_dict(claims),
        permission=Role(claims["scope"]),
        created_at=datetime.fromtimestamp(claims["iat"], tz=BRASILIA_TZ),
        expires_at=datetime.fromtimestamp(claims["exp"], tz=BRASILIA_TZ),
    )

    return Authentication(
        user=User(
            id=UUID(claims["sub"]) if isinstance(claims["sub"], str) else claims["sub"],
            role=Role(claims["scope"]),
            email=claims["grant_id"],
        ),
        refresh_token=RefreshToken(access_token=access),
    )


def refresh_token_entity_mapper(claims: dict) -> Authentication:
    """Transform JWT claims → Authentication entity (for refresh token)."""
    access = AccessToken(permission=Role(claims["scope"]))

    refresh = RefreshToken(
        access_token=access,
        refresh_claims=RefreshClaims.from_dict(claims),
        updated_at=datetime.fromtimestamp(claims["iat"], tz=BRASILIA_TZ),
        expires_at=datetime.fromtimestamp(claims["exp"], tz=BRASILIA_TZ),
    )

    return Authentication(
        user=User(
            id=UUID(claims["sub"]) if isinstance(claims["sub"], str) else claims["sub"],
            role=Role(claims["scope"]),
            email=claims["grant_id"],
        ),
        refresh_token=refresh,
    )


# ============================================================================
# ENTITY / MODELS
# ============================================================================
def _access_token_model_to_entity(model: AccessTokenModel) -> AccessToken:
    return AccessToken(
        id=model.id,
        hashed_jti=model.hashed_jti,
        previous_hashed_jti=model.previous_hashed_jti,
        created_at=model.created_at,
        expires_at=model.expires_at,
        permission=model.permission,
    )


def _refresh_token_model_to_entity(
    model: RefreshTokenModel,
    access_token: AccessToken | None,
) -> RefreshToken:
    refresh = RefreshToken(
        id=model.id,
        hashed_jti=model.hashed_jti,
        previous_hashed_jti=model.previous_hashed_jti,
        created_at=model.created_at,
        updated_at=model.updated_at,
        expires_at=model.expires_at,
        access_token=access_token,
    )
    refresh.revoked = model.revoked
    refresh.revoked_at = model.revoked_at
    return refresh


def _authentication_model_to_entity(model: AuthenticationModel) -> Authentication:
    mapped_user = user_model_entity_mapper(model.user) if model.user else None

    access_token = None
    if model.refresh_token and model.refresh_token.access_token:
        access_token = _access_token_model_to_entity(model.refresh_token.access_token)

    refresh_token = None
    if model.refresh_token:
        refresh_token = _refresh_token_model_to_entity(
            model.refresh_token, access_token
        )

    authentication = Authentication(
        id=model.id,
        ip_address=model.ip_address,
        user_agent=model.user_agent,
        device=model.device,
        accept_language=model.accept_language,
        accept_encoding=model.accept_encoding,
        origin=model.origin,
        referer=model.referrer,
        location=model.location,
        created_at=model.created_at,
        last_updated_at=model.last_updated_at,
        user=mapped_user if mapped_user else User(),
        refresh_token=refresh_token,
    )
    authentication.blacklisted = model.blacklisted
    return authentication


def _access_token_entity_to_model(entity: AccessToken) -> AccessTokenModel:
    return AccessTokenModel(
        id=entity.id,
        hashed_jti=entity.hashed_jti,
        previous_hashed_jti=entity.previous_hashed_jti,
        created_at=entity.created_at
        if entity.created_at
        else datetime.now(tz=BRASILIA_TZ),
        expires_at=entity.expires_at
        if entity.expires_at
        else datetime.now(tz=BRASILIA_TZ),
        permission=entity.permission,
    )


def _refresh_token_entity_to_model(entity: RefreshToken) -> RefreshTokenModel:
    access_token = (
        _access_token_entity_to_model(entity.access_token)
        if entity.access_token
        else None
    )
    return RefreshTokenModel(
        id=entity.id,
        hashed_jti=entity.hashed_jti if entity.hashed_jti else "",
        previous_hashed_jti=entity.previous_hashed_jti,
        created_at=entity.created_at
        if entity.created_at
        else datetime.now(tz=BRASILIA_TZ),
        updated_at=entity.updated_at
        if entity.updated_at
        else datetime.now(tz=BRASILIA_TZ),
        expires_at=entity.expires_at
        if entity.expires_at
        else datetime.now(tz=BRASILIA_TZ),
        revoked=entity.revoked,
        revoked_at=entity.revoked_at,
        access_token=access_token,
    )


def _authentication_entity_to_model(entity: Authentication) -> AuthenticationModel:
    refresh_token = (
        _refresh_token_entity_to_model(entity.refresh_token)
        if entity.refresh_token
        else None
    )
    model = AuthenticationModel(
        id=entity.id,
        user_id=entity.user.id,
        ip_address=entity.ip_address if entity.ip_address else "",
        user_agent=entity.user_agent if entity.user_agent else "",
        device=entity.device if entity.device else "",
        accept_language=entity.accept_language,
        accept_encoding=entity.accept_encoding,
        origin=entity.origin if entity.origin else "",
        referrer=entity.referer,
        location=entity.location,
        created_at=entity.created_at
        if entity.created_at
        else datetime.now(tz=BRASILIA_TZ),
        last_updated_at=entity.last_updated_at
        if entity.last_updated_at
        else datetime.now(tz=BRASILIA_TZ),
        blacklisted=entity.blacklisted,
    )
    model.refresh_token = refresh_token
    return model


def model_entity_mapper(model: AuthenticationModel) -> Authentication:
    return _authentication_model_to_entity(model)


def entity_model_mapper(entity: Authentication) -> AuthenticationModel:
    return _authentication_entity_to_model(entity)


def sync_entity_from_model(
    entity: Authentication, model: AuthenticationModel
) -> Authentication:
    """Sync database-generated values back to the entity."""
    entity.id = model.id
    entity.created_at = model.created_at
    entity.last_updated_at = model.last_updated_at

    if entity.refresh_token and model.refresh_token:
        entity.refresh_token.id = model.refresh_token.id
        entity.refresh_token.created_at = model.refresh_token.created_at
        entity.refresh_token.updated_at = model.refresh_token.updated_at

        if entity.refresh_token.access_token and model.refresh_token.access_token:
            entity.refresh_token.access_token.id = model.refresh_token.access_token.id
            entity.refresh_token.access_token.created_at = (
                model.refresh_token.access_token.created_at
            )

    return entity


# ============================================================================
# ENTITY / CACHE
# ============================================================================
def _iso(value: datetime | date | None) -> str | None:
    return value.isoformat() if value else None


def _user_entity_to_cache(entity: User) -> dict:
    return {
        "id": str(entity.id) if entity.id else None,
        "first_name": entity.name.first_name if entity.name else None,
        "last_name": entity.name.last_name if entity.name else None,
        "preferred_name": entity.name.preferred_name if entity.name else None,
        "gender": entity.gender.value if entity.gender else None,
        "birthdate": _iso(entity.birthdate),
        "email": str(entity.email) if entity.email else None,
        "phone": str(entity.phone) if entity.phone else None,
        "role": entity.role.value if entity.role else None,
        "is_active": entity.is_active,
        "created_at": _iso(entity.created_at),
        "updated_at": _iso(entity.updated_at),
    }


def _access_token_entity_to_cache(entity: AccessToken) -> dict:
    # The raw JWT ('token') and the transient 'claims' are never cached.
    return {
        "id": str(entity.id) if entity.id else None,
        "hashed_jti": entity.hashed_jti,
        "previous_hashed_jti": entity.previous_hashed_jti,
        "permission": entity.permission.value if entity.permission else None,
        "created_at": _iso(entity.created_at),
        "expires_at": _iso(entity.expires_at),
        "revoked": entity.revoked,
        "revoked_at": _iso(entity.revoked_at),
    }


def _refresh_token_entity_to_cache(entity: RefreshToken) -> dict:
    return {
        "id": str(entity.id) if entity.id else None,
        "hashed_jti": entity.hashed_jti,
        "previous_hashed_jti": entity.previous_hashed_jti,
        "created_at": _iso(entity.created_at),
        "updated_at": _iso(entity.updated_at),
        "expires_at": _iso(entity.expires_at),
        "revoked": entity.revoked,
        "revoked_at": _iso(entity.revoked_at),
        "access_token": _access_token_entity_to_cache(entity.access_token)
        if entity.access_token
        else None,
    }


def entity_cache_mapper(authentication: Authentication) -> str:
    """Transform Authentication entity → JSON string for cache."""
    return json.dumps(
        {
            "id": str(authentication.id) if authentication.id else None,
            "ip_address": authentication.ip_address,
            "user_agent": authentication.user_agent,
            "device": authentication.device,
            "location": authentication.location,
            "accept_language": authentication.accept_language,
            "accept_encoding": authentication.accept_encoding,
            "origin": authentication.origin,
            "referer": authentication.referer,
            "blacklisted": authentication.blacklisted,
            "created_at": _iso(authentication.created_at),
            "last_updated_at": _iso(authentication.last_updated_at),
            "user": _user_entity_to_cache(authentication.user)
            if authentication.user
            else None,
            "refresh_token": _refresh_token_entity_to_cache(
                authentication.refresh_token
            )
            if authentication.refresh_token
            else None,
        }
    )


def _user_cache_to_entity(data: dict) -> User:
    user = User(
        id=UUID(data["id"]) if data["id"] else None,
        name=Name(
            first_name=data["first_name"],
            last_name=data["last_name"],
            preferred_name=data["preferred_name"],
        )
        if data["first_name"]
        else None,
        gender=Gender(data["gender"]) if data["gender"] else None,
        birthdate=date.fromisoformat(data["birthdate"]) if data["birthdate"] else None,
        email=data["email"],
        phone=data["phone"],
        role=Role(data["role"]) if data["role"] else Role.USER,
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        updated_at=datetime.fromisoformat(data["updated_at"])
        if data["updated_at"]
        else None,
    )
    user.is_active = data["is_active"]
    return user


def _access_token_cache_to_entity(data: dict) -> AccessToken:
    access = AccessToken(
        id=UUID(data["id"]) if data["id"] else None,
        hashed_jti=data["hashed_jti"],
        previous_hashed_jti=data["previous_hashed_jti"],
        permission=Role(data["permission"]) if data["permission"] else Role.USER,
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        expires_at=datetime.fromisoformat(data["expires_at"])
        if data["expires_at"]
        else None,
    )
    access.revoked = data["revoked"]
    access.revoked_at = (
        datetime.fromisoformat(data["revoked_at"]) if data["revoked_at"] else None
    )
    return access


def _refresh_token_cache_to_entity(data: dict) -> RefreshToken:
    refresh = RefreshToken(
        id=UUID(data["id"]) if data["id"] else None,
        hashed_jti=data["hashed_jti"],
        previous_hashed_jti=data["previous_hashed_jti"],
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        updated_at=datetime.fromisoformat(data["updated_at"])
        if data["updated_at"]
        else None,
        expires_at=datetime.fromisoformat(data["expires_at"])
        if data["expires_at"]
        else None,
        access_token=_access_token_cache_to_entity(data["access_token"])
        if data["access_token"]
        else None,
    )
    refresh.revoked = data["revoked"]
    refresh.revoked_at = (
        datetime.fromisoformat(data["revoked_at"]) if data["revoked_at"] else None
    )
    return refresh


def cache_entity_mapper(raw: str) -> Authentication:
    """Transform JSON string from cache → Authentication entity."""
    data = json.loads(raw)

    authentication = Authentication(
        id=UUID(data["id"]) if data["id"] else None,
        ip_address=data["ip_address"],
        user_agent=data["user_agent"],
        device=data["device"],
        location=data["location"],
        accept_language=data["accept_language"],
        accept_encoding=data["accept_encoding"],
        origin=data["origin"],
        referer=data["referer"],
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        last_updated_at=datetime.fromisoformat(data["last_updated_at"])
        if data["last_updated_at"]
        else None,
        user=_user_cache_to_entity(data["user"]) if data["user"] else User(),
        refresh_token=_refresh_token_cache_to_entity(data["refresh_token"])
        if data["refresh_token"]
        else None,
    )
    authentication.blacklisted = data["blacklisted"]
    return authentication
```

---

## 9. `application/use_cases.py`

```python
from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID, uuid4

from loguru import logger

from app.core.settings import settings
from app.modules.authentication.application.exceptions import (
    AuthenticationException,
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    InvalidOtpCodeException,
    InvalidResetCodeException,
    PasswordMismatchException,
)
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
    ITokenService,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.entities import DomainError
from app.modules.user.domain.entities import User


class AuthenticationUseCases:
    """
    Use cases for Authentication.

    Dependencies are injected via constructor (Dependency Injection):
    - cache: IAuthenticationCache
    - repository: IAuthenticationRepository
    - shared_service: SharedUseCases
    - token_service: ITokenService
    """

    def __init__(
        self,
        cache: IAuthenticationCache,
        repository: IAuthenticationRepository,
        shared_service: SharedUseCases,
        token_service: ITokenService,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.shared_service = shared_service
        self.token_service = token_service
        self.shared_service.disable_exceptions()

    # ========================================================================
    # CREATE: LOGIN
    # ========================================================================
    async def login(self, authentication: Authentication) -> Authentication:
        """
        Login use case.

        Steps:
        1. Find user by email
        2. Verify password
        3. Find existing authentication (user + agent + device)
        4. If exists → renew tokens / else → create tokens
        5. Generate JWT tokens
        6. Hash tokens
        7. Persist to database
        """
        try:
            logger.debug(
                f"Initializing user login use case for user: {authentication.user.censored_email} in device: {authentication.device}."
            )

            # 1. Find user
            db_user: User | None = await self.shared_service.get_user_by_email(
                authentication.user
            )

            if not db_user:
                logger.info(
                    f"User with email {authentication.user.censored_email} not found, raising exception."
                )
                raise InvalidCredentialsException()

            # 2. Verify password
            if not await self.token_service.verify_password(
                authentication.user.password, db_user.hashed_password
            ):
                logger.info(
                    f"Invalid password for user {authentication.user.id}, raising exception."
                )
                raise InvalidCredentialsException()

            authentication.user = db_user

            # 3. Find existing authentication
            authentication_from_db = (
                await self.repository.get_by_user_id_agent_and_device(authentication)
            )

            now = datetime.now(BRASILIA_TZ)
            refresh_expires_at = now + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            # 4. Renew or create tokens
            if authentication_from_db:
                logger.debug(
                    f"Existing authentication found for user: {authentication.user.id}. Renewing tokens."
                )

                await self.cache.delete_by_access_token(authentication_from_db)
                await self.cache.delete_by_refresh_token(authentication_from_db)

                authentication = authentication_from_db.renew_tokens(
                    now, refresh_expires_at, access_expires_at
                )
            else:
                logger.debug(
                    f"No existing authentication found for user: {authentication.user.id}. Creating new authentication."
                )
                authentication = authentication.create_tokens(
                    now, refresh_expires_at, access_expires_at
                )

            # 5-6. Generate & Hash tokens
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            # 7. Persist
            if authentication_from_db:
                await self.repository.update(authentication)
            else:
                await self.repository.create(authentication)

            logger.debug(
                f"User {authentication.user.id} logged in successfully in device: {authentication.device}."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the login use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # SIGN UP
    # ========================================================================
    async def sign_up(self, user: User) -> User:
        """
        Sign up use case.

        Steps:
        1. Check if email exists
        2. Hash password
        3. Create new user
        4. Send verification email (TODO)
        """
        try:
            logger.debug(
                f"Initializing sign up use case for user: {user.censored_email}."
            )

            # 1. Check email
            existing_user = await self.shared_service.get_user_by_email(user)
            if existing_user:
                logger.info(f"User with email {user.censored_email} already exists.")
                raise EmailAlreadyExistsException(email=str(user.email))

            # 2. Hash password
            user.hashed_password = self.token_service.hash_password(user.password)

            # 3. Create user
            user = await self.shared_service.create_user(user)

            # 4. Send welcome email (TODO)
            logger.debug(f"Welcome email sent to {user.censored_email}.")

            logger.debug(
                f"User {user.censored_email} signed up successfully with id {user.id}."
            )
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the sign up use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # UPDATE: REFRESH
    # ========================================================================
    async def refresh(self, authentication: Authentication) -> Authentication:
        """
        Refresh tokens use case.

        Steps:
        1. Delete old cache
        2. Refresh access token
        3. Generate & hash new tokens
        4. Update database
        """
        try:
            logger.debug(
                f"Initializing user refresh tokens use case for user: {authentication.user.id}."
            )

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            now = datetime.now(BRASILIA_TZ)
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            authentication = authentication.refresh_access_token(now, access_expires_at)
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            await self.repository.update(authentication)

            logger.debug(
                f"User {authentication.user.id} refreshed tokens successfully."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the refresh tokens use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # DELETE: LOGOUT
    # ========================================================================
    async def logout(self, authentication: Authentication) -> Authentication:
        """
        Logout use case.

        Steps:
        1. Revoke tokens
        2. Persist revocation to database
        3. Delete cache
        """
        try:
            logger.debug(
                f"Initializing user logout use case for user: {authentication.user.id}."
            )

            authentication.revoke(datetime.now(BRASILIA_TZ))
            await self.repository.delete(authentication)

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            logger.debug(f"User {authentication.user.id} logged out successfully.")
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the logout use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # FORGOT PASSWORD
    # ========================================================================
    async def forgot_password(self, email: str) -> None:
        """
        Forgot password use case.

        Steps:
        1. Check if user exists
        2. Generate reset code
        3. Send email (TODO)
        """
        try:
            logger.debug(f"Initializing forgot password use case for email: {email}.")

            user = await self.shared_service.get_user_by_email(User(email=email))

            if not user:
                # Don't reveal whether email exists (security)
                logger.info(
                    f"User with email {email} not found, but returning success."
                )
                return

            # Generate reset code (TODO: implement)
            reset_code = str(uuid4())[:6].upper()

            # Send email (TODO: implement)
            logger.debug(f"Reset code sent to {email}.")

            logger.debug(f"Forgot password processed for {email}.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the forgot password use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # RESET PASSWORD
    # ========================================================================
    async def reset_password(
        self, code: str, password: str, confirm_password: str
    ) -> None:
        """
        Reset password use case.

        Steps:
        1. Validate reset code
        2. Validate password match
        3. Hash new password
        4. Update user
        """
        try:
            logger.debug("Initializing reset password use case.")

            if password != confirm_password:
                raise PasswordMismatchException()

            # Validate code (TODO: implement)
            # user = await self.shared_service.get_user_by_reset_code(code)
            # if not user:
            #     raise InvalidResetCodeException()

            # Update password (TODO: implement)
            logger.debug("Reset password processed successfully.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the reset password use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # LOCK SCREEN
    # ========================================================================
    async def lock_screen(self, authentication: Authentication, password: str) -> None:
        """
        Lock screen use case.

        Verify password before unlocking.
        """
        try:
            logger.debug(
                f"Initializing lock screen use case for user: {authentication.user.id}."
            )

            if not await self.token_service.verify_password(
                password, authentication.user.hashed_password
            ):
                raise InvalidCredentialsException()

            logger.debug(f"Lock screen unlocked for user {authentication.user.id}.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the lock screen use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # TWO-STEP VERIFICATION
    # ========================================================================
    async def two_step_verification(
        self, authentication: Authentication, country_code: str, phone_number: str
    ) -> None:
        """
        Two-step verification use case.

        Steps:
        1. Validate phone number
        2. Send OTP (TODO)
        """
        try:
            logger.debug(
                f"Initializing two-step verification for user: {authentication.user.id}."
            )

            full_phone = f"{country_code}{phone_number}"

            # Send OTP (TODO: implement)
            otp_code = str(uuid4())[:6]
            logger.debug(f"OTP {otp_code} sent to {full_phone}.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the two-step verification use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # TWO-STEP CODE
    # ========================================================================
    async def two_step_code(
        self, authentication: Authentication, code: str, dont_ask_again: bool
    ) -> Authentication:
        """
        Two-step code use case.

        Steps:
        1. Validate OTP code
        2. If valid, create tokens
        3. If dont_ask_again, remember device
        """
        try:
            logger.debug(
                f"Initializing two-step code verification for user: {authentication.user.id}."
            )

            # Validate OTP (TODO: implement)
            if code != "123456":  # Placeholder
                raise InvalidOtpCodeException()

            # Create tokens
            now = datetime.now(BRASILIA_TZ)
            refresh_expires_at = now + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            authentication = authentication.create_tokens(
                now, refresh_expires_at, access_expires_at
            )
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            await self.repository.create(authentication)

            # If dont_ask_again, remember device (TODO: implement)

            logger.debug(f"Two-step code verified for user {authentication.user.id}.")
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the two-step code use case."
            )
            raise AuthenticationException()
```

---

## 10. `infrastructure/models.py`

```python
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    UUID as SQUID,
)
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.enums import Role
from app.modules.shared.infrastructure.models import Base

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class AuthenticationModel(Base):
    """SQLAlchemy model for the authentications table."""

    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_authentications"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "user_agent",
            "device",
            name="uq_authentications_user_id_user_agent_device",
        ),
        Index(
            "ix_authentications_user_id_user_agent_device",
            "user_id",
            "user_agent",
            "device",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the authentication",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
            ondelete="CASCADE",
        ),
        name="user_id",
        comment="Identifier of the user who owns the authentication",
        nullable=False,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        name="ip_address",
        comment="IP address used when the authentication was created",
        nullable=False,
    )

    device: Mapped[str] = mapped_column(
        String(255),
        name="device",
        comment="Human readable device name",
        nullable=False,
    )

    user_agent: Mapped[str] = mapped_column(
        Text,
        name="user_agent",
        comment="User agent string of the client",
        nullable=False,
    )

    accept_language: Mapped[str | None] = mapped_column(
        String(255),
        name="accept_language",
        comment="Accept-Language header value of the client",
        nullable=True,
        default=None,
    )

    accept_encoding: Mapped[str | None] = mapped_column(
        String(255),
        name="accept_encoding",
        comment="accept_encoding header value of the client",
        nullable=True,
        default=None,
    )

    origin: Mapped[str] = mapped_column(
        String(255),
        name="origin",
        comment="Origin header value of the client",
        nullable=False,
    )

    referrer: Mapped[str | None] = mapped_column(
        String(255),
        name="referrer",
        comment="Referrer header value of the client",
        nullable=True,
        default=None,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        name="location",
        comment="Approximate geographic location of the client",
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the authentication was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="last_update_at",
        comment="Last time the authentication was updated",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    blacklisted: Mapped[bool] = mapped_column(
        Boolean,
        name="blacklisted",
        comment="Indicates whether the authentication is blacklisted",
        nullable=False,
        default=False,
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="authentications",
        lazy="noload",
    )

    refresh_token: Mapped["RefreshTokenModel | None"] = relationship(
        back_populates="authentication",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="noload",
    )


class RefreshTokenModel(Base):
    """SQLAlchemy model for the refresh_tokens table."""

    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_refresh_tokens"
    __table_args__ = (
        UniqueConstraint(
            "authentication_id",
            name="uq_refresh_tokens_authentication_id",
        ),
        Index(
            "ix_refresh_tokens_hashed_jti_revoked",
            "hashed_jti",
            "revoked",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the refresh token",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    authentication_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_authentications.id",
            ondelete="CASCADE",
        ),
        name="authentication_id",
        comment="Authentication associated with this refresh token",
        nullable=False,
    )

    hashed_jti: Mapped[str] = mapped_column(
        Text,
        name="hashed_jti",
        comment="Hashed JTI (JWT ID) value",
        nullable=False,
        unique=True,
    )

    previous_hashed_jti: Mapped[str | None] = mapped_column(
        Text,
        name="previous_hashed_jti",
        comment="Hashed JTI (JWT ID) value of the previous refresh token",
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the refresh token was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="updated_at",
        comment="Timestamp when the record was last updated",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        onupdate=func.now(),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="expires_at",
        comment="Expiration timestamp of the refresh token",
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        name="revoked",
        comment="Indicates whether the refresh token was revoked",
        nullable=False,
        default=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        name="revoked_at",
        comment="Timestamp when the refresh token was revoked",
        nullable=True,
        default=None,
    )

    authentication: Mapped["AuthenticationModel"] = relationship(
        back_populates="refresh_token",
        uselist=False,
        lazy="noload",
    )

    access_token: Mapped["AccessTokenModel | None"] = relationship(
        back_populates="refresh_token",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="noload",
    )


class AccessTokenModel(Base):
    """SQLAlchemy model for the access_tokens table."""

    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_access_tokens"
    __table_args__ = (
        UniqueConstraint(
            "refresh_id",
            name="uq_access_tokens_refresh_id",
        ),
        Index(
            "ix_access_tokens_hashed_jti_revoked",
            "hashed_jti",
            "revoked",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the access token",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    refresh_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_refresh_tokens.id",
            ondelete="CASCADE",
        ),
        name="refresh_id",
        comment="Refresh token associated with this access token",
        nullable=False,
    )

    hashed_jti: Mapped[str] = mapped_column(
        Text,
        name="hashed_jti",
        comment="Hashed JTI (JWT ID) value",
        nullable=False,
        unique=True,
    )

    previous_hashed_jti: Mapped[str | None] = mapped_column(
        Text,
        name="previous_hashed_jti",
        comment="Hashed JTI (JWT ID) value of the previous access token",
        nullable=True,
        default=None,
        unique=True,
    )

    permission: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="role_enum"),
        name="permission",
        comment="Permission level associated with the access token",
        nullable=False,
        default=Role.USER,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the access token was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="expires_at",
        comment="Expiration timestamp of the access token",
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        name="revoked",
        comment="Indicates whether the access token was revoked",
        nullable=False,
        default=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        name="revoked_at",
        comment="Timestamp when the access token was revoked",
        nullable=True,
        default=None,
    )

    refresh_token: Mapped["RefreshTokenModel"] = relationship(
        back_populates="access_token",
        uselist=False,
        lazy="noload",
    )
```

---

## 11. `infrastructure/repositories.py`

```python
from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.authentication.application.exceptions import AuthenticationException
from app.modules.authentication.application.interfaces import IAuthenticationRepository
from app.modules.authentication.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
    sync_entity_from_model,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.authentication.infrastructure.models import (
    AccessTokenModel,
    AuthenticationModel,
    RefreshTokenModel,
)
from app.modules.shared.application.exceptions import StandardException


class PostgresAuthenticationRepository(IAuthenticationRepository):
    """Implementation of IAuthenticationRepository using PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ========================================================================
    # CREATE
    # ========================================================================
    async def create(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Creating authentication for user {authentication.user.id} with device {authentication.device} in database."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            self.session.add(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, db_authentication
            )

            logger.info(
                f"Authentication created successfully for user {authentication.user.id} with device {authentication.device} in database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create authentication repository."
            )
            raise AuthenticationException()

    # ========================================================================
    # READ
    # ========================================================================
    async def get_by_user_id_agent_and_device(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by user id, agent and device for user {authentication.user.id}."
            )

            statement = (
                select(AuthenticationModel)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(
                    AuthenticationModel.user_id == authentication.user.id,
                    AuthenticationModel.user_agent == authentication.user_agent,
                    AuthenticationModel.device == authentication.device,
                    AuthenticationModel.blacklisted.is_(False),
                )
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for user {authentication.user.id} with device {authentication.device}."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for user {authentication.user.id}. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by user agent and device repository."
            )
            raise AuthenticationException()

    async def get_access_token_by_authentication(
        self,
        authentication: Authentication,
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by access token hashed_jti {authentication.refresh_token.access_token.hashed_jti}."
            )

            conditions = [
                AccessTokenModel.hashed_jti
                == authentication.refresh_token.access_token.hashed_jti,
                AuthenticationModel.user_agent == authentication.user_agent,
                AuthenticationModel.user_id == authentication.user.id,
                AccessTokenModel.revoked.is_(False),
                RefreshTokenModel.revoked.is_(False),
                AuthenticationModel.blacklisted.is_(False),
            ]

            if authentication.device is not None:
                conditions.append(AuthenticationModel.device == authentication.device)

            statement = (
                select(AuthenticationModel)
                .join(AuthenticationModel.refresh_token)
                .join(RefreshTokenModel.access_token)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(*conditions)
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for access token hashed_jti {authentication.refresh_token.access_token.hashed_jti}."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for access token. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get access token by hashed_jti repository."
            )
            raise AuthenticationException()

    async def get_refresh_token_by_authentication(
        self,
        authentication: Authentication,
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by refresh token hashed_jti {authentication.refresh_token.hashed_jti}."
            )

            conditions = [
                RefreshTokenModel.hashed_jti == authentication.refresh_token.hashed_jti,
                AuthenticationModel.user_agent == authentication.user_agent,
                AuthenticationModel.user_id == authentication.user.id,
                RefreshTokenModel.revoked.is_(False),
                AuthenticationModel.blacklisted.is_(False),
            ]

            if authentication.device is not None:
                conditions.append(AuthenticationModel.device == authentication.device)

            statement = (
                select(AuthenticationModel)
                .join(AuthenticationModel.refresh_token)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(*conditions)
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for refresh token hashed_jti {authentication.refresh_token.hashed_jti}."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for refresh token. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get refresh token by hashed_jti repository."
            )
            raise AuthenticationException()

    # ========================================================================
    # UPDATE
    # ========================================================================
    async def update(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Updating authentication {authentication.id} for user {authentication.user.id}."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            merged: AuthenticationModel = await self.session.merge(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, merged
            )

            logger.info(f"Authentication {authentication.id} updated successfully.")
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the update authentication repository."
            )
            raise AuthenticationException()

    # ========================================================================
    # DELETE
    # ========================================================================
    async def delete(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Persisting revoked authentication {authentication.id} for user {authentication.user.id}."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            merged: AuthenticationModel = await self.session.merge(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, merged
            )

            logger.info(f"Authentication {authentication.id} revoked successfully.")
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication repository."
            )
            raise AuthenticationException()
```

---

## 12. `infrastructure/caches.py`

```python
from __future__ import annotations

from loguru import logger
from redis.asyncio import Redis

from app.core.settings import settings
from app.modules.authentication.application.interfaces import IAuthenticationCache
from app.modules.authentication.application.mappers import (
    cache_entity_mapper,
    entity_cache_mapper,
)
from app.modules.authentication.domain.entities import Authentication


class RedisAuthenticationCache(IAuthenticationCache):
    """
    Implementation of IAuthenticationCache using Redis.

    Uses the Tombstone pattern to prevent race conditions:
    - On delete, a tombstone is written first
    - On insert, the tombstone is checked first; if present, skip the insert
    """

    def __init__(self, cache: Redis) -> None:
        self.cache = cache
        self.prefix = f"{settings.REDIS_NAMESPACE}:authentication:"

    def _key(self, suffix: str) -> str:
        return f"{self.prefix}{suffix}"

    def _tombstone(self, suffix: str) -> str:
        return f"{self.prefix}tombstone:{suffix}"

    # ========================================================================
    # CREATE
    # ========================================================================
    async def insert_by_access_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no access token hashed_jti. Skipping cache insert."
                )
                return

            suffix = f"access_token:{hashed_jti}"

            # Check tombstone first
            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(
                    f"Authentication '{authentication.id}' was invalidated while being read. Skipping cache insert by access token."
                )
                return

            logger.debug(
                f"Caching authentication '{authentication.id}' by access token."
            )

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(authentication),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(
                f"Authentication '{authentication.id}' cached successfully by access token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert authentication by access token cache. The request continues without caching."
            )
            return

    async def insert_by_refresh_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no refresh token hashed_jti. Skipping cache insert."
                )
                return

            suffix = f"refresh_token:{hashed_jti}"

            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(
                    f"Authentication '{authentication.id}' was invalidated while being read. Skipping cache insert by refresh token."
                )
                return

            logger.debug(
                f"Caching authentication '{authentication.id}' by refresh token."
            )

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(authentication),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(
                f"Authentication '{authentication.id}' cached successfully by refresh token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert authentication by refresh token cache. The request continues without caching."
            )
            return

    # ========================================================================
    # READ
    # ========================================================================
    async def get_by_access_token(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                return None

            logger.debug("Getting authentication by access token from cache.")

            raw = await self.cache.get(self._key(f"access_token:{hashed_jti}"))

            logger.debug(
                f"Authentication {'found' if raw else 'not found'} by access token in cache."
            )
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by access token cache. Falling back to the database."
            )
            return None

    async def get_by_refresh_token(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                return None

            logger.debug("Getting authentication by refresh token from cache.")

            raw = await self.cache.get(self._key(f"refresh_token:{hashed_jti}"))

            logger.debug(
                f"Authentication {'found' if raw else 'not found'} by refresh token in cache."
            )
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by refresh token cache. Falling back to the database."
            )
            return None

    # ========================================================================
    # DELETE
    # ========================================================================
    async def delete_by_access_token(self, authentication: Authentication) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no access token hashed_jti. Skipping cache delete."
                )
                return

            logger.debug(
                f"Invalidating authentication '{authentication.id}' by access token."
            )

            suffix = f"access_token:{hashed_jti}"

            # Write tombstone first, then delete
            await self.cache.set(
                self._tombstone(suffix),
                1,
                ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(
                f"Authentication '{authentication.id}' invalidated successfully by access token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication by access token cache. The entry remains until its ttl expires."
            )
            return

    async def delete_by_refresh_token(self, authentication: Authentication) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no refresh token hashed_jti. Skipping cache delete."
                )
                return

            logger.debug(
                f"Invalidating authentication '{authentication.id}' by refresh token."
            )

            suffix = f"refresh_token:{hashed_jti}"

            await self.cache.set(
                self._tombstone(suffix),
                1,
                ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(
                f"Authentication '{authentication.id}' invalidated successfully by refresh token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication by refresh token cache. The entry remains until its ttl expires."
            )
            return
```

---

## 13. `infrastructure/services.py`

```python
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
```

---

## 14. `presentation/schemas.py`

```python
from __future__ import annotations

from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.shared.domain.enums import ResponseMessages, Role


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
        "info": { ... }
    }
    """

    message: str = ResponseMessages.LOGIN_SUCCESS.value
    access_token: str
    refresh_token: str
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
    """Request model for sign up."""

    full_name: str
    username: str
    email: EmailStr
    phone_number: str | None = None
    password: str
    confirm_password: str
    agree_terms: bool

    model_config = ConfigDict(
        title="SignUpRequest",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "phone_number": "+555472664275",
                "password": "MyP@ssword123",
                "confirm_password": "MyP@ssword123",
                "agree_terms": True,
            },
        },
    )


class SignUpResponse(BaseModel):
    """Response model for sign up."""

    message: str = ResponseMessages.CREATED.value

    model_config = ConfigDict(
        title="SignUpResponse",
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "example": {"message": ResponseMessages.CREATED.value},
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
```

---

## 15. `presentation/routers.py`

```python
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestFormStrict
from loguru import logger

from app.core.security import (
    authenticate_logout,
    authenticate_refresh,
    authenticate_user,
    no_authentication,
)
from app.core.settings import settings
from app.modules.authentication.application.exceptions import AuthenticationException
from app.modules.authentication.application.mappers import (
    entity_forgot_password_mapper,
    entity_lock_screen_mapper,
    entity_login_mapper,
    entity_logout_mapper,
    entity_refresh_mapper,
    entity_reset_password_mapper,
    entity_sign_up_mapper,
    entity_two_step_code_mapper,
    entity_two_step_verification_mapper,
    login_entity_mapper,
    logout_entity_mapper,
    refresh_entity_mapper,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.domain.entities import Authentication
from app.modules.authentication.domain.enums import TokenType
from app.modules.authentication.presentation.dependencies import (
    get_authentication_use_cases,
)
from app.modules.authentication.presentation.docs import (
    forgot_password_docs,
    lock_screen_docs,
    login_docs,
    logout_docs,
    refresh_docs,
    reset_password_docs,
    router_docs,
    sign_up_docs,
    two_step_code_docs,
    two_step_verification_docs,
)
from app.modules.authentication.presentation.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LockScreenRequest,
    LockScreenResponse,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SignUpRequest,
    SignUpResponse,
    TwoStepCodeRequest,
    TwoStepCodeResponse,
    TwoStepVerificationRequest,
    TwoStepVerificationResponse,
)
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import CookieManagementException
from app.modules.user.application.mappers import (
    create_entity_mapper as sign_up_entity_mapper,
)

router = APIRouter(**router_docs)


# ============================================================================
# COOKIE HELPERS
# ============================================================================
def set_cookies(response: Response, authentication: Authentication) -> None:
    """Set HttpOnly cookies for tokens."""
    try:
        response.set_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            value=TokenType.BEARER.value,
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            value=authentication.refresh_token.access_token.token
            if authentication.refresh_token.access_token.token
            else "",
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            value=authentication.refresh_token.token
            if authentication.refresh_token.token
            else "",
            max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the set_cookies function.")
        raise CookieManagementException()


def delete_cookies(response: Response) -> None:
    """Delete cookies."""
    try:
        response.delete_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the delete_cookies function."
        )
        raise CookieManagementException()


# ============================================================================
# CREATE: LOGIN
# ============================================================================
@router.post("/login/", **login_docs)
@router.post("/login", include_in_schema=False)
async def login(
    request: Request,
    response: Response,
    _: Annotated[None, Depends(no_authentication)],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LoginResponse:
    """
    Login endpoint.

    Response:
    {
        "message": "User logged in successfully",
        "access_token": "...",
        "refresh_token": "...",
        "info": {
            "first_name": "System",
            "last_name": "Admin",
            ...
        }
    }
    """
    try:
        request_domain = login_entity_mapper(form_data, request)
        response_domain = await use_case.login(request_domain)
        output = entity_login_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the login endpoint.")
        raise AuthenticationException()


# ============================================================================
# SIGN UP
# ============================================================================
@router.post("/sign-up/", **sign_up_docs)
@router.post("/sign-up", include_in_schema=False)
async def sign_up(
    _: Annotated[None, Depends(no_authentication)],
    payload: SignUpRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> SignUpResponse:
    """
    Sign up endpoint.

    Creates a new user account.
    """
    try:
        request_domain = sign_up_entity_mapper(payload)
        response_domain = await use_case.sign_up(request_domain)
        output = entity_sign_up_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the sign up endpoint.")
        raise AuthenticationException()


# ============================================================================
# UPDATE: REFRESH
# ============================================================================
@router.patch("/refresh/", **refresh_docs)
@router.patch("/refresh", include_in_schema=False)
async def refresh(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_refresh)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> RefreshResponse:
    """Refresh tokens endpoint."""
    try:
        request_domain = refresh_entity_mapper(authentication)
        response_domain = await use_case.refresh(request_domain)
        output = entity_refresh_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the refresh endpoint.")
        raise AuthenticationException()


# ============================================================================
# DELETE: LOGOUT
# ============================================================================
@router.delete("/logout/", **logout_docs)
@router.delete("/logout", include_in_schema=False)
async def logout(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_logout)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LogoutResponse:
    """Logout endpoint."""
    try:
        request_domain = logout_entity_mapper(authentication)
        response_domain = await use_case.logout(request_domain)
        output = entity_logout_mapper(response_domain)

        delete_cookies(response)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the logout endpoint.")
        raise AuthenticationException()


# ============================================================================
# FORGOT PASSWORD
# ============================================================================
@router.post("/forgot-password/", **forgot_password_docs)
@router.post("/forgot-password", include_in_schema=False)
async def forgot_password(
    _: Annotated[None, Depends(no_authentication)],
    payload: ForgotPasswordRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> ForgotPasswordResponse:
    """
    Forgot password endpoint.

    Sends a reset code to the email.
    """
    try:
        await use_case.forgot_password(email=str(payload.email))
        return ForgotPasswordResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the forgot password endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# RESET PASSWORD
# ============================================================================
@router.post("/reset-password/", **reset_password_docs)
@router.post("/reset-password", include_in_schema=False)
async def reset_password(
    _: Annotated[None, Depends(no_authentication)],
    payload: ResetPasswordRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> ResetPasswordResponse:
    """
    Reset password endpoint.

    Validates the reset code and sets a new password.
    """
    try:
        await use_case.reset_password(
            code=payload.code,
            password=payload.password,
            confirm_password=payload.confirm_password,
        )
        return ResetPasswordResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the reset password endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# LOCK SCREEN
# ============================================================================
@router.post("/lock-screen/", **lock_screen_docs)
@router.post("/lock-screen", include_in_schema=False)
async def lock_screen(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: LockScreenRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LockScreenResponse:
    """
    Lock screen endpoint.

    Validates the password to unlock.
    """
    try:
        await use_case.lock_screen(
            authentication=authentication, password=payload.password
        )
        return LockScreenResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the lock screen endpoint.")
        raise AuthenticationException()


# ============================================================================
# TWO-STEP VERIFICATION
# ============================================================================
@router.post("/two-step-verification/", **two_step_verification_docs)
@router.post("/two-step-verification", include_in_schema=False)
async def two_step_verification(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: TwoStepVerificationRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> TwoStepVerificationResponse:
    """
    Two-step verification endpoint.

    Sends an OTP to the phone number.
    """
    try:
        await use_case.two_step_verification(
            authentication=authentication,
            country_code=payload.country_code,
            phone_number=payload.phone_number,
        )
        return TwoStepVerificationResponse()
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the two-step verification endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# TWO-STEP CODE
# ============================================================================
@router.post("/two-step-code/", **two_step_code_docs)
@router.post("/two-step-code", include_in_schema=False)
async def two_step_code(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: TwoStepCodeRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> TwoStepCodeResponse:
    """
    Two-step code endpoint.

    Validates the OTP code and issues tokens.
    """
    try:
        response_domain = await use_case.two_step_code(
            authentication=authentication,
            code=payload.code,
            dont_ask_again=payload.dont_ask_again,
        )

        set_cookies(response, response_domain)

        return entity_two_step_code_mapper(response_domain)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the two-step code endpoint."
        )
        raise AuthenticationException()
```

---

## 16. `presentation/dependencies.py`

```python
from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache_session
from app.core.database import get_async_session
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
    ITokenService,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.infrastructure.caches import RedisAuthenticationCache
from app.modules.authentication.infrastructure.repositories import (
    PostgresAuthenticationRepository,
)
from app.modules.authentication.infrastructure.services import TokenService
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.presentation.dependencies import get_shared_use_cases


def get_authentication_cache(
    cache: Redis = Depends(get_cache_session),
) -> IAuthenticationCache:
    """Create RedisAuthenticationCache."""
    return RedisAuthenticationCache(cache=cache)


def get_authentication_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IAuthenticationRepository:
    """Create PostgresAuthenticationRepository."""
    return PostgresAuthenticationRepository(session=session)


def get_token_service() -> ITokenService:
    """Create TokenService."""
    return TokenService()


def get_authentication_use_cases(
    cache: IAuthenticationCache = Depends(get_authentication_cache),
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    shared_service: SharedUseCases = Depends(get_shared_use_cases),
    token_service: ITokenService = Depends(get_token_service),
) -> AuthenticationUseCases:
    """
    Create AuthenticationUseCases with injected dependencies.

    This is where Dependency Injection happens:
    - cache → RedisAuthenticationCache
    - repository → PostgresAuthenticationRepository
    - shared_service → SharedUseCases
    - token_service → TokenService
    """
    return AuthenticationUseCases(
        cache=cache,
        repository=repository,
        shared_service=shared_service,
        token_service=token_service,
    )
```

---

## 17. `presentation/docs.py`

```python
from __future__ import annotations

from http import HTTPStatus

from app.modules.authentication.presentation.schemas import (
    ForgotPasswordResponse,
    LockScreenResponse,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    ResetPasswordResponse,
    SignUpResponse,
    TwoStepCodeResponse,
    TwoStepVerificationResponse,
)
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import StandardResponse

# ============================================================================
# MODULE DOCS
# ============================================================================
router_docs = {
    "prefix": "/api/v1/authentication",
    "tags": ["Authentication"],
    "responses": {
        400: {"model": StandardResponse, "description": "Bad Request"},
        401: {"model": StandardResponse, "description": "Unauthorized"},
        403: {"model": StandardResponse, "description": "Forbidden"},
        405: {"model": StandardResponse, "description": "Method Not Allowed"},
        422: {"model": StandardResponse, "description": "Form Validation Error"},
        500: {"model": StandardResponse, "description": "Internal Server Error"},
        502: {"model": StandardResponse, "description": "Bad Gateway"},
        504: {"model": StandardResponse, "description": "Gateway Timeout"},
    },
}


# ============================================================================
# LOGIN DOCS
# ============================================================================
login_docs = {
    "summary": "Endpoint to login a user.",
    "description": (
        "Authenticate a user and initiate a login session. "
        "Authentication tokens are returned via HttpOnly cookies."
    ),
    "response_description": (
        "Successful authentication. Access/refresh tokens are set in cookies and "
        "the JSON body returns tokens + user info."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LoginResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful login response (cookies + tokens + user info)",
            "model": LoginResponse,
            "headers": {
                "Set-Cookie": {
                    "description": (
                        "Returned multiple times to set `token_type`, `access_token`, "
                        "and `refresh_token` cookies."
                    ),
                    "schema": {"type": "string"},
                    "example": "access_token=<token>; HttpOnly; Path=/; SameSite=lax",
                }
            },
            "content": {
                "application/json": {
                    "examples": {
                        "Login Success": {
                            "summary": "Login response with tokens and user info",
                            "value": {
                                "message": ResponseMessages.LOGIN_SUCCESS.value,
                                "access_token": "eyJhbGciOi...",
                                "refresh_token": "eyJhbGciOi...",
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
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# SIGN UP DOCS
# ============================================================================
sign_up_docs = {
    "summary": "Endpoint to sign up a new user.",
    "description": (
        "Create a new user account. Public endpoint — no authentication is required."
    ),
    "response_description": "Successful sign up.",
    "status_code": HTTPStatus.CREATED,
    "response_model": SignUpResponse,
    "include_in_schema": True,
    "responses": {
        201: {
            "description": "User created successfully",
            "model": SignUpResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Sign Up Success": {
                            "summary": "User signed up successfully",
                            "value": {"message": ResponseMessages.CREATED.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# REFRESH DOCS
# ============================================================================
refresh_docs = {
    "summary": "Endpoint to refresh authentication tokens.",
    "description": (
        "Validates the `refresh_token` from HttpOnly cookies using `refresh_tokens` "
        "security dependency, then rotates and sets new `token_type`, `access_token`, "
        "and `refresh_token` cookies."
    ),
    "response_description": (
        "Successful token refresh. New access/refresh tokens and token type are set "
        "in cookies, and the JSON body returns a refresh confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": RefreshResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful refresh response",
            "model": RefreshResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Refresh Success": {
                            "summary": "Refresh token generated successfully",
                            "value": {
                                "message": ResponseMessages.REFRESH_SUCCESS.value
                            },
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# LOGOUT DOCS
# ============================================================================
logout_docs = {
    "summary": "Endpoint to logout a user.",
    "description": (
        "Invalidates the authenticated session and removes authentication cookies. "
        "The endpoint requires a valid authenticated user."
    ),
    "response_description": (
        "Successful logout. Authentication cookies are removed and the JSON body "
        "returns a logout confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LogoutResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful logout response",
            "model": LogoutResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Logout Success": {
                            "summary": "User logged out successfully",
                            "value": {"message": ResponseMessages.LOGOUT_SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# FORGOT PASSWORD DOCS
# ============================================================================
forgot_password_docs = {
    "summary": "Endpoint to request password reset.",
    "description": (
        "Send a password reset code to the user's email address. "
        "Always returns success to avoid revealing whether the email exists."
    ),
    "response_description": "Reset code sent (if email exists).",
    "status_code": HTTPStatus.OK,
    "response_model": ForgotPasswordResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Forgot password request processed",
            "model": ForgotPasswordResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Forgot Password Success": {
                            "summary": "Reset code sent",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# RESET PASSWORD DOCS
# ============================================================================
reset_password_docs = {
    "summary": "Endpoint to reset password with code.",
    "description": "Validate the reset code and set a new password for the user.",
    "response_description": "Password reset successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": ResetPasswordResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Password reset successfully",
            "model": ResetPasswordResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Reset Password Success": {
                            "summary": "Password reset successfully",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# LOCK SCREEN DOCS
# ============================================================================
lock_screen_docs = {
    "summary": "Endpoint to unlock the screen.",
    "description": (
        "Validate the user's password to unlock a locked screen. "
        "Requires a valid authenticated session."
    ),
    "response_description": "Screen unlocked successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": LockScreenResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Screen unlocked successfully",
            "model": LockScreenResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Lock Screen Success": {
                            "summary": "Screen unlocked",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# TWO-STEP VERIFICATION DOCS
# ============================================================================
two_step_verification_docs = {
    "summary": "Endpoint to initiate two-step verification.",
    "description": (
        "Send an OTP code to the specified phone number for two-step verification."
    ),
    "response_description": "OTP sent successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": TwoStepVerificationResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "OTP sent successfully",
            "model": TwoStepVerificationResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Two-Step Verification Success": {
                            "summary": "OTP sent",
                            "value": {"message": ResponseMessages.SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


# ============================================================================
# TWO-STEP CODE DOCS
# ============================================================================
two_step_code_docs = {
    "summary": "Endpoint to verify two-step code.",
    "description": "Validate the OTP code and issue authentication tokens.",
    "response_description": "OTP verified successfully, tokens issued.",
    "status_code": HTTPStatus.OK,
    "response_model": TwoStepCodeResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "OTP verified successfully",
            "model": TwoStepCodeResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Two-Step Code Success": {
                            "summary": "OTP verified, tokens issued",
                            "value": {
                                "message": ResponseMessages.SUCCESS.value,
                                "access_token": "eyJhbGciOi...",
                                "refresh_token": "eyJhbGciOi...",
                            },
                        }
                    }
                }
            },
        },
    },
}
```

---

## 18. สรุป API Endpoints ทั้งหมด

| # | Method | Path | Description | Auth |
|---|--------|------|-------------|------|
| 1 | POST | `/api/v1/authentication/login/` | Login | ❌ |
| 2 | POST | `/api/v1/authentication/sign-up/` | Sign up | ❌ |
| 3 | PATCH | `/api/v1/authentication/refresh/` | Refresh tokens | ✅ refresh |
| 4 | DELETE | `/api/v1/authentication/logout/` | Logout | ✅ |
| 5 | POST | `/api/v1/authentication/forgot-password/` | Request password reset | ❌ |
| 6 | POST | `/api/v1/authentication/reset-password/` | Reset with code | ❌ |
| 7 | POST | `/api/v1/authentication/lock-screen/` | Unlock screen | ✅ |
| 8 | POST | `/api/v1/authentication/two-step-verification/` | Send OTP | ✅ |
| 9 | POST | `/api/v1/authentication/two-step-code/` | Verify OTP | ✅ |

---

## 19. โครงสร้างโฟลเดอร์

```
app/modules/authentication/
├── domain/
│   ├── __init__.py
│   ├── entities.py
│   ├── enums.py
│   ├── events.py
│   ├── exceptions.py
│   └── value_objects.py
│
├── application/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── interfaces.py
│   ├── mappers.py
│   └── use_cases.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── caches.py
│   ├── models.py
│   ├── repositories.py
│   └── services.py
│
└── presentation/
    ├── __init__.py
    ├── dependencies.py
    ├── docs.py
    ├── routers.py
    └── schemas.py
```

---

## 20. Checklist

- [x] `domain/enums.py` - TokenType
- [x] `domain/events.py` - Domain events
- [x] `domain/exceptions.py` - Domain errors
- [x] `domain/value_objects.py` - Claims, RefreshClaims
- [x] `domain/entities.py` - Authentication, RefreshToken, AccessToken
- [x] `application/interfaces.py` - Protocols
- [x] `application/exceptions.py` - Application exceptions
- [x] `application/mappers.py` - Data transformations
- [x] `application/use_cases.py` - All use cases
- [x] `infrastructure/models.py` - SQLAlchemy models
- [x] `infrastructure/repositories.py` - Postgres implementation
- [x] `infrastructure/caches.py` - Redis implementation
- [x] `infrastructure/services.py` - Token service
- [x] `presentation/schemas.py` - Pydantic schemas
- [x] `presentation/routers.py` - FastAPI endpoints
- [x] `presentation/dependencies.py` - DI
- [x] `presentation/docs.py` - OpenAPI docs

---

หากต้องการให้ implement ส่วน TODO ไหนเพิ่มเติม (เช่น email service, OTP service, reset code storage) บอกได้เลยครับ!

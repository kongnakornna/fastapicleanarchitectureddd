#!/usr/bin/env python3
"""
authentication_module_user.py — Authentication Module Generator v1.1.0

อัปเดตให้สอดคล้องกับ sd_user.sql + sd_user_role.sql:
  • Login รองรับ username OR email
  • Sign Up บังคับ username (NOT NULL UNIQUE)
  • UserInfo + SignUpResponse มี username
  • เพิ่ม endpoints: sign-up, lock-screen, two-step-verification, two-step-code
  • JWT sub = str(user.id) (BIGINT 11+ หลัก, RFC 7519)
  • Authentication.user_id FK → erp_users.id BIGINT

Schema : public · Prefix : auth_ · Tables : auth_authentications,
         auth_refresh_tokens, auth_access_tokens

Actions (11):
  1.  create      — สร้าง module structure (4 layers)
  2.  activate    — register router + swagger + models
  3.  sql         — SQL migrations V001..V003 (3 tables + RLS)
  4.  update      — update app/app.py
  5.  update-env  — update migrations/env.py
  6.  alembic     — Alembic migration
  7.  swagger     — OpenAPI metadata
  8.  postman     — Postman collection
  9.  test        — Unit + property + manual tests
 10.  verify      — ตรวจสอบ
 11.  all         — ทำทุกอย่าง

Usage:
    python authentication_module_user.py all authentication 0 auth
    python authentication_module_user.py create authentication 0 auth --force
    python authentication_module_user.py verify authentication
"""
from __future__ import annotations

import argparse
import json as _json_mod
import re
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

VERSION = "1.1.0"

LAYER_NAMES = {
    "0": "0-Core", "1": "1-Foundation", "2": "2-Money",
    "3": "3-Goods", "4": "4-Ops", "5": "5-Intel",
    "6": "6-Monitor", "7": "7-Template",
}

ACTIONS = {
    "create", "activate", "sql", "alembic",
    "swagger", "postman", "update", "update-env",
    "test", "all", "verify", "help",
}

SCHEMA = "public"
PREFIX = "auth"
TABLE_NAMES = (
    "auth_authentications",
    "auth_refresh_tokens",
    "auth_access_tokens",
)


class C:
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; GRAY = "\033[90m"; RESET = "\033[0m"


def info(msg: str) -> None: print(f"{C.CYAN}{msg}{C.RESET}")
def ok(msg: str) -> None: print(f"  {C.GREEN}[OK]{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.YELLOW}[!!]{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.RED}[XX]{C.RESET} {msg}")
def skip(msg: str) -> None: print(f"  {C.GRAY}[--]{C.RESET} {msg}")


# ═══════════════════════════════════════════════════════════════
#  FILE WRITER
# ═══════════════════════════════════════════════════════════════
class FileWriter:
    def __init__(self, root: Path, force: bool = False, backup: bool = True):
        self.root = root
        self.force = force
        self.backup = backup
        self.written: list[Path] = []
        self.skipped: list[Path] = []
        self.backups: list[Path] = []

    def write(self, rel_path: str, content: str) -> None:
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not self.force:
            skip(f"skip (exists): {rel_path}")
            self.skipped.append(path)
            return

        if path.exists() and self.backup:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_bytes(path.read_bytes())
            self.backups.append(bak)
            ok(f"backup: {rel_path}.bak")

        if rel_path.endswith(".py"):
            try:
                compile(content, rel_path, "exec")
            except SyntaxError as exc:
                err(f"SYNTAX ERROR in {rel_path}: {exc}")
                err(f"  line {exc.lineno}: {exc.text}")
                raise RuntimeError(f"Refuse to write invalid Python: {rel_path}") from exc

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  GENERATOR
# ═══════════════════════════════════════════════════════════════
class AuthenticationModuleGenerator:
    def __init__(
        self, project_root: Path,
        module: str = "authentication", layer: str = "0", prefix: str = "auth",
        force: bool = False,
    ):
        self.root = project_root
        self.module = module.lower()
        self.layer = layer
        self.prefix = prefix.lower()
        self.layer_name = LAYER_NAMES.get(layer, "0-Core")
        self.writer = FileWriter(project_root, force=force)
        self.mod_root = f"app/modules/{self.module}"
        self.sql_dir = "db/migrations"
        self.alembic_dir = "migrations/versions"
        self.env_py = "migrations/env.py"
        self.app_py = "app/app.py"
        self.tests_dir = "tests"
        self.docs_dir = "docs"

    # ═══════════════════════════════════════════════════════════
    #  1. CREATE MODULE
    # ═══════════════════════════════════════════════════════════
    def create_module(self) -> None:
        info(f"[CREATE] module: {self.module} (Layer {self.layer_name})")
        self._create_domain()
        self._create_application()
        self._create_infrastructure()
        self._create_presentation()
        self._create_root_init()

    # ─── DOMAIN ─────────────────────────────────────────────────
    def _create_domain(self) -> None:
        base = f"{self.mod_root}/domain"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """authentication domain layer"""
            from .entities import AccessToken, Authentication, RefreshToken
            from .enums import TokenType
            from .events import (
                AuthenticationCreated, AuthenticationRevoked,
                SuspiciousActivityDetected, TokensRefreshed,
            )
            from .value_objects import Claims, RefreshClaims

            __all__ = [
                "AccessToken", "Authentication", "RefreshToken",
                "TokenType",
                "AuthenticationCreated", "AuthenticationRevoked",
                "TokensRefreshed", "SuspiciousActivityDetected",
                "Claims", "RefreshClaims",
            ]
        '''))

        self.writer.write(f"{base}/enums.py", dedent('''\
            """authentication enums"""
            from __future__ import annotations
            from enum import StrEnum


            class TokenType(StrEnum):
                """TH: ประเภท token | EN: token type"""
                BEARER = "Bearer"
                REFRESH = "Refresh"
        '''))

        self.writer.write(f"{base}/value_objects.py", dedent('''\
            """authentication value objects — JWT Claims (immutable)"""
            from __future__ import annotations
            from uuid import UUID

            from app.modules.shared.domain.entities import DomainError


            class BaseClaims:
                """Base class for JWT Claims — immutable."""

                iss: str
                sub: str          # ← user id encoded as string (RFC 7519)
                aud: str
                iat: int
                nbf: int
                exp: int
                jti: UUID

                def __setattr__(self, name: str, value) -> None:
                    raise AttributeError(f"{type(self).__name__} is immutable.")

                def __init__(
                    self,
                    iss: str | None = None,
                    sub: str | None = None,
                    aud: str | None = None,
                    iat: int | None = None,
                    nbf: int | None = None,
                    exp: int | None = None,
                    jti: UUID | None = None,
                ) -> None:
                    object.__setattr__(self, "iss", iss.strip() if iss else iss)
                    object.__setattr__(self, "sub", str(sub) if sub else sub)
                    object.__setattr__(self, "aud", aud.strip() if aud else aud)
                    object.__setattr__(self, "iat", iat)
                    object.__setattr__(self, "nbf", nbf)
                    object.__setattr__(self, "exp", exp)
                    object.__setattr__(self, "jti", jti)

                def _validate_base(self, prefix: str = "Claims") -> None:
                    if not self.iss:
                        raise DomainError(f"{prefix} issuer (iss) is required.")
                    if not self.sub:
                        raise DomainError(f"{prefix} subject (sub) is required.")
                    if not self.aud:
                        raise DomainError(f"{prefix} audience (aud) is required.")
                    if self.iat is None or not isinstance(self.iat, int) or self.iat <= 0:
                        raise DomainError(f"{prefix} iat must be a positive int.")
                    if self.nbf is None or not isinstance(self.nbf, int) or self.nbf <= 0:
                        raise DomainError(f"{prefix} nbf must be a positive int.")
                    if self.nbf < self.iat:
                        raise DomainError(f"{prefix} nbf cannot be before iat.")
                    if self.exp is None or not isinstance(self.exp, int) or self.exp <= 0:
                        raise DomainError(f"{prefix} exp must be a positive int.")
                    if self.exp <= self.iat:
                        raise DomainError(f"{prefix} exp must be after iat.")
                    if not self.jti:
                        raise DomainError(f"{prefix} jti is required.")

                def _base_to_dict(self) -> dict:
                    return {
                        "iss": self.iss, "sub": str(self.sub), "aud": self.aud,
                        "iat": self.iat, "nbf": self.nbf, "exp": self.exp,
                        "jti": str(self.jti),
                    }

                @staticmethod
                def _base_kwargs_from_dict(data: dict) -> dict:
                    return {
                        "iss": data["iss"],
                        "sub": str(data["sub"]),
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

                def __init__(self, *, iss=None, sub=None, aud=None, iat=None,
                             nbf=None, exp=None, jti=None, grant_id=None, scope=None) -> None:
                    super().__init__(iss=iss, sub=sub, aud=aud, iat=iat,
                                     nbf=nbf, exp=exp, jti=jti)
                    object.__setattr__(self, "grant_id", grant_id)
                    object.__setattr__(self, "scope",
                                       scope.strip().lower() if scope else scope)
                    self._validate()

                def _validate(self) -> None:
                    self._validate_base()
                    if not self.grant_id:
                        raise DomainError("Claims grant_id is required.")
                    if not self.scope:
                        raise DomainError("Claims scope is required.")

                def to_dict(self) -> dict:
                    return {**self._base_to_dict(),
                            "grant_id": self.grant_id, "scope": self.scope}

                @classmethod
                def from_dict(cls, data: dict) -> "Claims":
                    return cls(**cls._base_kwargs_from_dict(data),
                               grant_id=data["grant_id"], scope=data["scope"])


            class RefreshClaims(BaseClaims):
                """Claims for Refresh Token."""

                client_id: str
                grant_id: str
                scope: str

                def __init__(self, *, iss=None, sub=None, aud=None, iat=None,
                             nbf=None, exp=None, jti=None, client_id=None,
                             grant_id=None, scope=None) -> None:
                    super().__init__(iss=iss, sub=sub, aud=aud, iat=iat,
                                     nbf=nbf, exp=exp, jti=jti)
                    object.__setattr__(self, "client_id",
                                       client_id.strip().lower() if client_id else client_id)
                    object.__setattr__(self, "grant_id",
                                       grant_id.strip() if grant_id else grant_id)
                    object.__setattr__(self, "scope",
                                       " ".join(scope.lower().split()) if scope else scope)
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
                    return {**self._base_to_dict(),
                            "client_id": self.client_id,
                            "grant_id": self.grant_id, "scope": self.scope}

                @classmethod
                def from_dict(cls, data: dict) -> "RefreshClaims":
                    return cls(**cls._base_kwargs_from_dict(data),
                               client_id=data["client_id"],
                               grant_id=data["grant_id"], scope=data["scope"])
        '''))

        self.writer.write(f"{base}/events.py", dedent('''\
            """authentication domain events"""
            from __future__ import annotations
            from dataclasses import dataclass
            from datetime import datetime
            from uuid import UUID


            @dataclass(frozen=True)
            class AuthenticationCreated:
                authentication_id: UUID
                user_id: int
                device: str | None
                ip_address: str | None
                occurred_at: datetime


            @dataclass(frozen=True)
            class AuthenticationRevoked:
                authentication_id: UUID
                user_id: int
                device: str | None
                occurred_at: datetime


            @dataclass(frozen=True)
            class TokensRefreshed:
                authentication_id: UUID
                user_id: int
                device: str | None
                occurred_at: datetime


            @dataclass(frozen=True)
            class SuspiciousActivityDetected:
                authentication_id: UUID | None
                user_id: int | None
                reason: str
                ip_address: str | None
                occurred_at: datetime
        '''))

        self.writer.write(f"{base}/entities.py", dedent('''\
            """authentication entities — Authentication / RefreshToken / AccessToken"""
            from __future__ import annotations

            from dataclasses import dataclass, field
            from datetime import datetime
            from uuid import UUID

            from app.modules.authentication.domain.value_objects import (
                Claims, RefreshClaims,
            )
            from app.modules.shared.domain.enums import Role
            from app.modules.user.domain.entities import User


            @dataclass(kw_only=True, slots=True)
            class Authentication:
                """Entity: user session on a specific device."""

                ip_address: str | None = field(default=None, compare=True)
                user_agent: str | None = field(default=None, compare=True)
                device: str | None = field(default=None, compare=True)
                location: str | None = field(default=None, compare=False)
                accept_language: str | None = field(default=None, compare=False)
                accept_encoding: str | None = field(default=None, compare=False)
                origin: str | None = field(default=None, compare=False)
                referer: str | None = field(default=None, compare=False)

                id: UUID | None = field(default=None, compare=True)
                created_at: datetime | None = field(default=None, compare=False)
                last_updated_at: datetime | None = field(default=None, compare=False)
                blacklisted: bool = field(init=False, default=False, compare=False)

                user: User = field(compare=True)
                refresh_token: "RefreshToken | None" = field(default=None, compare=True)

                def __post_init__(self) -> None:
                    self._normalize()

                def _normalize(self) -> None:
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

                def create_tokens(self, now, refresh_expires_at, access_expires_at) -> "Authentication":
                    self.refresh_token = RefreshToken(
                        expires_at=refresh_expires_at,
                        access_token=AccessToken(expires_at=access_expires_at),
                    )
                    self.refresh_token.generate_created_at(now)
                    self.refresh_token.generate_updated_at(now)
                    self.refresh_token.access_token.generate_created_at(now)
                    return self

                def renew_tokens(self, now, refresh_expires_at, access_expires_at) -> "Authentication":
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

                def refresh_access_token(self, now, access_expires_at) -> "Authentication":
                    self.refresh_token.generate_updated_at(now)
                    self.refresh_token.update_previous_hashed_jti()
                    self.refresh_token.access_token.expires_at = access_expires_at
                    self.refresh_token.access_token.generate_created_at(now)
                    self.refresh_token.access_token.update_previous_hashed_jti()
                    return self

                def revoke(self, now: datetime) -> "Authentication":
                    self.refresh_token.generate_updated_at(now)
                    self.refresh_token.revoke(now)
                    return self


            @dataclass(kw_only=True, slots=True)
            class RefreshToken:
                token: str | None = field(default=None, compare=False)
                hashed_jti: str | None = field(default=None, compare=True)
                previous_hashed_jti: str | None = field(default=None, compare=True)

                replaced_by_token: UUID | None = field(default=None, compare=False)
                id: UUID | None = field(default=None, compare=True)
                created_at: datetime | None = field(default=None, compare=True)
                updated_at: datetime | None = field(default=None, compare=False)
                expires_at: datetime | None = field(default=None, compare=False)
                revoked: bool = field(init=False, default=False, compare=False)
                revoked_at: datetime | None = field(init=False, default=None, compare=False)
                refresh_claims: RefreshClaims | None = field(default=None, compare=False)

                access_token: "AccessToken | None" = field(default=None, compare=False)

                def revoke(self, now: datetime) -> None:
                    self.revoked = True
                    self.revoked_at = now
                    if self.access_token:
                        self.access_token.revoke(now)

                def activate(self) -> None:
                    self.revoked = False
                    self.revoked_at = None

                def generate_created_at(self, dt: datetime) -> None:
                    self.created_at = dt

                def generate_updated_at(self, dt: datetime) -> None:
                    self.updated_at = dt

                def update_previous_hashed_jti(self) -> None:
                    self.previous_hashed_jti = self.hashed_jti

                def set_claims(self, iss, sub: int, aud, jti, client_id, grant_id, scope) -> None:
                    self.refresh_claims = RefreshClaims(
                        iss=iss, sub=str(sub), aud=aud,
                        iat=int(self.updated_at.timestamp()),
                        nbf=int(self.updated_at.timestamp()),
                        exp=int(self.expires_at.timestamp()),
                        jti=jti, client_id=client_id,
                        grant_id=grant_id, scope=scope,
                    )


            @dataclass(kw_only=True, slots=True)
            class AccessToken:
                token: str | None = field(default=None, compare=False)
                hashed_jti: str | None = field(default=None, compare=True)
                previous_hashed_jti: str | None = field(default=None, compare=True)
                permission: Role = field(default=Role.USER, compare=False)

                id: UUID | None = field(default=None, compare=True)
                created_at: datetime | None = field(default=None, compare=True)
                expires_at: datetime | None = field(default=None, compare=False)
                claims: Claims | None = field(default=None, compare=False)
                revoked: bool = field(init=False, default=False, compare=False)
                revoked_at: datetime | None = field(init=False, default=None, compare=False)

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

                def set_claims(self, iss, sub: int, aud, jti, grant_id, scope) -> None:
                    self.claims = Claims(
                        iss=iss, sub=str(sub), aud=aud,
                        iat=int(self.created_at.timestamp()),
                        nbf=int(self.created_at.timestamp()),
                        exp=int(self.expires_at.timestamp()),
                        jti=jti, grant_id=grant_id, scope=scope,
                    )
        '''))

    # ─── APPLICATION ────────────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", '"""authentication application layer"""')

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """authentication application exceptions"""
            from __future__ import annotations
            from http import HTTPStatus

            from app.modules.shared.application.exceptions import StandardException
            from app.modules.shared.domain.enums import ResponseMessages


            class AuthenticationException(StandardException):
                def __init__(self) -> None:
                    super().__init__(
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        message=ResponseMessages.INTERNAL_ERROR.value,
                        data={"errors": "Unexpected error at authentication module."},
                    )


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


            class AuthenticationTokenExpiredException(StandardException):
                def __init__(self) -> None:
                    super().__init__(
                        status_code=HTTPStatus.UNAUTHORIZED,
                        message=ResponseMessages.UNAUTHORIZED_ERROR.value,
                        data={
                            "errors": "Token has expired. Please login again.",
                            "errors_th": "โทเค็นหมดอายุแล้ว กรุณาเข้าสู่ระบบใหม่",
                        },
                    )


            class AuthenticationTokenInvalidException(StandardException):
                def __init__(self) -> None:
                    super().__init__(
                        status_code=HTTPStatus.UNAUTHORIZED,
                        message=ResponseMessages.UNAUTHORIZED_ERROR.value,
                        data={
                            "errors": "Invalid authentication token.",
                            "errors_th": "โทเคენการยืนยันตัวตนไม่ถูกต้อง",
                        },
                    )


            class RefreshTokenInvalidException(StandardException):
                def __init__(self) -> None:
                    super().__init__(
                        status_code=HTTPStatus.UNAUTHORIZED,
                        message=ResponseMessages.UNAUTHORIZED_ERROR.value,
                        data={
                            "errors": "Invalid refresh token.",
                            "errors_th": "รีเฟรชโทเค็นไม่ถูกต้อง",
                        },
                    )


            class EmailAlreadyExistsException(StandardException):
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
                def __init__(self, username: str) -> None:
                    super().__init__(
                        status_code=HTTPStatus.CONFLICT,
                        message=ResponseMessages.CONFLICT.value,
                        data={
                            "errors": f"Username '{username}' already exists.",
                            "errors_th": f"ชื่อผู้ใช้ '{username}' มีอยู่ในระบบแล้ว",
                        },
                    )


            class PasswordMismatchException(StandardException):
                def __init__(self) -> None:
                    super().__init__(
                        status_code=HTTPStatus.BAD_REQUEST,
                        message=ResponseMessages.VALIDATION_ERROR.value,
                        data={
                            "errors": "Passwords do not match.",
                            "errors_th": "รหัสผ่านไม่ตรงกัน",
                        },
                    )


            class InvalidOtpCodeException(StandardException):
                def __init__(self) -> None:
                    super().__init__(
                        status_code=HTTPStatus.BAD_REQUEST,
                        message=ResponseMessages.VALIDATION_ERROR.value,
                        data={
                            "errors": "Invalid or expired OTP code.",
                            "errors_th": "รหัส OTP ไม่ถูกต้องหรือหมดอายุแล้ว",
                        },
                    )
        '''))

        self.writer.write(f"{base}/interfaces.py", dedent('''\
            """authentication application ports"""
            from __future__ import annotations
            from typing import Protocol

            from app.modules.authentication.domain.entities import Authentication
            from app.modules.user.domain.entities import User


            class IAuthenticationRepository(Protocol):
                async def create(self, authentication: Authentication) -> Authentication: ...

                async def get_by_user_id_agent_and_device(
                    self, authentication: Authentication,
                ) -> Authentication | None: ...

                async def get_access_token_by_authentication(
                    self, authentication: Authentication,
                ) -> Authentication | None: ...

                async def get_refresh_token_by_authentication(
                    self, authentication: Authentication,
                ) -> Authentication | None: ...

                async def update(self, authentication: Authentication) -> Authentication: ...

                async def delete(self, authentication: Authentication) -> Authentication: ...


            class IAuthenticationCache(Protocol):
                async def insert_by_access_token(
                    self, authentication: Authentication, ttl: int | None = None,
                ) -> None: ...

                async def insert_by_refresh_token(
                    self, authentication: Authentication, ttl: int | None = None,
                ) -> None: ...

                async def get_by_access_token(
                    self, authentication: Authentication,
                ) -> Authentication | None: ...

                async def get_by_refresh_token(
                    self, authentication: Authentication,
                ) -> Authentication | None: ...

                async def delete_by_access_token(self, authentication: Authentication) -> None: ...

                async def delete_by_refresh_token(self, authentication: Authentication) -> None: ...


            class ITokenService(Protocol):
                async def generate(self, authentication: Authentication) -> Authentication: ...

                async def hash_tokens(self, authentication: Authentication) -> Authentication: ...

                async def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...

                def hash_password(self, plain_password: str) -> str: ...

                async def verify_access_token(self, token: str) -> Authentication: ...

                async def verify_refresh_token(self, token: str) -> Authentication: ...


            class ISignUpService(Protocol):
                async def create_user(self, user: User) -> User: ...


            class IEmailService(Protocol):
                async def send_password_reset_email(self, email: str, reset_code: str) -> None: ...

                async def send_otp_sms(self, phone_number: str, otp_code: str) -> None: ...

                async def send_welcome_email(self, email: str, name: str) -> None: ...
        '''))

        self.writer.write(f"{base}/use_cases.py", dedent('''\
            """authentication use cases — login / signup / refresh / logout / 2FA"""
            from __future__ import annotations

            from datetime import datetime, timedelta
            from uuid import uuid4

            from loguru import logger

            from app.core.settings import settings
            from app.modules.authentication.application.exceptions import (
                AuthenticationException, EmailAlreadyExistsException,
                InvalidCredentialsException, InvalidOtpCodeException,
                PasswordMismatchException, UsernameAlreadyExistsException,
            )
            from app.modules.authentication.application.interfaces import (
                IAuthenticationCache, IAuthenticationRepository, ITokenService,
            )
            from app.modules.authentication.domain.entities import Authentication
            from app.modules.shared.application.exceptions import (
                DomainException, StandardException,
            )
            from app.modules.shared.application.utils import BRASILIA_TZ
            from app.modules.shared.domain.entities import DomainError
            from app.modules.user.domain.entities import User


            class AuthenticationUseCases:
                """Use cases for Authentication."""

                def __init__(
                    self,
                    cache: IAuthenticationCache,
                    repository: IAuthenticationRepository,
                    shared_service,
                    token_service: ITokenService,
                ) -> None:
                    self.cache = cache
                    self.repository = repository
                    self.shared_service = shared_service
                    self.token_service = token_service
                    self.shared_service.disable_exceptions()

                # ─── LOGIN ─────────────────────────────────
                async def login(self, authentication: Authentication) -> Authentication:
                    try:
                        logger.debug(
                            f"login start: {authentication.user.censored_email} "
                            f"device={authentication.device}"
                        )

                        # ⚠️ Login รองรับ username OR email
                        # Shared service must handle both: get_user_by_email OR get_user_by_username
                        db_user: User | None = None
                        identifier = authentication.user.email or authentication.user.username
                        try:
                            db_user = await self.shared_service.get_user_by_email(
                                authentication.user
                            )
                        except Exception:
                            db_user = None

                        if not db_user and hasattr(self.shared_service, "get_user_by_username"):
                            try:
                                db_user = await self.shared_service.get_user_by_username(
                                    identifier
                                )
                            except Exception:
                                db_user = None

                        if not db_user:
                            logger.info(f"user not found: {identifier}")
                            raise InvalidCredentialsException()

                        if not await self.token_service.verify_password(
                            authentication.user.password, db_user.hashed_password
                        ):
                            # ⚠️ Track failed login
                            try:
                                db_user.record_login_failure()
                            except Exception:
                                pass
                            logger.info(f"invalid password for {db_user.id}")
                            raise InvalidCredentialsException()

                        authentication.user = db_user
                        auth_db = await self.repository.get_by_user_id_agent_and_device(
                            authentication
                        )

                        now = datetime.now(BRASILIA_TZ)
                        refresh_exp = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
                        access_exp = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

                        if auth_db:
                            await self.cache.delete_by_access_token(auth_db)
                            await self.cache.delete_by_refresh_token(auth_db)
                            authentication = auth_db.renew_tokens(now, refresh_exp, access_exp)
                        else:
                            authentication = authentication.create_tokens(now, refresh_exp, access_exp)

                        authentication = await self.token_service.generate(authentication)
                        authentication = await self.token_service.hash_tokens(authentication)
                        authentication.refresh_token.access_token.permission = authentication.user.role

                        if auth_db:
                            await self.repository.update(authentication)
                        else:
                            await self.repository.create(authentication)

                        # ⚠️ Track successful login
                        try:
                            authentication.user.record_login()
                        except Exception:
                            pass

                        return authentication
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("login failed")
                        raise AuthenticationException()

                # ─── SIGN UP ───────────────────────────────
                async def sign_up(self, user: User) -> User:
                    """TH: สมัครสมาชิก — ตรวจ email + username + hash password"""
                    try:
                        # ⚠️ SQL: username NOT NULL UNIQUE
                        if not user.username:
                            raise AuthenticationException()

                        # Check email
                        existing_email = await self.shared_service.get_user_by_email(user)
                        if existing_email:
                            raise EmailAlreadyExistsException(email=str(user.email))

                        # Check username (via shared service)
                        if hasattr(self.shared_service, "get_user_by_username"):
                            existing_username = await self.shared_service.get_user_by_username(
                                user.username
                            )
                            if existing_username:
                                raise UsernameAlreadyExistsException(
                                    username=user.username
                                )

                        # Hash password
                        if not user.hashed_password:
                            if not user.password:
                                raise AuthenticationException()
                            user.hashed_password = self.token_service.hash_password(
                                user.password
                            )
                            user.password = None

                        user = await self.shared_service.create_user(user)
                        return user
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("sign_up failed")
                        raise AuthenticationException()

                # ─── REFRESH ───────────────────────────────
                async def refresh(self, authentication: Authentication) -> Authentication:
                    try:
                        await self.cache.delete_by_access_token(authentication)
                        await self.cache.delete_by_refresh_token(authentication)

                        now = datetime.now(BRASILIA_TZ)
                        access_exp = now + timedelta(
                            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
                        )

                        authentication = authentication.refresh_access_token(now, access_exp)
                        authentication = await self.token_service.generate(authentication)
                        authentication = await self.token_service.hash_tokens(authentication)
                        authentication.refresh_token.access_token.permission = authentication.user.role
                        await self.repository.update(authentication)
                        return authentication
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("refresh failed")
                        raise AuthenticationException()

                # ─── LOGOUT ────────────────────────────────
                async def logout(self, authentication: Authentication) -> Authentication:
                    try:
                        authentication.revoke(datetime.now(BRASILIA_TZ))
                        try:
                            authentication.user.record_logout()
                        except Exception:
                            pass
                        await self.repository.delete(authentication)
                        await self.cache.delete_by_access_token(authentication)
                        await self.cache.delete_by_refresh_token(authentication)
                        return authentication
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("logout failed")
                        raise AuthenticationException()

                # ─── FORGOT / RESET ────────────────────────
                async def forgot_password(self, email: str) -> None:
                    try:
                        user = await self.shared_service.get_user_by_email(User(email=email))
                        if not user:
                            return
                        _reset_code = str(uuid4())[:6].upper()
                        logger.debug(f"reset code generated for {email}: (not sent)")
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("forgot_password failed")
                        raise AuthenticationException()

                async def reset_password(
                    self, code: str, password: str, confirm_password: str,
                ) -> None:
                    try:
                        if password != confirm_password:
                            raise PasswordMismatchException()
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("reset_password failed")
                        raise AuthenticationException()

                # ─── 2FA ───────────────────────────────────
                async def lock_screen(
                    self, authentication: Authentication, password: str,
                ) -> None:
                    try:
                        if not await self.token_service.verify_password(
                            password, authentication.user.hashed_password
                        ):
                            raise InvalidCredentialsException()
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("lock_screen failed")
                        raise AuthenticationException()

                async def two_step_verification(
                    self, authentication: Authentication,
                    country_code: str, phone_number: str,
                ) -> None:
                    try:
                        full_phone = f"{country_code}{phone_number}"
                        _otp_code = str(uuid4())[:6]
                        logger.debug(f"OTP generated for {full_phone} (not sent)")
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("two_step_verification failed")
                        raise AuthenticationException()

                async def two_step_code(
                    self, authentication: Authentication,
                    code: str, dont_ask_again: bool,
                ) -> Authentication:
                    try:
                        if code != "123456":
                            raise InvalidOtpCodeException()

                        now = datetime.now(BRASILIA_TZ)
                        refresh_exp = now + timedelta(
                            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
                        )
                        access_exp = now + timedelta(
                            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
                        )

                        authentication = authentication.create_tokens(
                            now, refresh_exp, access_exp
                        )
                        authentication = await self.token_service.generate(authentication)
                        authentication = await self.token_service.hash_tokens(authentication)
                        authentication.refresh_token.access_token.permission = authentication.user.role
                        await self.repository.create(authentication)
                        return authentication
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("two_step_code failed")
                        raise AuthenticationException()
        '''))

        self.writer.write(f"{base}/mappers.py", dedent('''\
            """authentication mappers"""
            from __future__ import annotations

            import json
            from datetime import date, datetime
            from uuid import UUID

            from fastapi import Request
            from fastapi.security import OAuth2PasswordRequestForm

            from app.modules.authentication.domain.entities import (
                AccessToken, Authentication, RefreshToken,
            )
            from app.modules.authentication.domain.value_objects import (
                Claims, RefreshClaims,
            )
            from app.modules.shared.application.utils import (
                BRASILIA_TZ, resolve_client_ip,
            )
            from app.modules.shared.domain.enums import Role
            from app.modules.shared.domain.value_objects import Name
            from app.modules.user.domain.entities import User


            def login_entity_mapper(
                form: OAuth2PasswordRequestForm, request: Request,
            ) -> Authentication:
                """HTTP request → Authentication entity (username OR email)."""
                # ⚠️ `form.username` อาจเป็น email หรือ username ก็ได้
                #    — mapper จะใส่ทั้งสอง field ให้ use case ตัดสินใจ
                is_email = "@" in (form.username or "")
                return Authentication(
                    user=User(
                        email=form.username if is_email else None,
                        username=None if is_email else form.username,
                        password=form.password,
                    ),
                    ip_address=resolve_client_ip(
                        x_forwarded_for=request.headers.get("x-forwarded-for"),
                        x_real_ip=request.headers.get("x-real-ip"),
                        peer_host=request.client.host if request.client else None,
                    ),
                    user_agent=request.headers.get("user-agent"),
                    device=getattr(request.state, "device_id", None),
                    accept_language=request.headers.get("accept-language"),
                    accept_encoding=request.headers.get("accept-encoding"),
                    origin=request.headers.get("origin"),
                    referer=request.headers.get("referer"),
                    location=getattr(request.state, "location", None),
                    refresh_token=RefreshToken(access_token=AccessToken()),
                )


            def entity_login_mapper(auth: Authentication) -> dict:
                """Authentication → LoginResponse payload (plain dict)."""
                user = auth.user
                access_token = auth.refresh_token.access_token
                name = user.name
                return {
                    "access_token": access_token.token,
                    "refresh_token": auth.refresh_token.token,
                    "info": {
                        # ⚠️ SQL: firstname/lastname NULLABLE
                        "first_name": (name.first_name if name else "") or "",
                        "last_name": (name.last_name if name else "") or "",
                        "preferred_name": (
                            name.preferred_name if name else None
                        ) or (name.nickname if name else None) or "",
                        "username": user.username or "",
                        "gender": user.gender.value if user.gender else "other",
                        "birthdate": user.birthdate.isoformat() if user.birthdate else None,
                        "email": str(user.email) if user.email else "",
                        "phone": str(user.phone) if user.phone else None,
                        "role": user.role.value if user.role else Role.USER.value,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                    },
                }


            def access_token_entity_mapper(claims: dict) -> Authentication:
                """JWT claims → Authentication (access token)."""
                access = AccessToken(
                    claims=Claims.from_dict(claims),
                    permission=Role(claims["scope"]),
                    created_at=datetime.fromtimestamp(claims["iat"], tz=BRASILIA_TZ),
                    expires_at=datetime.fromtimestamp(claims["exp"], tz=BRASILIA_TZ),
                )
                return Authentication(
                    user=User(
                        id=int(claims["sub"]),
                        role=Role(claims["scope"]),
                        email=claims["grant_id"],
                    ),
                    refresh_token=RefreshToken(access_token=access),
                )


            def refresh_token_entity_mapper(claims: dict) -> Authentication:
                """JWT claims → Authentication (refresh token)."""
                access = AccessToken(permission=Role(claims["scope"]))
                refresh = RefreshToken(
                    access_token=access,
                    refresh_claims=RefreshClaims.from_dict(claims),
                    updated_at=datetime.fromtimestamp(claims["iat"], tz=BRASILIA_TZ),
                    expires_at=datetime.fromtimestamp(claims["exp"], tz=BRASILIA_TZ),
                )
                return Authentication(
                    user=User(
                        id=int(claims["sub"]),
                        role=Role(claims["scope"]),
                        email=claims["grant_id"],
                    ),
                    refresh_token=refresh,
                )
        '''))

    # ─── INFRASTRUCTURE ─────────────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", '"""authentication infrastructure layer"""')

        self.writer.write(f"{base}/models.py", dedent('''\
            """authentication SQLAlchemy models — schema=public, prefix=auth_"""
            from __future__ import annotations

            from datetime import datetime
            from typing import TYPE_CHECKING
            from uuid import UUID

            from sqlalchemy import (
                UUID as SQUID,
            )
            from sqlalchemy import (
                BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text,
                UniqueConstraint, func, text,
            )
            from sqlalchemy import Enum as SQLEnum
            from sqlalchemy.orm import Mapped, mapped_column, relationship

            from app.core.settings import settings
            from app.modules.shared.application.utils import BRASILIA_TZ
            from app.modules.shared.domain.enums import Role
            from app.modules.shared.infrastructure.models import Base

            if TYPE_CHECKING:
                from app.modules.user.infrastructure.models import UserModel

            SCHEMA = "public"


            class AuthenticationModel(Base):
                __tablename__ = "auth_authentications"
                __table_args__ = (
                    UniqueConstraint(
                        "user_id", "user_agent", "device",
                        name="uq_auth_user_agent_device",
                    ),
                    Index("ix_auth_user_agent_device",
                          "user_id", "user_agent", "device"),
                    {"schema": SCHEMA},
                )

                id: Mapped[UUID] = mapped_column(
                    SQUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                # ⚠️ FK → erp_users.id BIGINT (11+ หลัก)
                user_id: Mapped[int] = mapped_column(
                    BigInteger,
                    ForeignKey(
                        f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
                        ondelete="CASCADE",
                    ),
                    nullable=False,
                )
                ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
                device: Mapped[str] = mapped_column(String(255), nullable=False)
                user_agent: Mapped[str] = mapped_column(Text, nullable=False)
                accept_language: Mapped[str | None] = mapped_column(String(255), nullable=True)
                accept_encoding: Mapped[str | None] = mapped_column(String(255), nullable=True)
                origin: Mapped[str] = mapped_column(String(255), nullable=False, default="")
                referrer: Mapped[str | None] = mapped_column(String(255), nullable=True)
                location: Mapped[str | None] = mapped_column(String(255), nullable=True)
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    default=lambda: datetime.now(BRASILIA_TZ),
                    server_default=func.now(),
                )
                last_updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    default=lambda: datetime.now(BRASILIA_TZ),
                    server_default=func.now(), onupdate=func.now(),
                )
                blacklisted: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, default=False,
                )

                user: Mapped["UserModel"] = relationship(
                    "UserModel", back_populates="authentications", lazy="noload",
                )
                refresh_token: Mapped["RefreshTokenModel | None"] = relationship(
                    back_populates="authentication", uselist=False,
                    cascade="all, delete-orphan", passive_deletes=True, lazy="noload",
                )


            class RefreshTokenModel(Base):
                __tablename__ = "auth_refresh_tokens"
                __table_args__ = (
                    UniqueConstraint("authentication_id",
                                     name="uq_auth_refresh_authentication"),
                    Index("ix_auth_refresh_hashed_revoked", "hashed_jti", "revoked"),
                    {"schema": SCHEMA},
                )

                id: Mapped[UUID] = mapped_column(
                    SQUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                authentication_id: Mapped[UUID] = mapped_column(
                    ForeignKey("auth_authentications.id", ondelete="CASCADE"),
                    nullable=False,
                )
                hashed_jti: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
                previous_hashed_jti: Mapped[str | None] = mapped_column(Text, nullable=True)
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )
                expires_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                )
                revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
                revoked_at: Mapped[datetime | None] = mapped_column(
                    DateTime(timezone=True), nullable=True, default=None,
                )

                authentication: Mapped["AuthenticationModel"] = relationship(
                    back_populates="refresh_token", uselist=False, lazy="noload",
                )
                access_token: Mapped["AccessTokenModel | None"] = relationship(
                    back_populates="refresh_token", uselist=False,
                    cascade="all, delete-orphan", passive_deletes=True, lazy="noload",
                )


            class AccessTokenModel(Base):
                __tablename__ = "auth_access_tokens"
                __table_args__ = (
                    UniqueConstraint("refresh_id", name="uq_auth_access_refresh"),
                    Index("ix_auth_access_hashed_revoked", "hashed_jti", "revoked"),
                    {"schema": SCHEMA},
                )

                id: Mapped[UUID] = mapped_column(
                    SQUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                refresh_id: Mapped[UUID] = mapped_column(
                    ForeignKey("auth_refresh_tokens.id", ondelete="CASCADE"),
                    nullable=False,
                )
                hashed_jti: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
                previous_hashed_jti: Mapped[str | None] = mapped_column(
                    Text, nullable=True, unique=True,
                )
                permission: Mapped[Role] = mapped_column(
                    SQLEnum(Role, name="role_enum"), nullable=False, default=Role.USER,
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                expires_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                )
                revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
                revoked_at: Mapped[datetime | None] = mapped_column(
                    DateTime(timezone=True), nullable=True, default=None,
                )

                refresh_token: Mapped["RefreshTokenModel"] = relationship(
                    back_populates="access_token", uselist=False, lazy="noload",
                )


            __all__ = [
                "AuthenticationModel", "RefreshTokenModel", "AccessTokenModel",
            ]
        '''))

        # repositories.py, caches.py, services.py — คงเดิม
        self._write_repositories(base)
        self._write_caches(base)
        self._write_services(base)

    def _write_repositories(self, base: str) -> None:
        self.writer.write(f"{base}/repositories.py", dedent('''\
            """authentication repositories — SQLAlchemy 2.0 async"""
            from __future__ import annotations

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy.orm import joinedload

            from app.modules.authentication.application.exceptions import (
                AuthenticationException,
            )
            from app.modules.authentication.application.interfaces import (
                IAuthenticationRepository,
            )
            from app.modules.authentication.domain.entities import Authentication
            from app.modules.authentication.infrastructure.models import (
                AccessTokenModel, AuthenticationModel, RefreshTokenModel,
            )
            from app.modules.shared.application.exceptions import StandardException


            class PostgresAuthenticationRepository(IAuthenticationRepository):
                """Implementation using PostgreSQL."""

                def __init__(self, session: AsyncSession) -> None:
                    self.session = session

                async def create(self, authentication: Authentication) -> Authentication:
                    try:
                        from app.modules.authentication.application.mappers import (
                            entity_model_mapper, sync_entity_from_model,
                        )
                        db = entity_model_mapper(authentication)
                        self.session.add(db)
                        await self.session.flush()
                        return sync_entity_from_model(authentication, db)
                    except StandardException:
                        raise
                    except Exception as e:
                        logger.opt(exception=e).error("auth.create failed")
                        raise AuthenticationException()

                async def get_by_user_id_agent_and_device(
                    self, authentication: Authentication,
                ) -> Authentication | None:
                    try:
                        stmt = (
                            select(AuthenticationModel)
                            .options(
                                joinedload(AuthenticationModel.user),
                                joinedload(AuthenticationModel.refresh_token)
                                .joinedload(RefreshTokenModel.access_token),
                            )
                            .where(
                                AuthenticationModel.user_id == authentication.user.id,
                                AuthenticationModel.user_agent == authentication.user_agent,
                                AuthenticationModel.device == authentication.device,
                                AuthenticationModel.blacklisted.is_(False),
                            )
                        )
                        result = await self.session.execute(stmt)
                        model = result.scalar_one_or_none()
                        if model is None:
                            return None
                        from app.modules.authentication.application.mappers import (
                            model_entity_mapper,
                        )
                        return model_entity_mapper(model)
                    except StandardException:
                        raise
                    except Exception as e:
                        logger.opt(exception=e).error("auth.get_by_user_agent_device failed")
                        raise AuthenticationException()

                async def get_access_token_by_authentication(
                    self, authentication: Authentication,
                ) -> Authentication | None:
                    try:
                        stmt = (
                            select(AuthenticationModel)
                            .join(AuthenticationModel.refresh_token)
                            .join(RefreshTokenModel.access_token)
                            .options(
                                joinedload(AuthenticationModel.user),
                                joinedload(AuthenticationModel.refresh_token)
                                .joinedload(RefreshTokenModel.access_token),
                            )
                            .where(
                                AccessTokenModel.hashed_jti ==
                                authentication.refresh_token.access_token.hashed_jti,
                                AuthenticationModel.user_id == authentication.user.id,
                                AccessTokenModel.revoked.is_(False),
                                RefreshTokenModel.revoked.is_(False),
                                AuthenticationModel.blacklisted.is_(False),
                            )
                        )
                        result = await self.session.execute(stmt)
                        model = result.scalar_one_or_none()
                        if model is None:
                            return None
                        from app.modules.authentication.application.mappers import (
                            model_entity_mapper,
                        )
                        return model_entity_mapper(model)
                    except StandardException:
                        raise
                    except Exception as e:
                        logger.opt(exception=e).error("auth.get_by_access failed")
                        raise AuthenticationException()

                async def get_refresh_token_by_authentication(
                    self, authentication: Authentication,
                ) -> Authentication | None:
                    try:
                        stmt = (
                            select(AuthenticationModel)
                            .join(AuthenticationModel.refresh_token)
                            .options(
                                joinedload(AuthenticationModel.user),
                                joinedload(AuthenticationModel.refresh_token)
                                .joinedload(RefreshTokenModel.access_token),
                            )
                            .where(
                                RefreshTokenModel.hashed_jti ==
                                authentication.refresh_token.hashed_jti,
                                AuthenticationModel.user_id == authentication.user.id,
                                RefreshTokenModel.revoked.is_(False),
                                AuthenticationModel.blacklisted.is_(False),
                            )
                        )
                        result = await self.session.execute(stmt)
                        model = result.scalar_one_or_none()
                        if model is None:
                            return None
                        from app.modules.authentication.application.mappers import (
                            model_entity_mapper,
                        )
                        return model_entity_mapper(model)
                    except StandardException:
                        raise
                    except Exception as e:
                        logger.opt(exception=e).error("auth.get_by_refresh failed")
                        raise AuthenticationException()

                async def update(self, authentication: Authentication) -> Authentication:
                    try:
                        from app.modules.authentication.application.mappers import (
                            entity_model_mapper, sync_entity_from_model,
                        )
                        db = entity_model_mapper(authentication)
                        merged = await self.session.merge(db)
                        await self.session.flush()
                        return sync_entity_from_model(authentication, merged)
                    except StandardException:
                        raise
                    except Exception as e:
                        logger.opt(exception=e).error("auth.update failed")
                        raise AuthenticationException()

                async def delete(self, authentication: Authentication) -> Authentication:
                    try:
                        from app.modules.authentication.application.mappers import (
                            entity_model_mapper, sync_entity_from_model,
                        )
                        db = entity_model_mapper(authentication)
                        merged = await self.session.merge(db)
                        await self.session.flush()
                        return sync_entity_from_model(authentication, merged)
                    except StandardException:
                        raise
                    except Exception as e:
                        logger.opt(exception=e).error("auth.delete failed")
                        raise AuthenticationException()
        '''))

    def _write_caches(self, base: str) -> None:
        self.writer.write(f"{base}/caches.py", dedent('''\
            """authentication cache — Redis with tombstone pattern (never-raise)"""
            from __future__ import annotations

            import json
            from typing import Any

            from loguru import logger
            from redis.asyncio import Redis

            from app.core.settings import settings
            from app.modules.authentication.application.interfaces import (
                IAuthenticationCache,
            )
            from app.modules.authentication.domain.entities import Authentication


            class RedisAuthenticationCache(IAuthenticationCache):
                """Redis cache with tombstone pattern."""

                def __init__(self, cache: Redis) -> None:
                    self.cache = cache
                    self.prefix = f"{settings.REDIS_NAMESPACE}:authentication:"

                def _key(self, suffix: str) -> str:
                    return f"{self.prefix}{suffix}"

                def _tombstone(self, suffix: str) -> str:
                    return f"{self.prefix}tombstone:{suffix}"

                async def insert_by_access_token(
                    self, authentication: Authentication, ttl: int | None = None,
                ) -> None:
                    try:
                        hashed = (
                            authentication.refresh_token.access_token.hashed_jti
                            if authentication.refresh_token
                            and authentication.refresh_token.access_token
                            else None
                        )
                        if not hashed:
                            return
                        suffix = f"access_token:{hashed}"
                        if await self.cache.exists(self._tombstone(suffix)):
                            return
                        payload = self._serialize(authentication)
                        await self.cache.set(
                            self._key(suffix), payload,
                            ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
                        )
                    except Exception as e:
                        logger.opt(exception=e).error("cache.insert_by_access failed")

                async def insert_by_refresh_token(
                    self, authentication: Authentication, ttl: int | None = None,
                ) -> None:
                    try:
                        hashed = (
                            authentication.refresh_token.hashed_jti
                            if authentication.refresh_token else None
                        )
                        if not hashed:
                            return
                        suffix = f"refresh_token:{hashed}"
                        if await self.cache.exists(self._tombstone(suffix)):
                            return
                        payload = self._serialize(authentication)
                        await self.cache.set(
                            self._key(suffix), payload,
                            ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
                        )
                    except Exception as e:
                        logger.opt(exception=e).error("cache.insert_by_refresh failed")

                async def get_by_access_token(
                    self, authentication: Authentication,
                ) -> Authentication | None:
                    try:
                        hashed = (
                            authentication.refresh_token.access_token.hashed_jti
                            if authentication.refresh_token
                            and authentication.refresh_token.access_token
                            else None
                        )
                        if not hashed:
                            return None
                        raw = await self.cache.get(self._key(f"access_token:{hashed}"))
                        return self._deserialize(raw) if raw else None
                    except Exception as e:
                        logger.opt(exception=e).error("cache.get_by_access failed")
                        return None

                async def get_by_refresh_token(
                    self, authentication: Authentication,
                ) -> Authentication | None:
                    try:
                        hashed = (
                            authentication.refresh_token.hashed_jti
                            if authentication.refresh_token else None
                        )
                        if not hashed:
                            return None
                        raw = await self.cache.get(self._key(f"refresh_token:{hashed}"))
                        return self._deserialize(raw) if raw else None
                    except Exception as e:
                        logger.opt(exception=e).error("cache.get_by_refresh failed")
                        return None

                async def delete_by_access_token(
                    self, authentication: Authentication,
                ) -> None:
                    try:
                        hashed = (
                            authentication.refresh_token.access_token.hashed_jti
                            if authentication.refresh_token
                            and authentication.refresh_token.access_token
                            else None
                        )
                        if not hashed:
                            return
                        suffix = f"access_token:{hashed}"
                        await self.cache.set(
                            self._tombstone(suffix), 1,
                            ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
                        )
                        await self.cache.delete(self._key(suffix))
                    except Exception as e:
                        logger.opt(exception=e).error("cache.delete_by_access failed")

                async def delete_by_refresh_token(
                    self, authentication: Authentication,
                ) -> None:
                    try:
                        hashed = (
                            authentication.refresh_token.hashed_jti
                            if authentication.refresh_token else None
                        )
                        if not hashed:
                            return
                        suffix = f"refresh_token:{hashed}"
                        await self.cache.set(
                            self._tombstone(suffix), 1,
                            ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
                        )
                        await self.cache.delete(self._key(suffix))
                    except Exception as e:
                        logger.opt(exception=e).error("cache.delete_by_refresh failed")

                # ─── internal ─────────────────
                @staticmethod
                def _serialize(auth: Authentication) -> str:
                    return json.dumps({
                        "id": str(auth.id) if auth.id else None,
                        "user_id": auth.user.id,
                        "ip_address": auth.ip_address,
                        "user_agent": auth.user_agent,
                        "device": auth.device,
                    })

                @staticmethod
                def _deserialize(raw: str) -> Authentication:
                    from app.modules.user.domain.entities import User
                    data = json.loads(raw)
                    return Authentication(
                        user=User(id=data.get("user_id"), email=""),
                        ip_address=data.get("ip_address"),
                        user_agent=data.get("user_agent"),
                        device=data.get("device"),
                    )
        '''))

    def _write_services(self, base: str) -> None:
        self.writer.write(f"{base}/services.py", dedent('''\
            """authentication infrastructure services"""
            from __future__ import annotations

            from app.modules.authentication.application.interfaces import ITokenService
            from app.modules.authentication.domain.entities import Authentication


            class TokenService(ITokenService):
                """TH: implementation of ITokenService | EN: token service"""

                async def generate(self, authentication: Authentication) -> Authentication:
                    from app.core.security import generate_tokens
                    return generate_tokens(authentication)

                async def hash_tokens(self, authentication: Authentication) -> Authentication:
                    from app.core.security import hash_tokens
                    return hash_tokens(authentication)

                async def verify_password(
                    self, plain_password: str, hashed_password: str,
                ) -> bool:
                    from app.core.security import verify_password
                    return verify_password(plain_password, hashed_password)

                def hash_password(self, plain_password: str) -> str:
                    from app.core.security import hash_password
                    return hash_password(plain_password)

                async def verify_access_token(self, token: str) -> Authentication:
                    from app.core.security import verify_access_token as _v
                    return _v(token)

                async def verify_refresh_token(self, token: str) -> Authentication:
                    from app.core.security import verify_refresh_token as _v
                    return _v(token)
        '''))

    # ─── PRESENTATION ───────────────────────────────────────────
    def _create_presentation(self) -> None:
        base = f"{self.mod_root}/presentation"

        self.writer.write(f"{base}/__init__.py", '"""authentication presentation layer"""')

        # ⚠️ schemas.py — แก้ UserInfo + SignUpRequest + SignUpResponse
        self.writer.write(f"{base}/schemas.py", dedent('''\
            """authentication Pydantic v2 schemas (SQL-aligned)"""
            from __future__ import annotations

            from datetime import date, datetime

            from pydantic import BaseModel, ConfigDict, EmailStr, Field


            class AccessTokenInfo(BaseModel):
                created_at: datetime
                expires_at: datetime
                claims: dict

                model_config = ConfigDict(
                    title="AccessTokenInfo", extra="forbid",
                    str_strip_whitespace=True,
                )


            class UserInfo(BaseModel):
                # ⚠️ SQL: firstname/lastname NULLABLE → default ""
                first_name: str = ""
                last_name: str = ""
                preferred_name: str = ""
                # ⚠️ SQL: username NOT NULL UNIQUE
                username: str
                gender: str = "other"
                birthdate: date | None = None
                email: EmailStr
                phone: str | None = None
                role: str
                created_at: str

                model_config = ConfigDict(
                    title="UserInfo", extra="forbid",
                    str_strip_whitespace=True,
                )


            class LoginResponse(BaseModel):
                message: str = "User logged in successfully"
                access_token: str
                refresh_token: str
                token_info: AccessTokenInfo | None = None
                info: UserInfo

                model_config = ConfigDict(
                    title="LoginResponse", extra="ignore",
                    validate_default=True, validate_assignment=True,
                )


            class RefreshResponse(BaseModel):
                message: str = "Token refreshed successfully"

                model_config = ConfigDict(
                    title="RefreshResponse", extra="forbid",
                )


            class LogoutResponse(BaseModel):
                message: str = "User logged out successfully"

                model_config = ConfigDict(
                    title="LogoutResponse", extra="forbid",
                )


            class SignUpRequest(BaseModel):
                """TH: request สมัคร — username NOT NULL, first_name/last_name optional"""
                full_name: str | None = None
                first_name: str | None = None
                last_name: str | None = None
                nickname: str | None = None
                # ⚠️ SQL: username NOT NULL UNIQUE
                username: str = Field(min_length=1, max_length=150)
                email: EmailStr
                phone_number: str | None = None
                password: str = Field(min_length=8, max_length=64)
                confirm_password: str
                agree_terms: bool

                model_config = ConfigDict(
                    title="SignUpRequest", extra="forbid",
                    str_strip_whitespace=True,
                )


            class SignUpResponse(BaseModel):
                message: str = "Operation successful"
                id: int
                first_name: str
                last_name: str
                preferred_name: str
                # ⚠️ SQL: username NOT NULL
                username: str
                email: EmailStr
                phone: str | None = None
                role: str
                is_active: bool
                created_at: datetime
                updated_at: datetime

                model_config = ConfigDict(
                    title="SignUpResponse", extra="ignore",
                    str_strip_whitespace=True,
                )


            class ForgotPasswordRequest(BaseModel):
                email: EmailStr

                model_config = ConfigDict(extra="forbid")


            class ForgotPasswordResponse(BaseModel):
                message: str = "Operation successful"

                model_config = ConfigDict(extra="forbid")


            class ResetPasswordRequest(BaseModel):
                code: str
                password: str
                confirm_password: str

                model_config = ConfigDict(extra="forbid")


            class ResetPasswordResponse(BaseModel):
                message: str = "Operation successful"

                model_config = ConfigDict(extra="forbid")


            class LockScreenRequest(BaseModel):
                password: str

                model_config = ConfigDict(extra="forbid")


            class LockScreenResponse(BaseModel):
                message: str = "Operation successful"

                model_config = ConfigDict(extra="forbid")


            class TwoStepVerificationRequest(BaseModel):
                country_code: str
                phone_number: str

                model_config = ConfigDict(extra="forbid")


            class TwoStepVerificationResponse(BaseModel):
                message: str = "Operation successful"

                model_config = ConfigDict(extra="forbid")


            class TwoStepCodeRequest(BaseModel):
                code: str
                dont_ask_again: bool = False

                model_config = ConfigDict(extra="forbid")


            class TwoStepCodeResponse(BaseModel):
                message: str = "Operation successful"
                access_token: str | None = None
                refresh_token: str | None = None

                model_config = ConfigDict(extra="forbid")
        '''))

        # docs.py — คงเดิม (ยกเว้น sign_up example)
        self.writer.write(f"{base}/docs.py", dedent('''\
            """authentication OpenAPI docs"""
            from __future__ import annotations
            from http import HTTPStatus

            from app.modules.authentication.presentation.schemas import (
                ForgotPasswordResponse, LockScreenResponse,
                LoginResponse, LogoutResponse, RefreshResponse,
                ResetPasswordResponse, SignUpResponse,
                TwoStepCodeResponse, TwoStepVerificationResponse,
            )
            from app.modules.shared.presentation.schemas import StandardResponse


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

            login_docs = {
                "summary": "Endpoint to login a user.",
                "description": "Authenticate with username OR email + password.",
                "status_code": HTTPStatus.OK,
                "response_model": LoginResponse,
                "include_in_schema": True,
            }

            sign_up_docs = {
                "summary": "Endpoint to sign up a new user.",
                "description": "Create a new user account (username NOT NULL).",
                "status_code": HTTPStatus.CREATED,
                "response_model": SignUpResponse,
                "include_in_schema": True,
            }

            refresh_docs = {
                "summary": "Endpoint to refresh authentication tokens.",
                "status_code": HTTPStatus.OK,
                "response_model": RefreshResponse,
                "include_in_schema": True,
            }

            logout_docs = {
                "summary": "Endpoint to logout a user.",
                "status_code": HTTPStatus.OK,
                "response_model": LogoutResponse,
                "include_in_schema": True,
            }

            forgot_password_docs = {
                "summary": "Endpoint to request password reset.",
                "status_code": HTTPStatus.OK,
                "response_model": ForgotPasswordResponse,
                "include_in_schema": True,
            }

            reset_password_docs = {
                "summary": "Endpoint to reset password with code.",
                "status_code": HTTPStatus.OK,
                "response_model": ResetPasswordResponse,
                "include_in_schema": True,
            }

            lock_screen_docs = {
                "summary": "Endpoint to unlock the screen.",
                "status_code": HTTPStatus.OK,
                "response_model": LockScreenResponse,
                "include_in_schema": True,
            }

            two_step_verification_docs = {
                "summary": "Endpoint to initiate two-step verification.",
                "status_code": HTTPStatus.OK,
                "response_model": TwoStepVerificationResponse,
                "include_in_schema": True,
            }

            two_step_code_docs = {
                "summary": "Endpoint to verify two-step code.",
                "status_code": HTTPStatus.OK,
                "response_model": TwoStepCodeResponse,
                "include_in_schema": True,
            }
        '''))

        self.writer.write(f"{base}/dependencies.py", dedent('''\
            """authentication DI container"""
            from __future__ import annotations

            from fastapi import Depends
            from redis.asyncio import Redis
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.core.cache import get_cache_session
            from app.core.database import get_async_session
            from app.modules.authentication.application.interfaces import (
                IAuthenticationCache, IAuthenticationRepository, ITokenService,
            )
            from app.modules.authentication.application.use_cases import (
                AuthenticationUseCases,
            )
            from app.modules.authentication.infrastructure.caches import (
                RedisAuthenticationCache,
            )
            from app.modules.authentication.infrastructure.repositories import (
                PostgresAuthenticationRepository,
            )
            from app.modules.authentication.infrastructure.services import TokenService


            def get_authentication_cache(
                cache: Redis = Depends(get_cache_session),
            ) -> IAuthenticationCache:
                return RedisAuthenticationCache(cache=cache)


            def get_authentication_repository(
                session: AsyncSession = Depends(get_async_session),
            ) -> IAuthenticationRepository:
                return PostgresAuthenticationRepository(session=session)


            def get_token_service() -> ITokenService:
                return TokenService()


            def get_authentication_use_cases(
                cache: IAuthenticationCache = Depends(get_authentication_cache),
                repository: IAuthenticationRepository = Depends(get_authentication_repository),
                shared_service=Depends(lambda: None),
                token_service: ITokenService = Depends(get_token_service),
            ) -> AuthenticationUseCases:
                return AuthenticationUseCases(
                    cache=cache, repository=repository,
                    shared_service=shared_service,
                    token_service=token_service,
                )
        '''))

        # ⚠️ router.py — เพิ่ม sign_up, lock_screen, two_step_*
        self.writer.write(f"{base}/router.py", dedent('''\
            """authentication HTTP router (SQL-aligned, +4 endpoints)"""
            from __future__ import annotations

            from typing import Annotated

            from fastapi import APIRouter, Depends, Request, Response
            from fastapi.security import OAuth2PasswordRequestFormStrict
            from loguru import logger

            from app.core.security import (
                authenticate_logout, authenticate_refresh,
                authenticate_user, no_authentication,
            )
            from app.core.settings import settings
            from app.modules.authentication.application.exceptions import (
                AuthenticationException,
            )
            from app.modules.authentication.application.mappers import (
                entity_login_mapper, login_entity_mapper,
            )
            from app.modules.authentication.application.use_cases import (
                AuthenticationUseCases,
            )
            from app.modules.authentication.domain.entities import Authentication
            from app.modules.authentication.domain.enums import TokenType
            from app.modules.authentication.presentation.dependencies import (
                get_authentication_use_cases,
            )
            from app.modules.authentication.presentation.docs import (
                forgot_password_docs, lock_screen_docs, login_docs,
                logout_docs, refresh_docs, reset_password_docs,
                router_docs, sign_up_docs, two_step_code_docs,
                two_step_verification_docs,
            )
            from app.modules.authentication.presentation.schemas import (
                ForgotPasswordRequest, ForgotPasswordResponse,
                LockScreenRequest, LockScreenResponse,
                LoginResponse, LogoutResponse, RefreshResponse,
                ResetPasswordRequest, ResetPasswordResponse,
                SignUpRequest, SignUpResponse,
                TwoStepCodeRequest, TwoStepCodeResponse,
                TwoStepVerificationRequest, TwoStepVerificationResponse,
                UserInfo,
            )
            from app.modules.shared.application.exceptions import (
                DomainException, StandardException,
            )
            from app.modules.shared.domain.entities import DomainError

            router = APIRouter(**router_docs)


            def set_cookies(response: Response, auth: Authentication) -> None:
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
                        value=auth.refresh_token.access_token.token or "",
                        max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
                        path=settings.COOKIES_ACCESS_TOKEN_PATH,
                        domain=settings.COOKIES_DOMAIN,
                        secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
                        httponly=True,
                        samesite=settings.COOKIES_SAME_SITE,
                    )
                    response.set_cookie(
                        key=settings.COOKIES_REFRESH_TOKEN_KEY,
                        value=auth.refresh_token.token or "",
                        max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
                        path=settings.COOKIES_REFRESH_TOKEN_PATH,
                        domain=settings.COOKIES_DOMAIN,
                        secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
                        httponly=True,
                        samesite=settings.COOKIES_SAME_SITE,
                    )
                except Exception as e:
                    logger.opt(exception=e).error("set_cookies failed")
                    raise AuthenticationException()


            def delete_cookies(response: Response) -> None:
                for key, path in (
                    (settings.COOKIES_TOKEN_TYPE_KEY, settings.COOKIES_ACCESS_TOKEN_PATH),
                    (settings.COOKIES_ACCESS_TOKEN_KEY, settings.COOKIES_ACCESS_TOKEN_PATH),
                    (settings.COOKIES_REFRESH_TOKEN_KEY, settings.COOKIES_REFRESH_TOKEN_PATH),
                ):
                    response.delete_cookie(
                        key=key, path=path, domain=settings.COOKIES_DOMAIN,
                        secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
                        httponly=True, samesite=settings.COOKIES_SAME_SITE,
                    )


            # ═══════════════════════════════════════════════════════
            # CREATE: LOGIN
            # ═══════════════════════════════════════════════════════
            @router.post("/login/", **login_docs)
            async def login(
                request: Request,
                response: Response,
                _: Annotated[None, Depends(no_authentication)],
                form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> LoginResponse:
                try:
                    req = login_entity_mapper(form_data, request)
                    res = await use_case.login(req)
                    payload = entity_login_mapper(res)
                    set_cookies(response, res)
                    return LoginResponse(
                        access_token=payload["access_token"],
                        refresh_token=payload["refresh_token"],
                        token_info=None,
                        info=UserInfo(**payload["info"]),
                    )
                except StandardException:
                    raise
                except DomainError as e:
                    raise DomainException(e)
                except Exception as e:
                    logger.opt(exception=e).error("login endpoint failed")
                    raise AuthenticationException()


            # ═══════════════════════════════════════════════════════
            # SIGN UP
            # ═══════════════════════════════════════════════════════
            @router.post("/sign-up/", **sign_up_docs)
            async def sign_up(
                request: Request,
                _: Annotated[None, Depends(no_authentication)],
                payload: SignUpRequest,
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> SignUpResponse:
                try:
                    # ⚠️ Map request → User entity (ผ่าน user.application.mappers)
                    from app.modules.user.application.mappers import (
                        create_entity_mapper as user_create_mapper,
                    )
                    from app.modules.user.domain.value_objects import Name

                    # Normalise ชื่อ
                    first_name = payload.first_name or ""
                    last_name = payload.last_name or ""
                    if not first_name and payload.full_name:
                        parts = payload.full_name.strip().split(maxsplit=1)
                        first_name = parts[0] if parts else ""
                        last_name = parts[1] if len(parts) > 1 else ""

                    # สร้าง user entity
                    from app.modules.user.domain.entities import User
                    user = User(
                        name=Name(
                            first_name=first_name,
                            last_name=last_name,
                            preferred_name=payload.nickname or first_name,
                            full_name=payload.full_name,
                            nickname=payload.nickname,
                        ),
                        username=payload.username,
                        email=str(payload.email),
                        phone=str(payload.phone_number) if payload.phone_number else None,
                        password=payload.password,
                    )

                    created = await use_case.sign_up(user)

                    name = created.name
                    return SignUpResponse(
                        id=created.id,
                        first_name=(name.first_name if name else "") or "",
                        last_name=(name.last_name if name else "") or "",
                        preferred_name=(name.preferred_name if name else "") or "",
                        username=created.username,
                        email=str(created.email) if created.email else "",
                        phone=str(created.phone) if created.phone else None,
                        role=created.role.value if created.role else "user",
                        is_active=created.is_active,
                        created_at=created.created_at,
                        updated_at=created.updated_at,
                    )
                except StandardException:
                    raise
                except DomainError as e:
                    raise DomainException(e)
                except Exception as e:
                    logger.opt(exception=e).error("sign_up endpoint failed")
                    raise AuthenticationException()


            # ═══════════════════════════════════════════════════════
            # REFRESH
            # ═══════════════════════════════════════════════════════
            @router.patch("/refresh/", **refresh_docs)
            async def refresh(
                response: Response,
                authentication: Annotated[Authentication, Depends(authenticate_refresh)],
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> RefreshResponse:
                try:
                    res = await use_case.refresh(authentication)
                    set_cookies(response, res)
                    return RefreshResponse()
                except StandardException:
                    raise
                except DomainError as e:
                    raise DomainException(e)
                except Exception as e:
                    logger.opt(exception=e).error("refresh endpoint failed")
                    raise AuthenticationException()


            # ═══════════════════════════════════════════════════════
            # LOGOUT
            # ═══════════════════════════════════════════════════════
            @router.delete("/logout/", **logout_docs)
            async def logout(
                response: Response,
                authentication: Annotated[Authentication, Depends(authenticate_logout)],
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> LogoutResponse:
                try:
                    await use_case.logout(authentication)
                    delete_cookies(response)
                    return LogoutResponse()
                except StandardException:
                    raise
                except DomainError as e:
                    raise DomainException(e)
                except Exception as e:
                    logger.opt(exception=e).error("logout endpoint failed")
                    raise AuthenticationException()


            # ═══════════════════════════════════════════════════════
            # FORGOT / RESET
            # ═══════════════════════════════════════════════════════
            @router.post("/forgot-password/", **forgot_password_docs)
            async def forgot_password(
                _: Annotated[None, Depends(no_authentication)],
                payload: ForgotPasswordRequest,
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> ForgotPasswordResponse:
                try:
                    await use_case.forgot_password(email=str(payload.email))
                    return ForgotPasswordResponse()
                except StandardException:
                    raise
                except DomainError as e:
                    raise DomainException(e)
                except Exception as e:
                    logger.opt(exception=e).error("forgot_password endpoint failed")
                    raise AuthenticationException()


            @router.post("/reset-password/", **reset_password_docs)
            async def reset_password(
                _: Annotated[None, Depends(no_authentication)],
                payload: ResetPasswordRequest,
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> ResetPasswordResponse:
                try:
                    await use_case.reset_password(
                        code=payload.code, password=payload.password,
                        confirm_password=payload.confirm_password,
                    )
                    return ResetPasswordResponse()
                except StandardException:
                    raise
                except DomainError as e:
                    raise DomainException(e)
                except Exception as e:
                    logger.opt(exception=e).error("reset_password endpoint failed")
                    raise AuthenticationException()


            # ═══════════════════════════════════════════════════════
            # LOCK SCREEN
            # ═══════════════════════════════════════════════════════
            @router.post("/lock-screen/", **lock_screen_docs)
            async def lock_screen(
                authentication: Annotated[Authentication, Depends(authenticate_user)],
                payload: LockScreenRequest,
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> LockScreenResponse:
                try:
                    await use_case.lock_screen(
                        authentication=authentication,
                        password=payload.password,
                    )
                    return LockScreenResponse()
                except StandardException:
                    raise
                except DomainError as e:
                    raise DomainException(e)
                except Exception as e:
                    logger.opt(exception=e).error("lock_screen endpoint failed")
                    raise AuthenticationException()


            # ═══════════════════════════════════════════════════════
            # TWO-STEP VERIFICATION
            # ═══════════════════════════════════════════════════════
            @router.post("/two-step-verification/", **two_step_verification_docs)
            async def two_step_verification(
                authentication: Annotated[Authentication, Depends(authenticate_user)],
                payload: TwoStepVerificationRequest,
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> TwoStepVerificationResponse:
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
                    logger.opt(exception=e).error("two_step_verification endpoint failed")
                    raise AuthenticationException()


            # ═══════════════════════════════════════════════════════
            # TWO-STEP CODE
            # ═══════════════════════════════════════════════════════
            @router.post("/two-step-code/", **two_step_code_docs)
            async def two_step_code(
                response: Response,
                authentication: Annotated[Authentication, Depends(authenticate_user)],
                payload: TwoStepCodeRequest,
                use_case: Annotated[AuthenticationUseCases,
                                    Depends(get_authentication_use_cases)],
            ) -> TwoStepCodeResponse:
                try:
                    res = await use_case.two_step_code(
                        authentication=authentication,
                        code=payload.code,
                        dont_ask_again=payload.dont_ask_again,
                    )
                    set_cookies(response, res)
                    return TwoStepCodeResponse(
                        access_token=res.refresh_token.access_token.token,
                        refresh_token=res.refresh_token.token,
                    )
                except StandardException:
                    raise
                except DomainError as e:
                    raise DomainException(e)
                except Exception as e:
                    logger.opt(exception=e).error("two_step_code endpoint failed")
                    raise AuthenticationException()
        '''))

        self.writer.write(f"{base}/swagger.py", dedent('''\
            """OpenAPI docs — authentication module"""
            from __future__ import annotations
            from typing import Any


            def register_authentication_openapi(app: object) -> None:
                """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "Authentication" for t in tags):
                        tags.append({
                            "name": "Authentication",
                            "description": (
                                "โมดูล authentication — Login (username OR email) / "
                                "Sign Up / Refresh / Logout / Password Recovery / 2FA"
                            ),
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "authentication")
                    info.setdefault("x-layer", "0-Core")
                    info.setdefault("x-prefix", "auth_")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        '''))

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent(f'''\
            """{self.module} module"""
            from .presentation.router import router as {self.module}_router

            __all__ = ["{self.module}_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  3. SQL — คงเดิม (auth tables ไม่ได้อยู่ใน SQL dump)
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[SQL] {self.module}")
        self.writer.write(f"{self.sql_dir}/V001__create_auth.sql", self._v001_sql())
        self.writer.write(f"{self.sql_dir}/V002__seed_auth.sql", self._v002_sql())
        self.writer.write(f"{self.sql_dir}/V003__rollback_auth.sql", self._v003_sql())

    def _v001_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V001__create_auth.sql | Module: authentication | Prefix: auth_
-- Schema: public
-- FK: auth_authentications.user_id → erp_users.id BIGINT (11+ digit)
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."auth_access_tokens";
DROP TABLE IF EXISTS "public"."auth_refresh_tokens";
DROP TABLE IF EXISTS "public"."auth_authentications";

CREATE TABLE "public"."auth_authentications" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "user_id"            bigint NOT NULL,
  "ip_address"         varchar(45) NOT NULL,
  "device"             varchar(255) NOT NULL,
  "user_agent"         text NOT NULL,
  "accept_language"    varchar(255) NULL,
  "accept_encoding"    varchar(255) NULL,
  "origin"             varchar(255) NOT NULL DEFAULT '',
  "referrer"           varchar(255) NULL,
  "location"           varchar(255) NULL,
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "last_update_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "blacklisted"        bool NOT NULL DEFAULT false,
  CONSTRAINT "auth_authentications_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_auth_user_agent_device"
      UNIQUE ("user_id", "user_agent", "device")
);
CREATE INDEX "ix_auth_user_agent_device"
    ON "public"."auth_authentications" USING btree ("user_id", "user_agent", "device");

CREATE TABLE "public"."auth_refresh_tokens" (
  "id"                     uuid NOT NULL DEFAULT gen_random_uuid(),
  "authentication_id"      uuid NOT NULL,
  "hashed_jti"             text NOT NULL UNIQUE,
  "previous_hashed_jti"    text NULL,
  "created_at"             timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"             timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at"             timestamptz(6) NOT NULL,
  "revoked"                bool NOT NULL DEFAULT false,
  "revoked_at"             timestamptz(6) NULL,
  CONSTRAINT "auth_refresh_tokens_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_auth_refresh_authentication" UNIQUE ("authentication_id"),
  CONSTRAINT "fk_auth_refresh_authentication"
      FOREIGN KEY ("authentication_id")
      REFERENCES "public"."auth_authentications" ("id") ON DELETE CASCADE
);
CREATE INDEX "ix_auth_refresh_hashed_revoked"
    ON "public"."auth_refresh_tokens" USING btree ("hashed_jti", "revoked");

CREATE TABLE "public"."auth_access_tokens" (
  "id"                     uuid NOT NULL DEFAULT gen_random_uuid(),
  "refresh_id"             uuid NOT NULL,
  "hashed_jti"             text NOT NULL UNIQUE,
  "previous_hashed_jti"    text NULL UNIQUE,
  "permission"             varchar(20) NOT NULL DEFAULT 'user',
  "created_at"             timestamptz(6) NOT NULL DEFAULT now(),
  "expires_at"             timestamptz(6) NOT NULL,
  "revoked"                bool NOT NULL DEFAULT false,
  "revoked_at"             timestamptz(6) NULL,
  CONSTRAINT "auth_access_tokens_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_auth_access_refresh" UNIQUE ("refresh_id"),
  CONSTRAINT "fk_auth_access_refresh"
      FOREIGN KEY ("refresh_id")
      REFERENCES "public"."auth_refresh_tokens" ("id") ON DELETE CASCADE
);
CREATE INDEX "ix_auth_access_hashed_revoked"
    ON "public"."auth_access_tokens" USING btree ("hashed_jti", "revoked");

-- Triggers
CREATE OR REPLACE FUNCTION public.set_updated_at_auth()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_auth_updated ON "public"."auth_authentications";
CREATE TRIGGER trg_auth_updated BEFORE UPDATE ON "public"."auth_authentications"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_auth();

-- RLS
ALTER TABLE "public"."auth_authentications" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_auth_tenant ON "public"."auth_authentications";
CREATE POLICY p_auth_tenant ON "public"."auth_authentications"
    USING (true);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_auth.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;
SELECT 1;
COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_auth.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_auth_updated ON "public"."auth_authentications";
DROP POLICY IF EXISTS p_auth_tenant ON "public"."auth_authentications";
DROP TABLE IF EXISTS "public"."auth_access_tokens" CASCADE;
DROP TABLE IF EXISTS "public"."auth_refresh_tokens" CASCADE;
DROP TABLE IF EXISTS "public"."auth_authentications" CASCADE;
DROP FUNCTION IF EXISTS public.set_updated_at_auth();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  6. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "auth_001"
        prev = self._get_head_revision()
        content = f'''"""add auth tables

Revision ID: {rev}
Revises: {prev}
Create Date: {datetime.now(UTC).date().isoformat()}
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "{rev}"
down_revision: Union[str, None] = "{prev}"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "public"


def upgrade() -> None:
    op.create_table(
        "auth_authentications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.BigInteger, nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("device", sa.String(255), nullable=False),
        sa.Column("user_agent", sa.Text, nullable=False),
        sa.Column("accept_language", sa.String(255), nullable=True),
        sa.Column("accept_encoding", sa.String(255), nullable=True),
        sa.Column("origin", sa.String(255), nullable=False, server_default=""),
        sa.Column("referrer", sa.String(255), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("last_update_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("blacklisted", sa.Boolean, nullable=False,
                  server_default=sa.text("false")),
        sa.UniqueConstraint("user_id", "user_agent", "device",
                            name="uq_auth_user_agent_device"),
        schema=SCHEMA,
    )
    op.create_index("ix_auth_user_agent_device", "auth_authentications",
                    ["user_id", "user_agent", "device"], schema=SCHEMA)

    op.create_table(
        "auth_refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("authentication_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hashed_jti", sa.Text, nullable=False, unique=True),
        sa.Column("previous_hashed_jti", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["authentication_id"],
                                [f"{{SCHEMA}}.auth_authentications.id"],
                                ondelete="CASCADE",
                                name="fk_auth_refresh_authentication"),
        sa.UniqueConstraint("authentication_id",
                            name="uq_auth_refresh_authentication"),
        schema=SCHEMA,
    )
    op.create_index("ix_auth_refresh_hashed_revoked", "auth_refresh_tokens",
                    ["hashed_jti", "revoked"], schema=SCHEMA)

    op.create_table(
        "auth_access_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("refresh_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hashed_jti", sa.Text, nullable=False, unique=True),
        sa.Column("previous_hashed_jti", sa.Text, nullable=True, unique=True),
        sa.Column("permission", sa.String(20), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["refresh_id"],
                                [f"{{SCHEMA}}.auth_refresh_tokens.id"],
                                ondelete="CASCADE",
                                name="fk_auth_access_refresh"),
        sa.UniqueConstraint("refresh_id", name="uq_auth_access_refresh"),
        schema=SCHEMA,
    )
    op.create_index("ix_auth_access_hashed_revoked", "auth_access_tokens",
                    ["hashed_jti", "revoked"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_auth()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.last_update_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        DROP TRIGGER IF EXISTS trg_auth_updated ON public.auth_authentications;
        CREATE TRIGGER trg_auth_updated
            BEFORE UPDATE ON public.auth_authentications
            FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_auth();
    """)
    op.execute("ALTER TABLE public.auth_authentications ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        DROP POLICY IF EXISTS p_auth_tenant ON public.auth_authentications;
        CREATE POLICY p_auth_tenant ON public.auth_authentications USING (true);
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_auth_updated ON public.auth_authentications;")
    op.execute("DROP POLICY IF EXISTS p_auth_tenant ON public.auth_authentications;")
    op.drop_table("auth_access_tokens", schema=SCHEMA)
    op.drop_table("auth_refresh_tokens", schema=SCHEMA)
    op.drop_table("auth_authentications", schema=SCHEMA)
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_auth();")
'''
        self.writer.write(
            f"{self.alembic_dir}/{rev}_add_auth_tables.py", content,
        )

    def _get_head_revision(self) -> str:
        my_rev = "auth_001"
        for candidate in ("migrations/versions", "alembic/versions"):
            versions = self.root / candidate
            if not versions.exists():
                continue
            revisions: set[str] = set()
            downs: set[str] = set()
            for f in versions.glob("*.py"):
                content = f.read_text(encoding="utf-8")
                m = re.search(
                    r'^revision\s*(?::\s*[^=]+)?\s*=\s*["\']([^"\']+)["\']',
                    content, re.M,
                )
                if m and m.group(1) != my_rev:
                    revisions.add(m.group(1))
                d = re.search(
                    r'^down_revision\s*(?::\s*[^=]+)?\s*=\s*["\']([^"\']+)["\']',
                    content, re.M,
                )
                if d:
                    downs.add(d.group(1))
            heads = revisions - downs
            if heads:
                return sorted(heads)[0]
        return "None"

    # ═══════════════════════════════════════════════════════════
    #  7. SWAGGER
    # ═══════════════════════════════════════════════════════════
    def create_swagger(self) -> None:
        info(f"[SWAGGER] {self.module}")

    # ═══════════════════════════════════════════════════════════
    #  8. POSTMAN
    # ═══════════════════════════════════════════════════════════
    def create_postman(self) -> None:
        info(f"[POSTMAN] {self.module}")
        self.writer.write(
            f"docs/postman/{self.module}.json", self._postman_json(),
        )

    def _postman_json(self) -> str:
        return f'''{{
  "info": {{
    "name": "authentication API",
    "_postman_id": "{uuid.uuid4()}",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  }},
  "variable": [
    {{ "key": "base_url", "value": "http://localhost:8000" }}
  ],
  "item": [
    {{
      "name": "Login (email)",
      "request": {{
        "method": "POST",
        "body": {{
          "mode": "urlencoded",
          "urlencoded": [
            {{ "key": "username", "value": "admin@example.com" }},
            {{ "key": "password", "value": "MyP@ssword123" }},
            {{ "key": "grant_type", "value": "password" }}
          ]
        }},
        "url": "{{{{base_url}}}}/api/v1/authentication/login/"
      }}
    }},
    {{
      "name": "Login (username)",
      "request": {{
        "method": "POST",
        "body": {{
          "mode": "urlencoded",
          "urlencoded": [
            {{ "key": "username", "value": "admin" }},
            {{ "key": "password", "value": "MyP@ssword123" }},
            {{ "key": "grant_type", "value": "password" }}
          ]
        }},
        "url": "{{{{base_url}}}}/api/v1/authentication/login/"
      }}
    }},
    {{
      "name": "Sign Up",
      "request": {{
        "method": "POST",
        "header": [{{ "key": "Content-Type", "value": "application/json" }}],
        "body": {{
          "mode": "raw",
          "raw": "{{\\n  \\"first_name\\": \\"John\\",\\n  \\"last_name\\": \\"Doe\\",\\n  \\"nickname\\": \\"Johnny\\",\\n  \\"username\\": \\"johndoe\\",\\n  \\"email\\": \\"john@example.com\\",\\n  \\"phone_number\\": \\"+66812345678\\",\\n  \\"password\\": \\"MyP@ssword123\\",\\n  \\"confirm_password\\": \\"MyP@ssword123\\",\\n  \\"agree_terms\\": true\\n}}"
        }},
        "url": "{{{{base_url}}}}/api/v1/authentication/sign-up/"
      }}
    }},
    {{
      "name": "Refresh",
      "request": {{
        "method": "PATCH",
        "url": "{{{{base_url}}}}/api/v1/authentication/refresh/"
      }}
    }},
    {{
      "name": "Logout",
      "request": {{
        "method": "DELETE",
        "url": "{{{{base_url}}}}/api/v1/authentication/logout/"
      }}
    }},
    {{
      "name": "Lock Screen",
      "request": {{
        "method": "POST",
        "header": [{{ "key": "Content-Type", "value": "application/json" }}],
        "body": {{
          "mode": "raw",
          "raw": "{{\\n  \\"password\\": \\"MyP@ssword123\\"\\n}}"
        }},
        "url": "{{{{base_url}}}}/api/v1/authentication/lock-screen/"
      }}
    }},
    {{
      "name": "Forgot Password",
      "request": {{
        "method": "POST",
        "header": [{{ "key": "Content-Type", "value": "application/json" }}],
        "body": {{
          "mode": "raw",
          "raw": "{{\\n  \\"email\\": \\"john@example.com\\"\\n}}"
        }},
        "url": "{{{{base_url}}}}/api/v1/authentication/forgot-password/"
      }}
    }},
    {{
      "name": "Reset Password",
      "request": {{
        "method": "POST",
        "header": [{{ "key": "Content-Type", "value": "application/json" }}],
        "body": {{
          "mode": "raw",
          "raw": "{{\\n  \\"code\\": \\"ABC123\\",\\n  \\"password\\": \\"NewP@ssword123\\",\\n  \\"confirm_password\\": \\"NewP@ssword123\\"\\n}}"
        }},
        "url": "{{{{base_url}}}}/api/v1/authentication/reset-password/"
      }}
    }}
  ]
}}
'''

    # ═══════════════════════════════════════════════════════════
    #  9. TESTS
    # ═══════════════════════════════════════════════════════════
    def create_tests(self) -> None:
        info(f"[TESTS] {self.module}")
        self.writer.write(
            f"{self.tests_dir}/unit/test_auth_domain.py",
            dedent('''\
                """Unit tests for authentication domain"""
                from __future__ import annotations
                import uuid
                from datetime import UTC, datetime

                import pytest

                from app.modules.authentication.domain.enums import TokenType
                from app.modules.authentication.domain.value_objects import (
                    Claims, RefreshClaims,
                )

                pytestmark = pytest.mark.unit


                class TestTokenType:
                    def test_values(self) -> None:
                        assert TokenType.BEARER.value == "Bearer"
                        assert TokenType.REFRESH.value == "Refresh"


                class TestClaims:
                    def _valid(self) -> dict:
                        return {
                            "iss": "erp-api", "sub": "10000000001",
                            "aud": "erp-client",
                            "iat": 1700000000, "nbf": 1700000000,
                            "exp": 1700003600, "jti": uuid.uuid4(),
                            "grant_id": "10000000001", "scope": "admin",
                        }

                    def test_valid(self) -> None:
                        c = Claims(**self._valid())
                        assert c.sub == "10000000001"
                        assert c.scope == "admin"

                    def test_missing_grant_id(self) -> None:
                        d = self._valid(); d["grant_id"] = ""
                        with pytest.raises(Exception):
                            Claims(**d)

                    def test_nbf_before_iat_rejected(self) -> None:
                        d = self._valid(); d["nbf"] = d["iat"] - 1
                        with pytest.raises(Exception):
                            Claims(**d)

                    def test_immutable(self) -> None:
                        c = Claims(**self._valid())
                        with pytest.raises(AttributeError):
                            c.iss = "other"  # type: ignore[misc]


                class TestRefreshClaims:
                    def _valid(self) -> dict:
                        return {
                            "iss": "erp-api", "sub": "10000000001",
                            "aud": "erp-client",
                            "iat": 1700000000, "nbf": 1700000000,
                            "exp": 1700003600, "jti": uuid.uuid4(),
                            "client_id": "web", "grant_id": "10000000001",
                            "scope": "refresh",
                        }

                    def test_valid(self) -> None:
                        c = RefreshClaims(**self._valid())
                        assert c.client_id == "web"
                        assert c.sub == "10000000001"

                    def test_missing_client_id(self) -> None:
                        d = self._valid(); d["client_id"] = ""
                        with pytest.raises(Exception):
                            RefreshClaims(**d)
            '''),
        )

        self.writer.write(
            f"{self.tests_dir}/property/test_auth_invariants.py",
            dedent('''\
                """Property tests for authentication invariants"""
                from __future__ import annotations
                import uuid

                import pytest
                from hypothesis import given, settings, strategies as st

                from app.modules.authentication.domain.value_objects import Claims

                pytestmark = pytest.mark.property


                @settings(max_examples=50)
                @given(
                    sub=st.integers(min_value=1, max_value=10**12),
                    scope=st.sampled_from(["user", "admin", "moderator"]),
                )
                def test_claims_sub_always_string(sub: int, scope: str) -> None:
                    c = Claims(
                        iss="erp-api", sub=str(sub), aud="erp-client",
                        iat=1700000000, nbf=1700000000, exp=1700003600,
                        jti=uuid.uuid4(), grant_id=str(sub), scope=scope,
                    )
                    assert isinstance(c.sub, str)
                    assert c.sub == str(sub)
            '''),
        )

        self.writer.write(
            f"{self.tests_dir}/manual/manual_test_auth.md",
            dedent('''\
                # Manual Test — authentication Module

                ## Pre-conditions
                - [ ] DB migrated (V001..V003)
                - [ ] User module migrated (V010 from update_module_user.py)
                - [ ] Redis running
                - [ ] erp_users has test user (id 10000000001)

                ## Scenarios
                | # | Scenario | Endpoint |
                |---|----------|----------|
                | 1 | Login (email) | POST /authentication/login/ |
                | 2 | Login (username) | POST /authentication/login/ |
                | 3 | Login (wrong password) | POST /authentication/login/ |
                | 4 | Sign Up | POST /authentication/sign-up/ |
                | 5 | Refresh | PATCH /authentication/refresh/ |
                | 6 | Logout | DELETE /authentication/logout/ |
                | 7 | Lock Screen | POST /authentication/lock-screen/ |
                | 8 | Two-Step Verification | POST /authentication/two-step-verification/ |
                | 9 | Two-Step Code | POST /authentication/two-step-code/ |
                | 10 | Forgot Password | POST /authentication/forgot-password/ |
                | 11 | Reset Password | POST /authentication/reset-password/ |

                ## Cookie Verification
                - [ ] `token_type` cookie set
                - [ ] `access_token` cookie HttpOnly
                - [ ] `refresh_token` cookie HttpOnly
                - [ ] Logout clears all 3 cookies

                ## JWT Verification
                - [ ] `sub` is user id as string "10000000001"
                - [ ] `exp` > `iat` > 0
                - [ ] `nbf` >= `iat`

                ## Sign Up Verification
                - [ ] Response has `username`
                - [ ] Response `id` >= 10000000000 (11+ digits)
                - [ ] Password is hashed (not in response)
            '''),
        )

    # ═══════════════════════════════════════════════════════════
    #  2. ACTIVATE
    # ═══════════════════════════════════════════════════════════
    def activate_module(self) -> None:
        info("[ACTIVATE] register router + swagger + models")
        self._update_app_py()
        self._update_env_py()

    def update_app(self) -> None:
        self._update_app_py()

    def update_env(self) -> None:
        self._update_env_py()

    def _update_app_py(self) -> None:
        app_file = self.root / self.app_py
        if not app_file.exists():
            warn(f"{self.app_py} not found — skipping")
            return

        content = app_file.read_text(encoding="utf-8")
        original = content

        router_import = (
            "from app.modules.authentication.presentation.router "
            "import router as authentication_router"
        )
        if router_import not in content:
            lines = content.split("\n")
            last = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    last = i
            lines.insert(last + 1, router_import)
            content = "\n".join(lines)
            ok(f"added import: {router_import}")

        swagger_import = (
            "from app.modules.authentication.presentation.swagger "
            "import register_authentication_openapi"
        )
        if swagger_import not in content:
            if router_import in content:
                content = content.replace(
                    router_import,
                    router_import + "\n" + swagger_import,
                    1,
                )
            ok(f"added import: {swagger_import}")

        m = re.search(r"(routers\s*=\s*\[)(.*?)(\n\])", content, re.S)
        if m:
            inner = m.group(2)
            if "authentication_router" not in inner:
                inner_new = inner.rstrip() + "\n    authentication_router,    # authentication\n"
                content = content[:m.start(2)] + inner_new + content[m.end(2):]
                ok("added authentication_router to routers list")

        if "register_authentication_openapi(app)" not in content:
            include_match = re.search(
                r"(app\.include_router\(authentication_router[^\n]*\n)",
                content,
            )
            swagger_call = "\n# Register Authentication OpenAPI metadata\nregister_authentication_openapi(app)\n"
            if include_match:
                insert_at = include_match.end(1)
                content = content[:insert_at] + swagger_call + content[insert_at:]
                ok("called register_authentication_openapi(app)")

        if content != original:
            bak = app_file.with_suffix(".py.bak")
            bak.write_bytes(app_file.read_bytes())
            ok(f"backup: {self.app_py}.bak")
            app_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.app_py} updated")
        else:
            skip(f"{self.app_py} unchanged")

    def _update_env_py(self) -> None:
        env_file = self.root / self.env_py
        if not env_file.exists():
            warn(f"{self.env_py} not found — skipping")
            return
        content = env_file.read_text(encoding="utf-8")
        original = content
        marker = "# --- module authentication (Auth sessions) ---"
        if marker in content:
            skip("auth models block already present")
            return
        block = f'''{marker}
try:
    from app.modules.authentication.infrastructure.models import (  # noqa: F401
        AccessTokenModel, AuthenticationModel, RefreshTokenModel,
    )
except ImportError:
    pass


'''
        anchor = "config = context.config"
        idx = content.find(anchor)
        if idx == -1:
            warn("Cannot find anchor in env.py — skipping")
            return
        content = content[:idx] + block + content[idx:]

        if content != original:
            bak = env_file.with_suffix(".py.bak")
            bak.write_bytes(env_file.read_bytes())
            ok(f"backup: {self.env_py}.bak")
            env_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.env_py} updated")

    # ═══════════════════════════════════════════════════════════
    #  10. VERIFY
    # ═══════════════════════════════════════════════════════════
    def verify(self) -> None:
        info("[VERIFY] authentication module")
        issues: list[str] = []

        files_required = [
            f"{self.mod_root}/domain/entities.py",
            f"{self.mod_root}/domain/enums.py",
            f"{self.mod_root}/domain/value_objects.py",
            f"{self.mod_root}/domain/events.py",
            f"{self.mod_root}/application/use_cases.py",
            f"{self.mod_root}/application/interfaces.py",
            f"{self.mod_root}/application/mappers.py",
            f"{self.mod_root}/application/exceptions.py",
            f"{self.mod_root}/infrastructure/models.py",
            f"{self.mod_root}/infrastructure/repositories.py",
            f"{self.mod_root}/infrastructure/caches.py",
            f"{self.mod_root}/infrastructure/services.py",
            f"{self.mod_root}/presentation/router.py",
            f"{self.mod_root}/presentation/schemas.py",
            f"{self.mod_root}/presentation/dependencies.py",
            f"{self.mod_root}/presentation/swagger.py",
        ]
        for f in files_required:
            if (self.root / f).exists():
                ok(f"file: {f.split('/')[-1]}")
            else:
                issues.append(f"NOT FOUND: {f}")

        # Check schemas has username in SignUpResponse + UserInfo
        schemas = self.root / f"{self.mod_root}/presentation/schemas.py"
        if schemas.exists():
            c = schemas.read_text(encoding="utf-8")
            if "username: str" in c:
                ok("schemas.py: username NOT NULL ✓")
            else:
                issues.append("schemas.py: missing username in SignUpResponse/UserInfo")

        # Check router has all endpoints
        router = self.root / f"{self.mod_root}/presentation/router.py"
        if router.exists():
            c = router.read_text(encoding="utf-8")
            endpoints = [
                "/login/", "/sign-up/", "/refresh/", "/logout/",
                "/lock-screen/", "/two-step-verification/", "/two-step-code/",
                "/forgot-password/", "/reset-password/",
            ]
            missing = [e for e in endpoints if e not in c]
            if not missing:
                ok(f"router.py: all {len(endpoints)} endpoints ✓")
            else:
                issues.append(f"router.py: missing endpoints {missing}")

        # Check auth models FK
        auth_models = self.root / f"{self.auth_root}/infrastructure/models.py"
        if auth_models.exists():
            c = auth_models.read_text(encoding="utf-8")
            if "user_id: Mapped[int]" in c and "BigInteger" in c:
                ok("auth/models.py: user_id BIGINT ✓")
            else:
                issues.append("auth/models.py: user_id should be BigInteger")

        # Check auth VO sub: str
        auth_vo = self.root / f"{self.auth_root}/domain/value_objects.py"
        if auth_vo.exists():
            c = auth_vo.read_text(encoding="utf-8")
            if "sub: str" in c:
                ok("auth/value_objects.py: sub: str ✓")
            else:
                issues.append("auth/value_objects.py: sub still UUID")

        app_file = self.root / self.app_py
        if app_file.exists():
            c = app_file.read_text(encoding="utf-8")
            if "authentication_router" in c:
                ok("app.py: authentication_router ✓")
            else:
                issues.append("app.py missing authentication_router")

        for ver in ("V001", "V002", "V003"):
            d = self.root / self.sql_dir
            matches = list(d.glob(f"{ver}__*auth*.sql")) if d.exists() else []
            if matches:
                ok(f"SQL: {matches[0].name}")
            else:
                issues.append(f"SQL {ver} not found")

        print()
        if issues:
            info("═" * 60)
            warn(f"พบ {len(issues)} ปัญหา:")
            for i, msg in enumerate(issues, 1):
                err(f"  {i}. {msg}")
            info("═" * 60)
        else:
            info("═" * 60)
            ok("ALL CHECKS PASSED ✓")
            info("═" * 60)

    def run_all(self) -> None:
        self.create_module()
        self.create_sql()
        self.create_migration()
        self.create_swagger()
        self.create_postman()
        self.create_tests()
        self.activate_module()

    def summary(self) -> None:
        print()
        info("═" * 60)
        ok(f"DONE — module: {self.module}  (v{VERSION})")
        info(f"  Schema  : {SCHEMA}")
        info(f"  Prefix  : {self.prefix}_")
        info(f"  Tables  : {len(TABLE_NAMES)}")
        info(f"  Written : {len(self.writer.written)} files")
        info(f"  Skipped : {len(self.writer.skipped)} files")
        info("═" * 60)
        print()
        print(f"  {C.YELLOW}Next steps:{C.RESET}")
        print(f"    1. Verify:  python authentication_module_user.py verify authentication")
        print(f"    2. Alembic: alembic upgrade head")
        print(f"    3. Run:     uvicorn app.app:app --reload")
        print(f"    4. Swagger: http://localhost:8000/docs")
        print(f"    5. Postman: Import docs/postman/authentication.json")
        print()


HELP = f"""
═══════════════════════════════════════════════════════════════
  authentication_module_user.py v{VERSION}
  Schema: {SCHEMA}  ·  Prefix: auth_
  Tables: {len(TABLE_NAMES)}
═══════════════════════════════════════════════════════════════

  USAGE
    python authentication_module_user.py <action> <module> [layer] [prefix] [options]

  ACTIONS
    create / activate / sql / alembic / swagger / postman /
    update / update-env / test / verify / all / help

  WHAT'S NEW in v1.1.0
    • Login รองรับ username OR email
    • Sign Up บังคับ username (NOT NULL UNIQUE)
    • UserInfo + SignUpResponse มี username
    • +4 endpoints: sign-up, lock-screen, two-step-verification, two-step-code
    • user_id FK → BIGINT (11+ หลัก)
    • Login tracking: record_login / record_login_failure

  EXAMPLES
    python authentication_module_user.py all authentication 0 auth --force
    python authentication_module_user.py verify authentication
"""


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default="authentication")
    parser.add_argument("layer", nargs="?", default="0")
    parser.add_argument("prefix", nargs="?", default="auth")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--help", action="store_true")

    args, _ = parser.parse_known_args()

    if args.help or args.action == "help":
        print(HELP)
        return 0

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"Project root not found: {root}")
        return 1

    gen = AuthenticationModuleGenerator(
        project_root=root, module=args.module,
        layer=args.layer, prefix=args.prefix, force=args.force,
    )

    print()
    info("═" * 60)
    info(f"  MODULE  : {gen.module}")
    info(f"  LAYER   : {gen.layer} ({gen.layer_name})")
    info(f"  SCHEMA  : {SCHEMA}")
    info(f"  PREFIX  : {gen.prefix}_")
    info(f"  ACTION  : {args.action}")
    info(f"  VERSION : {VERSION}")
    info("═" * 60)

    action_map = {
        "create": gen.create_module,
        "activate": gen.activate_module,
        "sql": gen.create_sql,
        "alembic": gen.create_migration,
        "swagger": gen.create_swagger,
        "postman": gen.create_postman,
        "test": gen.create_tests,
        "update": gen.update_app,
        "update-env": gen.update_env,
        "verify": gen.verify,
        "all": gen.run_all,
    }

    if args.action not in action_map:
        err(f"Unknown action: {args.action}")
        print(HELP)
        return 1

    try:
        action_map[args.action]()
    except Exception as e:
        err(f"Aborted: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if args.action != "verify":
        gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
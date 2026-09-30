from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import uuid
from datetime import UTC, datetime
from functools import lru_cache

from fastapi import BackgroundTasks, Depends, WebSocket
from fastapi.requests import Request
from fastapi.security import APIKeyHeader, HTTPBearer, OAuth2PasswordBearer
from jwcrypto import jwt
from jwcrypto.common import JWException
from jwcrypto.jwe import InvalidJWEData
from jwcrypto.jws import InvalidJWSObject, InvalidJWSSignature
from jwcrypto.jwt import (
    JWTExpired,
    JWTInvalidClaimFormat,
    JWTInvalidClaimValue,
    JWTMissingClaim,
    JWTNotYetValid,
)
from loguru import logger
from pwdlib import PasswordHash

from app.core.settings import PathRule, settings
from app.modules.authentication.application.exceptions import (
    AuthenticationCookiesNotProvidedException,
    AuthenticationException,
    AuthenticationTokenException,
    AuthenticationTokenExpiredException,
    AuthenticationTokenInvalidException,
    AuthenticationTokenMalformedError,
    AuthenticationTokenNotYetValidException,
    HashingException,
    ModifiedTokenException,
    RefreshTokenException,
    RefreshTokenExpiredException,
    RefreshTokenInvalidEndpoint,
    RefreshTokenMalformedError,
    RefreshTokenNotProvidedException,
    RefreshTokenNotYetValidException,
    UserHasNotPermissionException,
)
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
)
from app.modules.authentication.application.mappers import (
    access_token_entity_mapper,
    refresh_token_entity_mapper,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.key.application.exceptions import (
    ApiKeyExpiredException,
    ApiKeyInvalidException,
    ApiKeyNotProvidedException,
    ApiKeyRevokedException,
    KeyException,
)
from app.modules.key.application.interfaces import IKeyCache, IKeyRepository
from app.modules.key.domain.entities import Key
from app.modules.shared.application.exceptions import (
    OriginNotAllowedException,
    StandardException,
)
from app.modules.shared.domain.enums import Role
from app.modules.shared.presentation.dependencies import (
    get_authentication_cache,
    get_authentication_repository,
    get_key_cache,
    get_key_repository,
)

# PASSWORD HASHING
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    try:
        return password_hasher.hash(password)
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during password hashing.")
        raise HashingException()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during password verification.")
        raise HashingException()


# ============================================================================
# JWT FORMAT HELPERS
# ============================================================================
def _detect_jwt_format(token: str) -> str:
    """TH: 3 segments=JWS, 5 segments=JWE | EN: detect JWT format by segment count"""
    if not token:
        return "EMPTY"
    parts = token.split(".")
    if len(parts) == 5:
        return "JWE"
    if len(parts) == 3:
        return "JWS"
    return "UNKNOWN"


def _b64url_decode(s: str) -> bytes:
    import base64

    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _peek_jwt_header_payload(token: str) -> tuple[dict, dict]:
    """TH: อ่าน header/payload ก่อน verify | EN: peek JWT header/payload"""
    try:
        parts = token.split(".")
        if len(parts) not in (3, 5):
            return {}, {}
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1])) if len(parts) == 3 else {}
        return header, payload
    except Exception:
        return {}, {}


def _all_cookie_values(request: Request, name: str) -> list[str]:
    """
    TH: อ่าน cookie ทุกตัวที่ชื่อ `name` จาก raw Cookie header
        (Starlette's request.cookies เก็บได้แค่ค่าสุดท้ายต่อชื่อ)
    EN: read ALL cookie values for `name` from raw Cookie header
        (Starlette's request.cookies keeps only one value per name)
    """
    raw = request.headers.get("cookie", "")
    values: list[str] = []
    for chunk in raw.split(";"):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        k, _, v = chunk.partition("=")
        if k.strip() == name:
            values.append(v.strip().strip('"'))
    return values


# ============================================================================
# JWT TOKEN (JWS + JWE)
# ============================================================================
def generate_tokens(authentication: Authentication) -> Authentication:
    try:
        if (
            authentication.refresh_token is None
            or authentication.refresh_token.access_token is None
        ):
            logger.error("generate_tokens called with incomplete token pair.")
            raise AuthenticationException()

        # ── access token ─────────────────────────────────────────────
        authentication.refresh_token.access_token.set_claims(
            iss=settings.JWT_ISSUER,
            sub=authentication.user.id,
            aud=settings.JWT_AUDIENCE,
            jti=uuid.uuid4(),
            grant_id=str(authentication.user.email),
            scope=str(authentication.user.role.value),
        )
        inner = jwt.JWT(
            header={"alg": "EdDSA", "typ": "access+jwt"},
            claims=authentication.refresh_token.access_token.claims.to_dict(),
        )
        inner.make_signed_token(settings.JWT_SIGNING_PRIVATE_KEY)
        outer = jwt.JWT(
            header={"alg": "ECDH-ES+A256KW", "enc": "A256GCM", "cty": "JWT"},
            claims=inner.serialize(),
        )
        outer.make_encrypted_token(settings.JWT_ENCRYPTION_PUBLIC_KEY)
        authentication.refresh_token.access_token.token = outer.serialize()

        if _detect_jwt_format(authentication.refresh_token.access_token.token) != "JWE":
            logger.error("Access token encryption FAILED — not a JWE.")
            raise AuthenticationException()

        # ── refresh token ────────────────────────────────────────────
        authentication.refresh_token.set_claims(
            iss=settings.JWT_ISSUER,
            sub=authentication.user.id,
            aud=settings.JWT_AUDIENCE,
            jti=uuid.uuid4(),
            client_id=str(settings.APPLICATION_URL),
            grant_id=str(authentication.user.email),
            scope=str(authentication.user.role.value),
        )
        inner = jwt.JWT(
            header={"alg": "EdDSA", "typ": "refresh+jwt"},
            claims=authentication.refresh_token.refresh_claims.to_dict(),
        )
        inner.make_signed_token(settings.JWT_SIGNING_PRIVATE_KEY)
        outer = jwt.JWT(
            header={"alg": "ECDH-ES+A256KW", "enc": "A256GCM", "cty": "JWT"},
            claims=inner.serialize(),
        )
        outer.make_encrypted_token(settings.JWT_ENCRYPTION_PUBLIC_KEY)
        authentication.refresh_token.token = outer.serialize()

        if _detect_jwt_format(authentication.refresh_token.token) != "JWE":
            logger.error("Refresh token encryption FAILED — not a JWE.")
            raise AuthenticationException()

        logger.debug("Tokens generated and encrypted as JWE (5 segments).")
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token generation.")
        raise AuthenticationException()


def _decode_nested_jwt(
    token: str,
    *,
    signing_key,
    encryption_key,
    mapper,
    token_kind: str,
) -> Authentication:
    """
    TH: decode nested JWT — รองรับทั้ง JWE (5 segments) และ bare JWS (3 segments)
        พร้อม pre-check `iss`/`alg` ก่อน verify
    EN: decode nested JWT — supports JWE + bare JWS; pre-checks iss/alg
    """
    fmt = _detect_jwt_format(token)

    if fmt == "JWE":
        outer = jwt.JWT(
            jwt=token,
            key=encryption_key,
            expected_type="JWE",
            algs=["ECDH-ES+A256KW", "A256GCM"],
        )
        inner_raw = outer.claims
    elif fmt == "JWS":
        header, payload = _peek_jwt_header_payload(token)
        alg = str(header.get("alg", ""))
        iss = str(payload.get("iss", ""))

        if alg and alg != "EdDSA":
            logger.warning(
                f"{token_kind} rejected: header.alg='{alg}' (expected 'EdDSA'). "
                f"Token appears to be from another system."
            )
            raise RefreshTokenMalformedError(cause=f"invalid alg: {alg}") \
                if "refresh" in token_kind.lower() \
                else AuthenticationTokenMalformedError(cause=f"invalid alg: {alg}")

        if iss and iss != settings.JWT_ISSUER:
            logger.warning(
                f"{token_kind} rejected: iss='{iss}' "
                f"(expected '{settings.JWT_ISSUER}')."
            )
            raise RefreshTokenMalformedError(cause=f"invalid iss: {iss}") \
                if "refresh" in token_kind.lower() \
                else AuthenticationTokenMalformedError(cause=f"invalid iss: {iss}")

        logger.warning(f"{token_kind} is a bare JWS (legacy).")
        inner_raw = token
    else:
        raise RefreshTokenMalformedError(cause="unknown format") \
            if "refresh" in token_kind.lower() \
            else AuthenticationTokenMalformedError(cause="unknown format")

    inner = jwt.JWT(
        jwt=inner_raw,
        key=signing_key,
        expected_type="JWS",
        algs=["EdDSA"],
        check_claims={"iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE},
    )
    return mapper(json.loads(inner.claims))


def decode_nested_access_token(token: str) -> Authentication:
    try:
        return _decode_nested_jwt(
            token,
            signing_key=settings.JWT_SIGNING_PUBLIC_KEY,
            encryption_key=settings.JWT_ENCRYPTION_PRIVATE_KEY,
            mapper=access_token_entity_mapper,
            token_kind="Access token",
        )
    except JWTExpired:
        raise AuthenticationTokenExpiredException()
    except JWTNotYetValid:
        raise AuthenticationTokenNotYetValidException()
    except (JWTMissingClaim, JWTInvalidClaimValue, JWTInvalidClaimFormat) as e:
        logger.opt(exception=e).warning("Access token invalid claim.")
        raise AuthenticationTokenException()
    except InvalidJWSSignature as e:
        logger.opt(exception=e).warning("Access token invalid signature.")
        raise AuthenticationTokenException()
    except (InvalidJWEData, InvalidJWSObject) as e:
        logger.opt(exception=e).warning("Access token invalid format.")
        raise AuthenticationTokenException()
    except json.JSONDecodeError as e:
        raise AuthenticationTokenMalformedError(cause=str(e))
    except JWException as e:
        logger.opt(exception=e).error("Access token JWException.")
        raise AuthenticationTokenException()
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            f"Unexpected access token decode error: {type(e).__name__}: {e}"
        )
        raise AuthenticationTokenException()


def decode_nested_refresh_token(token: str) -> Authentication:
    try:
        return _decode_nested_jwt(
            token,
            signing_key=settings.JWT_SIGNING_PUBLIC_KEY,
            encryption_key=settings.JWT_ENCRYPTION_PRIVATE_KEY,
            mapper=refresh_token_entity_mapper,
            token_kind="Refresh token",
        )
    except JWTExpired:
        raise RefreshTokenExpiredException()
    except JWTNotYetValid:
        raise RefreshTokenNotYetValidException()
    except (JWTMissingClaim, JWTInvalidClaimValue, JWTInvalidClaimFormat) as e:
        logger.opt(exception=e).warning("Refresh token invalid claim.")
        raise RefreshTokenException(cause=str(e))
    except InvalidJWSSignature as e:
        logger.opt(exception=e).warning("Refresh token invalid signature.")
        raise RefreshTokenException(cause=str(e))
    except (InvalidJWEData, InvalidJWSObject) as e:
        logger.opt(exception=e).warning("Refresh token invalid format.")
        raise RefreshTokenException(cause=str(e))
    except json.JSONDecodeError as e:
        raise RefreshTokenMalformedError(cause=str(e))
    except JWException as e:
        logger.opt(exception=e).error("Refresh token JWException.")
        raise RefreshTokenException(cause=str(e))
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            f"Unexpected refresh token decode error: {type(e).__name__}: {e}"
        )
        raise RefreshTokenException(cause=f"{type(e).__name__}: {e}")


# ============================================================================
# JWT HASHING
# ============================================================================
def _token_fingerprint(material: str, namespace: str) -> str:
    try:
        key = bytes.fromhex(settings.JWT_HASH_FINGERPRINT)
        msg = f"{namespace}:{material}".encode()
        return hmac.new(key, msg, hashlib.sha256).hexdigest()
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token hashing.")
        raise HashingException()


def hash_tokens(authentication: Authentication) -> Authentication:
    try:
        if authentication.refresh_token and authentication.refresh_token.access_token:
            claims = authentication.refresh_token.access_token.claims
            authentication.refresh_token.access_token.hashed_jti = (
                _token_fingerprint(str(claims.jti), "access-jti")
                if claims and claims.jti
                else None
            )
        if authentication.refresh_token:
            claims = authentication.refresh_token.refresh_claims
            authentication.refresh_token.hashed_jti = (
                _token_fingerprint(str(claims.jti), "refresh-jti")
                if claims and claims.jti
                else None
            )
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token hashing.")
        raise HashingException()


# ============================================================================
# PATH RULE MATCHING
# ============================================================================
@lru_cache(maxsize=512)
def _compile_path_rule(endpoint: str) -> re.Pattern[str]:
    parts = re.split(r"\{[^}]+\}", endpoint)
    escaped = r"[^/]+".join(re.escape(part) for part in parts)
    escaped = escaped.rstrip("/") + "/?"
    return re.compile(f"^{escaped}$")


def _match_path_rules(paths: tuple[PathRule, ...], path: str, method: str) -> bool:
    for allowed_path in paths:
        if allowed_path["method"] != method:
            continue
        try:
            pattern = _compile_path_rule(allowed_path["endpoint"])
        except re.error as e:
            logger.opt(exception=e).error(f"Invalid path rule: {allowed_path}")
            continue
        if pattern.match(path):
            return True
    return False


def _describe_rules(paths: tuple[PathRule, ...], method: str | None = None) -> str:
    items = [
        f"{p['method']} {p['endpoint']}"
        for p in paths
        if method is None or p["method"] == method
    ]
    return ", ".join(items) if items else "<empty>"


# ============================================================================
# API KEY AUTHENTICATION
# ============================================================================
api_key_header = APIKeyHeader(
    name=settings.AUTH_API_KEY_NAME,
    scheme_name=settings.AUTH_API_KEY_SCHEME_NAME,
    description=settings.AUTH_API_KEY_DESCRIPTION,
    auto_error=False,
)
http_bearer = HTTPBearer(auto_error=False)


def _api_key_fingerprint(material: str) -> str:
    try:
        key = bytes.fromhex(settings.API_KEY_HASH_FINGERPRINT)
        msg = f"api-key:{material}".encode()
        return hmac.new(key, msg, hashlib.sha256).hexdigest()
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during API key hashing.")
        raise HashingException()


def generate_api_key(key: Key) -> Key:
    try:
        key.prefix = settings.API_KEY_PREFIX
        random_part = secrets.token_urlsafe(settings.API_KEY_ENTROPY_BYTES)
        raw_key = f"{key.prefix}_{random_part}"
        key.plain_key = raw_key
        key.hashed_key = _api_key_fingerprint(raw_key)
        key.last_four = random_part[-4:]
        return key
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during API key generation.")
        raise KeyException()


def _has_access_to_api_key_endpoint(path: str, method: str) -> bool:
    try:
        return _match_path_rules(settings.SECURITY_API_KEY_ALLOWED_PATHS, path, method)
    except StandardException:
        return False
    except Exception as e:
        logger.opt(exception=e).error("Error in API key endpoint check.")
        return False


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    try:
        return hmac.compare_digest(_api_key_fingerprint(plain_key), hashed_key)
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during API key verification.")
        raise HashingException()


async def _resolve_api_key(
    request: Request,
    background_tasks: BackgroundTasks,
    plain_key: str | None = Depends(api_key_header),
    repository: IKeyRepository = Depends(get_key_repository),
    cache: IKeyCache = Depends(get_key_cache),
) -> Key:
    if not plain_key:
        raise ApiKeyNotProvidedException()
    fingerprint = _api_key_fingerprint(plain_key)
    db_key: Key | None = await cache.get_by_hashed_key(fingerprint)
    if db_key is None:
        db_key = await repository.get_key_by_hashed_key(fingerprint)
        if db_key is not None:
            background_tasks.add_task(cache.insert, db_key)
    if db_key is None or not verify_api_key(plain_key, db_key.hashed_key):
        raise ApiKeyInvalidException()
    if not db_key.is_active:
        raise ApiKeyRevokedException()
    if db_key.expires_at is not None and db_key.expires_at < datetime.now(UTC):
        raise ApiKeyExpiredException()
    return db_key


async def authenticate_api_key(
    request: Request, key: Key = Depends(_resolve_api_key)
) -> Key:
    try:
        if not _has_access_to_api_key_endpoint(request.url.path, request.method):
            raise UserHasNotPermissionException()
        return key
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("Error in API key authentication.")
        raise KeyException()


# ============================================================================
# BEARER TOKEN AUTHENTICATION
# ============================================================================
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/authentication/login/",
    refreshUrl="/api/v1/authentication/refresh/",
    scheme_name=settings.AUTH_BEARER_TOKEN_SCHEME_NAME,
    description=settings.AUTH_BEARER_TOKEN_SCHEME_DESCRIPTION,
    auto_error=False,
)


def _matches_authentication_binding(
    cached: Authentication, authentication: Authentication
) -> bool:
    if cached.blacklisted:
        return False
    if cached.refresh_token is None or cached.refresh_token.revoked:
        return False
    if cached.user is None or cached.user.id != authentication.user.id:
        return False
    if cached.user_agent != authentication.user_agent:
        return False
    if authentication.device is not None and cached.device != authentication.device:
        return False
    return True


def _is_refresh_endpoint(path: str) -> bool:
    """Accept both /refresh and /refresh/ (trailing slash optional)."""
    return path.rstrip("/").endswith("/api/v1/authentication/refresh")


def _is_logout_endpoint(path: str) -> bool:
    return path.rstrip("/").endswith("/api/v1/authentication/logout")


async def _resolve_access_token_authentication(
    request: Request,
    background_tasks: BackgroundTasks,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    cache: IAuthenticationCache = Depends(get_authentication_cache),
) -> Authentication:
    credentials = await http_bearer(request)
    if credentials is None:
        token = request.cookies.get(settings.COOKIES_ACCESS_TOKEN_KEY, None)
        device = request.cookies.get(settings.COOKIES_DEVICE_KEY, None)
    else:
        token = credentials.credentials
        device = None

    if not token or (credentials is None and not device):
        raise AuthenticationCookiesNotProvidedException()

    authentication = decode_nested_access_token(token)
    authentication = hash_tokens(authentication)
    authentication.device = device
    authentication.user_agent = (
        (request.headers.get("user-agent") or "").lower().strip()
    )

    db_authentication: Authentication | None = await cache.get_by_access_token(
        authentication
    )
    if db_authentication is not None:
        access_token = (
            db_authentication.refresh_token.access_token
            if db_authentication.refresh_token
            else None
        )
        if (
            access_token is None
            or access_token.revoked
            or not _matches_authentication_binding(db_authentication, authentication)
        ):
            db_authentication = None

    if db_authentication is None:
        db_authentication = await repository.get_access_token_by_authentication(
            authentication
        )
        if db_authentication is not None:
            background_tasks.add_task(
                cache.insert_by_access_token,
                db_authentication,
                settings.REDIS_SESSION_TTL_SECONDS,
            )

    if (
        db_authentication is None
        or db_authentication.refresh_token is None
        or db_authentication.refresh_token.access_token is None
    ):
        raise AuthenticationTokenInvalidException()

    authentication = db_authentication
    if authentication.user.role != authentication.refresh_token.access_token.permission:
        raise ModifiedTokenException()
    return authentication


def _assert_endpoint_access(request: Request, authentication: Authentication) -> None:
    if not _has_access_to_endpoint(
        request.url.path, request.method, authentication.user.role
    ):
        raise UserHasNotPermissionException()


def _has_access_to_endpoint(path: str, method: str, role: Role | None = None) -> bool:
    try:
        if role is None:
            paths = settings.SECURITY_NO_AUTH_PATHS
        elif role == Role.ADMIN:
            paths = settings.SECURITY_ADMIN_ALLOWED_PATHS
        elif role == Role.MANAGER:
            paths = settings.SECURITY_MANAGER_ALLOWED_PATHS
        else:
            paths = settings.SECURITY_USER_ALLOWED_PATHS
        return _match_path_rules(paths, path, method)
    except StandardException:
        return False
    except Exception as e:
        logger.opt(exception=e).error("Error in endpoint access check.")
        return False


async def no_authentication(request: Request) -> None:
    """
    Public endpoint guard — always allow; log warning if active credentials present.
    """
    try:
        has_cookies = bool(request.cookies)
        has_bearer = (request.headers.get("authorization") or "").lower().startswith(
            "bearer "
        )
        if has_cookies or has_bearer:
            logger.warning(
                f"Active session credentials on public endpoint "
                f"'{request.url.path}' ({request.method})."
            )
        return
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("Error in no_authentication.")
        raise AuthenticationException()


async def authenticate_user(
    request: Request,
    authentication: Authentication = Depends(_resolve_access_token_authentication),
) -> Authentication:
    try:
        _assert_endpoint_access(request, authentication)
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("Error in authenticate_user.")
        raise AuthenticationException()


async def authenticate_manager(
    request: Request,
    authentication: Authentication = Depends(_resolve_access_token_authentication),
) -> Authentication:
    try:
        if authentication.refresh_token.access_token.permission == Role.USER:
            raise UserHasNotPermissionException()
        _assert_endpoint_access(request, authentication)
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("Error in authenticate_manager.")
        raise AuthenticationException()


async def authenticate_admin(
    request: Request,
    authentication: Authentication = Depends(_resolve_access_token_authentication),
) -> Authentication:
    try:
        if authentication.refresh_token.access_token.permission != Role.ADMIN:
            raise UserHasNotPermissionException()
        _assert_endpoint_access(request, authentication)
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("Error in authenticate_admin.")
        raise AuthenticationException()

async def authenticate_refresh(
    request: Request,
    background_tasks: BackgroundTasks,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    cache: IAuthenticationCache = Depends(get_authentication_cache),
) -> Authentication:
    """
    TH: Authenticate refresh endpoint — ลองทุก refresh_token cookie
        จนกว่าจะเจอตัวที่ decode สำเร็จ + อยู่ใน DB
        (Postman บางครั้งส่ง cookie เก่า + ใหม่พร้อมกัน → ต้องวนจนเจอตัวจริง)
    EN: Authenticate refresh — try every refresh_token cookie until one
        decodes successfully AND exists in DB.
    """
    try:
        logger.debug(
            f"Authenticating refresh endpoint '{request.url.path}' "
            f"({request.method})."
        )

        if not _is_refresh_endpoint(request.url.path):
            raise RefreshTokenInvalidEndpoint()

        tokens = _all_cookie_values(request, settings.COOKIES_REFRESH_TOKEN_KEY)
        logger.debug(f"Found {len(tokens)} refresh_token cookie(s).")

        device = request.cookies.get(settings.COOKIES_DEVICE_KEY, None)

        if not tokens:
            raise RefreshTokenNotProvidedException()
        if not device:
            logger.info("Refresh requested without device cookie.")
            raise RefreshTokenNotProvidedException()

        user_agent = (request.headers.get("user-agent") or "").lower().strip()
        db_authentication: Authentication | None = None
        last_error: StandardException | None = None

        for i, token in enumerate(tokens, start=1):
            fmt = _detect_jwt_format(token)
            logger.debug(
                f"Trying refresh_token #{i}/{len(tokens)} (format={fmt})."
            )
            try:
                authentication = decode_nested_refresh_token(token)
                authentication = hash_tokens(authentication)
                authentication.device = device
                authentication.user_agent = user_agent

                logger.debug(
                    f"[DEBUG-REFRESH #{i}] user_id={authentication.user.id} "
                    f"device={device!r} user_agent={user_agent!r} "
                    f"hashed_jti={authentication.refresh_token.hashed_jti}"
                )

                # ── Cache-aside ─────────────────────────────────────
                db_auth: Authentication | None = await cache.get_by_refresh_token(
                    authentication
                )
                if db_auth is not None and not _matches_authentication_binding(
                    db_auth, authentication
                ):
                    logger.info(
                        f"refresh_token #{i}: cached auth binding mismatch. "
                        f"Falling back to DB."
                    )
                    db_auth = None

                if db_auth is None:
                    db_auth = await repository.get_refresh_token_by_authentication(
                        authentication
                    )

                if db_auth is None:
                    logger.info(
                        f"refresh_token #{i} decoded but NOT FOUND IN DB. "
                        f"Trying next cookie."
                    )
                    continue  # ← ลอง cookie ถัดไป ไม่ break

                # ── Success ────────────────────────────────────────
                db_authentication = db_auth
                logger.debug(f"refresh_token #{i} accepted.")
                break

            except StandardException as e:
                logger.info(
                    f"refresh_token #{i} rejected: {type(e).__name__}: {e}"
                )
                last_error = e
                continue

        if db_authentication is None:
            logger.warning(
                f"All {len(tokens)} refresh_token cookie(s) failed. "
                f"last_error="
                f"{type(last_error).__name__ if last_error else 'None'}"
            )
            raise last_error or AuthenticationTokenInvalidException()

        # ── Repopulate cache in background ─────────────────────────
        background_tasks.add_task(
            cache.insert_by_refresh_token,
            db_authentication,
            settings.REDIS_SESSION_TTL_SECONDS,
        )

        logger.debug(
            f"Refresh authenticated for user "
            f"'{db_authentication.user.email}'."
        )
        return db_authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            f"Error in authenticate_refresh: {type(e).__name__}: {e}"
        )
        raise RefreshTokenException(cause=f"{type(e).__name__}: {e}")

async def authenticate_logout(
    request: Request,
    authentication: Authentication = Depends(_resolve_access_token_authentication),
) -> Authentication:
    try:
        if not _is_logout_endpoint(request.url.path):
            raise RefreshTokenInvalidEndpoint()
        if not _has_access_to_endpoint(
            request.url.path, request.method, authentication.user.role
        ):
            raise UserHasNotPermissionException()
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(f"Error in authenticate_logout: {e}")
        raise RefreshTokenException(cause=f"{type(e).__name__}: {e}")


async def authenticate_websocket(
    websocket: WebSocket,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    cache: IAuthenticationCache = Depends(get_authentication_cache),
) -> Authentication:
    try:
        origin = (websocket.headers.get("origin") or "").strip()
        if origin not in [str(o) for o in settings.SECURITY_ALLOW_ORIGINS]:
            raise OriginNotAllowedException()

        token = websocket.cookies.get(settings.COOKIES_ACCESS_TOKEN_KEY, None)
        device = websocket.cookies.get(settings.COOKIES_DEVICE_KEY, None)
        if not token or not device:
            raise AuthenticationCookiesNotProvidedException()

        authentication = decode_nested_access_token(token)
        authentication = hash_tokens(authentication)
        authentication.device = device
        authentication.user_agent = (
            (websocket.headers.get("user-agent") or "").lower().strip()
        )

        db_authentication: Authentication | None = await cache.get_by_access_token(
            authentication
        )
        if db_authentication is not None:
            access_token = (
                db_authentication.refresh_token.access_token
                if db_authentication.refresh_token
                else None
            )
            if (
                access_token is None
                or access_token.revoked
                or not _matches_authentication_binding(
                    db_authentication, authentication
                )
            ):
                db_authentication = None

        if db_authentication is None:
            db_authentication = await repository.get_access_token_by_authentication(
                authentication
            )

        if (
            db_authentication is None
            or db_authentication.refresh_token is None
            or db_authentication.refresh_token.access_token is None
        ):
            raise AuthenticationTokenInvalidException()

        authentication = db_authentication
        if (
            authentication.user.role
            != authentication.refresh_token.access_token.permission
        ):
            raise ModifiedTokenException()
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(f"Error in authenticate_websocket: {e}")
        raise AuthenticationException()

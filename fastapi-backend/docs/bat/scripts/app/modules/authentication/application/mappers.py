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
    AccessTokenInfo,
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
    """
    Transform Authentication entity → LoginResponse.

    Includes:
    - access_token, refresh_token (raw JWTs)
    - token_info: created_at, expires_at, claims (access token metadata)
    - info: user profile
    """
    user = _authentication.user
    access_token = _authentication.refresh_token.access_token

    # === User Info ===
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

    # === Access Token Info ===
    token_info = AccessTokenInfo(
        created_at=access_token.created_at
        if access_token.created_at
        else datetime.now(tz=BRASILIA_TZ),
        expires_at=access_token.expires_at
        if access_token.expires_at
        else datetime.now(tz=BRASILIA_TZ),
        claims=access_token.claims.to_dict() if access_token.claims else {},
    )

    return LoginResponse(
        access_token=access_token.token,
        refresh_token=_authentication.refresh_token.token,
        token_info=token_info,
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


def entity_forgot_password_mapper(
    _user: User | None = None,
) -> ForgotPasswordResponse:
    return ForgotPasswordResponse()


def entity_reset_password_mapper(
    _user: User | None = None,
) -> ResetPasswordResponse:
    return ResetPasswordResponse()


def entity_lock_screen_mapper(_user: User | None = None) -> LockScreenResponse:
    return LockScreenResponse()


def entity_two_step_verification_mapper(
    _user: User | None = None,
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

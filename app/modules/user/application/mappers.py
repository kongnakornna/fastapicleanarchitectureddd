"""user mappers — entity ↔ model ↔ response (SQL-aligned)"""
from __future__ import annotations

from datetime import datetime

from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.enums import ResponseMessages, Role
from app.modules.shared.presentation.schemas import CreateResponse
from app.modules.user.domain.entities import User
from app.modules.user.domain.enums import (
    Gender, OnlineStatus, UserStatus,
)
from app.modules.user.domain.value_objects import (
    Name, UserPreferences, UserSecurity,
)
from app.modules.user.infrastructure.models import UserModel


# ═════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════
def _int_to_bool(value: int | None) -> bool:
    """TH: SQL int2 (0/1) → bool"""
    if value is None:
        return False
    return bool(value)


# ═════════════════════════════════════════════════════════
# ENTITY ↔ MODEL
# ═════════════════════════════════════════════════════════
def model_entity_mapper(model: UserModel) -> User:
    """TH: DB row → User entity (จาก erp_users)"""
    user = User(                              # ← เปลี่ยนจาก return เป็น assign
        id=model.id,
        name=Name(
            first_name=model.first_name or "",
            last_name=model.last_name or "",
            preferred_name=model.preferred_name or None,
            full_name=model.full_name or None,
            nickname=model.nickname or None,
        ),
        username=model.username or "",
        email=model.email,
        phone=model.phone,
        mobile_number=model.mobile_number or None,
        line_id=model.line_id or None,
        id_card=model.id_card or None,
        gender=Gender(model.gender) if model.gender else None,
        birthdate=model.birthdate,
        avatar=model.avatar or None,
        avatar_path=model.avatar_path or None,
        message=model.message or None,
        remark=model.remark or None,
        hashed_password=model.hashed_password or None,
        temporary_password=model.temporary_password or None,
        role=Role(model.role) if model.role else Role.USER,
        status=UserStatus(model.status) if model.status else UserStatus.ACTIVE,
        online_status=OnlineStatus(model.online_status) if model.online_status else OnlineStatus.OFFLINE,
        active_status=model.active_status,
        network_id=model.network_id,
        network_type_id=model.network_type_id,
        type_id=model.type_id,
        system_id=model.system_id,
        location_id=model.location_id,
        deleted_at=model.deleted_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
        # ⚠️ ไม่มี is_active=... ที่นี่ — ลบออก!
    )

    # ✅ set init=False field หลัง construction
    user.is_active = model.is_active if model.is_active is not None else True

    return user

def entity_model_mapper(user: User) -> UserModel:
    """TH: User entity → DB model"""
    if not user.hashed_password:
        raise ValueError(
            "entity_model_mapper: hashed_password is None — hash first"
        )
    return UserModel(
        id=user.id,
        first_name=(user.name.first_name if user.name else None) or None,
        last_name=(user.name.last_name if user.name else None) or None,
        preferred_name=(user.name.preferred_name if user.name else None),
        full_name=user.name.full_name if user.name else None,
        nickname=user.name.nickname if user.name else None,
        username=user.username or "",
        email=str(user.email) if user.email else "",
        phone=str(user.phone) if user.phone else None,
        mobile_number=user.mobile_number,
        line_id=user.line_id,
        id_card=user.id_card,
        gender=user.gender,
        birthdate=user.birthdate,
        avatar=user.avatar,
        avatar_path=user.avatar_path,
        message=user.message,
        remark=user.remark,
        hashed_password=user.hashed_password,
        temporary_password=user.temporary_password,
        role=user.role,
        status=user.status,
        online_status=user.online_status,
        active_status=1 if user.is_active else 0,
        network_id=user.network_id,
        network_type_id=user.network_type_id,
        type_id=user.type_id,
        system_id=user.system_id,
        location_id=user.location_id,
        deleted_at=user.deleted_at,
        is_verified=user.security.is_verified,
        is_superuser=user.security.is_superuser,
        verification_code=user.security.verification_code,
        password_reset_token=user.security.password_reset_token,
        password_reset_at=user.security.password_reset_at,
        login_failed_count=user.security.login_failed_count,
        last_sign_in_at=user.security.last_sign_in_at,
        public_notification=int(user.preferences.public_notification),
        sms_notification=int(user.preferences.sms_notification),
        email_notification=int(user.preferences.email_notification),
        line_notification=int(user.preferences.line_notification),
        public_status=user.preferences.public_status,
        information_agreement_status=user.preferences.information_agreement_status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


# ═════════════════════════════════════════════════════════
# DTOS
# ═════════════════════════════════════════════════════════
def create_entity_mapper(payload) -> User:
    """TH: request payload → User entity (รองรับ SignUpRequest + CreateRequest)"""
    first_name = getattr(payload, "first_name", None) or ""
    last_name = getattr(payload, "last_name", None) or ""
    preferred_name = getattr(payload, "preferred_name", None)
    nickname = getattr(payload, "nickname", None)

    name = Name(
        first_name=first_name,
        last_name=last_name,
        preferred_name=preferred_name or nickname or first_name or None,
        full_name=(
            getattr(payload, "full_name", None)
            or f"{first_name} {last_name}".strip()
            or None
        ),
        nickname=nickname,
    )

    raw_password = getattr(payload, "password", None)
    if not raw_password:
        raise ValueError("password is required")

    # ⚠️ SignUpRequest ใช้ phone_number / CreateRequest ใช้ phone → รองรับทั้งคู่
    phone = (
        getattr(payload, "phone", None)
        or getattr(payload, "phone_number", None)
    )

    return User(
        name=name,
        username=getattr(payload, "username", None) or "",
        email=getattr(payload, "email", None),
        phone=phone,
        mobile_number=getattr(payload, "mobile_number", None),
        line_id=getattr(payload, "line_id", None),
        id_card=getattr(payload, "id_card", None),
        gender=getattr(payload, "gender", None),
        birthdate=getattr(payload, "birthdate", None),
        password=raw_password,
        network_id=getattr(payload, "network_id", None),
        network_type_id=getattr(payload, "network_type_id", None),
        type_id=getattr(payload, "type_id", None),
        system_id=getattr(payload, "system_id", None),
        location_id=getattr(payload, "location_id", None),
    )


def entity_me_mapper(user: User) -> dict:
    """TH: User → /me response dict"""
    if user is None:
        raise ValueError("entity_me_mapper: user is None")
    name = user.name
    return {
        "id": user.id,
        "first_name": (name.first_name if name else "") or "",
        "last_name": (name.last_name if name else "") or "",
        "preferred_name": (name.preferred_name if name else "") or "",
        "full_name": (name.full_name if name else None),
        "nickname": (name.nickname if name else None),
        "username": user.username,
        "email": str(user.email) if user.email else "",
        "phone": str(user.phone) if user.phone else None,
        "mobile_number": user.mobile_number,
        "line_id": user.line_id,
        "gender": user.gender.value if user.gender else None,
        "birthdate": user.birthdate.isoformat() if user.birthdate else None,
        "avatar": user.avatar,
        "avatar_path": user.avatar_path,
        "role": user.role.value if user.role else Role.USER.value,
        "status": int(user.status.value) if user.status else 1,
        "online_status": user.online_status.value if user.online_status else "0",
        "is_verified": user.security.is_verified,
        "is_superuser": user.security.is_superuser,
        "last_sign_in_at": (
            user.security.last_sign_in_at.isoformat()
            if user.security.last_sign_in_at else None
        ),
        "created_at": (
            user.created_at.isoformat() if user.created_at
            else datetime.now(BRASILIA_TZ).isoformat()
        ),
    }


# ═════════════════════════════════════════════════════════
# HELPERS สำหรับ routers.py
# ═════════════════════════════════════════════════════════
def me_entity_mapper(authentication) -> User:
    """TH: ดึง User จาก Authentication | EN: extract User from Authentication"""
    return authentication.user


def entity_create_mapper(user: User):
    """
    TH: map User entity → CreateResponse envelope
    EN: map User entity → CreateResponse envelope
    """
    if user is None or user.id is None:
        raise ValueError("entity_create_mapper requires persisted user with id")

    fields = set(getattr(CreateResponse, "model_fields", {}).keys())

    if {"code", "method", "path", "timestamp", "details"}.issubset(fields):
        return CreateResponse(
            code=201,
            method="POST",
            path="/api/v1/user",
            timestamp=datetime.now(BRASILIA_TZ),
            details={
                "message": ResponseMessages.CREATED.value,
                "data": {"id": str(user.id)},
            },
        )

    if {"code", "message", "data"}.issubset(fields):
        return CreateResponse(
            code=201,
            message=ResponseMessages.CREATED.value,
            data={"id": str(user.id)},
        )

    if "message" in fields:
        return CreateResponse(message=ResponseMessages.CREATED.value)

    raise ValueError(
        f"Unsupported CreateResponse fields: {sorted(fields)}. "
        "Please check shared/presentation/schemas.py"
    )

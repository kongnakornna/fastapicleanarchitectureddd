from __future__ import annotations

from datetime import datetime

from automapper import mapper
from datetime import date, datetime

from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.enums import Role
from app.modules.user.domain.entities import User
from app.modules.user.domain.enums import Gender
from app.modules.user.presentation.schemas import MeResponse
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.domain.value_objects import Name
from app.modules.user.infrastructure.models import UserModel
from app.modules.user.presentation.schemas import (
    CreateRequest,
    CreateResponse,
    MeResponse,
)


# =====================================================================
# HELPERS
# =====================================================================
def _split_full_name(full_name: str | None) -> tuple[str, str]:
    """TH: แยก full_name | EN: split full_name"""
    parts = (full_name or "").strip().split(maxsplit=1)
    return (parts[0] if parts else "", parts[1] if len(parts) > 1 else "")


def _extract_name_fields(payload) -> tuple[str, str, str | None]:
    """TH: ดึง (first, last, preferred) | EN: extract name fields"""
    if hasattr(payload, "first_name") and hasattr(payload, "last_name"):
        return (
            payload.first_name or "",
            payload.last_name or "",
            getattr(payload, "preferred_name", None),
        )
    first_name, last_name = _split_full_name(getattr(payload, "full_name", None))
    return first_name, last_name, getattr(payload, "preferred_name", None)


# =====================================================================
# ENTITY / DTOS
# =====================================================================
def create_entity_mapper(payload: CreateRequest) -> User:
    """
    TH: map request payload → User entity (explicit — กัน automapper พา field เกิน)
    EN: map request payload → User entity (explicit mapping)
    """
    first_name, last_name, preferred_name = _extract_name_fields(payload)

    name = Name(
        first_name=first_name,
        last_name=last_name,
        preferred_name=preferred_name or first_name,
    )

    raw_password = getattr(payload, "password", None)
    if not raw_password:
        raise ValueError("password is required")

    phone = getattr(payload, "phone", None) or getattr(payload, "phone_number", None)

    user_kwargs: dict = {
        "name": name,
        "email": getattr(payload, "email", None),
        "password": raw_password,
    }

    if phone:
        user_kwargs["phone"] = phone

    gender = getattr(payload, "gender", None)
    if gender is not None:
        user_kwargs["gender"] = gender

    birthdate = getattr(payload, "birthdate", None)
    if birthdate is not None:
        user_kwargs["birthdate"] = birthdate

    return User(**user_kwargs)


def entity_create_mapper(user: User) -> CreateResponse:
    """
    TH: map User entity → CreateResponse envelope (auto-detect signature)
    EN: map User entity → CreateResponse envelope (auto-detect signature)
    """
    if user is None or user.id is None:
        raise ValueError("entity_create_mapper requires persisted user with id")

    fields = set(getattr(CreateResponse, "model_fields", {}).keys())

    # ── Signature A: code, method, path, timestamp, details ──
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

    # ── Signature B: code, message, data ──
    if {"code", "message", "data"}.issubset(fields):
        return CreateResponse(
            code=201,
            message=ResponseMessages.CREATED.value,
            data={"id": str(user.id)},
        )

    # ── Signature C: message only ──
    if "message" in fields:
        return CreateResponse(message=ResponseMessages.CREATED.value)

    raise ValueError(
        f"Unsupported CreateResponse fields: {sorted(fields)}. "
        "Please paste shared/presentation/schemas.py"
    )


def me_entity_mapper(authentication: Authentication) -> User:
    """TH: ดึง User จาก Authentication | EN: extract User from Authentication"""
    return authentication.user


def entity_me_mapper(user: User) -> MeResponse:
    """
    TH: map User → MeResponse (explicit construction แทน automapper)
        เพื่อคุม default ของ nullable field ให้ชัดเจน

    EN: map User → MeResponse (explicit construction instead of automapper)
        to make nullable-field defaults explicit.
    """
    if user is None:
        # กันกรณี Authentication.user เป็น None จริง ๆ (ไม่ควรเกิดหลัง resolve)
        raise ValueError("entity_me_mapper: user is None")

    name = user.name
    return MeResponse(
        first_name=(name.first_name if name else "") or "",
        last_name=(name.last_name if name else "") or "",
        preferred_name=(name.preferred_name if name else "") or "",
        gender=user.gender,                         # None ได้ → response field เป็น optional แล้ว
        birthdate=user.birthdate,                   # None ได้
        email=str(user.email) if user.email else "",
        phone=str(user.phone) if user.phone else None,
        role=user.role or Role.USER,
        created_at=user.created_at or datetime.now(BRASILIA_TZ),
    )


# =====================================================================
# ENTITY / MODELS
# =====================================================================
def model_entity_mapper(model: UserModel) -> User:
    """TH: DB row → User entity | EN: DB row → User entity"""
    return mapper.to(User).map(
        model,
        fields_mapping={
            "id": model.id,
            "name": Name(
                first_name=model.first_name,
                last_name=model.last_name,
                preferred_name=model.preferred_name,
            ),
            "gender": model.gender,
            "birthdate": model.birthdate,
            "email": str(model.email),
            "phone": str(model.phone) if model.phone else None,
            "hashed_password": model.hashed_password,
            "role": model.role,
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        },
    )


def entity_model_mapper(user: User) -> UserModel:
    """TH: User entity → DB model | EN: User entity → DB model"""
    if not user.hashed_password:
        raise ValueError(
            "entity_model_mapper: user.hashed_password is None — hash before persist"
        )

    return mapper.to(UserModel).map(
        user,
        fields_mapping={
            "id": user.id,
            "first_name": user.name.first_name if user.name else "",
            "last_name": user.name.last_name if user.name else "",
            "preferred_name": user.name.preferred_name if user.name else "",
            "gender": user.gender,
            "birthdate": user.birthdate,
            "email": str(user.email) if user.email else None,
            "phone": str(user.phone) if user.phone else None,
            "hashed_password": user.hashed_password,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    )

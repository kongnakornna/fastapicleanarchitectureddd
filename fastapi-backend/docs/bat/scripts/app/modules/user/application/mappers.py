from automapper import mapper

from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.domain.value_objects import Name
from app.modules.user.domain.entities import User
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
    """
    แยก full_name เป็น (first_name, last_name)

    ตัวอย่าง:
        "Demo"          → ("Demo", "")
        "John Doe"      → ("John", "Doe")
        "John van Doe"  → ("John", "van Doe")   # แยกที่ช่องว่างแรก
        "" หรือ None    → ("", "")
    """
    parts = (full_name or "").strip().split(maxsplit=1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def _extract_name_fields(payload) -> tuple[str, str, str | None]:
    """
    ดึง (first_name, last_name, preferred_name) จาก payload

    รองรับ 2 รูปแบบ:
        1. มี first_name / last_name ตรง ๆ (เช่น CreateRequest)
        2. มีแค่ full_name (เช่น SignUpRequest) → split ให้อัตโนมัติ
    """
    # แบบที่ 1: มี first_name/last_name ตรง ๆ
    if hasattr(payload, "first_name") and hasattr(payload, "last_name"):
        return (
            payload.first_name or "",
            payload.last_name or "",
            getattr(payload, "preferred_name", None),
        )

    # แบบที่ 2: มีแค่ full_name → split ให้
    first_name, last_name = _split_full_name(getattr(payload, "full_name", None))
    return first_name, last_name, getattr(payload, "preferred_name", None)


# =====================================================================
# ENTITY / DTOS
# =====================================================================
def create_entity_mapper(payload: CreateRequest) -> User:
    """
    Map request payload → User domain entity

    ใช้ได้ทั้ง CreateRequest และ SignUpRequest เพราะ:
    - ตรวจชื่อ field ของ name แบบ dynamic (first_name/last_name หรือ full_name)
    - ตรวจ field ของเบอร์โทร (phone หรือ phone_number) แล้ว map ให้ตรงกัน
    """
    first_name, last_name, preferred_name = _extract_name_fields(payload)

    fields_mapping: dict = {
        "name": Name(
            first_name=first_name,
            last_name=last_name,
            preferred_name=preferred_name,
        ),
    }

    # SignUpRequest ใช้ชื่อ field ว่า phone_number แต่ User entity ใช้ phone
    # ถ้า payload มี phone_number และไม่มี phone → map ให้ตรง
    if hasattr(payload, "phone_number") and not hasattr(payload, "phone"):
        fields_mapping["phone"] = payload.phone_number

    return mapper.to(User).map(payload, fields_mapping=fields_mapping)


def entity_create_mapper(user: User) -> CreateResponse:
    """Map User entity → CreateResponse DTO"""
    return mapper.to(CreateResponse).map(user)


def me_entity_mapper(authentication: Authentication) -> User:
    """ดึง User ออกจาก Authentication entity โดยตรง"""
    return authentication.user


def entity_me_mapper(user: User) -> MeResponse:
    """
    Map User entity → MeResponse DTO
    ต้อง flatten Name value object ให้เป็น field แบน
    และแปลง value object (email, phone) ให้เป็น string
    """
    return mapper.to(MeResponse).map(
        user,
        fields_mapping={
            "first_name": user.name.first_name,
            "last_name": user.name.last_name,
            "preferred_name": user.name.preferred_name,
            "email": str(user.email),
            "phone": str(user.phone) if user.phone else None,
        },
    )


# =====================================================================
# ENTITY / MODELS
# =====================================================================
def model_entity_mapper(model: UserModel) -> User:
    """
    Map infrastructure model (DB row) → User domain entity
    ต้องประกอบ Name value object จาก first_name/last_name/preferred_name
    และแปลง string จาก DB กลับเป็น value object
    """
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
    """
    Map User domain entity → infrastructure model (ก่อนบันทึก DB)
    ต้อง flatten Name value object ให้เป็นคอลัมน์แบน
    """
    return mapper.to(UserModel).map(
        user,
        fields_mapping={
            "id": user.id,
            "first_name": user.name.first_name,
            "last_name": user.name.last_name,
            "preferred_name": user.name.preferred_name,
            "gender": user.gender,
            "birthdate": user.birthdate,
            "email": str(user.email),
            "phone": str(user.phone) if user.phone else None,
            "hashed_password": user.hashed_password,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    )

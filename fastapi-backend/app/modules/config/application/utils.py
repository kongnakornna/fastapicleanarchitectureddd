"""
Application Utils — ฟังก์ชันช่วยเหลือของ config
get_config: helper สำหรับดึงค่า config พร้อม default
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from .exceptions import ConfigException, ConfigKeyNotFoundException
from .interfaces import (
    IConfigCache,
    IConfigRepository,
    ISecretCipher,
)
from .use_cases import ConfigUseCases


async def get_config(
    key: str,
    default: Any = None,
    user_id: str | None = None,
    *,
    repo: IConfigRepository,
    cache: IConfigCache,
    cipher: ISecretCipher,
    events: Any = None,
) -> Any:
    """
    Get config helper — ดึงค่า config พร้อม typed value
    หากไม่พบ key จะคืน default (ไม่ throw)

    Args:
        key: config key
        default: ค่าเริ่มต้นหากไม่พบ
        user_id: user id สำหรับ override
        repo, cache, cipher, events: dependencies

    Returns:
        typed value ของ config หรือ default
    """
    try:
        use_cases = ConfigUseCases(repo=repo, cache=cache, cipher=cipher, events=events)
        entry = await use_cases.get_effective(key, user_id=user_id)
        return entry.typed_value()
    except ConfigKeyNotFoundException:
        return default
    except ConfigException as e:
        logger.warning(f"get_config fallback to default for '{key}': {e}")
        return default


def make_cache_key(tenant_id: str, user_id: str | None, key: str) -> str:
    """สร้าง cache key มาตรฐาน: {tenant}:{user|-}:{key}"""
    return f"{tenant_id}:{user_id or '-'}:{key}"


def resolve_scope_id(scope: str, tenant_id: str, user_id: str | None) -> str:
    """
    คืน scope_id ตาม scope
    - GLOBAL → 'GLOBAL'
    - TENANT → tenant_id
    - USER   → user_id
    """
    if scope == "GLOBAL":
        return "GLOBAL"
    if scope == "TENANT":
        return tenant_id
    if scope == "USER":
        return user_id or ""
    return tenant_id

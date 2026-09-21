"""tenancy application utils."""

import re

SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,30}$")


def validate_slug(slug: str) -> bool:
    """ตรวจสอบ slug — Validate slug format."""
    return bool(SLUG_PATTERN.match(slug))


def generate_schema_name(tenant_id: str) -> str:
    """สร้าง schema name — Generate schema name."""
    safe = tenant_id.replace("-", "_")
    return f"tenant_{safe}"

"""tenant_context infrastructure models — ไม่มี (context ไม่ persist).

Context ไม่ถูก persist ลง DB — resolve จาก public.tenants แทน
Context is not persisted — resolved from public.tenants instead
"""

from app.shared.base_model import Base  # noqa: F401  (kept for parity)

__all__: list[str] = []

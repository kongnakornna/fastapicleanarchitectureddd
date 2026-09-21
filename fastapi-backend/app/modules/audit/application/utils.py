"""
Audit Utilities — ยูทิลิตี้ audit
Audit Utilities — decorator + helpers for audit module
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from audit.domain.enums import AuditAction
from loguru import logger


def diff_states(
    before: dict[str, Any] | None, after: dict[str, Any] | None
) -> list[dict[str, Any]]:
    """
    Compute field-level diff — คำนวณส่วนต่างระดับ field

    Returns list of {field, before, after} for changed keys only.
    """
    before = before or {}
    after = after or {}
    keys = set(before) | set(after)
    return [
        {"field": k, "before": before.get(k), "after": after.get(k)}
        for k in sorted(keys)
        if before.get(k) != after.get(k)
    ]


def auditable(
    action: str,
    resource_type: str,
    resource_id_arg: str = "id",
    extract_before: Callable | None = None,
    extract_after: Callable | None = None,
):
    """
    Decorator to auto-log auditable use cases — decorator บันทึก audit อัตโนมัติ

    Usage:
        @auditable(AuditAction.UPDATE, "Invoice", resource_id_arg="invoice_id")
        async def update_invoice(self, invoice_id, ...):
            ...

    Note: The wrapped callable must have access to `self.audit` (AuditUseCases).
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            # Resolve self (bound method) — หา self
            self_obj = args[0] if args else None
            audit_uc = getattr(self_obj, "audit", None)

            if audit_uc is None:
                # No audit use case available → just run
                # ไม่มี audit use case → รันปกติ
                return await fn(*args, **kwargs)

            # Resolve resource id — หา resource id
            resource_id = kwargs.get(resource_id_arg)
            if resource_id is None and len(args) > 1:
                resource_id = args[1]

            # Capture before state
            # เก็บ before state
            before: dict[str, Any] = {}
            if extract_before is not None:
                try:
                    before = extract_before(*args, **kwargs) or {}
                except Exception as e:
                    logger.warning(f"auditable: extract_before failed: {e}")

            try:
                result = await fn(*args, **kwargs)
            except Exception:
                # On failure, still record attempt with empty after
                # ถ้า fail ยังบันทึก attempt ด้วย after ว่าง
                try:
                    await audit_uc.log(
                        action=action,
                        resource_type=resource_type,
                        resource_id=str(resource_id or "unknown"),
                        before=before,
                        after={},
                    )
                except Exception as audit_err:
                    logger.warning(f"auditable: post-failure audit failed: {audit_err}")
                raise

            # Capture after state
            # เก็บ after state
            after: dict[str, Any] = {}
            if extract_after is not None:
                try:
                    after = extract_after(result) or {}
                except Exception as e:
                    logger.warning(f"auditable: extract_after failed: {e}")

            # Append audit log (best-effort, never break business flow)
            # บันทึก audit log (best-effort ไม่ทำ business flow พัง)
            try:
                await audit_uc.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=str(resource_id or "unknown"),
                    before=before,
                    after=after,
                )
            except Exception as audit_err:
                logger.warning(f"auditable: post-success audit failed: {audit_err}")

            return result

        return wrapper

    return decorator


def severity_for(action: str) -> str:
    """Derive severity from action — หา severity จาก action"""
    try:
        act = AuditAction(action)
        return "CRITICAL" if act.is_critical() else "INFO"
    except ValueError:
        return "INFO"

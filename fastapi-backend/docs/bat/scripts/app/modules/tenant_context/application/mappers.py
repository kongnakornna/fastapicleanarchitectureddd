"""tenant_context application mappers — ตัวแปลงข้อมูล."""

from ..domain.value_objects import TenantContext


class TenantContextMapper:
    """TenantContextMapper — แปลง domain <-> dict/headers."""

    @staticmethod
    def to_context(data: dict) -> TenantContext:
        """แปลง dict เป็น TenantContext — Map dict to TenantContext."""
        return TenantContext(
            tenant_id=data.get("tenant_id", ""),
            user_id=data.get("user_id"),
            correlation_id=data.get("correlation_id", ""),
            request_id=data.get("request_id", ""),
            locale=data.get("locale", "th-TH"),
            timezone=data.get("timezone", "Asia/Bangkok"),
        )

    @staticmethod
    def to_headers(ctx: TenantContext) -> dict:
        """แปลง TenantContext เป็น headers — Map to headers."""
        return {
            "X-Tenant-ID": ctx.tenant_id,
            "X-Correlation-ID": ctx.correlation_id,
            "X-Request-ID": ctx.request_id,
            "Accept-Language": ctx.locale,
        }

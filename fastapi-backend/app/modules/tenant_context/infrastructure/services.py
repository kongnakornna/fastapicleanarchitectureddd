"""tenant_context infrastructure services — HeaderTenantExtractor.

ดึง tenant จาก HTTP header
Extract tenant from HTTP header
"""

from ..domain.exceptions import DomainError
from ..domain.value_objects import TenantContext


class HeaderTenantExtractor:
    """HeaderTenantExtractor — ดึง tenant จาก HTTP headers."""

    TENANT_HEADER = "X-Tenant-ID"
    CORRELATION_HEADER = "X-Correlation-ID"
    REQUEST_HEADER = "X-Request-ID"

    def extract(self, headers: dict) -> TenantContext:
        """ดึง tenant context จาก headers — Extract from headers."""
        # normalize header keys (case-insensitive)
        lower = {k.lower(): v for k, v in headers.items()}

        tenant_id = lower.get(self.TENANT_HEADER.lower(), "")
        if not tenant_id:
            raise DomainError(f"Missing required header: {self.TENANT_HEADER}")

        return TenantContext(
            tenant_id=tenant_id,
            user_id=lower.get("x-user-id"),
            correlation_id=lower.get(self.CORRELATION_HEADER.lower(), ""),
            request_id=lower.get(self.REQUEST_HEADER.lower(), ""),
            locale=lower.get("accept-language", "th-TH"),
            timezone=lower.get("x-timezone", "Asia/Bangkok"),
        )

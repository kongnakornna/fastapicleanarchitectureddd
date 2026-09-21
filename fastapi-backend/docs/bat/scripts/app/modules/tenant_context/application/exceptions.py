"""tenant_context application exceptions — ข้อยกเว้นแอปพลิเคชัน."""

from app.shared.exceptions import ApplicationException


class TenantContextException(ApplicationException):
    """TenantContextException — ข้อผิดพลาดระดับแอปพลิเคชัน."""

    code = "tctx_APP_ERROR"

    def __init__(self, message: str = "Tenant context operation failed"):
        self.message = message
        super().__init__(message)


class TenantNotFoundInContext(TenantContextException):
    """TenantNotFoundInContext — ไม่พบ tenant ใน context."""

    code = "tctx_NOT_FOUND"

    def __init__(self, message: str = "Tenant not found in context"):
        super().__init__(message)

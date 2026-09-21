"""tenancy application exceptions."""

from app.shared.exceptions import ApplicationException


class TenancyException(ApplicationException):
    """TenancyException — ข้อผิดพลาดแอปพลิเคชัน."""

    code = "ten_APP_ERROR"

    def __init__(self, message: str = "Tenancy operation failed"):
        self.message = message
        super().__init__(message)


class TenantNotFoundException(TenancyException):
    """TenantNotFoundException — ไม่พบ tenant."""

    code = "ten_NOT_FOUND"

    def __init__(self, message: str = "Tenant not found"):
        super().__init__(message)


class TenantSlugConflictException(TenancyException):
    """TenantSlugConflictException — slug ซ้ำ."""

    code = "ten_SLUG_CONFLICT"

    def __init__(self, slug: str = ""):
        super().__init__(f"Slug already exists: {slug}")

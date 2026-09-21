"""tenant_context domain exceptions — ข้อยกเว้นโดเมน."""

from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for tenant_context — ละเมิดกฎโดเมน."""

    code = "tctx_DOMAIN_ERROR"

    def __init__(self, message: str = "Tenant context domain error"):
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message

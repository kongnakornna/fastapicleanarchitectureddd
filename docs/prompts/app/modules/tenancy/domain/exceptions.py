"""tenancy domain exceptions — ข้อยกเว้นโดเมน."""
from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """DomainError — ละเมิดกฎโดเมน."""
    code = "ten_DOMAIN_ERROR"

    def __init__(self, message: str = "Tenancy domain error"):
        self.message = message
        super().__init__(message)
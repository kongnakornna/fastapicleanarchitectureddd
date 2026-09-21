"""Idempotency domain exceptions — ข้อยกเว้นโดเมน"""


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดโดเมน"""

    def __init__(self, message: str = "Domain error"):
        self.message = message
        super().__init__(message)

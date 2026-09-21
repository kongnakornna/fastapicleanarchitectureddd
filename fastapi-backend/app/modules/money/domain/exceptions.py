"""Money domain exceptions — ข้อยกเว้นโดเมนเงิน"""


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดระดับโดเมน"""

    def __init__(self, message: str = "Domain error"):
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message

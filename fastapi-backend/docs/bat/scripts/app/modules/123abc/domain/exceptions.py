"""123Abc domain exceptions — ข้อยกเว้นโดเมน 123abc"""


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดระดับโดเมน"""

    def __init__(self, message: str = "Domain error") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class DuplicateCodeError(DomainError):
    """DuplicateCodeError — code ซ้ำใน tenant เดียวกัน"""

    def __init__(self, code: str) -> None:
        super().__init__(f"code {code!r} already exists")


class InvalidAmountError(DomainError):
    """InvalidAmountError — amount ไม่ถูกต้อง"""

    def __init__(self, message: str = "amount must be >= 0") -> None:
        super().__init__(message)


class InvalidStatusTransitionError(DomainError):
    """InvalidStatusTransitionError — เปลี่ยนสถานะไม่ถูกต้อง"""

    def __init__(self, message: str = "invalid status transition") -> None:
        super().__init__(message)


class 123AbcNotFoundError(DomainError):
    """123AbcNotFoundError — ไม่พบ 123abc"""

    def __init__(self, entity_id: object | None = None) -> None:
        super().__init__(f"123abc not found: {entity_id!r}")
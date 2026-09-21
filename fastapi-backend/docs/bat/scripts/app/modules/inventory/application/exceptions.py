"""Inventory application exceptions — ข้อยกเว้นแอปพลิเคชัน"""


class StandardException(Exception):
    """StandardException — ข้อผิดพลาดมาตรฐานที่รู้จัก (business)"""

    def __init__(self, message: str = "operation failed") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class DuplicateCodeError(StandardException):
    """DuplicateCodeError — code ซ้ำ"""

    def __init__(self, code: str) -> None:
        super().__init__(f"code {code!r} already exists")


class InventoryNotFoundError(StandardException):
    """InventoryNotFoundError — ไม่พบ entity"""

    def __init__(self, entity_id: object | None = None) -> None:
        super().__init__(f"inventory not found: {entity_id!r}")


class VersionConflictError(StandardException):
    """VersionConflictError — version ไม่ตรง"""

    def __init__(self, expected: int, actual: int) -> None:
        super().__init__(f"version conflict: expected {expected}, got {actual}")
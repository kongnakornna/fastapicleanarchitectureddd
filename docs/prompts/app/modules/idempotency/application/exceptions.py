"""Idempotency application exceptions — ข้อยกเว้นแอปพลิเคชัน"""


class StandardException(Exception):
    """StandardException — ข้อผิดพลาดมาตรฐาน"""
    pass


class IdempotencyException(StandardException):
    """IdempotencyException — ข้อผิดพลาด idempotency"""

    def __init__(self, message: str = "Idempotency operation failed"):
        self.message = message
        super().__init__(message)


class IdempotencyConflictException(IdempotencyException):
    """IdempotencyConflictException — ความขัดแย้ง idempotency"""

    def __init__(self, message: str = "Idempotency conflict"):
        super().__init__(message)


class IdempotencyStoreException(IdempotencyException):
    """IdempotencyStoreException — ข้อผิดพลาด store"""

    def __init__(self, message: str = "Idempotency store error"):
        super().__init__(message)
"""Shared domain exceptions — ข้อยกเว้นโดเมนกลาง

TH: แยกออกมาเพื่อตัด circular import ระหว่าง
    domain/entities.py  <->  domain/value_objects.py
EN: Split out to break the circular import between
    domain/entities.py  <->  domain/value_objects.py
"""
from __future__ import annotations


class DomainError(Exception):
    """DomainError — ข้อผิดพลาดระดับโดเมน"""

    def __init__(self, message: str = "Domain error") -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class DomainErrors:
    """DomainErrors — รวม error code ของโดเมน"""

    NOT_FOUND   = "DOMAIN_NOT_FOUND"
    INVALID     = "DOMAIN_INVALID"
    DUPLICATE   = "DOMAIN_DUPLICATE"
    CONFLICT    = "DOMAIN_CONFLICT"


__all__ = ["DomainError", "DomainErrors"]
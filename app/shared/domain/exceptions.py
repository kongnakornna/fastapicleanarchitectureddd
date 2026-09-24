# app/modules/shared/domain/exceptions.py
"""
TH: Domain exceptions ของ shared layer
EN: shared-layer domain exceptions
"""
from __future__ import annotations

from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """TH: domain error เดี่ยว | EN: single domain error"""

    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "Domain rule violated") -> None:
        self.message: str = message
        super().__init__()
        try:
            self.args = (message,)
        except Exception:
            pass

    def __str__(self) -> str:
        return self.message


class DomainErrors(DomainException):
    """TH: รวม domain error หลายตัว | EN: aggregate multiple domain errors"""

    code: str = "DOMAIN_ERRORS"

    def __init__(self, errors: list[str] | None = None) -> None:
        self.errors: list[str] = list(errors) if errors else []
        self.message: str = (
            "; ".join(self.errors) if self.errors else "Domain validation failed"
        )
        super().__init__()
        try:
            self.args = (self.message,)
        except Exception:
            pass

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"DomainErrors({self.errors!r})"


__all__ = ["DomainError", "DomainErrors"]
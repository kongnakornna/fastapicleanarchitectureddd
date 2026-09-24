"""pdpa application exceptions"""
from __future__ import annotations


class ApplicationError(Exception):
    """TH: base | EN: base"""


class DuplicateConsentError(ApplicationError):
    """TH: consent ซ้ำ | EN: duplicate consent"""


class DSARNotFoundAppError(ApplicationError):
    """TH: ไม่พบ DSAR | EN: DSAR not found"""


class ConsentNotFoundAppError(ApplicationError):
    """TH: ไม่พบ consent | EN: consent not found"""


class PolicyNotFoundAppError(ApplicationError):
    """TH: ไม่พบ policy | EN: policy not found"""


class CookieConsentNotFoundAppError(ApplicationError):
    """TH: ไม่พบ cookie consent | EN: cookie consent not found"""


class VersionConflictError(ApplicationError):
    """TH: version ไม่ตรง | EN: version conflict"""


class IdentityVerificationRequiredError(ApplicationError):
    """TH: ต้องยืนยันตัวตน | EN: identity verification required"""


class IdempotencyConflictError(ApplicationError):
    """TH: คำขอเดียวกันกำลังประมวลผล | EN: same key in progress"""


class IdempotencyMismatchError(ApplicationError):
    """TH: payload ไม่ตรงกับ key เดิม | EN: payload mismatch for key"""
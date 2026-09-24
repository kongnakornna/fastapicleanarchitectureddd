"""pdpa domain exceptions"""
from __future__ import annotations


class PDPAError(Exception):
    """TH: base | EN: base"""


class ConsentRequiredError(PDPAError):
    """TH: ต้องได้รับความยินยอมก่อน"""


class InvalidConsentStateError(PDPAError):
    """TH: สถานะไม่ถูกต้อง"""


class ConsentAlreadyGrantedError(PDPAError):
    """TH: ให้ความยินยอมซ้ำ"""


class DSARNotFoundError(PDPAError):
    """TH: ไม่พบ DSAR"""


class DSARExpiredError(PDPAError):
    """TH: DSAR เกิน deadline"""


class PrivacyPolicyNotFoundError(PDPAError):
    """TH: ไม่พบ privacy policy"""


class InvalidIdentityVerificationError(PDPAError):
    """TH: ยืนยันตัวตนไม่สำเร็จ"""

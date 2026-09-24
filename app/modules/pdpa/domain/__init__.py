"""pdpa domain layer"""
from .entities import ConsentLog, DSARRequest, PrivacyPolicy, CookieConsent
from .enums import (
    ConsentStatus, DSARStatus, DSARType,
    PrivacyPolicyStatus, PurposeCategory, IdempotencyStatus,
)
from .value_objects import (
    ConsentId, PurposeCode, DataSubjectId, Evidence, EncryptionKeyVersion,
)
from .events import (
    ConsentGranted, ConsentRevoked, DSARSubmitted, DSARCompleted,
    DataErasureRequested, PrivacyPolicyPublished,
)
from .exceptions import (
    PDPAError, ConsentRequiredError, InvalidConsentStateError,
    ConsentAlreadyGrantedError, DSARNotFoundError, DSARExpiredError,
    PrivacyPolicyNotFoundError, InvalidIdentityVerificationError,
)
from .idempotency import IdempotencyRecord, compute_request_hash

__all__ = [
    "ConsentLog", "DSARRequest", "PrivacyPolicy", "CookieConsent",
    "ConsentStatus", "DSARStatus", "DSARType", "PrivacyPolicyStatus",
    "PurposeCategory", "IdempotencyStatus",
    "ConsentId", "PurposeCode", "DataSubjectId", "Evidence",
    "EncryptionKeyVersion",
    "ConsentGranted", "ConsentRevoked", "DSARSubmitted", "DSARCompleted",
    "DataErasureRequested", "PrivacyPolicyPublished",
    "PDPAError", "ConsentRequiredError", "InvalidConsentStateError",
    "ConsentAlreadyGrantedError", "DSARNotFoundError", "DSARExpiredError",
    "PrivacyPolicyNotFoundError", "InvalidIdentityVerificationError",
    "IdempotencyRecord", "compute_request_hash",
]
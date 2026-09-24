"""pdpa enums — Enum ของ PDPA"""
from __future__ import annotations
from enum import StrEnum


class ConsentStatus(StrEnum):
    """TH: สถานะความยินยอม | EN: Consent status"""
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class PurposeCategory(StrEnum):
    """TH: หมวดวัตถุประสงค์ | EN: Purpose category"""
    DATA_COLLECTION = "DATA_COLLECTION"
    DATA_DELETION = "DATA_DELETION"
    USER_ACCOUNT = "USER_ACCOUNT"
    USAGE_LOGS = "USAGE_LOGS"
    TRANSACTION_HISTORY = "TRANSACTION_HISTORY"


class DSARType(StrEnum):
    """TH: ประเภท DSAR | EN: DSAR type"""
    ACCESS = "ACCESS"
    ERASURE = "ERASURE"
    WITHDRAW_CONSENT = "WITHDRAW_CONSENT"


class DSARStatus(StrEnum):
    """TH: สถานะ DSAR | EN: DSAR status"""
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class PrivacyPolicyStatus(StrEnum):
    """TH: สถานะนโยบาย | EN: Privacy policy status"""
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class IdempotencyStatus(StrEnum):
    """TH: สถานะ idempotency key | EN: Idempotency status"""
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
"""Idempotency enums — Enum สำหรับ idempotency"""
from enum import Enum


class IdempotencyStatus(str, Enum):
    """IdempotencyStatus — สถานะ idempotency"""
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IdempotencyConflict(str, Enum):
    """IdempotencyConflict — ประเภทความขัดแย้ง"""
    SAME_KEY_SAME_PAYLOAD = "SAME_KEY_SAME_PAYLOAD"
    SAME_KEY_DIFF_PAYLOAD = "SAME_KEY_DIFF_PAYLOAD"
    CONCURRENT = "CONCURRENT"
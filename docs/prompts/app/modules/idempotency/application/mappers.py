"""Idempotency mappers — ตัวแปลงข้อมูล"""
from ..domain.entities import IdempotencyRecord


class IdempotencyMapper:
    """IdempotencyMapper — ตัวแปลง record ไป-กลับ"""

    @staticmethod
    def to_schema(rec: IdempotencyRecord) -> dict:
        """แปลง record เป็น dict"""
        return {
            "key": rec.key,
            "status": rec.status,
            "request_hash": rec.request_hash,
            "response_status": rec.response_status,
            "response_body": rec.response_body,
            "expires_at": rec.expires_at.isoformat() if rec.expires_at else None,
        }

    @staticmethod
    def to_entity(data: dict) -> IdempotencyRecord:
        """แปลง dict เป็น record"""
        return IdempotencyRecord(
            key=data.get("key", ""),
            status=data.get("status", "IN_PROGRESS"),
            request_hash=data.get("request_hash", ""),
            response_status=data.get("response_status", 0),
            response_body=data.get("response_body", {}),
        )
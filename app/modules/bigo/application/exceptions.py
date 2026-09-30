"""bigo application exceptions"""
from __future__ import annotations


class ApplicationError(Exception):
    code: str = "APP_ERROR"
    http_status: int = 400


class ProfileNotFoundAppError(ApplicationError):
    code = "PROFILE_NOT_FOUND"; http_status = 404


class SnapshotNotFoundAppError(ApplicationError):
    code = "SNAPSHOT_NOT_FOUND"; http_status = 404


class LeakNotFoundAppError(ApplicationError):
    code = "LEAK_NOT_FOUND"; http_status = 404


class TopicNotFoundAppError(ApplicationError):
    code = "TOPIC_NOT_FOUND"; http_status = 404


class QueueNotFoundAppError(ApplicationError):
    code = "QUEUE_NOT_FOUND"; http_status = 404


class ConsumerNotFoundAppError(ApplicationError):
    code = "CONSUMER_NOT_FOUND"; http_status = 404


class MemoryLimitAppError(ApplicationError):
    code = "MEMORY_LIMIT_EXCEEDED"; http_status = 507


class LagThresholdAppError(ApplicationError):
    code = "LAG_THRESHOLD_EXCEEDED"; http_status = 429


class KafkaConnectionAppError(ApplicationError):
    code = "KAFKA_CONNECTION_ERROR"; http_status = 502

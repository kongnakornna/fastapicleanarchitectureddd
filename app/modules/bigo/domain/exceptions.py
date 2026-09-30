"""bigo domain exceptions"""
from __future__ import annotations


class BigOError(Exception):
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class MetricNotFoundError(BigOError):
    code = "METRIC_NOT_FOUND"


class ProfileNotFoundError(BigOError):
    code = "PROFILE_NOT_FOUND"


class SnapshotNotFoundError(BigOError):
    code = "SNAPSHOT_NOT_FOUND"


class LeakNotFoundError(BigOError):
    code = "LEAK_NOT_FOUND"


class TopicNotFoundError(BigOError):
    code = "TOPIC_NOT_FOUND"


class QueueNotFoundError(BigOError):
    code = "QUEUE_NOT_FOUND"


class ConsumerNotFoundError(BigOError):
    code = "CONSUMER_NOT_FOUND"


class AlertNotFoundError(BigOError):
    code = "ALERT_NOT_FOUND"


class MemoryLimitExceededError(BigOError):
    code = "MEMORY_LIMIT_EXCEEDED"


class LagThresholdExceededError(BigOError):
    code = "LAG_THRESHOLD_EXCEEDED"


class KafkaConnectionError(BigOError):
    code = "KAFKA_CONNECTION_ERROR"

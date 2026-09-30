"""bigo OpenAPI docs metadata"""
from __future__ import annotations

RESPONSE_PROFILE_200 = {
    "description": "Complexity analysis result",
    "content": {"application/json": {"example": {
        "id": "uuid",
        "function_name": "process_orders",
        "module": "app.services.orders",
        "complexity": "O(n log n)",
        "sample_size": 7,
        "r_squared": 0.984,
    }}},
}
RESPONSE_MEMORY_200 = {
    "description": "Memory snapshot",
    "content": {"application/json": {"example": {
        "snapshot_id": "uuid",
        "rss_mb": 384.2,
        "percent": 4.8,
        "pressure": "NORMAL",
    }}},
}
RESPONSE_KAFKA_LAG_200 = {
    "description": "Kafka consumer lag",
    "content": {"application/json": {"example": {
        "consumer_id": "uuid",
        "topic": "orders.events",
        "total_lag": 1523,
        "health": "HEALTHY",
    }}},
}
RESPONSE_ERROR_400 = {"description": "Domain error"}
RESPONSE_ERROR_404 = {"description": "Not found"}
RESPONSE_ERROR_429 = {"description": "Lag threshold exceeded"}
RESPONSE_ERROR_502 = {"description": "Kafka connection error"}
RESPONSE_ERROR_507 = {"description": "Memory limit exceeded"}

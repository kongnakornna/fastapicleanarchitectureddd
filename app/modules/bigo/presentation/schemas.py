"""bigo Pydantic v2 schemas"""
from __future__ import annotations
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProfileAnalyzeRequest(BaseModel):
    function_name: str = Field(..., min_length=1, max_length=200)
    module: str = ""
    sizes: list[int] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")


class ProfileResponse(BaseModel):
    id: str
    function_name: str
    module: str = ""
    complexity: str
    sample_size: int = 0
    avg_ms: float = 0.0
    p95_ms: float = 0.0
    captured_at: str = ""
    model_config = ConfigDict(extra="forbid")


class ProfileAnalyzeResponse(ProfileResponse):
    r_squared: float = 0.0
    coefficients: dict[str, float] = Field(default_factory=dict)


class MemorySnapshotResponse(BaseModel):
    snapshot_id: str
    rss_mb: float
    vms_mb: float
    percent: float
    pressure: str
    top_allocations: list[Any] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")


class MemoryLeakResponse(BaseModel):
    id: str
    location: str
    leak_type: str
    growth_mb_per_hour: float
    current_bytes: int
    samples: int = 0
    status: str
    model_config = ConfigDict(extra="forbid")


class ResolveLeakResponse(BaseModel):
    id: str
    status: str
    updated: bool
    model_config = ConfigDict(extra="forbid")


class KafkaTopicCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    partitions: int = Field(default=3, ge=1, le=1000)
    replication: int = Field(default=1, ge=1, le=10)
    retention_ms: int = Field(default=604800000, ge=1000)
    max_message_bytes: int = Field(default=1048576, ge=1024)
    model_config = ConfigDict(extra="forbid")


class KafkaTopicResponse(BaseModel):
    id: str
    name: str
    partitions: int
    replication_factor: int = 1
    is_active: bool = True
    already_exists: bool = False
    model_config = ConfigDict(extra="forbid")


class KafkaLagMonitorRequest(BaseModel):
    group_id: str = Field(..., min_length=1, max_length=300)
    topic: str = Field(..., min_length=1, max_length=300)
    threshold: int = Field(default=10000, ge=1)
    model_config = ConfigDict(extra="forbid")


class KafkaLagResponse(BaseModel):
    consumer_id: str
    topic: str
    group_id: str
    total_lag: int
    health: str
    partitions: list[dict[str, Any]] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")


class BackpressureRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=300)
    reason: str = "lag_exceeded"
    model_config = ConfigDict(extra="forbid")


class BackpressureResponse(BaseModel):
    topic: str
    active: bool
    reason: str = ""
    model_config = ConfigDict(extra="forbid")


class MetricCreateRequest(BaseModel):
    kind: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    value: float
    unit: str = ""
    labels: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")


class MetricResponse(BaseModel):
    id: str
    kind: str
    name: str
    value: float
    unit: str = ""
    captured_at: str = ""
    model_config = ConfigDict(extra="forbid")


class AlertTriggerRequest(BaseModel):
    severity: str = Field(..., pattern="^(INFO|WARNING|ERROR|CRITICAL)$")
    kind: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)
    payload: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")


class AlertResponse(BaseModel):
    alert_id: str
    severity: str
    kind: str
    message: str
    model_config = ConfigDict(extra="forbid")


class PipelineProcessRequest(BaseModel):
    n: int = Field(..., ge=0, le=10_000_000)
    algorithm_type: str = Field(default="O(n)", max_length=20)
    topic: str | None = None
    cache_key: str | None = None
    model_config = ConfigDict(extra="forbid")


class PipelineProcessResponse(BaseModel):
    trace_id: str
    n: int
    complexity: str
    status: str
    priority: str
    rss_mb: float
    pressure: str
    duration_ms: int
    kafka_partition: int
    kafka_sent: bool
    model_config = ConfigDict(extra="forbid")


class PipelineMetricsResponse(BaseModel):
    counters: dict[str, int] = Field(default_factory=dict)
    gauges: dict[str, float] = Field(default_factory=dict)
    histograms: dict[str, dict[str, float]] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")


class PipelineMemoryResponse(BaseModel):
    entries: int
    current_bytes: int
    max_bytes: int
    utilization: float
    pressure: str
    model_config = ConfigDict(extra="forbid")


class PipelineCheckRequest(BaseModel):
    n: int = Field(..., ge=0)
    algorithm_type: str = "O(n)"
    model_config = ConfigDict(extra="forbid")


class PipelineCheckResponse(BaseModel):
    n: int
    algorithm_type: str
    status: str
    priority: str
    model_config = ConfigDict(extra="forbid")


# ═══════════ ADMIN / CACHE / WS ═══════════
class AdminConfigResponse(BaseModel):
    max_n_linear: int
    max_n_quadratic: int
    max_n_cubic: int
    max_n_linearithmic: int
    warn_ratio: float
    memory_max_bytes: int
    memory_high_ratio: float
    memory_critical_ratio: float
    memory_default_ttl_s: int
    memory_evict_batch: int
    kafka_bootstrap: str
    kafka_topic: str
    kafka_dlq_topic: str
    kafka_partition_map: dict[str, int]
    kafka_max_retries: int
    kafka_backoff: list[float]
    kafka_flush_timeout_s: float
    compress_low_priority: bool
    sample_sizes: list[int]
    model_config = ConfigDict(extra="ignore")


class AdminConfigUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_n_linear: int | None = None
    max_n_quadratic: int | None = None
    max_n_cubic: int | None = None
    max_n_linearithmic: int | None = None
    warn_ratio: float | None = None
    memory_max_bytes: int | None = None
    memory_high_ratio: float | None = None
    memory_critical_ratio: float | None = None
    memory_default_ttl_s: int | None = None
    kafka_max_retries: int | None = None
    kafka_flush_timeout_s: float | None = None
    compress_low_priority: bool | None = None


class AdminCacheClearRequest(BaseModel):
    prefix: str | None = None
    model_config = ConfigDict(extra="forbid")


class AdminCacheClearResponse(BaseModel):
    deleted: int
    prefix: str


class AdminHealthResponse(BaseModel):
    status: str
    cache: dict[str, Any]
    memory: dict[str, Any]
    ws: dict[str, Any]


class AdminWSStatsResponse(BaseModel):
    connections: int
    rooms: dict[str, int]
    tenants: dict[str, int]
    heartbeat_interval_s: int
    max_per_tenant: int


class AdminWSListResponse(BaseModel):
    connections: list[dict[str, Any]]


class AdminWSBroadcastRequest(BaseModel):
    message: dict[str, Any]
    room: str | None = None
    tenant_id: str | None = None
    model_config = ConfigDict(extra="forbid")


class AdminWSBroadcastResponse(BaseModel):
    sent: int
    room: str | None = None
    tenant_id: str | None = None


class AdminWSKickResponse(BaseModel):
    conn_id: str
    kicked: bool

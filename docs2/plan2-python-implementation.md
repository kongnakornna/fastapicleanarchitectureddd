# Plan 2: Python Implementation Plan
## IoT Monitoring System - Full Code Translation

---

## 0. Scope

แปลงโค้ดทั้งหมดจาก Go (`icmongolang`) ไปเป็น Python (`fastapiddd`)
โดยใช้โครงสร้าง DDD + Clean Architecture ที่มีอยู่แล้ว

**Go Source Files (ที่ต้องแปลง):**
- `config/config.go` (213 lines)
- `pkg/influxdb/client.go` (625 lines)
- `pkg/mqtt/client.go` (441 lines)
- `pkg/httpErrors/httpErrors.go` (308 lines)
- `pkg/helpers/iot.go` (405 lines)
- `pkg/utils/validator.go` (19 lines)
- `pkg/utils/form.go` (28 lines)
- `internal/modules/queue/manager.go` (329 lines)
- `internal/modules/queue/noop_queue.go` (34 lines)
- `internal/modules/iot/` (ทั้งหมด ~4000 lines)

**Total: ~7,600 lines Go -> ~5,000 lines Python (est.)**

---

## 1. Phase 1: Core Infrastructure

### 1.1 Settings Update
```
File: app/core/settings.py
Action: EDIT
```

เพิ่ม IoT config fields:

```python
# เพิ่มใน class Settings(BaseSettings):

# InfluxDB
INFLUXDB_URL: str = "http://localhost:8086"
INFLUXDB_TOKEN: str = ""
INFLUXDB_ORG: str = "my-org"
INFLUXDB_BUCKET: str = "iot_sensors"
INFLUXDB_TIMEOUT: int = 30

# MQTT
MQTT_BROKER: str = "tcp://localhost:1883"
MQTT_CLIENT_ID: str = ""
MQTT_USERNAME: str = ""
MQTT_PASSWORD: str = ""
MQTT_KEEPALIVE: int = 30
MQTT_CLEAN_SESSION: bool = True
MQTT_AUTO_RECONNECT: bool = True

# Queue
QUEUE_TYPE: str = "redis"  # redis | celery | noop
QUEUE_REDIS_URL: str = "redis://localhost:6379/1"
QUEUE_MAX_RETRIES: int = 3
```

---

### 1.2 InfluxDB Client
```
File: app/core/influxdb_client.py
Action: CREATE
Lines: ~400 (from pkg/influxdb/client.go 625 lines)
```

```python
"""
InfluxDB Client - แปลงจาก pkg/influxdb/client.go
ใช้ influxdb-client-python v2
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.query_api import QueryAPI
from influxdb_client.client.write_api import WriteAPI
from loguru import logger


@dataclass(frozen=True)
class QueryParams:
    """Query parameters for InfluxDB Flux queries"""
    start: str = "-1h"
    stop: str = "now()"
    bucket: str = ""
    measurement: str = ""
    field: str = ""
    limit: int = 1000
    offset: int = 0
    window_period: str = "15s"
    mean: str = "last"
    tz_string: str = ""
    percentile: float = 0.95


@dataclass
class StatisticalResult:
    type: str
    value: Any
    time: str = ""
    data_points: int = 0


@dataclass
class SummaryStats:
    min: float = 0.0
    max: float = 0.0
    avg: float = 0.0
    count: int = 0
    std_dev: float = 0.0
    variance: float = 0.0
    median: float = 0.0
    p95: float = 0.0
    p99: float = 0.0


@dataclass
class QueryMetadata:
    query_time: str = ""
    duration: int = 0
    method: str = ""


@dataclass
class MeanCalculationResult:
    success: bool
    data: list[StatisticalResult] = field(default_factory=list)
    summary: SummaryStats | None = None
    error: str = ""
    metadata: QueryMetadata | None = None


@dataclass
class CountResult:
    total: int = 0
    method: str = ""
    error: str = ""


class InfluxDBClientWrapper:
    """InfluxDB client wrapper - แปลงจาก Go InfluxClient struct"""

    def __init__(self, url: str, token: str, org: str, bucket: str, timeout: int = 30):
        self._org = org
        self._bucket = bucket
        self._timeout = timeout

        self._client = InfluxDBClient(
            url=url,
            token=token,
            org=org,
            timeout=timeout * 1000,  # milliseconds
        )
        self._write_api: WriteAPI = self._client.write_api()
        self._query_api: QueryAPI = self._client.query_api()

        logger.info(f"InfluxDB client initialized: url={url}, org={org}, bucket={bucket}")

    def close(self) -> None:
        self._client.close()

    @property
    def bucket(self) -> str:
        return self._bucket

    def write_data(
        self,
        measurement: str,
        fields: dict[str, Any],
        tags: dict[str, str] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        point = Point(measurement)
        if tags:
            for k, v in tags.items():
                point = point.tag(k, v)
        for k, v in fields.items():
            point = point.field(k, v)
        if timestamp:
            point = point.time(timestamp)
        else:
            point = point.time(datetime.utcnow())

        self._write_api.write(bucket=self._bucket, record=point)
        self._write_api.flush()

    def write_point(
        self,
        measurement: str,
        tags: dict[str, str],
        fields: dict[str, Any],
        timestamp: datetime,
    ) -> None:
        self.write_data(measurement, fields, tags, timestamp)

    def query_filter_data(self, params: QueryParams) -> list[dict[str, Any]]:
        bucket = params.bucket or self._bucket
        flux_query = f'''
            from(bucket: "{bucket}")
                |> range(start: {params.start}, stop: {params.stop})
                |> filter(fn: (r) => r["_measurement"] == "{params.measurement}")
                |> filter(fn: (r) => r["_field"] == "{params.field}")
                |> limit(n: {params.limit}, offset: {params.offset})
                |> yield(name: "filtered_data")
        '''
        return self._execute_query(flux_query, params.tz_string)

    def query_device_chart(self, params: QueryParams) -> list[dict[str, Any]]:
        return self.query_filter_data(params)

    def query_filter_data_rs(self, params: QueryParams) -> list[dict[str, Any]]:
        """Query with ascending sort"""
        bucket = params.bucket or self._bucket
        flux_query = f'''
            from(bucket: "{bucket}")
                |> range(start: {params.start}, stop: {params.stop})
                |> filter(fn: (r) => r["_measurement"] == "{params.measurement}")
                |> filter(fn: (r) => r["_field"] == "{params.field}")
                |> sort(columns: ["_time"], desc: false)
                |> limit(n: {params.limit}, offset: {params.offset})
                |> yield(name: "sorted_data")
        '''
        return self._execute_query(flux_query, params.tz_string)

    def count_rows(self, params: QueryParams) -> CountResult:
        bucket = params.bucket or self._bucket
        start = params.start or "-30d"
        stop = params.stop or "now()"

        flux_query = f'''
            from(bucket: "{bucket}")
                |> range(start: {start}, stop: {stop})
                |> filter(fn: (r) => r["_measurement"] == "{params.measurement}")
                |> filter(fn: (r) => r["_field"] == "{params.field}")
                |> count()
                |> yield(name: "count")
        '''
        try:
            results = self._execute_query(flux_query, params.tz_string)
            if results and "_value" in results[0]:
                return CountResult(total=int(results[0]["_value"]), method="direct_count")
            return CountResult(total=0, method="no_data")
        except Exception as e:
            return CountResult(total=0, error=str(e))

    def calculate_statistics(self, params: QueryParams) -> MeanCalculationResult:
        start_time = time.time()
        bucket = params.bucket or self._bucket
        start = params.start or "-15s"
        stop = params.stop or "now()"
        mean_type = params.mean or "last"
        window_period = params.window_period or "15s"

        flux_query = self._build_statistic_query(
            bucket, start, stop, params.measurement, params.field,
            mean_type, window_period, params.percentile,
        )

        try:
            results = self._execute_query(flux_query, params.tz_string)
            stats = []
            for r in results:
                if "_value" in r:
                    stat = StatisticalResult(type=mean_type, value=r["_value"])
                    if "_time" in r:
                        stat.time = str(r["_time"])
                    stats.append(stat)

            summary = None
            if len(results) > 1 and mean_type in ("mean", "median"):
                summary = self._calculate_summary(params)

            return MeanCalculationResult(
                success=True,
                data=stats,
                summary=summary,
                metadata=QueryMetadata(
                    query_time=datetime.utcnow().isoformat(),
                    duration=int((time.time() - start_time) * 1000),
                    method=mean_type,
                ),
            )
        except Exception as e:
            return MeanCalculationResult(
                success=False,
                error=str(e),
                metadata=QueryMetadata(
                    query_time=datetime.utcnow().isoformat(),
                    duration=int((time.time() - start_time) * 1000),
                    method=mean_type,
                ),
            )

    def _build_statistic_query(
        self, bucket: str, start: str, stop: str,
        measurement: str, field: str, mean_type: str,
        window_period: str, percentile: float,
    ) -> str:
        base = f'from(bucket: "{bucket}") |> range(start: {start}, stop: {stop})'
        filters = (
            f'|> filter(fn: (r) => r["_measurement"] == "{measurement}")'
            f'|> filter(fn: (r) => r["_field"] == "{field}")'
        )

        if mean_type in ("mean", "average"):
            return f'{base} {filters} |> aggregateWindow(every: {window_period}, fn: mean, createEmpty: false) |> yield(name: "mean")'
        elif mean_type == "median":
            return f'{base} {filters} |> aggregateWindow(every: {window_period}, fn: median, createEmpty: false) |> yield(name: "median")'
        elif mean_type == "mode":
            return f'{base} {filters} |> group(columns: ["_value"]) |> count() |> group(columns: ["_measurement"]) |> top(n: 1, columns: ["_value"]) |> yield(name: "mode")'
        elif mean_type == "first":
            return f'{base} {filters} |> first() |> yield(name: "first")'
        elif mean_type == "stddev":
            return f'{base} {filters} |> stddev() |> yield(name: "stddev")'
        elif mean_type == "variance":
            return f'{base} {filters} |> variance() |> yield(name: "variance")'
        elif mean_type == "percentile":
            return f'{base} {filters} |> percentile(percentile: {percentile:.6f}) |> yield(name: "percentile")'
        else:  # last (default)
            return f'{base} {filters} |> last() |> yield(name: "last")'

    def _calculate_summary(self, params: QueryParams) -> SummaryStats | None:
        bucket = params.bucket or self._bucket
        start = params.start or "-1h"
        stop = params.stop or "now()"

        flux_query = f'''
            from(bucket: "{bucket}")
                |> range(start: {start}, stop: {stop})
                |> filter(fn: (r) => r["_measurement"] == "{params.measurement}")
                |> filter(fn: (r) => r["_field"] == "{params.field}")
                |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
                |> yield(name: "summary")
        '''
        results = self._execute_query(flux_query, params.tz_string)
        if not results:
            return None

        values = [r["_value"] for r in results if "_value" in r and isinstance(r["_value"], (int, float))]
        if not values:
            return None

        import math
        values_sorted = sorted(values)
        n = len(values)
        total = sum(values)
        mean = total / n
        variance = sum((v - mean) ** 2 for v in values) / n

        return SummaryStats(
            min=values_sorted[0],
            max=values_sorted[-1],
            avg=mean,
            count=n,
            std_dev=math.sqrt(variance) if variance > 0 else 0.0,
            variance=variance,
            median=values_sorted[n // 2],
            p95=values_sorted[int(n * 0.95)] if n > 1 else values_sorted[0],
            p99=values_sorted[int(n * 0.99)] if n > 1 else values_sorted[0],
        )

    def _execute_query(self, flux_query: str, tz_string: str) -> list[dict[str, Any]]:
        logger.debug(f"Executing InfluxDB query: {flux_query[:200]}...")
        tables = self._query_api.query(flux_query, org=self._org)

        results = []
        for table in tables:
            for record in table.records:
                row = {
                    "_time": record.get_time(),
                    "_measurement": record.get_measurement(),
                    "_field": record.get_field(),
                    "_value": record.get_value(),
                }
                results.append(row)

        return results
```

---

### 1.3 MQTT Client
```
File: app/core/mqtt_client.py
Action: CREATE
Lines: ~350 (from pkg/mqtt/client.go 441 lines)
```

```python
"""
MQTT Client - แปลงจาก pkg/mqtt/client.go
ใช้ paho-mqtt
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

import paho.mqtt.client as mqtt
from loguru import logger


class MQTTClient:
    """MQTT client with request-response pattern support"""

    def __init__(
        self,
        broker: str,
        client_id: str = "",
        username: str = "",
        password: str = "",
        keepalive: int = 30,
        clean_session: bool = True,
    ):
        self._broker = broker
        self._client_id = client_id or f"python-client-{int(time.time())}"
        self._connected = False

        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self._client_id,
            clean_session=clean_session,
        )

        if username:
            self._client.username_pw_set(username, password)

        # TLS for self-signed certs (internal testing)
        self._client.tls_set(cert_reqs=mqtt.ssl.CERT_NONE)

        # Connection callbacks
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        # Request manager for request-response pattern
        self._pending: dict[str, list[_PendingRequest]] = {}
        self._lock = threading.Lock()
        self._subscription_count: dict[str, int] = {}

        logger.info(f"MQTT client created: broker={broker}, client_id={self._client_id}")

    def connect(self) -> None:
        host, port = self._parse_broker(self._broker)
        self._client.connect(host, port)
        self._client.loop_start()

        # Wait for connection
        timeout = 10
        start = time.time()
        while not self._connected and (time.time() - start) < timeout:
            time.sleep(0.1)

        if not self._connected:
            raise ConnectionError(f"MQTT connection timeout after {timeout}s")

        logger.info("MQTT connected")

    def disconnect(self) -> None:
        if self._client and self._connected:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False
            logger.info("MQTT disconnected")

    def publish(
        self,
        topic: str,
        payload: str | bytes,
        qos: int = 0,
        retain: bool = False,
    ) -> None:
        if not self._connected:
            raise ConnectionError("MQTT client not connected")

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        result = self._client.publish(topic, payload, qos=qos, retain=retain)
        result.wait_for_publish()

    def subscribe(
        self,
        topic: str,
        callback: Callable[[str, bytes], None] | None = None,
        qos: int = 0,
    ) -> None:
        if not self._connected:
            raise ConnectionError("MQTT client not connected")

        def _default_callback(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
            if callback:
                callback(msg.topic, msg.payload)

        self._client.subscribe(topic, qos=qos)
        if callback:
            self._client.message_callback_add(topic, _default_callback)

    def unsubscribe(self, topic: str) -> None:
        if self._connected:
            self._client.unsubscribe(topic)

    def is_connected(self) -> bool:
        return self._connected

    def request_data(
        self,
        request_topic: str,
        response_topic: str,
        payload: Any,
        timeout: float = 30.0,
    ) -> Any:
        """Request-response pattern - publish to request_topic, wait on response_topic"""
        if not self._connected:
            raise ConnectionError("MQTT client not connected")

        wait_topic = response_topic or request_topic

        # Publish request
        msg_payload = self._serialize_payload(payload)
        self._client.publish(request_topic, msg_payload, qos=1)

        # Wait for response
        return self._get_topic(wait_topic, int(timeout * 1000))

    def get_data_from_topic(
        self,
        topic: str,
        timeout: float = 30.0,
    ) -> bytes:
        """Subscribe to topic and wait for one message"""
        if not self._connected:
            raise ConnectionError("MQTT client not connected")

        result: list[bytes] = []
        event = threading.Event()

        def _on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
            if msg.topic == topic:
                result.append(msg.payload)
                event.set()

        self._client.subscribe(topic, qos=0)
        self._client.message_callback_add(topic, _on_message)

        try:
            if not event.wait(timeout):
                raise TimeoutError(f"No message from topic {topic} after {timeout}s")
            return result[0] if result else b""
        finally:
            self._client.unsubscribe(topic)
            self._client.message_callback_remove(topic)

    # --- Internal methods ---

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        self._connected = True
        logger.info("MQTT connected")

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        self._connected = False
        logger.warning(f"MQTT disconnected: reason={reason_code}")

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        msg: mqtt.MQTTMessage,
    ) -> None:
        topic = msg.topic
        with self._lock:
            if topic in self._pending and self._pending[topic]:
                req = self._pending[topic].pop(0)
                if not self._pending[topic]:
                    del self._pending[topic]
                    self._decrement_subscription(topic)
                req.resolve(msg.payload)

    def _get_topic(self, topic: str, timeout_ms: int) -> Any:
        with self._lock:
            if topic not in self._pending:
                self._increment_subscription(topic)
            elif not self._pending[topic]:
                self._increment_subscription(topic)

            result_event = threading.Event()
            result_value: list[Any] = []
            error_value: list[Exception] = []

            req = _PendingRequest(
                resolve=lambda data: (result_value.append(data), result_event.set()),
                reject=lambda err: (error_value.append(err), result_event.set()),
                topic=topic,
            )
            self._pending.setdefault(topic, []).append(req)

        # Timeout thread
        def _timeout_handler():
            time.sleep(timeout_ms / 1000.0)
            with self._lock:
                if topic in self._pending and req in self._pending[topic]:
                    self._pending[topic].remove(req)
                    if not self._pending[topic]:
                        del self._pending[topic]
                        self._decrement_subscription(topic)
                    req.reject(TimeoutError(f"Timeout: no message from topic {topic} after {timeout_ms}ms"))

        timer = threading.Thread(target=_timeout_handler, daemon=True)
        timer.start()

        result_event.wait(timeout=timeout_ms / 1000.0 + 1)

        if error_value:
            raise error_value[0]
        return result_value[0] if result_value else None

    def _increment_subscription(self, topic: str) -> None:
        count = self._subscription_count.get(topic, 0)
        if count == 0:
            self._client.subscribe(topic, qos=0)
            self._subscription_count[topic] = 1
        else:
            self._subscription_count[topic] = count + 1

    def _decrement_subscription(self, topic: str) -> None:
        count = self._subscription_count.get(topic, 0)
        if count <= 1:
            self._client.unsubscribe(topic)
            self._subscription_count.pop(topic, None)
        else:
            self._subscription_count[topic] = count - 1

    def _serialize_payload(self, payload: Any) -> bytes:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, str):
            return payload.encode()
        return json.dumps(payload).encode()

    @staticmethod
    def _parse_broker(broker: str) -> tuple[str, int]:
        """Parse 'tcp://host:port' or 'host:port' or 'host'"""
        broker = broker.replace("tcp://", "").replace("ssl://", "")
        parts = broker.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 1883
        return host, port


@dataclass
class _PendingRequest:
    resolve: Callable[[Any], None]
    reject: Callable[[Exception], None]
    topic: str = ""
```

---

### 1.4 Queue Manager
```
File: app/core/queue/manager.py
Action: CREATE
Lines: ~200 (from internal/modules/queue/manager.go 329 lines)
```

```python
"""
Redis Queue Manager - แปลงจาก internal/modules/queue/manager.go
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

import redis
from loguru import logger


@dataclass
class QueueMessage:
    id: str
    topic: str
    payload: dict[str, Any]
    created_at: float
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"  # pending, processing, completed, failed
    error: str = ""


class RedisQueue:
    """Redis-backed queue with delayed messages and dead letter queue"""

    def __init__(
        self,
        redis_client: redis.Redis,
        topic: str,
        max_retries: int = 3,
        worker_count: int = 1,
    ):
        self._redis = redis_client
        self._topic = topic
        self._max_retries = max_retries
        self._worker_count = worker_count
        self._handlers: dict[str, Callable] = {}
        self._running = False

        # Redis keys
        self._queue_key = f"queue:{topic}:pending"
        self._processing_key = f"queue:{topic}:processing"
        self._dlq_key = f"queue:{topic}:dead_letter"
        self._stats_key = f"queue:{topic}:stats"

    def register_handler(self, topic: str, handler: Callable) -> None:
        self._handlers[topic] = handler

    def publish(self, topic: str, payload: dict[str, Any]) -> str:
        msg = QueueMessage(
            id=str(uuid.uuid4()),
            topic=topic,
            payload=payload,
            created_at=time.time(),
            max_retries=self._max_retries,
        )
        self._redis.lpush(self._queue_key, json.dumps({
            "id": msg.id,
            "topic": msg.topic,
            "payload": msg.payload,
            "created_at": msg.created_at,
            "retry_count": msg.retry_count,
            "max_retries": msg.max_retries,
            "status": msg.status,
        }))
        self._redis.hincrby(self._stats_key, "published", 1)
        logger.debug(f"Message published to queue: topic={topic}, id={msg.id}")
        return msg.id

    def consume(self, timeout: int = 5) -> QueueMessage | None:
        result = self._redis.brpop(self._queue_key, timeout=timeout)
        if result is None:
            return None

        _, data = result
        msg_dict = json.loads(data)
        msg = QueueMessage(**msg_dict)
        msg.status = "processing"

        # Move to processing
        self._redis.lpush(self._processing_key, json.dumps({
            "id": msg.id,
            "topic": msg.topic,
            "payload": msg.payload,
            "created_at": msg.created_at,
            "retry_count": msg.retry_count,
            "max_retries": msg.max_retries,
            "status": msg.status,
        }))

        return msg

    def complete(self, msg_id: str) -> None:
        # Remove from processing
        items = self._redis.lrange(self._processing_key, 0, -1)
        for item in items:
            data = json.loads(item)
            if data["id"] == msg_id:
                self._redis.lrem(self._processing_key, 1, item)
                break
        self._redis.hincrby(self._stats_key, "completed", 1)

    def retry(self, msg: QueueMessage) -> None:
        msg.retry_count += 1
        if msg.retry_count >= msg.max_retries:
            self._move_to_dlq(msg)
            return

        # Re-queue with delay
        self._redis.lpush(self._queue_key, json.dumps({
            "id": msg.id,
            "topic": msg.topic,
            "payload": msg.payload,
            "created_at": msg.created_at,
            "retry_count": msg.retry_count,
            "max_retries": msg.max_retries,
            "status": "pending",
        }))
        self._redis.hincrby(self._stats_key, "retried", 1)

    def _move_to_dlq(self, msg: QueueMessage) -> None:
        msg.status = "failed"
        self._redis.lpush(self._dlq_key, json.dumps({
            "id": msg.id,
            "topic": msg.topic,
            "payload": msg.payload,
            "created_at": msg.created_at,
            "retry_count": msg.retry_count,
            "max_retries": msg.max_retries,
            "status": msg.status,
            "error": msg.error,
        }))
        self._redis.hincrby(self._stats_key, "dead_letter", 1)
        logger.warning(f"Message moved to DLQ: topic={msg.topic}, id={msg.id}")

    def get_stats(self) -> dict[str, int]:
        stats = self._redis.hgetall(self._stats_key)
        return {k.decode(): int(v.decode()) for k, v in stats.items()}

    def get_dlq_messages(self, limit: int = 10) -> list[dict]:
        items = self._redis.lrange(self._dlq_key, 0, limit - 1)
        return [json.loads(item) for item in items]

    def clear_dlq(self) -> int:
        return self._redis.delete(self._dlq_key)

    def process_messages(self) -> None:
        """Process messages in a loop"""
        self._running = True
        while self._running:
            msg = self.consume(timeout=1)
            if msg is None:
                continue

            handler = self._handlers.get(msg.topic)
            if handler is None:
                handler = self._handlers.get("*")  # wildcard handler

            if handler:
                try:
                    handler(msg)
                    self.complete(msg.id)
                except Exception as e:
                    msg.error = str(e)
                    self.retry(msg)
                    logger.error(f"Message processing failed: {e}")
            else:
                logger.warning(f"No handler for topic: {msg.topic}")
                self.complete(msg.id)

    def stop(self) -> None:
        self._running = False


class NoopQueue:
    """No-op fallback queue"""

    def publish(self, topic: str, payload: dict[str, Any]) -> str:
        logger.debug(f"NoopQueue: publish to {topic}")
        return str(uuid.uuid4())

    def consume(self, timeout: int = 5) -> None:
        return None

    def get_stats(self) -> dict[str, int]:
        return {}
```

---

## 2. Phase 2: IoT Domain Layer

### 2.1 Base Entity
```
File: app/modules/shared/domain/base.py
Action: CREATE (if not exists)
```

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BaseEntity:
    id: int = field(default=0, metadata={"primary_key": True})
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
```

---

### 2.2 IoT Entities

```
Files: app/modules/iot/domain/entities/
Action: CREATE all 8 files
```

**2.2.1 Device**
```python
# app/modules/iot/domain/entities/device.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from app.modules.shared.domain.base import BaseEntity


@dataclass
class Device(BaseEntity):
    """Device entity - แปลงจาก models/device.go"""
    hardware_id: int = 0
    type_id: int = 0
    location_id: int = 0
    device_sn: str = ""
    device_name: str = ""
    device_type: str = ""
    location_name: str = ""

    # MQTT config
    mqtt_id: int = 0
    mqtt_main_id: int = 0
    mqtt_host: str = ""
    mqtt_port: int = 1883
    mqtt_topic: str = ""
    mqtt_name: str = ""
    mqtt_username: str = ""
    mqtt_password: str = ""

    # Device info
    unit: str = ""
    status: str = "offline"
    icon: str = ""
    icon_color: str = ""
    description: str = ""
    firmware_version: str = ""

    # Related entities (not persisted directly)
    device_config: DeviceConfig | None = None
    device_status: DeviceStatus | None = None

    @property
    def mqtt_broker(self) -> str:
        return f"tcp://{self.mqtt_host}:{self.mqtt_port}" if self.mqtt_host else ""


@dataclass
class DeviceConfig(BaseEntity):
    """Device config - แปลงจาก models/device_config.go"""
    device_id: int = 0
    max_value: float = 0.0
    min_value: float = 0.0
    warning_threshold: float = 0.0
    alert_threshold: float = 0.0
    recovery_warning: float = 0.0
    recovery_alert: float = 0.0
    calibration_offset: float = 0.0
    calibration_multiplier: float = 1.0
    mqtt_control_on: str = ""
    mqtt_control_off: str = ""
    action_name: str = ""
    config_json: str = ""


@dataclass
class DeviceStatus(BaseEntity):
    """Device status - แปลงจาก models/device_status.go"""
    device_id: int = 0
    is_online: bool = False
    last_seen: datetime | None = None
    last_value: float = 0.0
    last_alarm: int = 0
    count_alarm: int = 0
    event: int = 0
    status: str = "offline"
    sensor_data: str = ""
    sensor_min: float = 0.0
    sensor_max: float = 0.0
    sensor_avg: float = 0.0
    battery: float = 0.0
    rssi: int = 0


@dataclass
class DeviceAlert(BaseEntity):
    """Device alert - แปลงจาก models/device_alert.go"""
    device_id: int = 0
    alert_type: str = ""
    severity: str = "low"  # low, medium, high, critical
    title: str = ""
    message: str = ""
    value_data: float = 0.0
    value_alarm: float = 0.0
    resolved: bool = False
    acknowledged: bool = False
    resolved_at: datetime | None = None


@dataclass
class IoTData(BaseEntity):
    """IoT data - แปลงจาก models/iot_data.go"""
    device_id: int = 0
    data_json: str = ""
    timestamp: datetime | None = None
    location_id: int = 0
    metadata_json: str = ""


@dataclass
class AlarmLog(BaseEntity):
    """Alarm log - แปลงจาก models/alarm_log.go"""
    device_id: int = 0
    alarm_action_id: int = 0
    alarm_type: int = 0
    alarm_status: int = 0
    value_data: float = 0.0
    value_alarm: float = 0.0
    title: str = ""
    subject: str = ""
    content: str = ""
    data_alarm: int = 0
    data_alarm_raw: int = 0
    event_control: int = 0
    message_mqtt_control: str = ""


@dataclass
class ActivityLog(BaseEntity):
    """Activity log - แปลงจาก models/activity_log.go"""
    log_type: str = ""
    device_id: int = 0
    user_id: int = 0
    severity: str = "info"
    data_json: str = ""
    description: str = ""


@dataclass
class Schedule(BaseEntity):
    """Schedule - แปลงจาก models/schedule.go"""
    schedule_id: int = 0
    device_id: int = 0
    start_time: str = ""
    end_time: str = ""
    event: str = ""
    monday: bool = False
    tuesday: bool = False
    wednesday: bool = False
    thursday: bool = False
    friday: bool = False
    saturday: bool = False
    sunday: bool = False
```

---

### 2.3 Value Objects

```
Files: app/modules/iot/domain/value_objects/
Action: CREATE all 3 files
```

**2.3.1 Alarm**
```python
# app/modules/iot/domain/value_objects/alarm.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AlarmDetailDTO:
    """Alarm detail input - แปลงจาก pkg/helpers/iot.go"""
    hardware_id: Any
    value_data: Any
    value_alarm: Any
    value_relay: Any = None
    value_control_relay: Any = None
    max_value: Any = None
    min_value: Any = None
    status_alert: Any = None
    status_warning: Any = None
    recovery_warning: Any = None
    recovery_alert: Any = None
    device_name: str = ""
    action_name: str = ""
    mqtt_name: str = ""
    mqtt_control_on: str = ""
    mqtt_control_off: str = ""
    count_alarm: Any = 0
    event: Any = 0
    unit: str = ""
    sensor_value_data: Any = None


@dataclass(frozen=True)
class AlarmDetailResult:
    """Alarm detail output"""
    status: int
    status_control: int
    alarm_type_id: int
    type_id: int
    hardware_id: int
    alarm_status_set: int
    title: str
    subject: str
    content: str
    value_data: Any
    value_alarm: Any
    value_relay: Any
    value_control_relay: Any
    data_alarm: int
    data_alarm_raw: int
    max_value: Any
    min_value: Any
    event_control: int
    message_mqtt_control: str
    sensor_data: Any
    count_alarm: int
    mqtt_name: str
    mqtt_name_str: str
    device_name_str: str
    mqtt_control_on_str: str
    unit: str
    sensor_value: Any
    status_alert_val: int = 0
    status_warning_val: int = 0
    recovery_warning_val: int = 0
    recovery_alert_val: int = 0
    device_name_val: str = ""
    alarm_action_name: str = ""
    mqtt_control_on_val: str = ""
    mqtt_control_off_val: str = ""
    event_val: int = 0
    timestamp: str = ""
    lang: str = ""


@dataclass(frozen=True)
class MQTTConfig:
    """MQTT configuration value object"""
    broker: str
    client_id: str = ""
    username: str = ""
    password: str = ""
    keepalive: int = 30
    clean_session: bool = True


@dataclass(frozen=True)
class InfluxDBConfig:
    """InfluxDB configuration value object"""
    url: str
    token: str
    org: str
    bucket: str
    timeout: int = 30


@dataclass(frozen=True)
class Location:
    """Location value object"""
    location_id: int = 0
    location_name: str = ""
    config_data: str = ""
```

---

### 2.4 Alarm Logic Helper
```
File: app/modules/iot/domain/helpers/alarm_logic.py
Action: CREATE
Lines: ~350 (from pkg/helpers/iot.go 405 lines)
```

```python
"""
Alarm Logic - แปลงจาก pkg/helpers/iot.go
evaluation logic สำหรับ alarm threshold checking
"""

from __future__ import annotations

from typing import Any

from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO, AlarmDetailResult


# Thai messages
_THAI_MESSAGES = {
    "warning": "คำเตือน มีความผิดปกติ",
    "critical": "ภาวะวิกฤตต้องแก้ไขทันที",
    "recovery_warning": "คืนสู่ภาวะปกติ (คำเตือน)",
    "recovery_critical": "คืนสู่ภาวะปกติ (วิกฤต)",
    "normal": "ปกติ",
    "critical_max": "วิกฤต มีค่าสูงเกินกำหนด",
    "critical_min": "วิกฤต มีค่าต่ำกว่ากำหนด",
}

# English messages
_ENGLISH_MESSAGES = {
    "warning": "Warning",
    "critical": "Critical",
    "recovery_warning": "Recovery Warning",
    "recovery_critical": "Recovery Critical",
    "normal": "Normal",
    "critical_max": "Critical! Maximum limit.",
    "critical_min": "Critical! Minimum limit",
}


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return 0


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _normalize_sensor_value(value: Any) -> Any:
    if isinstance(value, str):
        if value.upper() in ("ON", "OFF"):
            return value.upper()
        try:
            return float(value)
        except ValueError:
            return value
    return value


def evaluate_alarm(dto: AlarmDetailDTO, lang: str = "th") -> AlarmDetailResult:
    """Main alarm evaluation - แปลงจาก processAlarmDetail()"""
    messages = _THAI_MESSAGES if lang == "th" else _ENGLISH_MESSAGES

    hardware_id = _to_int(dto.hardware_id)
    type_id = hardware_id

    sensor_value = _normalize_sensor_value(dto.value_data)
    max_val = _to_float(dto.max_value)
    min_val = _to_float(dto.min_value)
    status_alert = _to_int(dto.status_alert)
    status_warning = _to_int(dto.status_warning)
    recovery_warning = _to_int(dto.recovery_warning)
    recovery_alert = _to_int(dto.recovery_alert)
    count_alarm = _to_int(dto.count_alarm)
    event = _to_int(dto.event)

    unit = dto.unit
    mqtt_name = dto.mqtt_name
    device_name = dto.device_name
    alarm_action_name = dto.action_name
    mqtt_control_on = dto.mqtt_control_on
    mqtt_control_off = dto.mqtt_control_off
    value_alarm = dto.value_alarm
    value_relay = dto.value_relay
    value_control_relay = dto.value_control_relay

    sensor_data: Any = None
    value_data: Any = None

    # Determine sensor data based on hardware type
    if hardware_id == 1:
        sensor_data = dto.value_data
        value_data = dto.value_data
    elif hardware_id == 2:
        if _to_int(dto.value_alarm) == 1:
            sensor_data = 1
            value_data = 1
            sensor_value = 1
        else:
            sensor_data = _to_int(dto.value_alarm)
            value_data = _to_int(dto.value_alarm)
            sensor_value = _to_int(dto.value_alarm)
    elif hardware_id == 3:
        sensor_data = _to_int(dto.value_alarm)
        value_data = dto.value_data
        sensor_value = dto.value_data
    elif hardware_id == 4:
        sensor_data = dto.value_data
        value_data = dto.value_data
    else:
        sensor_data = _to_int(dto.value_alarm)
        value_data = dto.value_data

    alarm_status_set = 999
    data_alarm = 0
    data_alarm_raw = 0
    event_control = event
    message_mqtt_control = mqtt_control_off
    if event == 1:
        message_mqtt_control = mqtt_control_on

    status = 5
    title = messages["normal"]
    subject = messages["normal"]
    content = messages["normal"] + " "

    # --- Evaluation rules (matching Go logic exactly) ---

    if hardware_id == 3 and sensor_value in (1, 0, "ON", "OFF", "on", "off"):
        alarm_status_set = 999
        title = messages["normal"]
        subject = messages["normal"]
        content = f"{messages['normal']} {sensor_value} {unit}"
        status = 5

    elif hardware_id == 4 and sensor_value != 1:
        alarm_status_set = 2
        title = messages["critical"]
        subject = f"{mqtt_name} {messages['critical']} {device_name} : {sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {messages['critical']} {device_name} :{sensor_value} {unit}"
        data_alarm = status_warning
        data_alarm_raw = status_warning
        status = 2

    elif hardware_id == 4 and sensor_value == 1:
        alarm_status_set = 999
        title = messages["normal"]
        subject = messages["normal"]
        content = f"{messages['normal']} {sensor_value} {unit}"
        status = 5

    elif max_val != 0 and _to_float(sensor_value) >= max_val and hardware_id in (1, 2):
        alarm_status_set = 2
        title = messages["critical_max"]
        subject = f"{mqtt_name} {messages['critical_max']} {device_name} : {sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {messages['critical_max']} {device_name} :{sensor_value} {unit}"
        data_alarm = status_warning
        data_alarm_raw = status_warning
        status = 2

    elif min_val != 0 and _to_float(sensor_value) <= min_val and hardware_id in (1, 2):
        alarm_status_set = 1
        title = messages["critical_min"]
        subject = f"{mqtt_name} {messages['critical_min']} {device_name} : {sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {messages['critical_min']} {device_name} :{sensor_value} {unit}"
        data_alarm = status_warning
        data_alarm_raw = status_warning
        status = 1

    elif (hardware_id == 1 and status_warning > 0
          and _to_float(sensor_value) >= float(status_warning)
          and _to_float(sensor_value) < float(status_alert)):
        alarm_status_set = 1
        title = messages["warning"]
        subject = f"{mqtt_name} {messages['warning']} : {device_name} : {sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {messages['warning']}: {device_name} :{sensor_value} {unit}"
        data_alarm = status_warning
        data_alarm_raw = status_warning
        status = 1

    elif hardware_id == 1 and status_alert > 0 and _to_float(sensor_value) >= float(status_alert):
        alarm_status_set = 2
        title = messages["critical"]
        subject = f"{mqtt_name} {messages['critical']} : {device_name} :{sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {messages['critical']}: {device_name} :{sensor_value} {unit}"
        data_alarm = status_alert
        data_alarm_raw = status_alert
        status = 2

    elif _to_int(value_alarm) == 0 and hardware_id in (2, 3, 4):
        is_critical = (hardware_id == 4)
        if is_critical:
            alarm_status_set = 2
            title = messages["critical"]
        else:
            alarm_status_set = 1
            title = messages["warning"]
        subject = f"{mqtt_name} {title} : {device_name} : {sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {title}: {device_name} :{sensor_value} {unit}"
        if is_critical:
            data_alarm = status_alert
            data_alarm_raw = status_alert
        else:
            data_alarm = status_warning
            data_alarm_raw = status_warning
        status = 2 if is_critical else 1

    elif (count_alarm >= 1 and recovery_warning > 0
          and _to_float(sensor_value) <= float(recovery_warning)
          and hardware_id in (1, 2)):
        alarm_status_set = 3
        title = messages["recovery_warning"]
        subject = f"{mqtt_name} {messages['recovery_warning']} : {device_name} :{sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {messages['recovery_warning']}: {device_name} :{sensor_value} {unit}"
        data_alarm = recovery_warning
        data_alarm_raw = recovery_warning
        event_control = 0
        if event == 1:
            event_control = 1
            message_mqtt_control = mqtt_control_off
        else:
            message_mqtt_control = mqtt_control_on
        status = 3

    elif (count_alarm >= 1 and recovery_alert > 0
          and _to_float(sensor_value) <= float(recovery_alert)
          and hardware_id in (1, 2)):
        alarm_status_set = 4
        title = f"{mqtt_name} {messages['recovery_critical']}"
        subject = f"{mqtt_name} {messages['recovery_critical']} :{device_name} :{sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {messages['recovery_critical']} :{device_name} :{sensor_value} {unit}"
        data_alarm = recovery_alert
        data_alarm_raw = recovery_alert
        event_control = 0
        if event == 1:
            event_control = 1
            message_mqtt_control = mqtt_control_off
        else:
            message_mqtt_control = mqtt_control_on
        status = 4

    elif count_alarm >= 1 and _to_int(value_alarm) >= 1 and hardware_id in (2, 3, 4):
        alarm_status_set = 4
        title = f"{mqtt_name} {messages['recovery_critical']}"
        subject = f"{mqtt_name} {messages['recovery_critical']} :{device_name} :{sensor_value} {unit}"
        content = f"{mqtt_name} {alarm_action_name} {messages['recovery_critical']} :{device_name} :{sensor_value} {unit}"
        data_alarm = recovery_alert
        data_alarm_raw = recovery_alert
        event_control = 0
        if event == 1:
            event_control = 1
            message_mqtt_control = mqtt_control_off
        else:
            message_mqtt_control = mqtt_control_on
        status = 4

    else:
        alarm_status_set = 999
        title = messages["normal"]
        subject = messages["normal"]
        content = messages["normal"] + " "
        data_alarm = 0
        data_alarm_raw = 0
        status = 5

    return AlarmDetailResult(
        status=status,
        status_control=status,
        alarm_type_id=hardware_id,
        type_id=type_id,
        hardware_id=hardware_id,
        alarm_status_set=alarm_status_set,
        title=title,
        subject=subject,
        content=content,
        value_data=value_data,
        value_alarm=value_alarm,
        value_relay=value_relay,
        value_control_relay=value_control_relay,
        data_alarm=data_alarm,
        data_alarm_raw=data_alarm_raw,
        max_value=max_val,
        min_value=min_val,
        event_control=event_control,
        message_mqtt_control=message_mqtt_control,
        sensor_data=sensor_data,
        count_alarm=count_alarm,
        mqtt_name=mqtt_name,
        mqtt_name_str=mqtt_name,
        device_name_str=device_name,
        mqtt_control_on_str=mqtt_control_on,
        unit=unit,
        sensor_value=sensor_value,
        status_alert_val=status_alert,
        status_warning_val=status_warning,
        recovery_warning_val=recovery_warning,
        recovery_alert_val=recovery_alert,
        device_name_val=device_name,
        alarm_action_name=alarm_action_name,
        mqtt_control_on_val=mqtt_control_on,
        mqtt_control_off_val=mqtt_control_off,
        event_val=event,
        timestamp="",
        lang=lang,
    )
```

---

## 3. Phase 3: IoT Infrastructure Layer (Repositories)

```
Files: app/modules/iot/infrastructure/
Action: CREATE all 8 repository files
```

### 3.1 Device Repository
```python
# app/modules/iot/infrastructure/device_repository.py
from __future__ import annotations

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.device import Device


class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, device_id: int) -> Device | None:
        result = await self._session.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()

    async def find_by_hardware_id(self, hardware_id: int) -> Device | None:
        result = await self._session.execute(
            select(Device).where(Device.hardware_id == hardware_id)
        )
        return result.scalar_one_or_none()

    async def find_by_mqtt_topic(self, topic: str) -> Device | None:
        result = await self._session.execute(
            select(Device).where(Device.mqtt_topic == topic)
        )
        return result.scalar_one_or_none()

    async def find_by_location(self, location_id: int) -> list[Device]:
        result = await self._session.execute(
            select(Device).where(
                and_(Device.location_id == location_id, Device.is_active.is_(True))
            )
        )
        return list(result.scalars().all())

    async def find_all_active(self) -> list[Device]:
        result = await self._session.execute(
            select(Device).where(Device.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Device], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Device).where(Device.is_active.is_(True))
        )
        total = count_result.scalar() or 0

        query = (
            select(Device)
            .where(Device.is_active.is_(True))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        devices = list(result.scalars().all())
        return devices, total

    async def create(self, device: Device) -> Device:
        self._session.add(device)
        await self._session.flush()
        return device

    async def update(self, device: Device) -> Device:
        await self._session.flush()
        return device

    async def delete(self, device_id: int) -> bool:
        device = await self.find_by_id(device_id)
        if device:
            device.is_active = False
            await self._session.flush()
            return True
        return False
```

### 3.2 Other Repositories (same pattern)

```python
# DeviceConfigRepository
class DeviceConfigRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_device_id(self, device_id: int) -> DeviceConfig | None:
        result = await self._session.execute(
            select(DeviceConfig).where(DeviceConfig.device_id == device_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, config: DeviceConfig) -> DeviceConfig:
        existing = await self.find_by_device_id(config.device_id)
        if existing:
            for k, v in vars(config).items():
                if k != "id" and v is not None:
                    setattr(existing, k, v)
            await self._session.flush()
            return existing
        self._session.add(config)
        await self._session.flush()
        return config


# DeviceStatusRepository
class DeviceStatusRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_device_id(self, device_id: int) -> DeviceStatus | None:
        result = await self._session.execute(
            select(DeviceStatus).where(DeviceStatus.device_id == device_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, status: DeviceStatus) -> DeviceStatus:
        existing = await self.find_by_device_id(status.device_id)
        if existing:
            for k, v in vars(status).items():
                if k != "id" and v is not None:
                    setattr(existing, k, v)
            await self._session.flush()
            return existing
        self._session.add(status)
        await self._session.flush()
        return status


# DeviceAlertRepository
class DeviceAlertRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, alert: DeviceAlert) -> DeviceAlert:
        self._session.add(alert)
        await self._session.flush()
        return alert


# IoTDataRepository
class IoTDataRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: IoTData) -> IoTData:
        self._session.add(data)
        await self._session.flush()
        return data

    async def find_latest(self, device_id: int, limit: int = 10) -> list[IoTData]:
        result = await self._session.execute(
            select(IoTData)
            .where(IoTData.device_id == device_id)
            .order_by(IoTData.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def find_by_date_range(
        self, device_id: int, start: str, end: str
    ) -> list[IoTData]:
        result = await self._session.execute(
            select(IoTData)
            .where(
                and_(
                    IoTData.device_id == device_id,
                    IoTData.created_at >= start,
                    IoTData.created_at <= end,
                )
            )
            .order_by(IoTData.created_at.desc())
        )
        return list(result.scalars().all())

    async def find_paginated(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[IoTData], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(IoTData)
        )
        total = count_result.scalar() or 0
        query = (
            select(IoTData)
            .order_by(IoTData.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def cleanup_old(self, days: int) -> int:
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self._session.execute(
            select(IoTData).where(IoTData.created_at < cutoff)
        )
        old_data = list(result.scalars().all())
        for item in old_data:
            await self._session.delete(item)
        return len(old_data)


# AlarmLogRepository
class AlarmLogRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, log: AlarmLog) -> AlarmLog:
        self._session.add(log)
        await self._session.flush()
        return log

    async def count_by_device(self, device_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(AlarmLog).where(
                AlarmLog.device_id == device_id
            )
        )
        return result.scalar() or 0


# ActivityLogRepository
class ActivityLogRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, log: ActivityLog) -> ActivityLog:
        self._session.add(log)
        await self._session.flush()
        return log


# ScheduleRepository
class ScheduleRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_active_schedules(self) -> list[Schedule]:
        result = await self._session.execute(
            select(Schedule).where(Schedule.is_active.is_(True))
        )
        return list(result.scalars().all())
```

---

## 4. Phase 4: IoT Application Layer (Use Case)

```
File: app/modules/iot/application/use_case.py
Action: CREATE
Lines: ~800 (from internal/modules/iot/usecase/usecase.go 1924 lines)
```

```python
"""
IoT Use Case - แปลงจาก internal/modules/iot/usecase/usecase.go
Main business logic for IoT module
"""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from redis import Redis

from app.core.influxdb_client import InfluxDBClientWrapper, QueryParams
from app.core.mqtt_client import MQTTClient
from app.modules.iot.domain.entities.device import Device, DeviceConfig, DeviceStatus
from app.modules.iot.domain.entities.iot_data import IoTData
from app.modules.iot.domain.entities.alarm_log import AlarmLog
from app.modules.iot.domain.entities.activity_log import ActivityLog
from app.modules.iot.domain.value_objects.alarm import AlarmDetailDTO, AlarmDetailResult
from app.modules.iot.domain.helpers.alarm_logic import evaluate_alarm
from app.modules.iot.infrastructure.device_repository import DeviceRepository
from app.modules.iot.infrastructure.device_config_repository import DeviceConfigRepository
from app.modules.iot.infrastructure.device_status_repository import DeviceStatusRepository
from app.modules.iot.infrastructure.device_alert_repository import DeviceAlertRepository
from app.modules.iot.infrastructure.iot_data_repository import IoTDataRepository
from app.modules.iot.infrastructure.alarm_log_repository import AlarmLogRepository
from app.modules.iot.infrastructure.activity_log_repository import ActivityLogRepository


class IoTUseCase:
    """IoT use case - แปลงจาก MQTT3UseCase interface"""

    def __init__(
        self,
        device_repository: DeviceRepository,
        device_config_repository: DeviceConfigRepository,
        device_status_repository: DeviceStatusRepository,
        device_alert_repository: DeviceAlertRepository,
        iot_data_repository: IoTDataRepository,
        alarm_log_repository: AlarmLogRepository,
        activity_log_repository: ActivityLogRepository,
        mqtt_client: MQTTClient | None,
        influxdb_client: InfluxDBClientWrapper,
        redis_client: Redis,
    ):
        self._device_repo = device_repository
        self._device_config_repo = device_config_repository
        self._device_status_repo = device_status_repository
        self._device_alert_repo = device_alert_repository
        self._iot_data_repo = iot_data_repository
        self._alarm_log_repo = alarm_log_repository
        self._activity_log_repo = activity_log_repository
        self._mqtt_client = mqtt_client
        self._influxdb = influxdb_client
        self._redis = redis_client

    def is_connected(self) -> bool:
        return self._mqtt_client is not None and self._mqtt_client.is_connected()

    def is_cache_enabled(self) -> bool:
        try:
            self._redis.ping()
            return True
        except Exception:
            return False

    # --- MQTT Data ---

    async def get_topic_data(self, topic: str) -> dict[str, Any]:
        """Get data from MQTT topic with Redis caching"""
        cache_key = f"mqtt:topic:{topic}"

        # Check cache first
        if self.is_cache_enabled():
            cached = self._redis.get(cache_key)
            if cached:
                return json.loads(cached)

        # MQTT request
        if not self.is_connected():
            raise ConnectionError("MQTT client not connected")

        result = self._mqtt_client.request_data(topic, topic, "", timeout=5.0)

        # Cache result (5 seconds)
        if self.is_cache_enabled() and result is not None:
            self._redis.setex(cache_key, 5, json.dumps(result, default=str))

        return result if isinstance(result, dict) else {"data": result}

    # --- Device Control ---

    async def device_control(self, device_id: int, command: str) -> dict[str, Any]:
        """Send control command to a single device"""
        device = await self._device_repo.find_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        topic = device.mqtt_topic
        payload = {"command": command, "device_id": device_id}

        if self.is_connected():
            self._mqtt_client.publish(topic, json.dumps(payload), qos=1)

        await self._log_activity(device_id, "control", f"Command: {command}")

        return {"status": "sent", "device_id": device_id, "command": command}

    async def device_controls(
        self, device_ids: list[int], command: str
    ) -> dict[str, Any]:
        """Send control command to multiple devices"""
        results = []
        for device_id in device_ids:
            try:
                result = await self.device_control(device_id, command)
                results.append(result)
            except Exception as e:
                results.append({"device_id": device_id, "error": str(e)})

        return {"results": results, "total": len(device_ids)}

    # --- Device List ---

    async def get_device_list(self) -> list[dict[str, Any]]:
        devices = await self._device_repo.find_all_active()
        return [self._device_to_dict(d) for d in devices]

    async def get_device_list_page(
        self, page: int, page_size: int
    ) -> dict[str, Any]:
        devices, total = await self._device_repo.find_all_paginated(page, page_size)
        return {
            "devices": [self._device_to_dict(d) for d in devices],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_device_buckets(self) -> list[str]:
        """Get InfluxDB buckets"""
        return [self._influxdb.bucket]

    async def get_device_list_by_location(
        self, location_id: int
    ) -> list[dict[str, Any]]:
        devices = await self._device_repo.find_by_location(location_id)
        return [self._device_to_dict(d) for d in devices]

    # --- Sensor Charts ---

    async def get_senser_charts(
        self, device_id: int, start_time: str, end_time: str, limit: int
    ) -> list[dict[str, Any]]:
        params = QueryParams(
            start=start_time, stop=end_time, limit=limit,
            measurement="sensor_data", field="value",
        )
        return self._influxdb.query_filter_data(params)

    async def get_senser_data(
        self, device_id: int, field: str, limit: int
    ) -> list[dict[str, Any]]:
        params = QueryParams(
            limit=limit, measurement="sensor_data", field=field,
        )
        return self._influxdb.query_filter_data(params)

    async def get_senser_data_chart(
        self, device_id: int, field: str,
        start_time: str, end_time: str, limit: int,
    ) -> list[dict[str, Any]]:
        params = QueryParams(
            start=start_time, stop=end_time, limit=limit,
            measurement="sensor_data", field=field,
        )
        return self._influxdb.query_device_chart(params)

    async def get_device_senser_charts(
        self, device_id: int, limit: int
    ) -> list[dict[str, Any]]:
        params = QueryParams(limit=limit, measurement="sensor_data", field="value")
        return self._influxdb.query_filter_data(params)

    # --- Alarm Status ---

    async def get_alarm_device_status(self) -> list[dict[str, Any]]:
        """Get alarm status for all devices"""
        devices = await self._device_repo.find_all_active()
        results = []

        for device in devices:
            try:
                config = await self._device_config_repo.find_by_device_id(device.id)
                status = await self._device_status_repo.find_by_device_id(device.id)

                mqtt_data = await self._get_cached_mqtt_data(device.mqtt_topic)

                alarm_result = evaluate_alarm(
                    AlarmDetailDTO(
                        hardware_id=device.hardware_id,
                        value_data=mqtt_data.get("value", 0) if mqtt_data else 0,
                        value_alarm=mqtt_data.get("alarm", 0) if mqtt_data else 0,
                        max_value=config.max_value if config else 0,
                        min_value=config.min_value if config else 0,
                        status_alert=config.alert_threshold if config else 0,
                        status_warning=config.warning_threshold if config else 0,
                        recovery_warning=config.recovery_warning if config else 0,
                        recovery_alert=config.recovery_alert if config else 0,
                        device_name=device.device_name,
                        action_name=config.action_name if config else "",
                        mqtt_name=device.mqtt_name,
                        mqtt_control_on=config.mqtt_control_on if config else "",
                        mqtt_control_off=config.mqtt_control_off if config else "",
                        count_alarm=status.count_alarm if status else 0,
                        event=status.event if status else 0,
                        unit=device.unit,
                    )
                )

                results.append({
                    "device_id": device.id,
                    "device_name": device.device_name,
                    "alarm_status": alarm_result.alarm_status_set,
                    "title": alarm_result.title,
                    "subject": alarm_result.subject,
                    "content": alarm_result.content,
                    "status": alarm_result.status,
                    "value_data": alarm_result.value_data,
                })
            except Exception as e:
                logger.error(f"Error evaluating alarm for device {device.id}: {e}")

        return results

    async def get_alarm_device_status_control(self) -> list[dict[str, Any]]:
        return await self.get_alarm_device_status()

    # --- Monitor ---

    async def get_monitor_device_group(
        self, location_id: int
    ) -> dict[str, Any]:
        """Get monitor data grouped by device"""
        devices = await self._device_repo.find_by_location(location_id)
        groups = {}

        for device in devices:
            try:
                config = await self._device_config_repo.find_by_device_id(device.id)
                mqtt_data = await self._get_cached_mqtt_data(device.mqtt_topic)

                # Apply calibration
                raw_value = mqtt_data.get("value", 0) if mqtt_data else 0
                if config and config.calibration_multiplier != 0:
                    calibrated = (raw_value * config.calibration_multiplier) + config.calibration_offset
                else:
                    calibrated = raw_value

                location_name = device.location_name or "Unknown"
                if location_name not in groups:
                    groups[location_name] = []

                groups[location_name].append({
                    "device_id": device.id,
                    "device_name": device.device_name,
                    "hardware_id": device.hardware_id,
                    "value": calibrated,
                    "unit": device.unit,
                    "status": device.status,
                    "mqtt_topic": device.mqtt_topic,
                })
            except Exception as e:
                logger.error(f"Error monitoring device {device.id}: {e}")

        return {"groups": groups, "location_id": location_id}

    async def get_monitor_device_chart(
        self, location_id: int, field: str,
        start_time: str, end_time: str,
    ) -> list[dict[str, Any]]:
        params = QueryParams(
            start=start_time, stop=end_time,
            measurement="sensor_data", field=field,
        )
        return self._influxdb.query_filter_data(params)

    async def get_topic_data_device_chart(
        self, topic: str, field: str,
        start_time: str, end_time: str,
    ) -> list[dict[str, Any]]:
        params = QueryParams(
            start=start_time, stop=end_time,
            measurement="sensor_data", field=field,
        )
        return self._influxdb.query_filter_data(params)

    # --- Device Status ---

    async def get_device_status(self, device_id: int) -> dict[str, Any]:
        status = await self._device_status_repo.find_by_device_id(device_id)
        if not status:
            raise ValueError(f"Device status not found for device {device_id}")
        return self._status_to_dict(status)

    async def update_device_status(
        self, device_id: int, status_str: str
    ) -> dict[str, Any]:
        status = await self._device_status_repo.find_by_device_id(device_id)
        if not status:
            status = DeviceStatus(device_id=device_id)

        status.status = status_str
        updated = await self._device_status_repo.upsert(status)
        return self._status_to_dict(updated)

    # --- Device Config ---

    async def get_device_config(self, device_id: int) -> dict[str, Any]:
        config = await self._device_config_repo.find_by_device_id(device_id)
        if not config:
            raise ValueError(f"Device config not found for device {device_id}")
        return self._config_to_dict(config)

    async def update_device_config(
        self, device_id: int, config_data: dict[str, Any]
    ) -> dict[str, Any]:
        config = await self._device_config_repo.find_by_device_id(device_id)
        if not config:
            config = DeviceConfig(device_id=device_id)

        for key, value in config_data.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)

        updated = await self._device_config_repo.upsert(config)
        return self._config_to_dict(updated)

    # --- Process MQTT Data ---

    async def process_mqtt_data(
        self, topic: str, payload: bytes
    ) -> dict[str, Any]:
        """Process incoming MQTT data"""
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {"raw": payload.decode(errors="replace")}

        # Find device by topic
        device = await self._device_repo.find_by_mqtt_topic(topic)
        if not device:
            logger.warning(f"No device found for topic: {topic}")
            return {"status": "ignored", "topic": topic}

        # Save IoT data
        iot_data = IoTData(
            device_id=device.id,
            data_json=json.dumps(data),
        )
        await self._iot_data_repo.create(iot_data)

        # Update device status
        status = await self._device_status_repo.find_by_device_id(device.id)
        if not status:
            status = DeviceStatus(device_id=device.id)

        status.is_online = True
        status.last_seen = None  # will be set by DB default
        if "value" in data:
            status.last_value = float(data["value"])
        await self._device_status_repo.upsert(status)

        return {"status": "processed", "device_id": device.id, "topic": topic}

    # --- Data Queries ---

    async def get_latest_data(
        self, device_id: int, limit: int
    ) -> list[dict[str, Any]]:
        data_list = await self._iot_data_repo.find_latest(device_id, limit)
        return [self._iot_data_to_dict(d) for d in data_list]

    async def get_data_by_date_range(
        self, device_id: int, start: str, end: str
    ) -> list[dict[str, Any]]:
        data_list = await self._iot_data_repo.find_by_date_range(device_id, start, end)
        return [self._iot_data_to_dict(d) for d in data_list]

    async def list_iot_data(
        self, page: int, page_size: int
    ) -> dict[str, Any]:
        data_list, total = await self._iot_data_repo.find_paginated(page, page_size)
        return {
            "data": [self._iot_data_to_dict(d) for d in data_list],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_device_stats(self, device_id: int) -> dict[str, Any]:
        params = QueryParams(
            measurement="sensor_data", field="value", mean="mean",
        )
        result = self._influxdb.calculate_statistics(params)
        return {
            "device_id": device_id,
            "success": result.success,
            "data": [{"type": s.type, "value": s.value} for s in result.data],
            "summary": vars(result.summary) if result.summary else None,
        }

    async def export_data(
        self, device_ids: list[int], start: str, end: str, fmt: str
    ) -> dict[str, Any]:
        all_data = []
        for device_id in device_ids:
            data = await self.get_data_by_date_range(device_id, start, end)
            all_data.extend(data)

        return {
            "format": fmt,
            "count": len(all_data),
            "data": all_data,
        }

    async def cleanup_old_data(self, days: int) -> dict[str, Any]:
        deleted = await self._iot_data_repo.cleanup_old(days)
        return {"deleted": deleted, "days": days}

    # --- Internal Helpers ---

    async def _get_cached_mqtt_data(self, topic: str) -> dict[str, Any] | None:
        if not self.is_connected():
            return None

        cache_key = f"mqtt:topic:{topic}"
        if self.is_cache_enabled():
            cached = self._redis.get(cache_key)
            if cached:
                return json.loads(cached)

        try:
            result = self._mqtt_client.request_data(topic, topic, "", timeout=3.0)
            if result and self.is_cache_enabled():
                self._redis.setex(cache_key, 5, json.dumps(result, default=str))
            return result if isinstance(result, dict) else {"value": result}
        except Exception as e:
            logger.debug(f"MQTT data fetch failed for {topic}: {e}")
            return None

    async def _log_activity(
        self, device_id: int, action: str, details: str
    ) -> None:
        log = ActivityLog(
            device_id=device_id,
            log_type=action,
            description=details,
        )
        await self._activity_log_repo.create(log)

    def _device_to_dict(self, device: Device) -> dict[str, Any]:
        return {
            "id": device.id,
            "hardware_id": device.hardware_id,
            "device_name": device.device_name,
            "device_type": device.device_type,
            "mqtt_topic": device.mqtt_topic,
            "mqtt_name": device.mqtt_name,
            "unit": device.unit,
            "status": device.status,
            "is_active": device.is_active,
            "location_id": device.location_id,
            "location_name": device.location_name,
        }

    def _status_to_dict(self, status: DeviceStatus) -> dict[str, Any]:
        return {
            "device_id": status.device_id,
            "is_online": status.is_online,
            "last_seen": status.last_seen.isoformat() if status.last_seen else None,
            "last_value": status.last_value,
            "count_alarm": status.count_alarm,
            "event": status.event,
            "status": status.status,
        }

    def _config_to_dict(self, config: DeviceConfig) -> dict[str, Any]:
        return {
            "device_id": config.device_id,
            "max_value": config.max_value,
            "min_value": config.min_value,
            "warning_threshold": config.warning_threshold,
            "alert_threshold": config.alert_threshold,
            "recovery_warning": config.recovery_warning,
            "recovery_alert": config.recovery_alert,
            "calibration_offset": config.calibration_offset,
            "calibration_multiplier": config.calibration_multiplier,
            "mqtt_control_on": config.mqtt_control_on,
            "mqtt_control_off": config.mqtt_control_off,
            "action_name": config.action_name,
        }

    def _iot_data_to_dict(self, data: IoTData) -> dict[str, Any]:
        return {
            "id": data.id,
            "device_id": data.device_id,
            "data_json": data.data_json,
            "timestamp": data.timestamp.isoformat() if data.timestamp else None,
            "created_at": data.created_at.isoformat() if data.created_at else None,
        }
```

---

## 5. Phase 5: IoT Presentation Layer

### 5.1 Schemas
```
File: app/modules/iot/presentation/schemas.py
Action: CREATE
```

```python
# (same as 03-api-endpoint-mapping.md section 2)
```

### 5.2 Router
```
File: app/modules/iot/presentation/router.py
Action: CREATE
```

```python
# (same as 03-api-endpoint-mapping.md section 1)
```

---

## 6. Phase 6: Docker & Config

### 6.1 docker-compose.yaml Updates
```yaml
services:
  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: admin12345678
      DOCKER_INFLUXDB_INIT_ORG: my-org
      DOCKER_INFLUXDB_INIT_BUCKET: iot_sensors
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: my-super-secret-token
    volumes:
      - influxdb_data:/var/lib/influxdb2

  mosquitto:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log

volumes:
  influxdb_data:
```

### 6.2 .env Additions
```env
# InfluxDB
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=my-super-secret-token
INFLUXDB_ORG=my-org
INFLUXDB_BUCKET=iot_sensors
INFLUXDB_TIMEOUT=30

# MQTT
MQTT_BROKER=tcp://localhost:1883
MQTT_CLIENT_ID=fastapi-iot-client
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_KEEPALIVE=30
```

### 6.3 pyproject.toml Updates
```toml
dependencies = [
    # ... existing deps ...
    "influxdb-client>=1.40.0",
    "paho-mqtt>=2.1.0",
]
```

---

## 7. File Creation Summary

| # | File | Action | Lines | Source |
|---|------|--------|-------|--------|
| 1 | `app/core/settings.py` | EDIT | +20 | config.go |
| 2 | `app/core/influxdb_client.py` | CREATE | ~400 | pkg/influxdb/client.go |
| 3 | `app/core/mqtt_client.py` | CREATE | ~350 | pkg/mqtt/client.go |
| 4 | `app/core/queue/__init__.py` | CREATE | 1 | - |
| 5 | `app/core/queue/manager.py` | CREATE | ~200 | queue/manager.go |
| 6 | `app/core/queue/noop_queue.py` | CREATE | ~30 | queue/noop_queue.go |
| 7 | `app/modules/iot/__init__.py` | CREATE | 1 | - |
| 8 | `app/modules/iot/domain/__init__.py` | CREATE | 1 | - |
| 9 | `app/modules/iot/domain/entities/__init__.py` | CREATE | 1 | - |
| 10 | `app/modules/iot/domain/entities/device.py` | CREATE | ~80 | models/device.go |
| 11 | `app/modules/iot/domain/entities/device_config.py` | CREATE | ~30 | models/device_config.go |
| 12 | `app/modules/iot/domain/entities/device_status.py` | CREATE | ~30 | models/device_status.go |
| 13 | `app/modules/iot/domain/entities/device_alert.py` | CREATE | ~25 | models/device_alert.go |
| 14 | `app/modules/iot/domain/entities/iot_data.py` | CREATE | ~25 | models/iot_data.go |
| 15 | `app/modules/iot/domain/entities/alarm_log.py` | CREATE | ~25 | models/alarm_log.go |
| 16 | `app/modules/iot/domain/entities/activity_log.py` | CREATE | ~20 | models/activity_log.go |
| 17 | `app/modules/iot/domain/entities/schedule.py` | CREATE | ~25 | models/schedule.go |
| 18 | `app/modules/iot/domain/value_objects/__init__.py` | CREATE | 1 | - |
| 19 | `app/modules/iot/domain/value_objects/alarm.py` | CREATE | ~100 | pkg/helpers/iot.go |
| 20 | `app/modules/iot/domain/value_objects/mqtt.py` | CREATE | ~15 | config.go |
| 21 | `app/modules/iot/domain/value_objects/location.py` | CREATE | ~10 | models/location.go |
| 22 | `app/modules/iot/domain/helpers/__init__.py` | CREATE | 1 | - |
| 23 | `app/modules/iot/domain/helpers/alarm_logic.py` | CREATE | ~350 | pkg/helpers/iot.go |
| 24 | `app/modules/iot/infrastructure/__init__.py` | CREATE | 1 | - |
| 25 | `app/modules/iot/infrastructure/device_repository.py` | CREATE | ~100 | repository/device_repo.go |
| 26 | `app/modules/iot/infrastructure/device_config_repository.py` | CREATE | ~40 | repository/device_config_repo.go |
| 27 | `app/modules/iot/infrastructure/device_status_repository.py` | CREATE | ~40 | repository/device_status_repo.go |
| 28 | `app/modules/iot/infrastructure/device_alert_repository.py` | CREATE | ~20 | repository/device_alert_repo.go |
| 29 | `app/modules/iot/infrastructure/iot_data_repository.py` | CREATE | ~80 | repository/iot_data_repo.go |
| 30 | `app/modules/iot/infrastructure/alarm_log_repository.py` | CREATE | ~30 | repository/alarm_log_repo.go |
| 31 | `app/modules/iot/infrastructure/activity_log_repository.py` | CREATE | ~20 | repository/activity_log_repo.go |
| 32 | `app/modules/iot/infrastructure/schedule_repository.py` | CREATE | ~20 | repository/schedule_repo.go |
| 33 | `app/modules/iot/application/__init__.py` | CREATE | 1 | - |
| 34 | `app/modules/iot/application/use_case.py` | CREATE | ~800 | usecase/usecase.go |
| 35 | `app/modules/iot/presentation/__init__.py` | CREATE | 1 | - |
| 36 | `app/modules/iot/presentation/schemas.py` | CREATE | ~120 | presenter/presenter.go |
| 37 | `app/modules/iot/presentation/router.py` | CREATE | ~300 | delivery/http/handler.go |
| 38 | `pyproject.toml` | EDIT | +2 | - |
| 39 | `.env` | EDIT | +10 | - |
| 40 | `docker-compose.yaml` | EDIT | +30 | - |

**Total: 39 files (38 CREATE + 2 EDIT)**
**Estimated: ~3,400 lines Python**

---

## 8. Execution Order

```
Step 1:  Edit settings.py
Step 2:  Create influxdb_client.py
Step 3:  Create mqtt_client.py
Step 4:  Create queue/ module
Step 5:  Create domain/entities/ (8 files)
Step 6:  Create domain/value_objects/ (3 files)
Step 7:  Create domain/helpers/alarm_logic.py
Step 8:  Create infrastructure/ (8 repositories)
Step 9:  Create application/use_case.py
Step 10: Create presentation/schemas.py
Step 11: Create presentation/router.py
Step 12: Update docker-compose.yaml
Step 13: Update .env
Step 14: Update pyproject.toml
Step 15: Create Alembic migration
Step 16: Test & verify
```

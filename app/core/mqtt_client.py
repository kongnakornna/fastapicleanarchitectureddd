from __future__ import annotations

import json
import ssl
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import paho.mqtt.client as mqtt
from loguru import logger


@dataclass
class _PendingRequest:
    resolve: Callable[[Any], None]
    reject: Callable[[Exception], None]
    topic: str = ""


class MQTTClient:
    """MQTT client with request-response pattern support.

    Translated from Go: pkg/mqtt/client.go
    Uses paho-mqtt.
    """

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
        self._keepalive = keepalive
        self._connected = False

        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self._client_id,
            clean_session=clean_session,
        )

        if username:
            self._client.username_pw_set(username, password)

        self._client.tls_set(cert_reqs=ssl.CERT_NONE)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

        self._pending: dict[str, list[_PendingRequest]] = {}
        self._lock = threading.Lock()
        self._subscription_count: dict[str, int] = {}

        logger.info(
            f"MQTT client created: broker={broker}, client_id={self._client_id}"
        )

    def connect(self) -> None:
        host, port = self._parse_broker(self._broker)
        self._client.connect(host, port, keepalive=self._keepalive)
        self._client.loop_start()

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
        payload: str | bytes | dict[str, Any],
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

        self._client.subscribe(topic, qos=qos)
        if callback:

            def _on_message(
                client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
            ) -> None:
                callback(msg.topic, msg.payload)

            self._client.message_callback_add(topic, _on_message)

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
        """Request-response pattern: publish to request_topic, wait on response_topic."""
        if not self._connected:
            raise ConnectionError("MQTT client not connected")

        wait_topic = response_topic or request_topic

        msg_payload = self._serialize_payload(payload)
        self._client.publish(request_topic, msg_payload, qos=1)

        return self._get_topic(wait_topic, int(timeout * 1000))

    def get_data_from_topic(
        self,
        topic: str,
        timeout: float = 30.0,
    ) -> bytes:
        """Subscribe to topic and wait for one message."""
        if not self._connected:
            raise ConnectionError("MQTT client not connected")

        result: list[bytes] = []
        event = threading.Event()

        def _on_message(
            client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
        ) -> None:
            if msg.topic == topic:
                result.append(msg.payload)
                event.set()

        self._client.subscribe(topic, qos=0)
        self._client.message_callback_add(topic, _on_message)

        try:
            if not event.wait(timeout):
                raise TimeoutError(
                    f"No message from topic {topic} after {timeout}s"
                )
            return result[0] if result else b""
        finally:
            self._client.unsubscribe(topic)
            self._client.message_callback_remove(topic)

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
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
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
            if topic not in self._pending or not self._pending[topic]:
                self._increment_subscription(topic)

            result_event = threading.Event()
            result_value: list[Any] = []
            error_value: list[Exception] = []

            def resolve(data: Any) -> None:
                result_value.append(data)
                result_event.set()

            def reject(err: Exception) -> None:
                error_value.append(err)
                result_event.set()

            req = _PendingRequest(resolve=resolve, reject=reject, topic=topic)
            self._pending.setdefault(topic, []).append(req)

        def _timeout_handler() -> None:
            time.sleep(timeout_ms / 1000.0)
            with self._lock:
                if topic in self._pending and req in self._pending[topic]:
                    self._pending[topic].remove(req)
                    if not self._pending[topic]:
                        del self._pending[topic]
                        self._decrement_subscription(topic)
                    req.reject(
                        TimeoutError(
                            f"Timeout: no message from topic {topic} after {timeout_ms}ms"
                        )
                    )

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
        """Parse 'tcp://host:port' or 'host:port' or 'host'."""
        broker = broker.replace("tcp://", "").replace("ssl://", "")
        parts = broker.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 1883
        return host, port

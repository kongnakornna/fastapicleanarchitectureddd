"""
app/core/mqtt_client.py — MQTT client wrapper (paho-mqtt)

TH: wrapper สำหรับ MQTT — subscribe + publish + cache latest message per topic
EN: MQTT client wrapper — subscribe + publish + cache latest per topic

ใช้ใน iot module (dependencies._get_mqtt_client) สำหรับ device control + sensor ingest
"""
from __future__ import annotations

import threading
import time
from collections import deque
from typing import Any

import paho.mqtt.client as mqtt
from loguru import logger


# ═══════════════════════════════════════════════════════════════
#  CLIENT
# ═══════════════════════════════════════════════════════════════
class MQTTClient:
    """
    TH: MQTT client — thread-safe, non-blocking
    EN: MQTT client — thread-safe, non-blocking
    """

    MAX_HISTORY_PER_TOPIC = 100

    def __init__(
        self,
        broker: str,
        client_id: str = "",
        username: str = "",
        password: str = "",
        keepalive: int = 30,
    ) -> None:
        self._broker = broker
        self._client_id = client_id or f"fastapi-{int(time.time())}"
        self._username = username
        self._password = password
        self._keepalive = keepalive

        self._host: str = ""
        self._port: int = 1888
        self._client: mqtt.Client | None = None
        self._connected: bool = False
        self._lock = threading.Lock()

        # topic → deque of {payload, timestamp}
        self._messages: dict[str, deque[dict[str, Any]]] = {}

        self._parse_broker()

    # ───────────────────────────────────────────────────────────
    #  PARSING
    # ───────────────────────────────────────────────────────────
    def _parse_broker(self) -> None:
        """TH: parse broker URL: mqtt://host:port → host, port"""
        url = self._broker
        if "://" in url:
            _, url = url.split("://", 1)

        if ":" in url:
            self._host, port_str = url.rsplit(":", 1)
            try:
                self._port = int(port_str)
            except ValueError:
                self._port = 1888
        else:
            self._host = url
            self._port = 1888

    # ───────────────────────────────────────────────────────────
    #  CONNECT
    # ───────────────────────────────────────────────────────────
    def connect(self) -> bool:
        """TH: connect ไป MQTT broker | EN: connect to broker"""
        try:
            client = mqtt.Client(client_id=self._client_id)

            if self._username:
                client.username_pw_set(self._username, self._password or None)

            client.on_connect = self._on_connect
            client.on_disconnect = self._on_disconnect
            client.on_message = self._on_message

            client.connect(self._host, self._port, self._keepalive)
            client.loop_start()

            # รอ connect (สูงสุด 2 วินาที)
            for _ in range(20):
                if self._connected:
                    break
                time.sleep(0.1)

            self._client = client
            if self._connected:
                logger.info(f"MQTT connected: {self._host}:{self._port}")
                return True

            logger.warning(f"MQTT connect timeout: {self._host}:{self._port}")
            return False

        except Exception as exc:
            logger.error(f"MQTT connect failed: {exc}")
            self._connected = False
            return False

    # ───────────────────────────────────────────────────────────
    #  PUBLISH / SUBSCRIBE
    # ───────────────────────────────────────────────────────────
    def is_connected(self) -> bool:
        return self._connected

    def publish(self, topic: str, message: str, qos: int = 1) -> bool:
        """TH: publish ข้อความไปยัง topic | EN: publish message to topic"""
        if not self._connected or self._client is None:
            return False
        try:
            result = self._client.publish(topic, message, qos=qos)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as exc:
            logger.warning(f"MQTT publish failed: {exc}")
            return False

    def subscribe(self, topic: str, qos: int = 1) -> bool:
        """TH: subscribe topic | EN: subscribe topic"""
        if not self._connected or self._client is None:
            return False
        try:
            result = self._client.subscribe(topic, qos=qos)
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        except Exception as exc:
            logger.warning(f"MQTT subscribe failed: {exc}")
            return False

    def get_data_from_topic(self, topic: str, timeout: int = 5) -> str | None:
        """
        TH: ดึง payload ล่าสุดจาก topic (ใช้ cache)
        EN: get latest payload from topic (uses cache)

        Note: timeout ถูกใช้เป็น threshold สำหรับ "ความเก่า" ของข้อมูล
        — ถ้า message เก่ากว่า timeout → return None
        """
        with self._lock:
            msgs = self._messages.get(topic)
            if not msgs:
                return None

            latest = msgs[-1]
            age = time.time() - latest["timestamp"]
            if age > timeout:
                # ข้อมูลเก่าเกิน — แต่ยัง return อยู่ (iot ต้องการค่าล่าสุดเสมอ)
                logger.debug(f"MQTT data stale ({age:.1f}s > {timeout}s): {topic}")
            return latest["payload"]

    # ───────────────────────────────────────────────────────────
    #  INTERNAL CALLBACKS
    # ───────────────────────────────────────────────────────────
    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: dict,
        rc: int,
    ) -> None:
        self._connected = (rc == 0)
        if self._connected:
            logger.info("MQTT on_connect: OK")
            # subscribe wildcard
            client.subscribe("iot/#", qos=1)
        else:
            logger.warning(f"MQTT on_connect failed: rc={rc}")

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int,
    ) -> None:
        self._connected = False
        if rc != 0:
            logger.warning(f"MQTT disconnected unexpectedly: rc={rc}")
        else:
            logger.info("MQTT disconnected gracefully")

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        msg: mqtt.MQTTMessage,
    ) -> None:
        """TH: รับ message → cache | EN: receive message → cache"""
        try:
            payload = msg.payload.decode("utf-8", errors="ignore")
        except Exception:
            payload = str(msg.payload)

        with self._lock:
            bucket = self._messages.setdefault(
                msg.topic, deque(maxlen=self.MAX_HISTORY_PER_TOPIC),
            )
            bucket.append({
                "topic": msg.topic,
                "payload": payload,
                "timestamp": time.time(),
                "qos": msg.qos,
            })

    # ───────────────────────────────────────────────────────────
    #  LIFECYCLE
    # ───────────────────────────────────────────────────────────
    def disconnect(self) -> None:
        """TH: ปิดการเชื่อมต่อ | EN: disconnect"""
        if self._client:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
            finally:
                self._client = None
                self._connected = False
                logger.info("MQTT disconnected")

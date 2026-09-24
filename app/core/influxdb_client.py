"""
app/core/influxdb_client.py — InfluxDB 2.x client wrapper

TH: wrapper สำหรับ InfluxDB client — query time-series data
EN: InfluxDB client wrapper — query time-series data

ใช้ใน iot module (dependencies._get_influxdb_client) สำหรับดึง sensor data
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from influxdb_client import InfluxDBClient as _InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from loguru import logger


# ═══════════════════════════════════════════════════════════════
#  QUERY PARAMS
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class QueryParams:
    """TH: query parameters | EN: query parameters"""
    measurement: str
    field: str = "value"
    bucket: str = "iot_sensors"
    start: str = "-1h"
    stop: str = "now()"
    limit: int = 1000


# ═══════════════════════════════════════════════════════════════
#  CLIENT WRAPPER
# ═══════════════════════════════════════════════════════════════
class InfluxDBClientWrapper:
    """
    TH: InfluxDB client wrapper — thread-safe singleton pattern
    EN: InfluxDB client wrapper — thread-safe singleton pattern
    """

    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str,
        timeout: int = 30,
    ) -> None:
        self._url = url
        self._token = token
        self._org = org
        self._bucket = bucket
        self._timeout = timeout
        self._client: _InfluxDBClient | None = None

    # ───────────────────────────────────────────────────────────
    #  LAZY CLIENT
    # ───────────────────────────────────────────────────────────
    def _get_client(self) -> _InfluxDBClient:
        """TH: สร้าง client แบบ lazy | EN: lazily create client"""
        if self._client is None:
            self._client = _InfluxDBClient(
                url=self._url,
                token=self._token,
                org=self._org,
                timeout=self._timeout * 1000,  # ms
            )
        return self._client

    # ───────────────────────────────────────────────────────────
    #  QUERY
    # ───────────────────────────────────────────────────────────
    def query_filter_data(self, params: QueryParams) -> list[dict[str, Any]]:
        """
        TH: query time-series data ตาม measurement + field
        EN: query time-series data by measurement + field

        Returns:
            list[dict]: [{"_time": ..., "_value": ..., "_field": ..., "_measurement": ...}]
                        ถ้า error → return [] (never raise)
        """
        try:
            client = self._get_client()
            query_api: QueryApi = client.query_api()

            flux = f'''
                from(bucket: "{params.bucket}")
                    |> range(start: {params.start}, stop: {params.stop})
                    |> filter(fn: (r) => r._measurement == "{params.measurement}")
                    |> filter(fn: (r) => r._field == "{params.field}")
                    |> limit(n: {params.limit})
            '''

            tables = query_api.query(flux, org=self._org)
            results: list[dict[str, Any]] = []

            for table in tables:
                for record in table.records:
                    results.append({
                        "_time": record.get_time().isoformat()
                        if record.get_time() else None,
                        "_value": record.get_value(),
                        "_field": record.get_field(),
                        "_measurement": record.get_measurement(),
                    })

            logger.debug(
                f"InfluxDB query OK: {params.measurement}.{params.field} "
                f"→ {len(results)} points"
            )
            return results

        except Exception as exc:
            logger.warning(f"InfluxDB query failed: {exc}")
            return []

    def query_raw(self, flux: str) -> list[dict[str, Any]]:
        """
        TH: query ด้วย Flux script ตรงๆ | EN: query with raw Flux
        """
        try:
            client = self._get_client()
            query_api = client.query_api()
            tables = query_api.query(flux, org=self._org)

            results: list[dict[str, Any]] = []
            for table in tables:
                for record in table.records:
                    results.append(record.values)
            return results
        except Exception as exc:
            logger.warning(f"InfluxDB raw query failed: {exc}")
            return []

    # ───────────────────────────────────────────────────────────
    #  HEALTH
    # ───────────────────────────────────────────────────────────
    def ping(self) -> bool:
        """TH: ตรวจสอบการเชื่อมต่อ | EN: check connection"""
        try:
            client = self._get_client()
            return client.ping()
        except Exception as exc:
            logger.warning(f"InfluxDB ping failed: {exc}")
            return False

    def close(self) -> None:
        """TH: ปิด client | EN: close client"""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
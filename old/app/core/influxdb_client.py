from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import WriteApi
from loguru import logger


@dataclass(frozen=True)
class QueryParams:
    """Query parameters for InfluxDB Flux queries."""

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
    """InfluxDB client wrapper.

    Translated from Go: pkg/influxdb/client.go
    Uses influxdb-client-python v2.
    """

    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str,
        timeout: int = 30,
    ):
        self._org = org
        self._bucket = bucket
        self._timeout = timeout

        self._client = InfluxDBClient(
            url=url,
            token=token,
            org=org,
            timeout=timeout * 1000,
        )
        self._write_api: WriteApi = self._client.write_api()
        self._query_api: QueryApi = self._client.query_api()

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
        point = point.time(timestamp) if timestamp else point.time(datetime.utcnow())
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
        flux_query = (
            f'from(bucket: "{bucket}")'
            f"|> range(start: {params.start}, stop: {params.stop})"
            f'|> filter(fn: (r) => r["_measurement"] == "{params.measurement}")'
            f'|> filter(fn: (r) => r["_field"] == "{params.field}")'
            f"|> limit(n: {params.limit}, offset: {params.offset})"
            f'|> yield(name: "filtered_data")'
        )
        return self._execute_query(flux_query)

    def query_device_chart(self, params: QueryParams) -> list[dict[str, Any]]:
        return self.query_filter_data(params)

    def query_filter_data_rs(self, params: QueryParams) -> list[dict[str, Any]]:
        bucket = params.bucket or self._bucket
        flux_query = (
            f'from(bucket: "{bucket}")'
            f"|> range(start: {params.start}, stop: {params.stop})"
            f'|> filter(fn: (r) => r["_measurement"] == "{params.measurement}")'
            f'|> filter(fn: (r) => r["_field"] == "{params.field}")'
            f'|> sort(columns: ["_time"], desc: false)'
            f"|> limit(n: {params.limit}, offset: {params.offset})"
            f'|> yield(name: "sorted_data")'
        )
        return self._execute_query(flux_query)

    def count_rows(self, params: QueryParams) -> CountResult:
        bucket = params.bucket or self._bucket
        start = params.start or "-30d"
        stop = params.stop or "now()"

        flux_query = (
            f'from(bucket: "{bucket}")'
            f"|> range(start: {start}, stop: {stop})"
            f'|> filter(fn: (r) => r["_measurement"] == "{params.measurement}")'
            f'|> filter(fn: (r) => r["_field"] == "{params.field}")'
            f"|> count()"
            f'|> yield(name: "count")'
        )
        try:
            results = self._execute_query(flux_query)
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
            results = self._execute_query(flux_query)
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
        self,
        bucket: str,
        start: str,
        stop: str,
        measurement: str,
        field: str,
        mean_type: str,
        window_period: str,
        percentile: float,
    ) -> str:
        base = f'from(bucket: "{bucket}") |> range(start: {start}, stop: {stop})'
        filters = (
            f'|> filter(fn: (r) => r["_measurement"] == "{measurement}")'
            f'|> filter(fn: (r) => r["_field"] == "{field}")'
        )

        if mean_type in ("mean", "average"):
            agg = f"aggregateWindow(every: {window_period}, fn: mean, createEmpty: false)"
            return f"{base} {filters} |> {agg} |> yield(name: \"mean\")"
        if mean_type == "median":
            agg = f"aggregateWindow(every: {window_period}, fn: median, createEmpty: false)"
            return f"{base} {filters} |> {agg} |> yield(name: \"median\")"
        if mean_type == "mode":
            grp = 'group(columns: ["_value"]) |> count() |> group(columns: ["_measurement"])'
            top = 'top(n: 1, columns: ["_value"])'
            return f"{base} {filters} |> {grp} |> {top} |> yield(name: \"mode\")"
        if mean_type == "first":
            return f'{base} {filters} |> first() |> yield(name: "first")'
        if mean_type == "stddev":
            return f'{base} {filters} |> stddev() |> yield(name: "stddev")'
        if mean_type == "variance":
            return f'{base} {filters} |> variance() |> yield(name: "variance")'
        if mean_type == "percentile":
            return (
                f"{base} {filters} |> percentile(percentile: {percentile:.6f})"
                f'|> yield(name: "percentile")'
            )
        # default: last
        return f'{base} {filters} |> last() |> yield(name: "last")'

    def _calculate_summary(self, params: QueryParams) -> SummaryStats | None:
        bucket = params.bucket or self._bucket
        start = params.start or "-1h"
        stop = params.stop or "now()"

        flux_query = (
            f'from(bucket: "{bucket}")'
            f"|> range(start: {start}, stop: {stop})"
            f'|> filter(fn: (r) => r["_measurement"] == "{params.measurement}")'
            f'|> filter(fn: (r) => r["_field"] == "{params.field}")'
            f"|> aggregateWindow(every: 1h, fn: mean, createEmpty: false)"
            f'|> yield(name: "summary")'
        )
        results = self._execute_query(flux_query)
        if not results:
            return None

        values = [
            r["_value"]
            for r in results
            if "_value" in r and isinstance(r["_value"], (int, float))
        ]
        if not values:
            return None

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
            p95=values_sorted[min(int(n * 0.95), n - 1)],
            p99=values_sorted[min(int(n * 0.99), n - 1)],
        )

    def _execute_query(self, flux_query: str) -> list[dict[str, Any]]:
        logger.debug(f"Executing InfluxDB query: {flux_query[:200]}...")
        tables = self._query_api.query(flux_query, org=self._org)

        results: list[dict[str, Any]] = []
        for table in tables:
            for record in table.records:
                results.append({
                    "_time": record.get_time(),
                    "_measurement": record.get_measurement(),
                    "_field": record.get_field(),
                    "_value": record.get_value(),
                })

        return results

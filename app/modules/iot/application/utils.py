"""iot application utils"""
from __future__ import annotations
from typing import Any


def parse_csv_payload(raw: str) -> dict[str, Any]:
    """TH: parse CSV payload → dict | EN: parse CSV payload"""
    result: dict[str, Any] = {}
    for i, val in enumerate(raw.split(",")):
        trimmed = val.strip()
        try:
            result[str(i)] = float(trimmed)
        except ValueError:
            result[str(i)] = trimmed
    result["raw"] = raw
    return result


def sanitize_payload(data: dict[str, Any]) -> dict[str, Any]:
    """TH: ทำความสะอาด payload | EN: sanitize payload"""
    MASK = {"password", "token", "secret", "mqtt_password"}
    return {k: ("***" if k in MASK else v) for k, v in data.items()}

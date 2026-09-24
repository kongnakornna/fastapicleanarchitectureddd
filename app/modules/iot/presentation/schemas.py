"""iot Pydantic v2 schemas"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ═══════════════════════════════════════════════════════════════
#  REQUESTS — Basic
# ═══════════════════════════════════════════════════════════════

class ControlRequest(BaseModel):
    """TH: คำสั่งควบคุม | EN: control request"""
    topic: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    model_config = ConfigDict(extra="forbid")


class UpdateDeviceStatusRequest(BaseModel):
    """TH: update device status (extra allowed) | EN: device status"""
    model_config = ConfigDict(extra="allow")


class UpdateDeviceConfigRequest(BaseModel):
    """TH: update device config | EN: device config"""
    config: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")


class ProcessMqttDataRequest(BaseModel):
    """TH: process MQTT data (manual ingest) | EN: manual MQTT ingest"""
    device_id: str = Field(..., min_length=1)
    raw_data: str = Field(..., min_length=1)
    model_config = ConfigDict(extra="forbid")


class ExportDataRequest(BaseModel):
    """TH: export data request | EN: data export"""
    device_id: str = ""
    start_date: str = ""
    end_date: str = ""
    format: str = Field(default="json", pattern="^(json|csv)$")
    model_config = ConfigDict(extra="forbid")


# ═══════════════════════════════════════════════════════════════
#  REQUESTS — Part 9: Batch Operations
# ═══════════════════════════════════════════════════════════════

class BatchProcessItem(BaseModel):
    """TH: รายการเดียวใน batch process | EN: single batch item"""
    device_id: str = Field(..., min_length=1)
    raw_data: str = Field(..., min_length=1)
    model_config = ConfigDict(extra="forbid")


class BatchProcessRequest(BaseModel):
    """
    TH: batch process MQTT payloads (สูงสุด 100 items)
    EN: batch process MQTT payloads (max 100 items)
    """
    items: list[BatchProcessItem] = Field(..., min_length=1, max_length=100)
    model_config = ConfigDict(extra="forbid")


class BatchControlItem(BaseModel):
    """TH: รายการ control เดียว | EN: single control item"""
    topic: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    model_config = ConfigDict(extra="forbid")


class BatchControlRequest(BaseModel):
    """
    TH: batch send control commands (สูงสุด 100 items)
    EN: batch send control commands (max 100 items)
    """
    items: list[BatchControlItem] = Field(..., min_length=1, max_length=100)
    model_config = ConfigDict(extra="forbid")


# ═══════════════════════════════════════════════════════════════
#  RESPONSES (Optional — ถ้าต้องการ typed responses)
# ═══════════════════════════════════════════════════════════════

class StatusResponse(BaseModel):
    """TH: สถานะ MQTT + cache | EN: MQTT + cache status"""
    mqtt_connected: bool
    cache_enabled: bool
    model_config = ConfigDict(extra="allow")


class BatchProcessResponse(BaseModel):
    """TH: ผลลัพธ์ batch process | EN: batch process result"""
    total: int
    success: int
    failed: int
    details: list[dict[str, Any]] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")


class BatchControlResponse(BaseModel):
    """TH: ผลลัพธ์ batch control | EN: batch control result"""
    total: int
    success: int
    failed: int
    results: list[bool] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")


class AlertChannelStatus(BaseModel):
    """TH: สถานะ alert channel | EN: alert channel status"""
    enabled: bool
    recipients: int
    model_config = ConfigDict(extra="allow")


class SchedulerJobInfo(BaseModel):
    """TH: ข้อมูล scheduler job | EN: scheduler job info"""
    id: str
    next_run: str | None = None
    trigger: str
    model_config = ConfigDict(extra="allow")


__all__ = [
    # Requests — Basic
    "ControlRequest",
    "UpdateDeviceStatusRequest",
    "UpdateDeviceConfigRequest",
    "ProcessMqttDataRequest",
    "ExportDataRequest",
    # Requests — Batch (Part 9)
    "BatchProcessItem",
    "BatchProcessRequest",
    "BatchControlItem",
    "BatchControlRequest",
    # Responses
    "StatusResponse",
    "BatchProcessResponse",
    "BatchControlResponse",
    "AlertChannelStatus",
    "SchedulerJobInfo",
]

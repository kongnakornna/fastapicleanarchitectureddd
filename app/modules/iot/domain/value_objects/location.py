from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocationConfig:
    """Location configuration value object."""

    location_id: int = 0
    location_name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    config_data: str = ""

"""ProviderConfig value object"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """TH: config ผู้ให้บริการ | EN: provider config VO"""
    name: str
    provider_type: str
    api_key: str
    base_url: str = ""
    timeout_seconds: int = 60

"""TH: Settings กลาง | EN: Central settings"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """TH: อ่านจาก env | EN: Load from env"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ─── App ──────────────────────────────────────
    app_name: str = "python-ddd-clean-arch"
    app_env: str = Field(default="dev", pattern="^(dev|staging|prod)$")
    debug: bool = False
    log_level: str = "INFO"
    log_json: bool = False

    # ─── Database ─────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/erp"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_echo: bool = False

    # ─── Redis ────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 300

    # ─── Kafka ────────────────────────────────────
    kafka_bootstrap: str = "localhost:9092"
    kafka_enabled: bool = False
    kafka_topic_prefix: str = "inventory"

    # ─── Security ─────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]
    request_max_bytes: int = 1_048_576


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """TH: singleton | EN: singleton"""
    return Settings()
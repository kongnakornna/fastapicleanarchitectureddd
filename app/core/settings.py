from __future__ import annotations

from collections.abc import Mapping
from functools import cached_property
from pathlib import Path
from types import MappingProxyType

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from jwcrypto import jwk
from pydantic import AnyHttpUrl, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from app.modules.shared.domain.enums import ApplicationEnvironment, CookieSameSite


# PathRule คือ mapping แบบ read-only ที่เก็บ "endpoint" กับ "method"
PathRule = Mapping[str, str]


def _path_rule(endpoint: str, method: str) -> PathRule:
    """Helper สร้าง PathRule แบบ read-only"""
    return MappingProxyType({"endpoint": endpoint, "method": method})


class Settings(BaseSettings):
    """ค่าคอนฟิกทั้งหมดของแอปพลิเคชัน"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_ignore_empty=True,
    )

    # ------------------------------------------------------------------
    # APPLICATION
    # ------------------------------------------------------------------
    APPLICATION_TITLE: str
    APPLICATION_SUMMARY: str
    APPLICATION_DESCRIPTION: str
    APPLICATION_VERSION: str
    APPLICATION_CONTACT_NAME: str
    APPLICATION_CONTACT_URL: str
    APPLICATION_CONTACT_EMAIL: str
    APPLICATION_CONTACT_PHONE: str
    APPLICATION_ENVIRONMENT: ApplicationEnvironment
    APPLICATION_PORT: int
    APPLICATION_CONNECT_TIMEOUT_SECONDS: int
    APPLICATION_URL: AnyHttpUrl
    APPLICATION_TABLE_PREFIX: str

    # API KEY
    API_KEY_PREFIX: str
    API_KEY_HASH_FINGERPRINT: str
    API_KEY_ENTROPY_BYTES: int

    # AUTH
    AUTH_BEARER_TOKEN_SCHEME_NAME: str
    AUTH_BEARER_TOKEN_SCHEME_DESCRIPTION: str
    AUTH_API_KEY_NAME: str
    AUTH_API_KEY_SCHEME_NAME: str
    AUTH_API_KEY_DESCRIPTION: str

    # COOKIES
    COOKIES_MAX_AGE_SECONDS: int
    COOKIES_TOKEN_TYPE_KEY: str
    COOKIES_ACCESS_TOKEN_KEY: str
    COOKIES_ACCESS_TOKEN_PATH: str
    COOKIES_REFRESH_TOKEN_KEY: str
    COOKIES_REFRESH_TOKEN_PATH: str
    COOKIES_DEVICE_KEY: str
    COOKIES_DOMAIN: str
    COOKIES_SAME_SITE: CookieSameSite

    # JWT
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_SIGNING_KEY_PASSWORD: str
    JWT_ENCRYPTION_KEY_PASSWORD: str
    JWT_AUTO_GENERATE_KEYS: bool
    JWT_KEYS_DIR: str
    JWT_SIGNING_PRIVATE_KEY_PATH: str
    JWT_SIGNING_PUBLIC_KEY_PATH: str
    JWT_ENCRYPTION_PRIVATE_KEY_PATH: str
    JWT_ENCRYPTION_PUBLIC_KEY_PATH: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_HASH_FINGERPRINT: str

    # LOGS
    LOGS_NAME: str
    LOGS_PATH: str
    LOGS_LEVEL: str
    LOGS_REQUEST_ID_LENGTH: int
    LOGS_PYGMENTS_STYLE: str

    # NGROK
    NGROK_AUTH_TOKEN: str = ""

    # POSTGRESQL
    POSTGRESQL_DATABASE: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: str

    # REDIS
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DB: int
    REDIS_USERNAME: str
    REDIS_SSL: bool
    REDIS_CONNECTION_TIMEOUT_SECONDS: int
    REDIS_SOCKET_TIMEOUT_SECONDS: int
    REDIS_DEFAULT_TTL_SECONDS: int
    REDIS_SESSION_TTL_SECONDS: int
    REDIS_TOMBSTONE_TTL_SECONDS: int
    REDIS_KEY_PREFIX: str
    REDIS_CACHE_VERSION: int
    REDIS_FLUSH_ON_STARTUP: bool
    REDIS_MAX_CONNECTIONS: int

    # SECURITY
    SECURITY_ALLOW_ORIGINS: list[str]
    SECURITY_ALLOW_HEADERS: list[str]
    SECURITY_ALLOW_METHODS: list[str]
    SECURITY_EMAIL_ALLOWED_DOMAINS: list[str]
    SECURITY_ADMIN_EMAIL: str
    SECURITY_ADMIN_PASSWORD: str

    # ==================================================================
    # GENERAL VALIDATORS
    # ==================================================================
    @field_validator("*", mode="before")
    @classmethod
    def strip_quotes(cls, v):
        if (
            isinstance(v, str)
            and len(v) >= 2
            and (
                (v.startswith('"') and v.endswith('"'))
                or (v.startswith("'") and v.endswith("'"))
            )
        ):
            return v[1:-1]
        return v

    @field_validator("COOKIES_SAME_SITE", mode="before")
    @classmethod
    def validate_cookies_same_site(cls, v):
        if isinstance(v, CookieSameSite):
            return v
        if isinstance(v, str):
            value = v.strip().strip('"').strip("'").lower()
            try:
                return CookieSameSite(value)
            except ValueError:
                pass
        raise ValueError(
            "Invalid COOKIES_SAME_SITE. Allowed values: 'lax', 'strict', 'none'."
        )

    @field_validator("APPLICATION_ENVIRONMENT", mode="before")
    @classmethod
    def validate_application_environment(cls, v):
        if isinstance(v, ApplicationEnvironment):
            return v
        if isinstance(v, str):
            value = v.strip().strip('"').strip("'").lower()
            try:
                return ApplicationEnvironment(value)
            except ValueError:
                pass
        raise ValueError(
            "Invalid APPLICATION_ENVIRONMENT. Allowed values: "
            "'dev', 'homolog', 'production'."
        )

    # ==================================================================
    # COMPUTED FIELDS
    # ==================================================================
    @computed_field
    @cached_property
    def APPLICATION_ENVIRONMENT_DEBUG(self) -> bool:
        return self.APPLICATION_ENVIRONMENT != ApplicationEnvironment.PRODUCTION.value

    @computed_field
    @cached_property
    def COOKIES_ACCESS_TOKEN_MAX_AGE(self) -> int:
        return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @computed_field
    @cached_property
    def COOKIES_REFRESH_TOKEN_MAX_AGE(self) -> int:
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # JWT KEY LOADERS
    @computed_field
    @cached_property
    def JWT_SIGNING_PRIVATE_KEY(self) -> jwk.JWK:
        with open(self.JWT_SIGNING_PRIVATE_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()
        return jwk.JWK.from_pem(
            pem_data,
            password=self.JWT_SIGNING_KEY_PASSWORD.encode("utf-8"),
        )

    @computed_field
    @cached_property
    def JWT_SIGNING_PUBLIC_KEY(self) -> jwk.JWK:
        with open(self.JWT_SIGNING_PUBLIC_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()
        return jwk.JWK.from_pem(pem_data)

    @computed_field
    @cached_property
    def JWT_ENCRYPTION_PRIVATE_KEY(self) -> jwk.JWK:
        with open(self.JWT_ENCRYPTION_PRIVATE_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()
        return jwk.JWK.from_pem(
            pem_data,
            password=self.JWT_ENCRYPTION_KEY_PASSWORD.encode("utf-8"),
        )

    @computed_field
    @cached_property
    def JWT_ENCRYPTION_PUBLIC_KEY(self) -> jwk.JWK:
        with open(self.JWT_ENCRYPTION_PUBLIC_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()
        return jwk.JWK.from_pem(pem_data)

    # POSTGRESQL URLS
    @computed_field
    @cached_property
    def POSTGRESQL_ASYNC_DATABASE_URL(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_HOST,
            port=int(self.POSTGRESQL_PORT),
            database=self.POSTGRESQL_DATABASE,
        )

    @computed_field
    @cached_property
    def POSTGRESQL_DATABASE_URL(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_HOST,
            port=int(self.POSTGRESQL_PORT),
            database=self.POSTGRESQL_DATABASE,
        )

    # REDIS
    @computed_field
    @cached_property
    def REDIS_URL(self) -> str:
        scheme = "rediss" if self.REDIS_SSL else "redis"
        return (
            f"{scheme}://{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}"
            f"@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )

    @computed_field
    @cached_property
    def REDIS_NAMESPACE(self) -> str:
        return f"{self.REDIS_KEY_PREFIX}:v{self.REDIS_CACHE_VERSION}"

    # ==================================================================
    # SECURITY PATH RULES
    # ==================================================================
    #
    #  ⚠️  กติกาสำคัญ:
    #  1. ชื่อ property ต้องเป็น UPPERCASE เป๊ะ ๆ เพราะ security.py เรียก
    #     settings.SECURITY_USER_ALLOWED_PATHS / SECURITY_MANAGER_ALLOWED_PATHS /
    #     SECURITY_ADMIN_ALLOWED_PATHS / SECURITY_NO_AUTH_PATHS
    #  2. endpoint ที่ใช้ Depends(no_authentication) ต้องอยู่ใน SECURITY_NO_AUTH_PATHS
    #  3. endpoint ที่ใช้ Depends(authenticate_user) ต้องอยู่ใน SECURITY_USER_ALLOWED_PATHS
    #     (manager/admin inherit ผ่าน * อยู่แล้ว)
    #  4. endpoint ที่ใช้ Depends(authenticate_manager) ต้องอยู่ใน SECURITY_MANAGER_ALLOWED_PATHS
    #  5. endpoint ที่ใช้ Depends(authenticate_admin) ต้องอยู่ใน SECURITY_ADMIN_ALLOWED_PATHS
    #  6. WebSocket / endpoint ที่ไม่มี dependency → ไม่ต้องใส่
    #

    @computed_field
    @cached_property
    def SECURITY_NO_AUTH_PATHS(self) -> tuple[PathRule, ...]:
        """
        Path ที่ไม่ต้อง authenticate — ใช้โดย no_authentication
        ต้องมีทุก endpoint ที่ประกาศ `Depends(no_authentication)`
        """
        return (
            # ═══ AUTHENTICATION ═══
            _path_rule("/api/v1/authentication/sign-up", "POST"),
            _path_rule("/api/v1/authentication/login", "POST"),
            _path_rule("/api/v1/authentication/logout", "DELETE"),
            # ═══ EXAMPLE ═══
            _path_rule("/api/v1/example", "POST"),
            # ═══ HEALTH ═══
            _path_rule("/health", "GET"),
            # ═══ USER (sign-up) ═══
            _path_rule("/api/v1/user", "POST"),
            # ═══ WEBSOCKET handshake ═══
            _path_rule("/api/v1/websocket/connect", "GET"),
            # ═══ IOT — PUBLIC (Depends(no_authentication)) ═══
            _path_rule("/iot/status", "GET"),
            _path_rule("/iot/ws/stats", "GET"),
            _path_rule("/iot/topic", "GET"),
            _path_rule("/iot/topicdevicechart", "GET"),
            _path_rule("/iot/device", "GET"),
            _path_rule("/iot/devicebuckets", "GET"),
            _path_rule("/iot/locationdevice", "GET"),
            _path_rule("/iot/sensercharts", "GET"),
            _path_rule("/iot/devicesensercharts", "GET"),
            _path_rule("/iot/monitordevicechart", "GET"),
            _path_rule("/iot/alarmdevicestatus", "GET"),
            _path_rule("/iot/alarmdevicestatuscontrol", "GET"),
            _path_rule("/iot/devicemqtt", "GET"),
            _path_rule("/iot/monitordevicegroup", "GET"),
            _path_rule("/iot/devicestatus", "GET"),
            _path_rule("/iot/deviceconfig", "GET"),
            _path_rule("/iot/deviceiotdata", "GET"),
            _path_rule("/iot/devicestats", "GET"),
            _path_rule("/iot/devicedataexport", "GET"),
            _path_rule("/iot/alerts/channels", "GET"),
            _path_rule("/iot/admin/scheduler/jobs", "GET"),
        )

    @computed_field
    @cached_property
    def SECURITY_USER_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:
        """
        Path ที่ user role ทั่วไปเข้าถึงได้ (authenticate_user)
        เริ่มจาก NO_AUTH_PATHS แล้วเพิ่ม endpoint ที่ต้อง login
        """
        return (
            *self.SECURITY_NO_AUTH_PATHS,
            # ═══ AUTHENTICATION ═══
            _path_rule("/api/v1/authentication/refresh", "PATCH"),
            # ═══ USER ═══
            _path_rule("/api/v1/user/me", "GET"),
            # ═══ NOTIFICATION ═══
            _path_rule("/api/v1/notification", "GET"),
            _path_rule("/api/v1/notification/{id}", "PATCH"),
            # ═══ IOT — PROTECTED (Depends(authenticate_user)) ═══
            _path_rule("/iot/controls", "GET"),
            _path_rule("/iot/control", "POST"),
            _path_rule("/iot/devicestatus", "PUT"),
            _path_rule("/iot/updatedeviceconfig", "PUT"),
            _path_rule("/iot/devicedatacleanup", "DELETE"),
            _path_rule("/iot/batch/process", "POST"),
            _path_rule("/iot/batch/control", "POST"),
            _path_rule("/iot/alerts/test", "POST"),
            _path_rule("/iot/processmqttdata", "POST"),
        )

    @computed_field
    @cached_property
    def SECURITY_MANAGER_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:
        """
        Path ที่ manager เข้าถึงได้ (authenticate_manager)
        inherit มาจาก USER_ALLOWED_PATHS แล้วเพิ่มสิทธิ์ manager
        """
        return (
            *self.SECURITY_USER_ALLOWED_PATHS,
            # ═══ KNOWLEDGE ═══
            _path_rule("/api/v1/knowledge", "POST"),
            _path_rule("/api/v1/knowledge", "GET"),
            _path_rule("/api/v1/knowledge/{id}", "PATCH"),
            _path_rule("/api/v1/knowledge/{id}", "DELETE"),
        )

    @computed_field
    @cached_property
    def SECURITY_ADMIN_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:
        """
        Path ที่ admin เข้าถึงได้ (authenticate_admin)
        inherit มาจาก MANAGER_ALLOWED_PATHS แล้วเพิ่มสิทธิ์ admin
        """
        return (
            *self.SECURITY_MANAGER_ALLOWED_PATHS,
            # ═══ HEALTH ═══
            _path_rule("/api/v1/alembic-version", "GET"),
            # ═══ KEY ═══
            _path_rule("/api/v1/key", "POST"),
            _path_rule("/api/v1/key", "GET"),
            _path_rule("/api/v1/key/{id}", "GET"),
            _path_rule("/api/v1/key/{id}", "PATCH"),
            _path_rule("/api/v1/key/{id}/rotate", "PATCH"),
            _path_rule("/api/v1/key/{id}", "DELETE"),
        )

    @computed_field
    @cached_property
    def SECURITY_API_KEY_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:
        """Path ที่ API key เข้าถึงได้ — ปิดไว้ทั้งหมดตอนนี้"""
        return ()

    # ==================================================================
    # JWT KEY GENERATION
    # ==================================================================
    def generate_authentication_keys(self) -> None:
        if not self.JWT_AUTO_GENERATE_KEYS:
            return

        keys_dir = Path(self.JWT_KEYS_DIR)
        keys_dir.mkdir(parents=True, exist_ok=True)

        signing_private = Path(self.JWT_SIGNING_PRIVATE_KEY_PATH)
        signing_public = Path(self.JWT_SIGNING_PUBLIC_KEY_PATH)
        encryption_private = Path(self.JWT_ENCRYPTION_PRIVATE_KEY_PATH)
        encryption_public = Path(self.JWT_ENCRYPTION_PUBLIC_KEY_PATH)

        if not signing_private.exists() or not signing_public.exists():
            _key = Ed25519PrivateKey.generate()
            signing_private.write_bytes(
                _key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(
                        self.JWT_SIGNING_KEY_PASSWORD.encode()
                    ),
                )
            )
            signing_public.write_bytes(
                _key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        if not encryption_private.exists() or not encryption_public.exists():
            _key = X25519PrivateKey.generate()
            encryption_private.write_bytes(
                _key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(
                        self.JWT_ENCRYPTION_KEY_PASSWORD.encode()
                    ),
                )
            )
            encryption_public.write_bytes(
                _key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

    # ==================================================================
    # INIT
    # ==================================================================
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.generate_authentication_keys()

        if ":" in self.POSTGRESQL_HOST:
            host_parts = self.POSTGRESQL_HOST.split(":")
            self.POSTGRESQL_HOST = host_parts[0]
            if len(host_parts) > 1 and not self.POSTGRESQL_PORT:
                self.POSTGRESQL_PORT = host_parts[1]

        for field_name in self.model_fields:
            value = getattr(self, field_name)
            if (
                isinstance(value, str)
                and len(value) >= 2
                and (
                    (value.startswith('"') and value.endswith('"'))
                    or (value.startswith("'") and value.endswith("'"))
                )
            ):
                setattr(self, field_name, value[1:-1])


settings = Settings()

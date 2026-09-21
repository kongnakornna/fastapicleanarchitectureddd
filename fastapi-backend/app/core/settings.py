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

# PathRule คือ mapping แบบ read-only ที่เก็บ "endpoint" กับ "method" ของแต่ละ path rule
# ใช้ MappingProxyType เพื่อกันการแก้ไขหลังสร้างแล้ว
PathRule = Mapping[str, str]


def _path_rule(endpoint: str, method: str) -> PathRule:
    """
    Helper สร้าง PathRule แบบ read-only

    Args:
        endpoint: path ของ endpoint เช่น "/api/v1/authentication/sign-up"
        method: HTTP method เช่น "POST", "GET"

    Returns:
        MappingProxyType ที่ไม่สามารถแก้ไขได้
    """
    return MappingProxyType({"endpoint": endpoint, "method": method})


class Settings(BaseSettings):
    """
    ค่าคอนฟิกทั้งหมดของแอปพลิเคชัน

    - โหลดจาก .env อัตโนมัติ
    - ค่าที่เป็น computed_field จะคำนวณตอนเข้าถึงครั้งแรก และ cache ไว้
    - ตอน __init__ จะ generate JWT keys ให้ถ้ายังไม่มี
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ไม่ error ถ้ามี env ที่ไม่รู้จัก
        case_sensitive=True,  # ชื่อ env ต้องตรงเป๊ะ
        env_ignore_empty=True,  # ข้าม env ที่เป็น string ว่าง
    )

    # ------------------------------------------------------------------
    # APPLICATION — ข้อมูลพื้นฐานของแอป
    # ------------------------------------------------------------------
    APPLICATION_TITLE: str
    APPLICATION_SUMMARY: str
    APPLICATION_DESCRIPTION: str
    APPLICATION_VERSION: str
    APPLICATION_CONTACT_NAME: str
    APPLICATION_CONTACT_URL: str
    APPLICATION_CONTACT_EMAIL: str
    APPLICATION_CONTACT_PHONE: str
    APPLICATION_ENVIRONMENT: ApplicationEnvironment  # dev / homolog / production
    APPLICATION_PORT: int
    APPLICATION_CONNECT_TIMEOUT_SECONDS: int
    APPLICATION_URL: AnyHttpUrl
    APPLICATION_TABLE_PREFIX: str

    # ------------------------------------------------------------------
    # API KEY — ค่าที่ใช้สร้าง/ตรวจ API key
    # ------------------------------------------------------------------
    API_KEY_PREFIX: str
    API_KEY_HASH_FINGERPRINT: str  # secret key (hex) สำหรับ HMAC hash
    API_KEY_ENTROPY_BYTES: int

    # ------------------------------------------------------------------
    # AUTH — ค่าที่ใช้ในเอกสาร OpenAPI (ชื่อ scheme, คำอธิบาย)
    # ------------------------------------------------------------------
    AUTH_BEARER_TOKEN_SCHEME_NAME: str
    AUTH_BEARER_TOKEN_SCHEME_DESCRIPTION: str
    AUTH_API_KEY_NAME: str
    AUTH_API_KEY_SCHEME_NAME: str
    AUTH_API_KEY_DESCRIPTION: str

    # ------------------------------------------------------------------
    # COOKIES — ค่าที่ใช้ตั้ง cookie ฝั่ง client
    # ------------------------------------------------------------------
    COOKIES_MAX_AGE_SECONDS: int
    COOKIES_TOKEN_TYPE_KEY: str
    COOKIES_ACCESS_TOKEN_KEY: str
    COOKIES_ACCESS_TOKEN_PATH: str
    COOKIES_REFRESH_TOKEN_KEY: str
    COOKIES_REFRESH_TOKEN_PATH: str
    COOKIES_DEVICE_KEY: str
    COOKIES_DOMAIN: str
    COOKIES_SAME_SITE: CookieSameSite

    # ------------------------------------------------------------------
    # JWT — ค่าที่ใช้สร้าง/ถอดรหัส token (JWS + JWE)
    # ------------------------------------------------------------------
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_SIGNING_KEY_PASSWORD: str
    JWT_ENCRYPTION_KEY_PASSWORD: str
    JWT_AUTO_GENERATE_KEYS: bool  # ถ้า true จะ generate key ให้ถ้ายังไม่มี
    JWT_KEYS_DIR: str
    JWT_SIGNING_PRIVATE_KEY_PATH: str
    JWT_SIGNING_PUBLIC_KEY_PATH: str
    JWT_ENCRYPTION_PRIVATE_KEY_PATH: str
    JWT_ENCRYPTION_PUBLIC_KEY_PATH: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_HASH_FINGERPRINT: str  # secret key (hex) สำหรับ HMAC hash jti

    # ------------------------------------------------------------------
    # LOGS — ค่าที่ใช้ตั้งค่า loguru
    # ------------------------------------------------------------------
    LOGS_NAME: str
    LOGS_PATH: str
    LOGS_LEVEL: str
    LOGS_REQUEST_ID_LENGTH: int
    LOGS_PYGMENTS_STYLE: str

    # ------------------------------------------------------------------
    # NGROK — ใช้ตอน dev เท่านั้น
    # ------------------------------------------------------------------
    NGROK_AUTH_TOKEN: str = ""

    # ------------------------------------------------------------------
    # POSTGRESQL — ค่าที่ใช้ต่อฐานข้อมูล
    # ------------------------------------------------------------------
    POSTGRESQL_DATABASE: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: str

    # ------------------------------------------------------------------
    # REDIS — ค่าที่ใช้ต่อ cache
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # SECURITY — allow list ต่าง ๆ + admin seed
    # ------------------------------------------------------------------
    SECURITY_ALLOW_ORIGINS: list[str]  # CORS allow list
    SECURITY_ALLOW_HEADERS: list[str]
    SECURITY_ALLOW_METHODS: list[str]
    SECURITY_EMAIL_ALLOWED_DOMAINS: list[str]
    SECURITY_ADMIN_EMAIL: str
    SECURITY_ADMIN_PASSWORD: str

    # ==================================================================
    # GENERAL VALIDATORS — ตัวตรวจสอบค่าพื้นฐาน
    # ==================================================================
    @field_validator("*", mode="before")
    @classmethod
    def strip_quotes(cls, v):
        """ตัดเครื่องหมายคำพูดหัว-ท้ายออกจาก string ทุก field (เผื่อ .env ใส่มา)"""
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
        """ตรวจว่า COOKIES_SAME_SITE เป็น lax / strict / none"""
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
        """ตรวจว่า APPLICATION_ENVIRONMENT เป็น dev / homolog / production"""
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
    # COMPUTED FIELDS — ค่าที่คำนวณจาก field อื่น (cache ไว้)
    # ==================================================================

    # APPLICATION ------------------------------------------------------
    @computed_field
    @cached_property
    def APPLICATION_ENVIRONMENT_DEBUG(self) -> bool:
        """True ถ้าไม่ใช่ production — ใช้เปิด debug mode"""
        return self.APPLICATION_ENVIRONMENT != ApplicationEnvironment.PRODUCTION.value

    # COOKIES ----------------------------------------------------------
    @computed_field
    @cached_property
    def COOKIES_ACCESS_TOKEN_MAX_AGE(self) -> int:
        """อายุ cookie ของ access token (วินาที)"""
        return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @computed_field
    @cached_property
    def COOKIES_REFRESH_TOKEN_MAX_AGE(self) -> int:
        """อายุ cookie ของ refresh token (วินาที)"""
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # JWT — โหลด key จากไฟล์ PEM ---------------------------------------
    @computed_field
    @cached_property
    def JWT_SIGNING_PRIVATE_KEY(self) -> jwk.JWK:
        """Private key สำหรับ sign (Ed25519) — โหลดจากไฟล์และถอดรหัสด้วย password"""
        with open(self.JWT_SIGNING_PRIVATE_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()

        return jwk.JWK.from_pem(
            pem_data,
            password=self.JWT_SIGNING_KEY_PASSWORD.encode("utf-8"),
        )

    @computed_field
    @cached_property
    def JWT_SIGNING_PUBLIC_KEY(self) -> jwk.JWK:
        """Public key สำหรับ verify signature"""
        with open(self.JWT_SIGNING_PUBLIC_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()

        return jwk.JWK.from_pem(pem_data)

    @computed_field
    @cached_property
    def JWT_ENCRYPTION_PRIVATE_KEY(self) -> jwk.JWK:
        """Private key สำหรับถอดรหัส (X25519)"""
        with open(self.JWT_ENCRYPTION_PRIVATE_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()

        return jwk.JWK.from_pem(
            pem_data,
            password=self.JWT_ENCRYPTION_KEY_PASSWORD.encode("utf-8"),
        )

    @computed_field
    @cached_property
    def JWT_ENCRYPTION_PUBLIC_KEY(self) -> jwk.JWK:
        """Public key สำหรับเข้ารหัส"""
        with open(self.JWT_ENCRYPTION_PUBLIC_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()

        return jwk.JWK.from_pem(pem_data)

    # POSTGRESQL — สร้าง connection URL --------------------------------
    @computed_field
    @cached_property
    def POSTGRESQL_ASYNC_DATABASE_URL(self) -> URL:
        """DSN สำหรับ async driver (asyncpg)"""
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
        """DSN สำหรับ sync driver (psycopg2) — ใช้กับ Alembic"""
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_HOST,
            port=int(self.POSTGRESQL_PORT),
            database=self.POSTGRESQL_DATABASE,
        )

    # REDIS ------------------------------------------------------------
    @computed_field
    @cached_property
    def REDIS_URL(self) -> str:
        """Redis DSN (ใช้ rediss:// ถ้าเปิด SSL)"""
        scheme = "rediss" if self.REDIS_SSL else "redis"
        return (
            f"{scheme}://{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}"
            f"@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )

    @computed_field
    @cached_property
    def REDIS_NAMESPACE(self) -> str:
        """
        Namespace ของ cache key ทุกตัว

        การ bump REDIS_CACHE_VERSION จะทำให้ generation เก่าเข้าถึงไม่ได้
        และ entry เก่าจะหมดอายุเองตาม TTL — ใช้แทนการ flush ทั้ง cache
        เมื่อมีการเปลี่ยน format ของ payload
        """
        return f"{self.REDIS_KEY_PREFIX}:v{self.REDIS_CACHE_VERSION}"

    # ==================================================================
    # SECURITY PATH RULES — allow list ของแต่ละ role
    # ==================================================================
    #
    # หมายเหตุ:
    # - path ที่นี่เช็คคู่กับ HTTP method
    # - ตัว match ใน security.py normalize trailing slash ให้แล้ว
    #   จึงไม่ต้องใส่ทั้ง "/path" และ "/path/" ซ้ำ
    # - ถ้าเพิ่ม endpoint สาธารณะใหม่ (เช่น sign-up) ต้องเพิ่มใน NO_AUTH_PATHS
    #   ไม่เช่นนั้นจะโดนบล็อกด้วย 403
    #

    @computed_field
    @cached_property
    def SECURITY_NO_AUTH_PATHS(self) -> tuple[PathRule, ...]:
        """
        Path ที่ไม่ต้อง authenticate — ใช้โดย `no_authentication`
        ถ้า path ไม่อยู่ในลิสต์นี้ dependency จะ raise 403 ทันที
        """
        return (
            # AUTHENTICATION — สมัคร / เข้าสู่ระบบ / ออกจากระบบ
            _path_rule("/api/v1/authentication/sign-up", "POST"),  # ← เพิ่มเข้ามาใหม่
            _path_rule("/api/v1/authentication/login", "POST"),
            _path_rule("/api/v1/authentication/logout", "DELETE"),
            # EXAMPLE
            _path_rule("/api/v1/example", "POST"),
            # HEALTH — health check
            _path_rule("/health", "GET"),
            # USER — สมัคร user (ถ้ามี endpoint แยกจาก sign-up)
            _path_rule("/api/v1/user", "POST"),
            # WEBSOCKET — handshake ครั้งแรก (ตรวจ token ใน dependency เอง)
            _path_rule("/api/v1/websocket/connect", "GET"),
        )

    @computed_field
    @cached_property
    def SECURITY_USER_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:
        """
        Path ที่ user role ทั่วไปเข้าถึงได้
        เริ่มจาก NO_AUTH_PATHS แล้วเพิ่ม endpoint ที่ต้อง login
        """
        return (
            *self.SECURITY_NO_AUTH_PATHS,
            # AUTHENTICATION — refresh token
            _path_rule("/api/v1/authentication/refresh", "PATCH"),
            # USER — ดูข้อมูลตัวเอง
            _path_rule("/api/v1/user/me", "GET"),
            # NOTIFICATION
            _path_rule("/api/v1/notification", "GET"),
            _path_rule("/api/v1/notification/{id}", "PATCH"),
        )

    @computed_field
    @cached_property
    def SECURITY_MANAGER_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:
        """
        Path ที่ manager เข้าถึงได้
        เริ่มจาก USER_ALLOWED_PATHS แล้วเพิ่มสิทธิ์ของ manager
        """
        return (
            *self.SECURITY_USER_ALLOWED_PATHS,
            # KNOWLEDGE — จัดการ knowledge base
            _path_rule("/api/v1/knowledge", "POST"),
            _path_rule("/api/v1/knowledge", "GET"),
            _path_rule("/api/v1/knowledge/{id}", "PATCH"),
            _path_rule("/api/v1/knowledge/{id}", "DELETE"),
        )

    @computed_field
    @cached_property
    def SECURITY_ADMIN_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:
        """
        Path ที่ admin เข้าถึงได้
        เริ่มจาก MANAGER_ALLOWED_PATHS แล้วเพิ่มสิทธิ์ของ admin
        """
        return (
            *self.SECURITY_MANAGER_ALLOWED_PATHS,
            # HEALTH — ดู alembic version
            _path_rule("/api/v1/alembic-version", "GET"),
            # KEY — จัดการ API key
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
        """
        Path ที่ API key เข้าถึงได้
        ตอนนี้ปิดไว้ทั้งหมด — ถ้าจะเปิด endpoint ไหนให้ API key ใช้ ค่อยเพิ่ม
        """
        return ()

    # ==================================================================
    # JWT KEY GENERATION — สร้าง key อัตโนมัติถ้ายังไม่มี
    # ==================================================================
    def generate_authentication_keys(self) -> None:
        """
        Generate Ed25519 (signing) และ X25519 (encryption) key pairs
        ถ้าเปิด JWT_AUTO_GENERATE_KEYS และไฟล์ยังไม่มี

        ใช้เฉพาะตอน dev — production ควรจัดการ key เอง
        """
        if not self.JWT_AUTO_GENERATE_KEYS:
            return

        keys_dir = Path(self.JWT_KEYS_DIR)
        keys_dir.mkdir(parents=True, exist_ok=True)

        signing_private = Path(self.JWT_SIGNING_PRIVATE_KEY_PATH)
        signing_public = Path(self.JWT_SIGNING_PUBLIC_KEY_PATH)
        encryption_private = Path(self.JWT_ENCRYPTION_PRIVATE_KEY_PATH)
        encryption_public = Path(self.JWT_ENCRYPTION_PUBLIC_KEY_PATH)

        # สร้าง signing key (Ed25519) ถ้ายังไม่มี
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

        # สร้าง encryption key (X25519) ถ้ายังไม่มี
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
    # INIT — post-processing หลังโหลดค่าจาก env
    # ==================================================================
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # สร้าง key อัตโนมัติ (ถ้าเปิด option)
        self.generate_authentication_keys()

        # รองรับกรณี POSTGRESQL_HOST มาในรูปแบบ "host:port" (เช่นจาก Heroku)
        if ":" in self.POSTGRESQL_HOST:
            host_parts = self.POSTGRESQL_HOST.split(":")
            self.POSTGRESQL_HOST = host_parts[0]
            if len(host_parts) > 1 and not self.POSTGRESQL_PORT:
                self.POSTGRESQL_PORT = host_parts[1]

        # ตัด quote ที่อาจหลงเหลือใน string field
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

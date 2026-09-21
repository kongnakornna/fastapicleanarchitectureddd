from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.exception_handler import (
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)
from app.core.middleware import (
    DeviceIdMiddleware,
    LogRequestMiddleware,
    ResponseFormattingMiddleware,
)
from app.core.resources import lifespan
from app.core.settings import settings
from app.modules.authentication.presentation.routers import (
    router as authentication_router,
)
from app.modules.example.presentation.routers import router as example_router
from app.modules.health.presentation.routers import router as health_router
from app.modules.key.presentation.routers import router as key_router
from app.modules.knowledge.presentation.routers import router as knowledge_router
from app.modules.notification.presentation.routers import (
    router as notification_router,
)
from app.modules.shared.domain.enums import ApplicationEnvironment
from app.modules.user.presentation.routers import router as user_router
from app.modules.websocket.presentation.routers import router as websocket_router
from app.modules.money.presentation.routers import router as money_router

# ═════════════════════════════════════════════════════════════════
# APPLICATION
# ═════════════════════════════════════════════════════════════════
app = FastAPI(
    title=settings.APPLICATION_TITLE,
    debug=settings.APPLICATION_ENVIRONMENT_DEBUG,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
    },
    lifespan=lifespan,
)


# ═════════════════════════════════════════════════════════════════
# CORS — ต้อง add เป็น middleware ตัวสุดท้าย → รันก่อนสุด (outermost)
# ═════════════════════════════════════════════════════════════════
# TH: รวบรวม origins จาก settings + เพิ่ม dev origins อัตโนมัติ
# EN: merge origins from settings + auto-add dev origins
def _build_cors_origins() -> list[str]:
    origins: list[str] = [str(o) for o in settings.SECURITY_ALLOW_ORIGINS]

    # TH: ใน dev mode เพิ่ม origins ที่ใช้บ่อย (localhost, 127.0.0.1)
    # EN: in dev mode add common origins (localhost, 127.0.0.1)
    if settings.APPLICATION_ENVIRONMENT_DEBUG:
        dev_origins = [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
        for origin in dev_origins:
            if origin not in origins:
                origins.append(origin)

    return origins


_cors_origins = _build_cors_origins()

_cors_methods = (
    [str(m) for m in settings.SECURITY_ALLOW_METHODS]
    if settings.SECURITY_ALLOW_METHODS
    else ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)

_cors_headers = (
    [str(h) for h in settings.SECURITY_ALLOW_HEADERS]
    if settings.SECURITY_ALLOW_HEADERS
    else ["*"]
)


# ═════════════════════════════════════════════════════════════════
# EXCEPTION HANDLERS
# ═════════════════════════════════════════════════════════════════
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)


# ═════════════════════════════════════════════════════════════════
# MIDDLEWARES
# ═════════════════════════════════════════════════════════════════
# ⚠️ ลำดับสำคัญ: FastAPI/Starlette add หลังสุด = รันก่อนสุด
#    1. DeviceIdMiddleware       ← รันที่ 4 (innermost)
#    2. LogRequestMiddleware     ← รันที่ 3
#    3. ResponseFormattingMiddleware ← รันที่ 2
#    4. CORSMiddleware           ← รันที่ 1 (outermost) ← ← ← ต้อง add หลังสุด
#
# EN: order matters — last added runs first (outermost).
#     CORS must be OUTERMOST so it handles OPTIONS preflight before other MWs.

app.add_middleware(DeviceIdMiddleware)
app.add_middleware(LogRequestMiddleware)
app.add_middleware(ResponseFormattingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=_cors_methods,
    allow_headers=_cors_headers,
    expose_headers=["x-request-id", "x-processed-time"],
    max_age=600,  # TH: cache preflight 10 นาที | EN: cache preflight 10 min
)


# ═════════════════════════════════════════════════════════════════
# ROUTERS
# ═════════════════════════════════════════════════════════════════
routers = [
    authentication_router,
    example_router,
    health_router,
    key_router,
    knowledge_router,
    notification_router,
    user_router,
    websocket_router,
    money_router,  # TH: เพิ่ม money ที่หายไป | EN: add missing money router
]

for router in routers:
    app.include_router(router)


# ═════════════════════════════════════════════════════════════════
# PRODUCTION SETTINGS
# ═════════════════════════════════════════════════════════════════
if settings.APPLICATION_ENVIRONMENT == ApplicationEnvironment.PRODUCTION.value:
    app.openapi_url = None
    app.docs_url = None
    app.redoc_url = None


# ═════════════════════════════════════════════════════════════════
# CUSTOM OPENAPI
# ═════════════════════════════════════════════════════════════════
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APPLICATION_TITLE,
        summary=settings.APPLICATION_SUMMARY,
        description=settings.APPLICATION_DESCRIPTION,
        version=settings.APPLICATION_VERSION,
        tags=[
            {"name": "Authentication", "description": "Endpoints for user authentication and authorization."},
            {"name": "Example", "description": "Example module for demonstrating application features."},
            {"name": "Health", "description": "Endpoints for monitoring the health of the application."},
            {"name": "Key", "description": "Endpoints for managing API keys."},
            {"name": "Knowledge", "description": "Endpoints for managing knowledge base resources."},
            {"name": "Notification", "description": "Endpoints for managing user notifications."},
            {"name": "User", "description": "Endpoints for managing user resources."},
            {"name": "WebSocket", "description": "WebSocket endpoints for real-time notifications."},
            {"name": "Money", "description": "Endpoints for money / currency operations."},
        ],
        contact={
            "name": settings.APPLICATION_CONTACT_NAME,
            "url": settings.APPLICATION_CONTACT_URL,
            "email": settings.APPLICATION_CONTACT_EMAIL,
            "phone": settings.APPLICATION_CONTACT_PHONE,
        },
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        settings.AUTH_BEARER_TOKEN_SCHEME_NAME: {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        settings.AUTH_API_KEY_SCHEME_NAME: {
            "type": "apiKey",
            "in": "header",
            "name": settings.AUTH_API_KEY_NAME,
            "description": "API Key necessary to access the API endpoints.",
        },
    }

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi

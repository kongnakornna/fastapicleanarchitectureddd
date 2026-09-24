from __future__ import annotations

from contextlib import asynccontextmanager

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
from app.core.resources import lifespan as _base_lifespan
from app.core.settings import settings
from app.modules.authentication.presentation.routers import (
    router as authentication_router,
)
from app.modules.example.presentation.routers import router as example_router
from app.modules.health.presentation.routers import router as health_router
from app.modules.iot.presentation.routers import router as iot_router
from app.modules.llm.presentation.router import router as llm_router
from app.modules.llm.presentation.swagger import register_llm_openapi

from app.modules.key.presentation.routers import router as key_router
from app.modules.knowledge.presentation.routers import router as knowledge_router
from app.modules.money.presentation.routers import router as money_router
from app.modules.notification.presentation.routers import (
    router as notification_router,
)
from app.modules.pdpa.presentation.routers import router as pdpa_router
from app.modules.shared.domain.enums import ApplicationEnvironment
from app.modules.user.presentation.routers import router as user_router
from app.modules.websocket.presentation.routers import router as websocket_router
from app.modules.vector_db.presentation.router import router as vdb_router
from app.modules.vector_db.presentation.swagger import register_vector_db_openapi
from app.modules.tool_calling.presentation.router import router as tools_router
from app.modules.tool_calling.presentation.swagger import register_tool_calling_openapi
from app.modules.structured_outputs.presentation.router import router as so_router
from app.modules.structured_outputs.presentation.swagger import register_structured_outputs_openapi
from app.modules.hybrid_search.presentation.router import router as hs_router
from app.modules.hybrid_search.presentation.swagger import register_hybrid_search_openapi
from app.modules.langchain.presentation.router import router as lc_router
from app.modules.langchain.presentation.swagger import register_langchain_openapi
from app.modules.llamaindex.presentation.router import router as li_router
from app.modules.llamaindex.presentation.swagger import register_llamaindex_openapi
from app.modules.rag.presentation.router import router as rag_router
from app.modules.rag.presentation.swagger import register_rag_openapi
from app.modules.ai_evaluation.presentation.router import router as eval_router
from app.modules.ai_evaluation.presentation.swagger import register_ai_evaluation_openapi


# ═════════════════════════════════════════════════════════════════
#  LIFESPAN WRAPPER — adds iot scheduler + alerting to base lifespan
# ═════════════════════════════════════════════════════════════════
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """
    TH: wrapper รอบ lifespan ของ resources.py — เพิ่ม iot scheduler + alerting
    EN: wraps resources.lifespan — adds iot scheduler + alerting init
    """
    import logging

    logger = logging.getLogger(__name__)

    # ─── Part 11: Start iot scheduler ────────────────
    try:
        # ═══ ใช้ session factory จริงของโปรเจกต์ (PGAsyncSession) ═══
        from app.core.database import PGAsyncSession
        from app.modules.iot.infrastructure.scheduler import (
            IotScheduler,
            set_scheduler_instance,
        )

        _sched = IotScheduler(session_factory=PGAsyncSession)
        _sched.start()
        set_scheduler_instance(_sched)
        app.state.iot_scheduler = _sched
        logger.info("✅ iot scheduler started (session_factory=PGAsyncSession)")
    except Exception as exc:
        logger.warning(f"⚠️ iot scheduler start failed: {exc}")

    # ─── Part 10: Init alerting channels ─────────────
    try:
        from app.modules.iot.infrastructure.alerting.dispatcher import (
            alert_dispatcher,
        )
        status = alert_dispatcher.get_channels_status()
        logger.info(f"✅ alerting channels: {list(status.keys())}")
    except Exception as exc:
        logger.warning(f"⚠️ alerting init failed: {exc}")

    # ─── Run original lifespan ───────────────────────
    try:
        async with _base_lifespan(app) as _state:
            yield _state
    finally:
        # ─── Part 11: Stop iot scheduler ─────────────
        try:
            if hasattr(app.state, "iot_scheduler"):
                app.state.iot_scheduler.stop()
                logger.info("✅ iot scheduler stopped")
        except Exception as exc:
            logger.warning(f"⚠️ iot scheduler stop failed: {exc}")


# ═════════════════════════════════════════════════════════════════
#  APPLICATION
# ═════════════════════════════════════════════════════════════════
app = FastAPI(
    title=settings.APPLICATION_TITLE,
    debug=settings.APPLICATION_ENVIRONMENT_DEBUG,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
    },
    lifespan=app_lifespan,  # ← ใช้ wrapper ที่ integrate Parts 8-14
)

app.include_router(li_router, prefix='/api/v1')
register_llamaindex_openapi(app)

app.include_router(lc_router, prefix='/api/v1')
register_langchain_openapi(app)

app.include_router(hs_router, prefix='/api/v1')
register_hybrid_search_openapi(app)

app.include_router(so_router, prefix='/api/v1')
register_structured_outputs_openapi(app)



# Register LLM OpenAPI metadata
register_llm_openapi(app)
# ═════════════════════════════════════════════════════════════════
#  CORS — ต้อง add เป็น middleware ตัวสุดท้าย → รันก่อนสุด (outermost)
# ═════════════════════════════════════════════════════════════════
def _build_cors_origins() -> list[str]:
    origins: list[str] = [str(o) for o in settings.SECURITY_ALLOW_ORIGINS]

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
#  EXCEPTION HANDLERS
# ═════════════════════════════════════════════════════════════════
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)


# ═════════════════════════════════════════════════════════════════
#  MIDDLEWARES
# ═════════════════════════════════════════════════════════════════
# ⚠️ ลำดับสำคัญ: FastAPI/Starlette add หลังสุด = รันก่อนสุด (outermost)
#
# Request flow (outermost → innermost):
#   1. CORSMiddleware
#   2. ResponseFormattingMiddleware
#   3. LogRequestMiddleware
#   4. DeviceIdMiddleware
#   5. TenantMiddleware           ← innermost (ก่อนเข้า router)
#   6. router handler
#
# EN: order matters — last added = outermost.

# ─── Part 12: TenantMiddleware (innermost) ───────
try:
    from app.middleware.tenant import TenantMiddleware
    app.add_middleware(TenantMiddleware)
except Exception as exc:
    import logging
    logging.getLogger(__name__).warning(
        f"⚠️ TenantMiddleware failed to load: {exc}"
    )

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
    max_age=600,
)


# ═════════════════════════════════════════════════════════════════
#  ROUTERS
# ═════════════════════════════════════════════════════════════════
routers = [
    authentication_router,
    example_router,
    health_router,
    iot_router,
    llm_router,    # llm module (Layer 5-Intel)    # iot module (Layer 6-Monitor) — includes Parts 8-14 endpoints
    key_router,
    knowledge_router,
    notification_router,
    user_router,
    websocket_router,
    money_router,
    pdpa_router,
    vdb_router,  # vector_db module
    tools_router,  # tool_calling module (Layer 5-Intel)
    rag_router,  # rag module
    eval_router,  # ai_evaluation module

]

for router in routers:
    app.include_router(router)


# ═════════════════════════════════════════════════════════════════
#  PRODUCTION SETTINGS
# ═════════════════════════════════════════════════════════════════
if settings.APPLICATION_ENVIRONMENT == ApplicationEnvironment.PRODUCTION.value:
    app.openapi_url = None
    app.docs_url = None
    app.redoc_url = None


# ═════════════════════════════════════════════════════════════════
#  CUSTOM OPENAPI
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
            {"name": "Tools", "description": "Tool Calling — registry + invoke + permissions."},
            {"name": "LLM", "description": "LLM Module — Unified LLM Gateway (OpenAI / Anthropic / Local)."},
            {"name": "iot", "description": "iot Module — Real-time Sensor & Alarm Monitoring (MQTT / InfluxDB / WebSocket). Includes batch ops, alerting, scheduler, idempotency."},
            {"name": "Key", "description": "Endpoints for managing API keys."},
            {"name": "Knowledge", "description": "Endpoints for managing knowledge base resources."},
            {"name": "Notification", "description": "Endpoints for managing user notifications."},
            {"name": "User", "description": "Endpoints for managing user resources."},
            {"name": "WebSocket", "description": "WebSocket endpoints for real-time notifications."},
            {"name": "Money", "description": "Endpoints for money / currency operations."},
            {"name": "PDPA", "description": "PDPA endpoints — Consent / DSAR / Privacy Policy / Cookie Consent."},
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

# Register Tool Calling OpenAPI metadata
register_tool_calling_openapi(app)

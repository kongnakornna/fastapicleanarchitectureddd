from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exception_handler import (
    http_exception_handler,
    internal_exception_handler,
    validation_exception_handler,
)
from app.core.middleware import (
    DeviceIdMiddleware,
    RateLimitMiddleware,
    ResponseFormattingMiddleware,
    log_request_middleware,
)
from app.core.resources import lifespan
from app.core.settings import settings
from app.modules.authentication.presentation.routers import (
    router as authentication_router,
)
from app.modules.batch.presentation.router import router as batch_router
from app.modules.customer.presentation.router import router as customer_router
from app.modules.dashboard.presentation.router import router as dashboard_router
from app.modules.document.presentation.router import router as document_router
from app.modules.email.presentation.router import router as email_router
from app.modules.example.presentation.routers import router as example_router
from app.modules.health.presentation.routers import router as health_router
from app.modules.i18n.presentation.router import router as i18n_router
from app.modules.iot.presentation.router import router as iot_router
from app.modules.items.presentation.router import router as items_router
from app.modules.payment.presentation.router import router as payment_router
from app.modules.purchaseorder.presentation.router import (
    router as purchaseorder_router,
)
from app.modules.quotation.presentation.router import router as quotation_router
from app.modules.report.presentation.router import router as report_router
from app.modules.shared.application.enums import ApplicationEnvironment
from app.modules.user.presentation.routers import router as user_router
from app.modules.wos.presentation.router import router as wos_router

# APPLICATION
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


# STATIC FILES
# app.mount("/static", StaticFiles(directory="app/static"), name="static")


# EXCEPTION HANDLERS
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)


# MIDDLEWARES
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.SECURITY_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=[str(method) for method in settings.SECURITY_ALLOW_METHODS],
    allow_headers=[str(header) for header in settings.SECURITY_ALLOW_HEADERS],
)
app.add_middleware(ResponseFormattingMiddleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)
app.add_middleware(DeviceIdMiddleware)
app.add_middleware(RateLimitMiddleware)


# ROUTERS
routers = [
    authentication_router,
    batch_router,
    customer_router,
    dashboard_router,
    document_router,
    email_router,
    example_router,
    health_router,
    i18n_router,
    items_router,
    payment_router,
    purchaseorder_router,
    quotation_router,
    report_router,
    user_router,
    iot_router,
    wos_router,
]


for router in routers:
    app.include_router(router)


# PRODUCTION SETTINGS
if ApplicationEnvironment.PRODUCTION.value == settings.APPLICATION_ENVIRONMENT:
    app.openapi_url = None
    app.docs_url = None
    app.redoc_url = None


# CUSTOM OPENAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APPLICATION_TITLE,
        summary=settings.APPLICATION_SUMMARY,
        description=settings.APPLICATION_DESCRIPTION,
        version=settings.APPLICATION_VERSION,
        tags=[
            {
                "name": "Authentication",
                "description": "Endpoints for user authentication and authorization.",
            },
            {
                "name": "Batch",
                "description": "Batch job management endpoints.",
            },
            {
                "name": "Customer",
                "description": "Customer and car management endpoints.",
            },
            {
                "name": "Dashboard",
                "description": "Dashboard statistics endpoints.",
            },
            {
                "name": "Document",
                "description": "Document management endpoints.",
            },
            {
                "name": "Email",
                "description": "Email sending and configuration endpoints.",
            },
            {
                "name": "Example",
                "description": "Example module for demonstrating application features.",
            },
            {
                "name": "Health",
                "description": "Endpoints for monitoring the health of the application.",
            },
            {
                "name": "I18n",
                "description": "Internationalization translation endpoints.",
            },
            {
                "name": "Item",
                "description": "Item management endpoints.",
            },
            {
                "name": "Payment",
                "description": "Payment and receipt management endpoints.",
            },
            {
                "name": "PurchaseOrder",
                "description": "Purchase order lifecycle management endpoints.",
            },
            {
                "name": "Quotation",
                "description": "Quotation management endpoints.",
            },
            {
                "name": "Report",
                "description": "PDF report generation endpoints.",
            },
            {
                "name": "User",
                "description": "Endpoints for managing user resources.",
            },
            {
                "name": "IoT MQTT3",
                "description": "IoT device monitoring and control endpoints.",
            },
            {
                "name": "WOS",
                "description": "Web Order System endpoints.",
            },
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
            "description": "JWT access token. Paste the token from login response. Can also be set via HttpOnly cookie.",
        },
        settings.AUTH_API_KEY_SCHEME_NAME: {
            "type": "apiKey",
            "in": "header",
            "name": settings.AUTH_API_KEY_HEADER,
            "description": "API key for service-to-service authentication. Uses the default admin user.",
        },
    }

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi

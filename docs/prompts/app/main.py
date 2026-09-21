# app/main.py - FastAPI entrypoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger


def create_app() -> FastAPI:
    """Application factory."""
    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- register module routers ---
    # from app.modules.health.presentation.routers import router as health_router
    # app.include_router(health_router)

    @app.get("/", tags=["Root"])
    async def root():
        return {"service": settings.app_name, "status": "ok"}

    return app


app = create_app()
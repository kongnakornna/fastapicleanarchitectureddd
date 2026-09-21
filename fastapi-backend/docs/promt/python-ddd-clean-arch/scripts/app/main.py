"""TH: FastAPI entry | EN: FastAPI entry"""
from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.db import dispose_engine
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.routes import router

log = structlog.get_logger()
_settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """TH: startup/shutdown | EN: startup/shutdown"""
    configure_logging(_settings.log_level, json=_settings.log_json)
    log.info("app.startup", env=_settings.app_env)
    try:
        yield
    finally:
        await dispose_engine()
        log.info("app.shutdown")


def create_app() -> FastAPI:
    """TH: app factory | EN: app factory"""
    app = FastAPI(
        title=_settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
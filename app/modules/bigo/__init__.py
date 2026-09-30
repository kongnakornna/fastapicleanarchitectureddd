"""bigo module — Big-O Monitoring & Resource Optimization"""
from .infrastructure.pipeline import BigOPipeline
from .presentation.management_router import admin_router as bigo_admin_router
from .presentation.router import router as bigo_router
from .presentation.ws_router import ws_router as bigo_ws_router

__all__ = [
    "bigo_router", "bigo_admin_router", "bigo_ws_router",
    "BigOPipeline",
]

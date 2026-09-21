"""
app/routes.py
TH: รวม router ทั้งหมด
EN: Aggregate all routers
"""
from fastapi import APIRouter

from app.core.health import router as health_router
from app.modules.inventory.presentation.routers import router as inventory_router

api_router = APIRouter(prefix="/api/v1")

# ─── Layer 3: Goods ───────────────────────────
api_router.include_router(inventory_router)

# ─── Root ─────────────────────────────────────
router = APIRouter()
router.include_router(api_router)
router.include_router(health_router)
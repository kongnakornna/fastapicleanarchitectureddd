# Register router for inventory

## 1. app/routes.py

เพิ่ม import ตาม layer 3:

    from app.modules.inventory.presentation.routers import router as inventory_router

จากนั้น include:

    api_router.include_router(inventory_router)

## 2. migrations/env.py

    from app.modules.inventory.infrastructure.models import InventoryModel  # noqa: F401

## 3. Verify

    uvicorn app.main:app --reload

    # open
    http://localhost:8000/docs
    http://localhost:8000/openapi.json

    # smoke
    curl -X GET http://localhost:8000/api/v1/inventory/
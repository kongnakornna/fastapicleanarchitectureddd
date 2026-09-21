# Register model in `migrations/env.py`

> Generator ได้ patch `migrations/env.py` ให้อัตโนมัติแล้ว
> (idempotent — รันซ้ำจะไม่เพิ่มบรรทัดซ้ำ)

## บรรทัดที่ถูกเพิ่ม

    # --- module inventory (auto-registered) ---
    from app.modules.inventory.infrastructure.models import InventoryModel  # noqa: F401

TH: register model เพื่อให้ Alembic/SQLAlchemy metadata รู้จัก
EN: register model so Alembic/SQLAlchemy metadata knows it

## ถ้าต้องการเพิ่มเอง (กรณีไฟล์ env.py ไม่มีตอน generate)

เพิ่มที่ด้านบนของ `migrations/env.py`:

    from app.modules.inventory.infrastructure.models import InventoryModel  # noqa: F401

และถ้า `env.py` ใช้ `_ = [...]` list ให้เพิ่ม `InventoryModel` เข้าไปด้วย
มิฉะนั้น autogenerate จะ emit `drop_table` ให้ตารางที่ยัง live อยู่

## Verify

    make migration m="create_inventory_model"
    make migrate

- [ ] migration ที่ generate **ไม่มี** `drop_table(...)` ที่ไม่คาดคิด
- [ ] ตาราง `tenant_inv.inventorys` ปรากฏใน migration
- [ ] RLS policy `p_inventory_tenant` ปรากฏใน migration
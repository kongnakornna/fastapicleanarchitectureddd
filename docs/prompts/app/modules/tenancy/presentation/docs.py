"""tenancy presentation docs."""
router_docs = {
    "tags": ["Tenancy"],
    "description": "Tenant management — จัดการผู้เช่า (Layer 1)",
}

create_docs = {"summary": "Create tenant — สร้าง tenant", "status_code": 201}
get_docs = {"summary": "Get tenant — ดึงข้อมูล tenant"}
list_docs = {"summary": "List tenants — แสดงรายการ"}
suspend_docs = {"summary": "Suspend tenant — ระงับ tenant"}
upgrade_docs = {"summary": "Upgrade plan — อัปเกรดแผน"}
from app.modules.wos.domain.entities.order import WosOrder


def _make_wos_order(**overrides):
    defaults = {
        "order_number": "WO-2025-001",
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "customer_phone": "0812345678",
        "items": [{"sku": "A001", "qty": 2}],
        "total_amount": 599.0,
        "status": "pending",
        "notes": "Rush order",
    }
    defaults.update(overrides)
    return WosOrder(**defaults)


# ============================================================
# WOS ORDER
# ============================================================


class TestWosOrder:
    def test_create_order(self):
        order = _make_wos_order()
        assert order.order_number == "WO-2025-001"
        assert order.customer_name == "John Doe"
        assert order.total_amount == 599.0
        assert order.status == "pending"

    def test_order_tablename(self):
        assert WosOrder.__tablename__ == "m_wos_order"

    def test_order_nullable_fields(self):
        order = _make_wos_order(customer_phone=None, items=None, notes=None)
        assert order.customer_phone is None
        assert order.items is None
        assert order.notes is None

    def test_order_defaults(self):
        order = _make_wos_order()
        assert order.status == "pending"

    def test_order_with_overrides(self):
        order = _make_wos_order(
            order_number="WO-2025-999",
            status="completed",
            total_amount=1200.0,
        )
        assert order.order_number == "WO-2025-999"
        assert order.status == "completed"
        assert order.total_amount == 1200.0

from uuid import uuid4

from app.modules.purchaseorder.domain.entities.purchase_order_detail import (
    PurchaseOrderDetail,
)
from app.modules.purchaseorder.domain.entities.purchase_order_header import (
    PurchaseOrderHeader,
)
from app.modules.purchaseorder.domain.entities.purchase_order_status_history import (
    PurchaseOrderStatusHistory,
)


def _make_purchase_order_header(**overrides):
    defaults = {
        "po_no": "PO-001",
        "quotation_id": None,
        "job_id": None,
        "supplier_id": None,
        "po_date": None,
        "expected_delivery_date": None,
        "actual_delivery_date": None,
        "status": "draft",
        "subtotal": 0,
        "tax_rate": 0,
        "tax_amount": 0,
        "discount_type": None,
        "discount_value": 0,
        "total": 0,
        "currency": "THB",
        "exchange_rate": 1,
        "shipping_cost": 0,
        "payment_terms": None,
        "delivery_address": None,
        "notes": None,
        "terms_and_conditions": None,
        "sent_at": None,
        "confirmed_at": None,
        "received_by": None,
    }
    defaults.update(overrides)
    return PurchaseOrderHeader(**defaults)


def _make_purchase_order_detail(**overrides):
    defaults = {
        "po_header_id": uuid4(),
        "part_id": None,
        "quantity_ordered": 10,
        "quantity_received": 0,
        "unit_price": 100.0,
        "total_price": 1000.0,
        "discount": 0.0,
        "net_price": 1000.0,
        "note": None,
    }
    defaults.update(overrides)
    return PurchaseOrderDetail(**defaults)


def _make_purchase_order_status_history(**overrides):
    defaults = {
        "po_header_id": uuid4(),
        "from_status": "draft",
        "to_status": "sent",
        "changed_by": None,
        "changed_at": None,
        "reason": None,
    }
    defaults.update(overrides)
    return PurchaseOrderStatusHistory(**defaults)


# ============================================================
# PURCHASE ORDER HEADER
# ============================================================


class TestPurchaseOrderHeader:
    def test_create_header(self):
        header = _make_purchase_order_header()
        assert header.po_no == "PO-001"
        assert header.status == "draft"
        assert header.currency == "THB"

    def test_header_tablename(self):
        assert PurchaseOrderHeader.__tablename__ == "m_purchase_order_header"

    def test_header_defaults(self):
        header = _make_purchase_order_header(subtotal=0, total=0, shipping_cost=0)
        assert header.subtotal == 0
        assert header.total == 0
        assert header.tax_rate == 0
        assert header.tax_amount == 0
        assert header.discount_value == 0
        assert header.shipping_cost == 0
        assert header.exchange_rate == 1

    def test_header_with_overrides(self):
        header = _make_purchase_order_header(
            po_no="PO-002", status="confirmed", total=5000.0
        )
        assert header.po_no == "PO-002"
        assert header.status == "confirmed"
        assert header.total == 5000.0


# ============================================================
# PURCHASE ORDER DETAIL
# ============================================================


class TestPurchaseOrderDetail:
    def test_create_detail(self):
        detail = _make_purchase_order_detail()
        assert detail.quantity_ordered == 10
        assert detail.unit_price == 100.0
        assert detail.total_price == 1000.0
        assert detail.net_price == 1000.0

    def test_detail_tablename(self):
        assert PurchaseOrderDetail.__tablename__ == "m_purchase_order_detail"

    def test_detail_defaults(self):
        detail = _make_purchase_order_detail(
            quantity_ordered=0, unit_price=0, total_price=0, discount=0, net_price=0
        )
        assert detail.quantity_ordered == 0
        assert detail.quantity_received == 0
        assert detail.unit_price == 0
        assert detail.total_price == 0
        assert detail.discount == 0
        assert detail.net_price == 0

    def test_detail_with_overrides(self):
        detail = _make_purchase_order_detail(quantity_ordered=20, unit_price=250.0)
        assert detail.quantity_ordered == 20
        assert detail.unit_price == 250.0


# ============================================================
# PURCHASE ORDER STATUS HISTORY
# ============================================================


class TestPurchaseOrderStatusHistory:
    def test_create_status_history(self):
        history = _make_purchase_order_status_history()
        assert history.from_status == "draft"
        assert history.to_status == "sent"
        assert history.reason is None

    def test_status_history_tablename(self):
        assert PurchaseOrderStatusHistory.__tablename__ == "m_purchase_order_status_history"

    def test_status_history_with_reason(self):
        history = _make_purchase_order_status_history(reason="Supplier confirmed")
        assert history.reason == "Supplier confirmed"

    def test_status_history_with_overrides(self):
        history = _make_purchase_order_status_history(
            from_status="sent", to_status="received"
        )
        assert history.from_status == "sent"
        assert history.to_status == "received"

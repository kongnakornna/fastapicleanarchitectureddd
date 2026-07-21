from app.modules.quotation.domain.entities.quotation import Quotation


def _make_quotation(**overrides):
    defaults = {
        "quotation_no": "QT-001",
        "job_id": None,
        "customer_id": None,
        "quotation_date": None,
        "expiry_date": None,
        "status": "draft",
        "subtotal": 0,
        "tax_rate": 0,
        "tax_amount": 0,
        "discount_type": None,
        "discount_value": 0,
        "total": 0,
        "amount_in_words_th": None,
        "amount_in_words_en": None,
        "currency": "THB",
        "exchange_rate": 1,
        "notes": None,
        "terms_and_conditions": None,
        "approved_by": None,
        "approved_at": None,
        "rejected_reason": None,
        "converted_to_po": False,
    }
    defaults.update(overrides)
    return Quotation(**defaults)


# ============================================================
# QUOTATION
# ============================================================


class TestQuotation:
    def test_create_quotation(self):
        quotation = _make_quotation()
        assert quotation.quotation_no == "QT-001"
        assert quotation.status == "draft"
        assert quotation.currency == "THB"
        assert quotation.converted_to_po is False

    def test_quotation_tablename(self):
        assert Quotation.__tablename__ == "m_quotation"

    def test_quotation_defaults(self):
        quotation = _make_quotation(subtotal=0, total=0)
        assert quotation.subtotal == 0
        assert quotation.total == 0
        assert quotation.tax_rate == 0
        assert quotation.tax_amount == 0
        assert quotation.discount_value == 0
        assert quotation.exchange_rate == 1
        assert quotation.converted_to_po is False

    def test_quotation_with_overrides(self):
        quotation = _make_quotation(
            quotation_no="QT-002", status="approved", total=10000.0
        )
        assert quotation.quotation_no == "QT-002"
        assert quotation.status == "approved"
        assert quotation.total == 10000.0

    def test_quotation_converted_to_po(self):
        quotation = _make_quotation(converted_to_po=True)
        assert quotation.converted_to_po is True

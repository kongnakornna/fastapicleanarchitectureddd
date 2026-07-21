from uuid import uuid4

from app.modules.payment.domain.entities.payment import Payment
from app.modules.payment.domain.entities.payment_history import PaymentHistory
from app.modules.payment.domain.entities.receipt import Receipt


def _make_payment(**overrides):
    defaults = {
        "payment_no": "PAY-001",
        "invoice_id": None,
        "job_id": None,
        "customer_id": None,
        "payment_date": None,
        "payment_method_id": None,
        "amount": 1500.0,
        "amount_received": 1500.0,
        "change_amount": 0.0,
        "currency": "THB",
        "exchange_rate": 1,
        "status": "pending",
        "reference_number": None,
        "bank_name": None,
        "cheque_number": None,
        "cheque_bank": None,
        "cheque_date": None,
        "notes": None,
        "received_by": None,
        "approved_by": None,
        "approved_at": None,
        "refunded_amount": 0.0,
        "refunded_at": None,
    }
    defaults.update(overrides)
    return Payment(**defaults)


def _make_receipt(**overrides):
    defaults = {
        "receipt_no": "RCT-001",
        "payment_id": uuid4(),
        "invoice_id": None,
        "customer_id": None,
        "receipt_date": None,
        "receipt_type": "standard",
        "amount": 1500.0,
        "amount_in_words_th": None,
        "amount_in_words_en": None,
        "currency": "THB",
        "status": "active",
        "notes": None,
        "issued_by": None,
    }
    defaults.update(overrides)
    return Receipt(**defaults)


def _make_payment_history(**overrides):
    defaults = {
        "payment_id": uuid4(),
        "from_status": "pending",
        "to_status": "approved",
        "changed_by": None,
        "changed_at": None,
        "reason": None,
    }
    defaults.update(overrides)
    return PaymentHistory(**defaults)


# ============================================================
# PAYMENT
# ============================================================


class TestPayment:
    def test_create_payment(self):
        payment = _make_payment()
        assert payment.payment_no == "PAY-001"
        assert payment.amount == 1500.0
        assert payment.status == "pending"
        assert payment.currency == "THB"

    def test_payment_tablename(self):
        assert Payment.__tablename__ == "m_payment"

    def test_payment_defaults(self):
        payment = _make_payment(amount=0, amount_received=0, change_amount=0)
        assert payment.amount == 0
        assert payment.amount_received == 0
        assert payment.change_amount == 0
        assert payment.exchange_rate == 1
        assert payment.refunded_amount == 0

    def test_payment_with_overrides(self):
        payment = _make_payment(payment_no="PAY-002", status="approved", amount=2500.0)
        assert payment.payment_no == "PAY-002"
        assert payment.status == "approved"
        assert payment.amount == 2500.0

    def test_payment_with_uuid_fields(self):
        uid = uuid4()
        payment = _make_payment(invoice_id=uid, customer_id=uid)
        assert payment.invoice_id == uid
        assert payment.customer_id == uid


# ============================================================
# RECEIPT
# ============================================================


class TestReceipt:
    def test_create_receipt(self):
        receipt = _make_receipt()
        assert receipt.receipt_no == "RCT-001"
        assert receipt.receipt_type == "standard"
        assert receipt.amount == 1500.0
        assert receipt.status == "active"

    def test_receipt_tablename(self):
        assert Receipt.__tablename__ == "m_receipt"

    def test_receipt_defaults(self):
        receipt = _make_receipt(amount=0, currency="THB")
        assert receipt.amount == 0
        assert receipt.currency == "THB"
        assert receipt.amount_in_words_th is None
        assert receipt.amount_in_words_en is None

    def test_receipt_with_overrides(self):
        receipt = _make_receipt(receipt_no="RCT-002", receipt_type="refund")
        assert receipt.receipt_no == "RCT-002"
        assert receipt.receipt_type == "refund"


# ============================================================
# PAYMENT HISTORY
# ============================================================


class TestPaymentHistory:
    def test_create_history(self):
        history = _make_payment_history()
        assert history.from_status == "pending"
        assert history.to_status == "approved"
        assert history.reason is None

    def test_history_tablename(self):
        assert PaymentHistory.__tablename__ == "m_payment_history"

    def test_history_with_reason(self):
        history = _make_payment_history(reason="Approved by manager")
        assert history.reason == "Approved by manager"

    def test_history_with_overrides(self):
        history = _make_payment_history(from_status="approved", to_status="refunded")
        assert history.from_status == "approved"
        assert history.to_status == "refunded"

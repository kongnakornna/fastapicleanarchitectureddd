from app.modules.email.domain.entities.email_config import EmailConfig
from app.modules.email.domain.entities.email_log import EmailLog


def _make_email_log(**overrides):
    defaults = {
        "to_address": "test@example.com",
        "cc": None,
        "bcc": None,
        "subject": "Test Subject",
        "body": "Test body content",
        "status": "pending",
        "error_message": None,
        "sent_at": None,
    }
    defaults.update(overrides)
    return EmailLog(**defaults)


def _make_email_config(**overrides):
    defaults = {
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "user@example.com",
        "from_email": "sender@example.com",
        "from_name": "Test Sender",
        "is_active": True,
    }
    defaults.update(overrides)
    return EmailConfig(**defaults)


# ============================================================
# EMAIL LOG
# ============================================================


class TestEmailLog:
    def test_create_email_log(self):
        log = _make_email_log()
        assert log.to_address == "test@example.com"
        assert log.subject == "Test Subject"
        assert log.body == "Test body content"
        assert log.status == "pending"

    def test_email_log_tablename(self):
        assert EmailLog.__tablename__ == "m_email_log"

    def test_email_log_defaults(self):
        log = _make_email_log(to_address="", subject="")
        assert log.to_address == ""
        assert log.cc is None
        assert log.bcc is None
        assert log.error_message is None
        assert log.sent_at is None

    def test_email_log_with_overrides(self):
        log = _make_email_log(to_address="other@example.com", status="sent")
        assert log.to_address == "other@example.com"
        assert log.status == "sent"


# ============================================================
# EMAIL CONFIG
# ============================================================


class TestEmailConfig:
    def test_create_email_config(self):
        config = _make_email_config()
        assert config.smtp_host == "smtp.example.com"
        assert config.smtp_port == 587
        assert config.smtp_user == "user@example.com"
        assert config.from_email == "sender@example.com"
        assert config.from_name == "Test Sender"
        assert config.is_active is True

    def test_email_config_tablename(self):
        assert EmailConfig.__tablename__ == "m_email_config"

    def test_email_config_defaults(self):
        config = _make_email_config(smtp_host="", is_active=False)
        assert config.smtp_host == ""
        assert config.is_active is False

    def test_email_config_with_overrides(self):
        config = _make_email_config(smtp_host="smtp.gmail.com", smtp_port=465)
        assert config.smtp_host == "smtp.gmail.com"
        assert config.smtp_port == 465

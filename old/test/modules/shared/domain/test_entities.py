from app.modules.shared.domain.entities import DomainError


class TestDomainError:
    def test_stores_message(self):
        exc = DomainError("something went wrong")
        assert exc.message == "something went wrong"

    def test_is_exception(self):
        exc = DomainError("fail")
        assert isinstance(exc, Exception)

    def test_str_representation(self):
        exc = DomainError("msg")
        assert str(exc) == "msg"

    def test_can_be_raised_and_caught(self):
        import pytest

        with pytest.raises(DomainError, match="boom"):
            raise DomainError("boom")

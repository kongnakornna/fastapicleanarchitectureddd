import pytest

from app.modules.example.domain.entities import Example
from app.modules.example.domain.value_objects import FullName
from app.modules.shared.presentation.exceptions import DomainError


def _make_example(**overrides):
    defaults = {"full_name": FullName(first_name="Jane", last_name="Smith")}
    defaults.update(overrides)
    return Example(**defaults)


class TestExampleConstruction:
    def test_create_with_valid_data(self):
        ex = _make_example()
        assert str(ex.full_name) == "Jane Smith"

    def test_message_property(self):
        ex = _make_example()
        assert ex.message == "Hello, Jane Smith!"


class TestExampleValidation:
    def test_rejects_empty_full_name(self):
        with pytest.raises(DomainError, match="Full name is required"):
            Example(full_name="")

    def test_rejects_john_doe(self):
        with pytest.raises(DomainError, match="John Doe name is not allowed"):
            _make_example(full_name=FullName(first_name="John", last_name="Doe"))

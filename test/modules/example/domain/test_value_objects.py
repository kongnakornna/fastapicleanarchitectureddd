import pytest

from app.modules.example.domain.value_objects import FullName
from app.modules.shared.presentation.exceptions import DomainError


class TestFullNameConstruction:
    def test_stores_names(self):
        fn = FullName(first_name="John", last_name="Doe")
        assert fn.first_name == "John"
        assert fn.last_name == "Doe"

    def test_capitalizes_names(self):
        fn = FullName(first_name="jane", last_name="sMITH")
        assert fn.first_name == "Jane"
        assert fn.last_name == "Smith"

    def test_strips_and_capitalizes(self):
        fn = FullName(first_name="  alice  ", last_name="  bob  ")
        assert fn.first_name == "alice"
        assert fn.last_name == "bob"


class TestFullNameValidation:
    def test_rejects_empty_first_name(self):
        with pytest.raises(DomainError, match="required"):
            FullName(first_name="", last_name="Doe")

    def test_rejects_empty_last_name(self):
        with pytest.raises(DomainError, match="required"):
            FullName(first_name="John", last_name="")

    def test_both_empty(self):
        with pytest.raises(DomainError, match="required"):
            FullName(first_name="", last_name="")


class TestFullNameEquality:
    def test_eq_same_values(self):
        a = FullName(first_name="John", last_name="Doe")
        b = FullName(first_name="John", last_name="Doe")
        assert a == b

    def test_eq_different_values(self):
        a = FullName(first_name="John", last_name="Doe")
        b = FullName(first_name="Jane", last_name="Doe")
        assert a != b

    def test_str_representation(self):
        fn = FullName(first_name="John", last_name="Doe")
        assert str(fn) == "John Doe"

    def test_eq_with_string(self):
        fn = FullName(first_name="John", last_name="Doe")
        assert fn == "John Doe"

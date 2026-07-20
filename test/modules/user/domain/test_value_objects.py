import pytest

from app.modules.shared.presentation.exceptions import DomainError
from app.modules.user.domain.value_objects import Email, Name, Phone

# ============================================================
# Name
# ============================================================


class TestNameValidation:
    def test_accepts_valid_name(self):
        name = Name(first_name="John", last_name="Doe")
        assert name.first_name == "John"
        assert name.last_name == "Doe"
        assert name.preferred_name == "John"

    def test_accepts_with_preferred_name(self):
        name = Name(first_name="John", last_name="Doe", preferred_name="Johnny")
        assert name.preferred_name == "Johnny"

    def test_strips_and_capitalizes(self):
        name = Name(first_name="  john  ", last_name="  doe  ")
        assert name.first_name == "John"
        assert name.last_name == "Doe"

    def test_rejects_empty_first_name(self):
        with pytest.raises(DomainError, match="First name and last name are required"):
            Name(first_name="", last_name="Doe")

    def test_rejects_empty_last_name(self):
        with pytest.raises(DomainError, match="First name and last name are required"):
            Name(first_name="John", last_name="")

    def test_rejects_short_first_name(self):
        with pytest.raises(DomainError, match="First name must be at least 3 characters"):
            Name(first_name="Jo", last_name="Doe")

    def test_rejects_short_last_name(self):
        with pytest.raises(DomainError, match="Last name must be at least 3 characters"):
            Name(first_name="John", last_name="Do")

    def test_rejects_long_first_name(self):
        with pytest.raises(DomainError, match="First name must not exceed 100 characters"):
            Name(first_name="A" * 101, last_name="Doe")

    def test_rejects_long_last_name(self):
        with pytest.raises(DomainError, match="Last name must not exceed 100 characters"):
            Name(first_name="John", last_name="D" * 101)

    def test_rejects_special_characters_in_first_name(self):
        with pytest.raises(DomainError, match="First name must contain only letters"):
            Name(first_name="John123", last_name="Doe")

    def test_rejects_special_characters_in_last_name(self):
        with pytest.raises(DomainError, match="Last name must contain only letters"):
            Name(first_name="John", last_name="D@e")

    def test_accepts_hyphen_and_apostrophe(self):
        name = Name(first_name="Mary-Anne", last_name="O'Brien")
        assert name.first_name == "Mary-anne"
        assert name.last_name == "O'brien"

    def test_str_representation(self):
        name = Name(first_name="John", last_name="Doe", preferred_name="Johnny")
        assert str(name) == "John Doe (Johnny)"

    def test_eq_same_values(self):
        a = Name(first_name="John", last_name="Doe")
        b = Name(first_name="John", last_name="Doe")
        assert a == b


# ============================================================
# Email
# ============================================================


class TestEmailValidation:
    def test_accepts_valid_email(self):
        email = Email(email="user@localhost.com")
        assert str(email) == "user@localhost.com"

    def test_normalizes_to_lowercase(self):
        email = Email(email="User@Localhost.Com")
        assert str(email) == "user@localhost.com"

    def test_strips_whitespace(self):
        email = Email(email="  user@localhost.com  ")
        assert str(email) == "user@localhost.com"

    def test_rejects_empty_email(self):
        with pytest.raises(DomainError, match="Email is required"):
            Email(email="")

    def test_rejects_invalid_format(self):
        with pytest.raises(DomainError, match="Invalid email format"):
            Email(email="not-an-email")

    def test_rejects_local_part_starts_with_dot(self):
        with pytest.raises(DomainError, match="local part must not start or end with a dot"):
            Email(email=".user@localhost.com")

    def test_rejects_local_part_ends_with_dot(self):
        with pytest.raises(DomainError, match="Invalid email format"):
            Email(email="user.@localhost.com")

    def test_rejects_consecutive_dots_in_local(self):
        with pytest.raises(DomainError, match="local part must not contain consecutive dots"):
            Email(email="user..name@localhost.com")

    def test_rejects_consecutive_dots_in_domain(self):
        with pytest.raises(DomainError, match="Invalid email format"):
            Email(email="user@localhost..com")

    def test_rejects_disallowed_domain(self):
        with pytest.raises(DomainError, match="is not allowed"):
            Email(email="user@blocked.com")

    def test_eq_same_email(self):
        a = Email(email="user@localhost.com")
        b = Email(email="USER@localhost.com")
        assert a == b

    def test_str_representation(self):
        email = Email(email="user@localhost.com")
        assert str(email) == "user@localhost.com"


# ============================================================
# Phone
# ============================================================


class TestPhoneValidation:
    def test_accepts_valid_phone(self):
        phone = Phone(phone="+66812345678")
        assert str(phone) == "+66812345678"

    def test_adds_plus_prefix_if_missing(self):
        phone = Phone(phone="66812345678")
        assert str(phone) == "+66812345678"

    def test_strips_spaces_and_dashes(self):
        phone = Phone(phone="+668-123-45678")
        assert str(phone) == "+66812345678"

    def test_rejects_empty_phone(self):
        with pytest.raises(DomainError):
            Phone(phone="")

    def test_rejects_non_digit_characters(self):
        with pytest.raises(DomainError, match="Phone number must contain only digits"):
            Phone(phone="+66abc12345")

    def test_rejects_too_short(self):
        with pytest.raises(DomainError, match="between 7 and 15 digits"):
            Phone(phone="+123456")

    def test_rejects_too_long(self):
        with pytest.raises(DomainError, match="between 7 and 15 digits"):
            Phone(phone="+12345678901234567")

    def test_eq_same_phone(self):
        a = Phone(phone="+66812345678")
        b = Phone(phone="+668 123 45678")
        assert a == b

    def test_str_representation(self):
        phone = Phone(phone="+66812345678")
        assert str(phone) == "+66812345678"

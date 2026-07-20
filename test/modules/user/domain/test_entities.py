from datetime import date

import pytest

from app.modules.shared.application.enums import Role
from app.modules.shared.presentation.exceptions import DomainError
from app.modules.user.application.enums import Gender, UserStatus
from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Email, Name, Phone


def _make_user(**overrides):
    defaults = {
        "name": Name(first_name="John", last_name="Doe"),
        "username": "johndoe",
        "gender": Gender.MALE,
        "birthdate": date(1990, 1, 15),
        "email": "john@localhost.com",
        "phone": "+66812345678",
        "password": "secret123",
    }
    defaults.update(overrides)
    return User(**defaults)


# ============================================================
# Construction & normalization
# ============================================================


class TestUserConstruction:
    def test_create_with_valid_data(self):
        user = _make_user()
        assert user.username == "johndoe"
        assert user.email == "john@localhost.com"
        assert user.phone == "+66812345678"
        assert user.status == UserStatus.ACTIVE
        assert user.role == Role.USER

    def test_normalizes_string_email_to_email_object(self):
        user = _make_user(email="john@localhost.com")
        assert isinstance(user.email, Email)

    def test_normalizes_string_phone_to_phone_object(self):
        user = _make_user(phone="+66812345678")
        assert isinstance(user.phone, Phone)

    def test_defaults_to_active_status(self):
        user = _make_user()
        assert user.status == UserStatus.ACTIVE

    def test_defaults_to_user_role(self):
        user = _make_user()
        assert user.role == Role.USER


# ============================================================
# Validation
# ============================================================


class TestUserValidation:
    def test_rejects_underage_user(self):
        today = date.today()
        underage_birthdate = today.replace(year=today.year - 17)
        with pytest.raises(DomainError, match="at least 18 years old"):
            _make_user(birthdate=underage_birthdate)

    def test_accepts_exactly_18_years_old(self):
        today = date.today()
        exact_18 = today.replace(year=today.year - 18)
        user = _make_user(birthdate=exact_18)
        assert user.birthdate == exact_18

    def test_skips_age_validation_when_birthdate_is_none(self):
        user = _make_user(birthdate=None)
        assert user.birthdate is None

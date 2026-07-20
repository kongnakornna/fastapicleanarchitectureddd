from app.modules.shared.application.enums import (
    ApplicationEnvironment,
    ResponseMessages,
    Role,
)


class TestApplicationEnvironment:
    def test_dev_value(self):
        assert ApplicationEnvironment.DEV == "dev"

    def test_homolog_value(self):
        assert ApplicationEnvironment.HOMOLOG == "homolog"

    def test_production_value(self):
        assert ApplicationEnvironment.PRODUCTION == "production"

    def test_is_str_enum(self):
        assert isinstance(ApplicationEnvironment.DEV, str)

    def test_all_members(self):
        assert len(ApplicationEnvironment) == 3


class TestRole:
    def test_admin_value(self):
        assert Role.ADMIN == "admin"

    def test_manager_value(self):
        assert Role.MANAGER == "manager"

    def test_user_value(self):
        assert Role.USER == "user"

    def test_is_str_enum(self):
        assert isinstance(Role.ADMIN, str)

    def test_all_members(self):
        assert len(Role) == 3


class TestResponseMessages:
    def test_success_message(self):
        assert ResponseMessages.SUCCESS.value == "Request processed successfully"

    def test_created_message(self):
        assert ResponseMessages.CREATED.value == "Resource created successfully"

    def test_internal_error_message(self):
        assert ResponseMessages.INTERNAL_ERROR.value == "Internal processing error"

    def test_is_not_empty(self):
        assert len(ResponseMessages) > 0

    def test_all_values_are_strings(self):
        for msg in ResponseMessages:
            assert isinstance(msg.value, str)

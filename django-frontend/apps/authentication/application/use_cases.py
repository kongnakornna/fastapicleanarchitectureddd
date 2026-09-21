from dataclasses import dataclass

from ..infrastructure.fastapi_auth_client import AuthAPIError, FastAPIAuthClient


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
    username: str


class LoginUseCase:
    def __init__(self, client=None):
        self.client = client or FastAPIAuthClient()

    def execute(self, username, password):
        try:
            data = self.client.login(username, password)
        except AuthAPIError:
            raise
        except Exception as e:
            raise AuthAPIError(500, str(e)) from e
        return LoginResult(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", ""),
            username=data.get("username", username),
        )


class SignUpUseCase:
    def __init__(self, client=None):
        self.client = client or FastAPIAuthClient()

    def execute(self, payload):
        return self.client.sign_up(payload)


class ForgotPasswordUseCase:
    def __init__(self, client=None):
        self.client = client or FastAPIAuthClient()

    def execute(self, email):
        return self.client.forgot_password(email)


class ResetPasswordUseCase:
    def __init__(self, client=None):
        self.client = client or FastAPIAuthClient()

    def execute(self, code, new_password, confirm_password):
        return self.client.reset_password(code, new_password, confirm_password)


class TwoStepCodeUseCase:
    def __init__(self, client=None):
        self.client = client or FastAPIAuthClient()

    def execute(self, code):
        return self.client.verify_two_step_code(code)


class TwoStepVerificationUseCase:
    def __init__(self, client=None):
        self.client = client or FastAPIAuthClient()

    def execute(self, country_code, phone_number):
        return self.client.setup_two_step(country_code, phone_number)

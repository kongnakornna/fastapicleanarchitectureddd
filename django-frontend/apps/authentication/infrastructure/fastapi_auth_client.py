from apps.shared.infrastructure.fastapi_client import fastapi


class AuthAPIError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(message)


class FastAPIAuthClient:
    """Proxy to FastAPI auth endpoints."""

    def _call(self, method, path, **kw):
        try:
            resp = fastapi.request(method, path, **kw)
            return resp.json() if resp.content else {}
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", 500)
            msg = getattr(e, "detail", None) or str(e)
            # try extract FastAPI detail
            resp = getattr(e, "response", None)
            if resp is not None:
                try:
                    data = resp.json()
                    msg = data.get("detail") or data.get("message") or msg
                except Exception:
                    pass
            raise AuthAPIError(status, msg)

    def login(self, username, password):
        return self._call("POST", "/auth/login", json={
            "username": username, "password": password,
        })

    def sign_up(self, payload):
        return self._call("POST", "/auth/register", json=payload)

    def forgot_password(self, email):
        return self._call("POST", "/auth/forgot-password", json={"email": email})

    def reset_password(self, code, new_password, confirm_password):
        return self._call("POST", "/auth/reset-password", json={
            "code": code, "newPassword": new_password, "confirmPassword": confirm_password,
        })

    def verify_two_step_code(self, code):
        return self._call("POST", "/auth/two-step/verify", json={"code": code})

    def setup_two_step(self, country_code, phone_number):
        return self._call("POST", "/auth/two-step/setup", json={
            "countryCode": country_code, "phoneNumber": phone_number,
        })

    def logout_all(self, access_token):
        return self._call("POST", "/auth/logout-all", token=access_token)

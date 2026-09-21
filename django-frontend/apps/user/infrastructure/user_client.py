from apps.shared.infrastructure.fastapi_client import fastapi

from ..domain.entities import Role, User


class UserClient:
    """Repository impl — proxy to FastAPI users/roles endpoints."""

    def __init__(self, token: str | None = None):
        self.token = token

    # ─── Users ─────────────────────────
    def list_users(self, *, page: int = 1, q: str = "") -> dict:
        params = {"page": page}
        if q:
            params["q"] = q
        data = fastapi.json("GET", "/users", token=self.token, params=params)
        return {
            "items": [self._to_user(x) for x in data.get("items", [])],
            "total": data.get("total", 0),
            "page": page,
        }

    def get_user(self, user_id: int) -> User:
        data = fastapi.json("GET", f"/users/{user_id}", token=self.token)
        return self._to_user(data)

    def create_user(self, payload: dict) -> User:
        data = fastapi.json("POST", "/users", token=self.token, json=payload)
        return self._to_user(data)

    def update_user(self, user_id: int, payload: dict) -> User:
        data = fastapi.json("PUT", f"/users/{user_id}", token=self.token, json=payload)
        return self._to_user(data)

    def delete_user(self, user_id: int) -> None:
        fastapi.request("DELETE", f"/users/{user_id}", token=self.token)

    # ─── Roles ─────────────────────────
    def list_roles(self) -> list[Role]:
        data = fastapi.json("GET", "/roles", token=self.token)
        return [self._to_role(x) for x in data]

    def get_role(self, role_id: int) -> Role:
        data = fastapi.json("GET", f"/roles/{role_id}", token=self.token)
        return self._to_role(data)

    def create_role(self, payload: dict) -> Role:
        data = fastapi.json("POST", "/roles", token=self.token, json=payload)
        return self._to_role(data)

    def update_role(self, role_id: int, payload: dict) -> Role:
        data = fastapi.json("PUT", f"/roles/{role_id}", token=self.token, json=payload)
        return self._to_role(data)

    def delete_role(self, role_id: int) -> None:
        fastapi.request("DELETE", f"/roles/{role_id}", token=self.token)

    # ─── Mappers ───────────────────────
    @staticmethod
    def _to_user(d: dict) -> User:
        return User(
            id=d["id"], username=d["username"], email=d["email"],
            full_name=d.get("fullName", d.get("full_name", "")),
            phone_number=d.get("phoneNumber", d.get("phone_number", "")),
            role_id=d.get("roleId", d.get("role_id", 0)),
            role_name=d.get("roleName", d.get("role_name", "")),
            is_active=d.get("isActive", d.get("is_active", True)),
        )

    @staticmethod
    def _to_role(d: dict) -> Role:
        return Role(
            id=d["id"], name=d["name"],
            description=d.get("description", ""),
            permissions=d.get("permissions", []),
        )

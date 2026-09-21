from apps.shared.infrastructure.fastapi_client import fastapi

from ..domain.entities import ApiKey


class KeyClient:
    def __init__(self, token: str | None = None):
        self.token = token

    def list_keys(self) -> list[ApiKey]:
        data = fastapi.json("GET", "/keys", token=self.token)
        return [self._to_key(x) for x in data]

    def get_key(self, key_id: int) -> ApiKey:
        return self._to_key(fastapi.json("GET", f"/keys/{key_id}", token=self.token))

    def create_key(self, name: str) -> dict:
        return fastapi.json("POST", "/keys", token=self.token, json={"name": name})

    def revoke_key(self, key_id: int) -> None:
        fastapi.request("DELETE", f"/keys/{key_id}", token=self.token)

    @staticmethod
    def _to_key(d: dict) -> ApiKey:
        return ApiKey(
            id=d["id"], name=d["name"], prefix=d.get("prefix", ""),
            created_at=d.get("createdAt", ""),
            last_used=d.get("lastUsed", ""),
            expires_at=d.get("expiresAt"),
            is_active=d.get("isActive", True),
        )

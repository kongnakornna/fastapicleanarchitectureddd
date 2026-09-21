from apps.shared.infrastructure.fastapi_client import fastapi

from ..domain.entities import Notification


class NotificationClient:
    def __init__(self, token: str | None = None):
        self.token = token

    def list(self, *, unread_only: bool = False) -> list[Notification]:
        params = {"unreadOnly": True} if unread_only else None
        data = fastapi.json("GET", "/notifications", token=self.token, params=params)
        return [self._to_notif(x) for x in data]

    def unread_count(self) -> int:
        try:
            return fastapi.json("GET", "/notifications/unread-count", token=self.token).get("count", 0)
        except Exception:
            return 0

    def mark_read(self, notif_id: int) -> None:
        fastapi.request("POST", f"/notifications/{notif_id}/read", token=self.token)

    def mark_all_read(self) -> None:
        fastapi.request("POST", "/notifications/read-all", token=self.token)

    @staticmethod
    def _to_notif(d: dict) -> Notification:
        return Notification(
            id=d["id"], title=d["title"], body=d.get("body", ""),
            category=d.get("category", "system"),
            is_read=d.get("isRead", False),
            created_at=d.get("createdAt", ""),
        )

import websockets
from django.conf import settings


class FastAPIWebSocketClient:
    """Async proxy client to FastAPI WebSocket endpoint."""

    def __init__(self, path: str, token: str | None = None):
        base = settings.FASTAPI_BASE_URL.replace("http://", "ws://").replace("https://", "wss://")
        self.url = f"{base.rstrip('/')}{path}"
        self.token = token

    async def connect(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return await websockets.connect(self.url, extra_headers=headers)

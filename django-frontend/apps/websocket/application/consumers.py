import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

from ..infrastructure.fastapi_ws_client import FastAPIWebSocketClient


class FastAPIProxyConsumer(AsyncWebsocketConsumer):
    """Bidirectional proxy: Browser ↔ Django Channels ↔ FastAPI WS."""

    async def connect(self):
        self.path = self.scope["url_route"]["kwargs"].get("path", "/ws")
        token = self.scope["session"].get("access_token")
        try:
            self.remote = await FastAPIWebSocketClient(
                f"/ws/{self.path}", token=token,
            ).connect()
        except Exception:
            await self.close(code=1011)
            return

        await self.accept()
        self.pump_task = asyncio.create_task(self._pump_remote_to_client())

    async def disconnect(self, code):
        if hasattr(self, "pump_task"):
            self.pump_task.cancel()
        if hasattr(self, "remote"):
            await self.remote.close()

    async def receive(self, text_data=None, bytes_data=None):
        if hasattr(self, "remote"):
            await self.remote.send(text_data or bytes_data)

    async def _pump_remote_to_client(self):
        try:
            async for msg in self.remote:
                await self.send(text_data=msg)
        except Exception:
            await self.close()

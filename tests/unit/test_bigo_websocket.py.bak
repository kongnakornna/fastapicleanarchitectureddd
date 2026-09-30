"""Unit tests for WebSocketManager"""
from __future__ import annotations
import pytest

from app.modules.bigo.infrastructure.websocket_manager import WebSocketManager

pytestmark = pytest.mark.unit


class FakeWS:
    def __init__(self): self.sent: list[str] = []
    async def send_text(self, s): self.sent.append(s)


@pytest.mark.asyncio
async def test_connect_disconnect():
    m = WebSocketManager()
    ws = FakeWS()
    conn = await m.connect(ws, tenant_id="t1")
    assert conn.id in m._conns
    await m.disconnect(conn.id)
    assert conn.id not in m._conns


@pytest.mark.asyncio
async def test_broadcast_room():
    m = WebSocketManager()
    a, b = FakeWS(), FakeWS()
    await m.connect(a, tenant_id="t1", rooms={"room1"})
    await m.connect(b, tenant_id="t1", rooms={"room2"})
    n = await m.broadcast({"x": 1}, room="room1")
    assert n == 1
    assert len(a.sent) == 1
    assert len(b.sent) == 0


@pytest.mark.asyncio
async def test_max_per_tenant():
    m = WebSocketManager(max_connections_per_tenant=2)
    await m.connect(FakeWS(), tenant_id="t1")
    await m.connect(FakeWS(), tenant_id="t1")
    with pytest.raises(RuntimeError):
        await m.connect(FakeWS(), tenant_id="t1")


@pytest.mark.asyncio
async def test_stats():
    m = WebSocketManager()
    await m.connect(FakeWS(), tenant_id="t1")
    s = m.stats()
    assert s["connections"] == 1
    assert "t1" in s["tenants"]

"""TH: WebSocket test — ครบ flow | EN: full flow WebSocket test"""
import asyncio
import sys

import httpx
import websockets


BASE = "http://localhost:8000"
WS = "ws://localhost:8000/api/v1/websocket/connect/"
EMAIL = "admin@example.com"
PASSWORD = "MyP@ssword123"


async def main() -> None:
    print("━" * 60)
    print("STEP 1: Sign-up (best-effort)")
    print("━" * 60)
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{BASE}/api/v1/authentication/sign-up/",
            json={
                "full_name": "Admin User",
                "username": "admin",
                "email": EMAIL,
                "password": PASSWORD,
                "confirm_password": PASSWORD,
                "agree_terms": True,
            },
        )
        print(f"Sign-up status: {r.status_code}")
        print(f"Sign-up body:   {r.text[:300]}")

    print()
    print("━" * 60)
    print("STEP 2: Login")
    print("━" * 60)
    async with httpx.AsyncClient(timeout=10) as client:
        # ⚠️ FIX: ต้องมี grant_type=password สำหรับ OAuth2PasswordRequestFormStrict
        r = await client.post(
            f"{BASE}/api/v1/authentication/login/",
            data={
                "username": EMAIL,
                "password": PASSWORD,
                "grant_type": "password",       # ← ← ← ตัวที่ขาดไป
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        print(f"Login status: {r.status_code}")
        print(f"Login body:   {r.text[:500]}")
        print(f"Set-Cookie:   {dict(r.cookies)}")

        if r.status_code != 200:
            print("❌ LOGIN FAILED — cannot continue")
            sys.exit(1)

        session_id = r.cookies.get("hub_session_id")
        access_token = r.cookies.get("access_token")

        if not session_id and not access_token:
            print("❌ No session cookie returned")
            sys.exit(1)

        print(f"✓ Session ID: {session_id[:12] if session_id else 'N/A'}...")

    print()
    print("━" * 60)
    print("STEP 3: WebSocket Connect")
    print("━" * 60)
    headers = {}
    if session_id:
        headers["Cookie"] = f"hub_session_id={session_id}"
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    print(f"URL:     {WS}")
    print(f"Headers: {list(headers.keys())}")

    try:
        async with websockets.connect(
            WS,
            additional_headers=headers,
            open_timeout=10,
        ) as ws:
            print("✅ WEBSOCKET CONNECTED")

            await ws.send("ping")
            print("📤 Sent: ping")

            try:
                async with asyncio.timeout(5):
                    msg = await ws.recv()
                    print(f"📨 Received: {msg}")
            except TimeoutError:
                print("⏱️  No message in 5s (server may not echo)")

            await asyncio.sleep(2)

        print("🔌 WebSocket closed normally")
        print()
        print("✅ ALL TESTS PASSED")

    except websockets.exceptions.InvalidStatus as e:
        print(f"❌ Handshake rejected: {e}")
        print(f"   Response: {e.response}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ WebSocket error: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

# ==============================================================
# WebSocket test script
# Steps:
# 1. Sign-up
# 2. Login
# 3. WebSocket Connect
# uv run python test_ws.py

# 1. Server รันอยู่ไหม
# curl http://localhost:8000/health

# 2. ลอง login ผ่าน curl
# curl -X POST http://localhost:8000/api/v1/authentication/login/ `
#   -H "Content-Type: application/x-www-form-urlencoded" `
#   -d "username=admin@example.com&password=MyP@ssword123&grant_type=password" `
#   -c cookies.txt -v

# 3. ดู cookie
# Get-Content cookies.txt

# ==============================================================

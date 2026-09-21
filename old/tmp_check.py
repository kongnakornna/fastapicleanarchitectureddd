from app.core.database import pg_engine
from sqlalchemy import text

conn = pg_engine.connect()

# Check sessions
result = conn.execute(text("SELECT id, user_id, device, user_agent FROM app_sessions ORDER BY created_at DESC LIMIT 3"))
print("=== SESSIONS ===")
for row in result:
    print(f"  session_id={row[0]}  user_id={row[1]}  device={row[2]}  ua={row[3]}")

# Check refresh tokens
result = conn.execute(text("SELECT id, session_id, hashed_jti FROM app_refresh_tokens ORDER BY created_at DESC LIMIT 3"))
print("\n=== REFRESH TOKENS ===")
for row in result:
    print(f"  rt_id={row[0]}  session_id={row[1]}  hashed_jti={row[2]}")

# Check access tokens
result = conn.execute(text("SELECT id, refresh_id, hashed_jti FROM app_access_tokens ORDER BY created_at DESC LIMIT 3"))
print("\n=== ACCESS TOKENS ===")
for row in result:
    print(f"  at_id={row[0]}  refresh_id={row[1]}  hashed_jti={row[2]}")

conn.close()

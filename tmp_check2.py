from app.core.database import pg_engine
from sqlalchemy import text

conn = pg_engine.connect()

# Check revoked/blacklisted status
result = conn.execute(text("""
    SELECT at.id, at.hashed_jti, at.revoked, rt.revoked as rt_revoked, s.blacklisted, s.user_id
    FROM app_access_tokens at
    JOIN app_refresh_tokens rt ON at.refresh_id = rt.id
    JOIN app_sessions s ON rt.session_id = s.id
    ORDER BY at.created_at DESC LIMIT 5
"""))
print("=== TOKEN STATUS ===")
for row in result:
    print(f"  at_id={row[0]}  hashed_jti={row[1][:16]}...  at_revoked={row[2]}  rt_revoked={row[3]}  blacklisted={row[4]}  user_id={row[5]}")

conn.close()

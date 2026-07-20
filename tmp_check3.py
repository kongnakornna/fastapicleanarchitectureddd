from app.core.database import pg_async_engine
from sqlalchemy import text
import asyncio

async def check():
    async with pg_async_engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT at.id, at.hashed_jti, at.revoked, rt.revoked as rt_revoked, 
                   s.blacklisted, s.user_id, s.id as session_id
            FROM app_access_tokens at
            JOIN app_refresh_tokens rt ON at.refresh_id = rt.id
            JOIN app_sessions s ON rt.session_id = s.id
            WHERE at.hashed_jti = '361e6be3af1a374c8b19ea595424b480b1294b6f51c3b76f3aaa550f84d766ea'
        """))
        rows = result.fetchall()
        print(f"Found {len(rows)} rows for hashed_jti check")
        for row in rows:
            print(f"  at_revoked={row[2]}  rt_revoked={row[3]}  blacklisted={row[4]}  user_id={row[5]}  session_id={row[6]}")
            print(f"  user_id type: {type(row[5])}")

asyncio.run(check())

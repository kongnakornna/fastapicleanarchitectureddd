import asyncio

from sqlalchemy import text

from app.core.database import get_session
from app.core.security import hash_password


async def main():
    for session in get_session():
        existing = session.execute(
            text("SELECT id FROM app_users WHERE username = :u"),
            {"u": "demoadmin"},
        ).fetchone()
        if existing:
            session.execute(
                text("DELETE FROM app_users WHERE username = :u"),
                {"u": "demoadmin"},
            )
            print("Deleted existing user 'demoadmin'.")

        hashed_pw = await hash_password("Demo@1234")
        session.execute(
            text("""
                INSERT INTO app_users (first_name, last_name, preferred_name, username, gender, birthdate, email, hashed_password, role, status, is_active)
                VALUES (:fn, :ln, :pn, :u, :g, :b, :e, :hp, :r, :s, :ia)
            """),
            {
                "fn": "Demo",
                "ln": "Admin",
                "pn": "Admin",
                "u": "demoadmin",
                "g": "MALE",
                "b": "1990-01-01",
                "e": "demoadmin@localhost.com",
                "hp": hashed_pw,
                "r": "ADMIN",
                "s": "ACTIVE",
                "ia": True,
            },
        )
        print("Admin user 'demoadmin' created with password 'Demo@1234'.")


if __name__ == "__main__":
    asyncio.run(main())

"""Diagnose login 401 — check if user exists and password matches."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app.core.database import pg_engine  # noqa: E402
from app.core.security import verify_password  # noqa: E402
from app.modules.user.infrastructure.models import UserModel  # noqa: E402


def main() -> None:
    email = "admin@example.com"
    plain_password = "MyP@ssword123"

    with pg_engine.connect() as conn:
        # 1. All users in DB
        all_users = conn.execute(
            select(UserModel.id, UserModel.email, UserModel.username, UserModel.role)
        ).all()
        print(f"Total users in erp_users: {len(all_users)}")
        for row in all_users:
            print(f"  id={row.id}  email={row.email}  username={row.username}  role={row.role}")

        # 2. Find by email
        user = conn.execute(
            select(UserModel).where(UserModel.email == email)
        ).scalar_one_or_none()

        if user is None:
            print(f"\n❌ User '{email}' NOT FOUND")
            print("→ Need to sign up first, or the seeder didn't run.")
            return

        print(f"\n✅ User '{email}' found: id={user.id}")

        # 3. Verify password
        match = verify_password(plain_password, user.hashed_password)
        print(f"Password '{plain_password}' matches stored hash: {match}")
        if not match:
            print("→ Password mismatch. Try a different password.")


if __name__ == "__main__":
    main()

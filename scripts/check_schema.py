"""Check DB schema for FK type mismatches."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.core.database import pg_engine  # noqa: E402


def main() -> None:
    with pg_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
        )
        tables = [row[0] for row in result]
        print("Tables:", tables)

        result = conn.execute(
            text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = 'erp_users' AND column_name = 'id'"
            )
        )
        print("erp_users.id:", [tuple(row) for row in result])

        result = conn.execute(
            text(
                "SELECT table_name, column_name, data_type "
                "FROM information_schema.columns "
                "WHERE table_name IN "
                "('erp_users','erp_keys','erp_authentications',"
                "'erp_refresh_tokens','erp_access_tokens') "
                "AND column_name IN "
                "('id','user_id','authentication_id','refresh_id',"
                "'created_by','updated_by') "
                "ORDER BY table_name, column_name"
            )
        )
        print("FK columns:")
        for row in result:
            print("  ", tuple(row))


if __name__ == "__main__":
    main()

"""Drop orphan erp_* enum types left behind by rolled-back CREATE TABLE."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.core.database import pg_engine  # noqa: E402

# Enum types created by the erp_* schema
_ENUMS = (
    "gender_enum",
    "role_enum",
    "user_status_enum",
    "online_status_enum",
    "notification_type_enum",
)


def main() -> None:
    with pg_engine.begin() as conn:
        for enum_name in _ENUMS:
            conn.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
            print(f"Dropped type (if existed): {enum_name}")


if __name__ == "__main__":
    main()
